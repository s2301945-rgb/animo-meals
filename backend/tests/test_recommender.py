from decimal import Decimal
import json
from functools import partial

from fastapi.testclient import TestClient
import httpx
from pydantic import SecretStr
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import limits, recommendations
from app.ai import MealPreferences, extract_preferences
from app.config import Settings
from app.database import Base, get_session
from app.import_menu import Dataset, apply_dataset
from app.main import app
from app.models import MenuItem, SavedPlan, SavedPlanItem, Stall

A = {'Authorization': 'Bearer ' + 'a' * 64}
B = {'Authorization': 'Bearer ' + 'b' * 64}


@pytest.fixture
def db_client():
    limits._buckets.clear()
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        stall = Stall(name='Test shop', location='Test location')
        other = Stall(name='Other test shop', location='Elsewhere')
        session.add_all([stall, other])
        session.flush()
        session.add_all([
            MenuItem(id=1, stall_id=stall.id, name='Chicken', description='Non-spicy', price=Decimal('60.50'), category='Main dish'),
            MenuItem(id=2, stall_id=stall.id, name='Rice', price=Decimal('15.00'), category='Side'),
            MenuItem(id=3, stall_id=stall.id, name='Water', price=Decimal('10.00'), category='Drink'),
            MenuItem(id=4, stall_id=other.id, name='Pork rice meal', description='Spicy', price=Decimal('50.00'), category='Main dish'),
            MenuItem(id=5, stall_id=stall.id, name='Retired chicken', price=Decimal('1.00'), category='Main dish', is_available=False),
        ])
        session.commit()

    def session_override():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = session_override
    with TestClient(app) as client:
        yield client, engine
    app.dependency_overrides.clear()
    engine.dispose()
    limits._buckets.clear()


def preferences(**overrides):
    return MealPreferences(**({'budget_php': None, 'preferred_food': 'chicken rice',
        'include_drink': True, 'avoid_spicy': True, 'prefer_same_stall': True, 'exclusions': ['pork']} | overrides))


def mock_groq(monkeypatch, handler):
    config = Settings(_env_file=None, groq_api_key=SecretStr('test-key'))
    monkeypatch.setattr(recommendations, 'extract_preferences', partial(
        extract_preferences, config=config, transport=httpx.MockTransport(handler)))


@pytest.mark.parametrize('prompt,food', [
    ('Chicken rice, non-spicy, and water', 'chicken rice'),
    ('Manok at kanin na hindi maanghang, may tubig', 'manok at kanin'),
    ('Manok kag kan-on, may tubig. Indi maanghang kag wala sing baboy.',
     'manok kag kan-on kag tubig'),
    ('Manok ug kan-on nga naay tubig. Ayaw og halang ug baboy.',
     'manok ug kan-on ug tubig'),
])
def test_ai_interpretation_becomes_exact_budget_combination(db_client, monkeypatch, prompt, food):
    client, engine = db_client
    if 'tubig' in food:
        with Session(engine) as session:
            session.add(MenuItem(stall_id=1, name='Cola', price=Decimal('5.00'), category='Drink'))
            session.commit()

    def provider(request):
        payload = json.loads(request.content)
        assert payload['messages'][-1] == {'role': 'user', 'content': prompt}
        assert payload['response_format']['json_schema']['strict'] is True
        return httpx.Response(200, json={'choices': [{
            'finish_reason': 'stop',
            'message': {'content': preferences(preferred_food=food).model_dump_json()},
        }]})

    mock_groq(monkeypatch, provider)
    response = client.post('/api/recommendations', json={'budget': '85.50', 'preferences': prompt})
    assert response.status_code == 200
    result = response.json()
    assert result['status'] == 'ok'
    assert len(result['suggestions']) == 1
    pick = result['suggestions'][0]
    assert [item['id'] for item in pick['items']] == [1, 2, 3]
    assert pick['total'] == '85.50' and pick['remaining'] == '0.00'
    assert result['preferences']['budget_php'] == 85.5
    assert 'live stock' in result['notice']


def test_one_cent_over_budget_and_unknown_spice_are_not_guessed(db_client, monkeypatch):
    client, engine = db_client
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences())
    assert client.post('/api/recommendations', json={'budget': '85.49', 'preferences': 'chicken'}).json()['suggestions'] == []
    with Session(engine) as session:
        session.get(MenuItem, 1).description = None
        session.commit()
    assert client.post('/api/recommendations', json={'budget': '100', 'preferences': 'non-spicy'}).json()['suggestions'] == []


def test_empty_catalog_never_calls_provider_or_invents_prices(db_client, monkeypatch):
    client, engine = db_client
    with Session(engine) as session:
        for item in session.scalars(select(MenuItem)):
            session.delete(item)
        session.commit()
    def forbidden(_):
        pytest.fail('Empty catalog must not call the AI provider')
    monkeypatch.setattr(recommendations, 'extract_preferences', forbidden)
    result = client.post('/api/recommendations', json={'budget': 100, 'preferences': 'chicken'}).json()
    assert result['suggestions'] == [] and result['preferences'] is None


def test_blank_preferences_uses_prices_without_ai(db_client, monkeypatch):
    client, _ = db_client
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: pytest.fail('No AI needed'))
    suggestions = client.post('/api/recommendations', json={'budget': '100'}).json()['suggestions']
    assert suggestions
    for suggestion in suggestions:
        assert Decimal(suggestion['total']) <= 100
        assert all(item['id'] != 5 for item in suggestion['items'])
        assert len({item['shop_name'] for item in suggestion['items']}) == 1


def test_multiple_shops_require_explicit_permission(db_client, monkeypatch):
    client, _ = db_client
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences(
        preferred_food='pork', avoid_spicy=None, exclusions=[], prefer_same_stall=True))
    assert client.post('/api/recommendations', json={'budget': 100, 'preferences': 'Pork and a drink'}).json()['suggestions'] == []
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences(
        preferred_food='pork', avoid_spicy=None, exclusions=[], prefer_same_stall=False))
    picks = client.post('/api/recommendations', json={'budget': 100, 'preferences': 'Pork and a drink, different shops okay'}).json()['suggestions']
    assert picks
    assert len({item['shop_name'] for item in picks[0]['items']}) == 2


def test_tagalog_aliases_and_recorded_exclusions(db_client, monkeypatch):
    client, _ = db_client
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences(preferred_food='manok kanin'))
    assert client.post('/api/recommendations', json={'budget': 100, 'preferences': 'Manok at kanin'}).json()['suggestions']
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences(exclusions=['manok']))
    assert client.post('/api/recommendations', json={'budget': 100, 'preferences': 'No chicken'}).json()['suggestions'] == []


@pytest.mark.parametrize('budget', ['0', '-1', 'NaN', 'Infinity', '10000.01', '85.501'])
def test_bad_recommendation_budget(db_client, budget):
    assert db_client[0].post('/api/recommendations', json={'budget': budget}).status_code == 422


def test_malformed_request_omits_submitted_values(db_client):
    client, _ = db_client
    response = client.post('/api/recommendations', content=b'{"private-sentinel":',
                           headers={'Content-Type': 'application/json'})
    assert response.status_code == 422
    assert response.json() == {'detail': 'The request contains invalid JSON.'}
    response = client.post('/api/recommendations', json={'budget': 'private-sentinel'})
    assert response.status_code == 422
    assert 'budget' in response.json()['detail']
    assert 'private-sentinel' not in response.text


def test_oversized_stream_is_rejected_before_json_parsing(db_client, monkeypatch):
    from app.request_limit import MAX_BODY_BYTES

    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: pytest.fail('No AI call expected'))
    chunks = iter([b'x' * MAX_BODY_BYTES, b'x'])
    response = db_client[0].post('/api/recommendations', content=chunks,
                                 headers={'Content-Type': 'application/json'})
    assert response.status_code == 413
    assert 'too large' in response.json()['detail']


@pytest.mark.parametrize('failure,expected', [('timeout', 503), (500, 503), (200, 503),
                                             (401, 503), (429, 429)])
def test_provider_failures_are_safe(db_client, monkeypatch, failure, expected):
    def provider(request):
        if failure == 'timeout':
            raise httpx.ReadTimeout('private transport details', request=request)
        if failure == 200:
            return httpx.Response(200, json={'choices': [{
                'finish_reason': 'stop',
                'message': {'content': 'private malformed provider output'},
            }]})
        return httpx.Response(failure, text='private provider body')

    mock_groq(monkeypatch, provider)
    response = db_client[0].post('/api/recommendations', json={'budget': 100, 'preferences': 'chicken'})
    assert response.status_code == expected
    assert 'clear the preference box' in response.json()['detail']
    assert 'private' not in response.text


def test_conflicting_budgets_require_user_correction(db_client, monkeypatch):
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda _: preferences(budget_php=200))
    assert db_client[0].post('/api/recommendations', json={'budget': 100, 'preferences': '200 pesos'}).status_code == 422


def test_recommendation_guard_limits_provider_calls(db_client, monkeypatch):
    calls = []
    monkeypatch.setattr(recommendations, 'extract_preferences', lambda text: calls.append(text) or preferences())
    client, _ = db_client
    for _ in range(6):
        assert client.post('/api/recommendations', json={'budget': 100, 'preferences': 'Chicken'}).status_code == 200
    response = client.post('/api/recommendations', json={'budget': 100, 'preferences': 'Chicken'})
    assert response.status_code == 429 and response.headers['retry-after'] == '60'
    assert len(calls) == 6


def test_visitor_full_crud_is_database_backed_and_isolated(db_client):
    client, engine = db_client
    created = client.post('/api/plans', headers=A, json={'title': 'Monday lunch', 'budget': '100', 'item_ids': [1, 2, 3]})
    assert created.status_code == 201
    plan = created.json()
    assert plan['total'] == '85.50' and 'owner_hash' not in plan
    path = f'/api/plans/{plan["id"]}'
    assert client.get('/api/plans', headers=A).headers['cache-control'] == 'no-store'
    assert client.get(path, headers=A).json()['title'] == 'Monday lunch'
    assert client.get('/api/plans', headers=B).json() == []
    for method, body in [('get', None), ('put', {'title': 'Stolen'}), ('delete', None)]:
        assert client.request(method, path, headers=B, json=body).status_code == 404
    assert client.put(path, headers=A, json={'title': 'Tipid Tuesday'}).json()['title'] == 'Tipid Tuesday'
    assert client.put(path, headers=A, json={'title': '   '}).status_code == 422
    with Session(engine) as session:
        session.get(MenuItem, 1).price = Decimal('999')
        session.commit()
        assert session.scalar(select(SavedPlan.title)) == 'Tipid Tuesday'
        from hashlib import sha256
        assert session.scalar(select(SavedPlan.owner_hash)) == sha256(('a' * 64).encode()).hexdigest()
    assert client.get(path, headers=A).json()['total'] == '85.50'
    assert client.delete(path, headers=A).status_code == 204
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(SavedPlanItem)) == 0


@pytest.mark.parametrize('headers', [{}, {'Authorization': 'Bearer password'}, {'Authorization': 'Bearer ' + 'A' * 64}])
def test_saved_boxes_require_valid_browser_secret(db_client, headers):
    assert db_client[0].get('/api/plans', headers=headers).status_code == 401


@pytest.mark.parametrize('items,budget,status', [([1, 1], 100, 422), ([999], 100, 409), ([5], 100, 409), ([1, 2, 3], '85.49', 409)])
def test_plan_revalidates_actual_catalog_prices(db_client, items, budget, status):
    assert db_client[0].post('/api/plans', headers=A, json={'title': 'Box', 'budget': budget, 'item_ids': items}).status_code == status


def test_meal_box_count_is_bounded(db_client):
    client, _ = db_client
    for index in range(20):
        assert client.post('/api/plans', headers=A, json={'title': f'Box {index}', 'budget': 100, 'item_ids': [1]}).status_code == 201
    limits._buckets.clear()
    assert client.post('/api/plans', headers=A, json={'title': 'One too many', 'budget': 100, 'item_ids': [1]}).status_code == 409


def test_admin_and_catalog_mutations_are_no_longer_exposed(db_client):
    client, _ = db_client
    assert client.get('/api/admin/auth-config').status_code == 404
    assert client.get('/api/admin/me').status_code == 404
    assert client.post('/api/stalls', json={'name': 'Injected'}).status_code == 405
    assert client.post('/api/menu-items', json={'name': 'Injected'}).status_code == 405
    assert client.post('/api/stalls/1/image', content=b'x').status_code == 404
    assert client.get('/api/stalls').status_code == 200


def test_dataset_import_is_idempotent_and_preserves_omitted_records(db_client):
    _, engine = db_client
    dataset = Dataset.model_validate({'shops': [{'name': 'Maria Rosa', 'menu_items': [
        {'name': 'Test-only dish', 'price': '60.50', 'category': 'Main dish'}]}]})
    for _ in range(2):
        with Session(engine) as session:
            apply_dataset(session, dataset)
            session.commit()
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 6
        assert session.scalar(select(MenuItem.price).where(MenuItem.name == 'Test-only dish')) == Decimal('60.50')


def test_dataset_rejects_unknown_shops_or_duplicate_items():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        Dataset.model_validate({'shops': [{'name': 'Invented shop', 'menu_items': []}]})
    with pytest.raises(ValidationError):
        Dataset.model_validate({'shops': [{'name': 'Maria Rosa', 'menu_items': [
            {'name': 'Duplicate', 'price': 5, 'category': 'Snack'},
            {'name': 'Duplicate', 'price': 6, 'category': 'Snack'}]}]})
