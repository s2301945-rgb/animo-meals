"""Exercise real CRUD against disposable SQL tables; mock only the identity provider."""
import base64
import json
from unittest.mock import Mock

import httpx
import pytest
from pydantic import SecretStr
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app import auth
from app.database import Base, get_session, make_engine
from app.main import app

ADMIN_ID = '11111111-1111-4111-8111-111111111111'
HEADERS = {'Authorization': 'Bearer test-access-token'}


@pytest.fixture
def client(monkeypatch):
    # This engine is independent of backend/.env and never touches Supabase data.
    from sqlalchemy import create_engine
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    from sqlalchemy import event

    @event.listens_for(engine, 'connect')
    def foreign_keys(connection, _):
        connection.execute('PRAGMA foreign_keys=ON')

    Base.metadata.create_all(engine)

    def session_override():
        with Session(engine) as session:
            yield session

    monkeypatch.setattr(auth.settings, 'supabase_url', 'https://test-project.supabase.co')
    monkeypatch.setattr(auth.settings, 'supabase_publishable_key', SecretStr('sb_publishable_test'))
    monkeypatch.setattr(auth.settings, 'admin_user_id', ADMIN_ID)
    monkeypatch.setattr(auth.httpx, 'get', Mock(return_value=httpx.Response(200, json={'id': ADMIN_ID})))
    app.dependency_overrides[get_session] = session_override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def shop(client, name='Test shop'):
    response = client.post('/api/stalls', headers=HEADERS,
                           json={'name': name, 'location': 'Test landmark'})
    assert response.status_code == 201, response.text
    return response.json()


def meal(stall_id, **changes):
    return {'stall_id': stall_id, 'name': 'Regular meal', 'price': '65.50',
            'category': 'Main dish', 'is_available': True, **changes}


def test_shop_and_menu_full_lifecycle(client):
    stall = shop(client)
    assert client.get('/api/stalls').json()[0]['id'] == stall['id']
    assert client.get(f'/api/stalls/{stall["id"]}').json()['name'] == 'Test shop'
    created = client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id']))
    assert created.status_code == 201
    item_id = created.json()['id']
    assert created.json()['price'] == '65.50'
    assert created.json()['updated_at']
    assert client.get(f'/api/menu-items/{item_id}').json()['stall_id'] == stall['id']

    renamed = client.put(f'/api/stalls/{stall["id"]}', headers=HEADERS,
                         json={'name': 'Updated shop', 'location': 'Gate 5'})
    assert renamed.status_code == 200
    second_shop = shop(client, 'Second shop')
    updated = client.put(f'/api/menu-items/{item_id}', headers=HEADERS,
                         json=meal(second_shop['id'], name='Updated meal', price='70.25',
                                   is_available=False, description='Regular menu'))
    assert updated.status_code == 200
    public_item = client.get('/api/menu-items').json()[0]
    assert public_item['name'] == 'Updated meal'
    assert public_item['price'] == '70.25'
    assert public_item['stall_name'] == 'Second shop'
    assert public_item['is_available'] is False
    assert client.delete(f'/api/stalls/{second_shop["id"]}', headers=HEADERS).status_code == 409
    assert client.get(f'/api/menu-items/{item_id}').status_code == 200
    assert client.delete(f'/api/menu-items/{item_id}', headers=HEADERS).status_code == 204
    assert client.get(f'/api/menu-items/{item_id}').status_code == 404
    assert client.get('/api/menu-items').json() == []
    assert client.delete(f'/api/stalls/{second_shop["id"]}', headers=HEADERS).status_code == 204
    assert client.get(f'/api/stalls/{second_shop["id"]}').status_code == 404


@pytest.mark.parametrize('method,path,payload', [
    ('post', '/api/stalls', {'name': 'Forbidden', 'location': 'Gate'}),
    ('put', '/api/stalls/1', {'name': 'Forbidden', 'location': 'Gate'}),
    ('delete', '/api/stalls/1', None),
    ('post', '/api/menu-items', meal(1)),
    ('put', '/api/menu-items/1', meal(1)),
    ('delete', '/api/menu-items/1', None),
])
def test_anonymous_cannot_write(client, method, path, payload):
    assert client.request(method, path, json=payload).status_code == 401
    assert client.get('/api/stalls').json() == []


@pytest.mark.parametrize('change', [
    {'price': '-1'}, {'price': '0'}, {'price': '10000.01'}, {'price': '65.501'},
    {'price': 'NaN'}, {'price': 'Infinity'}, {'price': 'abc'}, {'price': None},
    {'name': '   '}, {'name': 'x' * 121}, {'description': 'x' * 2001},
    {'category': 'Unknown'}, {'stall_id': 0}, {'stall_id': True},
    {'is_available': 'yes'}, {'unexpected_field': 'value'},
])
def test_invalid_menu_requests_cannot_create_or_overwrite_records(client, change):
    stall = shop(client)
    item_id = client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id'])).json()['id']
    payload = {**meal(stall['id']), **change}
    assert client.post('/api/menu-items', headers=HEADERS, json=payload).status_code == 422
    assert client.put(f'/api/menu-items/{item_id}', headers=HEADERS, json=payload).status_code == 422
    items = client.get('/api/menu-items').json()
    assert len(items) == 1
    assert items[0]['name'] == 'Regular meal'
    assert items[0]['price'] == '65.50'


def test_missing_required_fields_and_malformed_json(client):
    assert client.post('/api/menu-items', headers=HEADERS, json={}).status_code == 422
    response = client.post('/api/stalls', headers={**HEADERS, 'Content-Type': 'application/json'},
                           content='{bad json')
    assert response.status_code == 422


@pytest.mark.parametrize('payload', [
    {'name': ' ', 'location': 'Gate'}, {'name': 'Shop', 'location': ''},
    {'name': 'x' * 101, 'location': 'Gate'}, {'name': 'Shop', 'location': 'x' * 201},
    {'name': 'Shop', 'location': 'Gate', 'role': 'admin'},
])
def test_shop_input_validation(client, payload):
    assert client.post('/api/stalls', headers=HEADERS, json=payload).status_code == 422
    assert client.get('/api/stalls').json() == []


def test_trimmed_shop_names_and_duplicate_conflicts(client):
    original = shop(client, '  Same Shop  ')
    assert original['name'] == 'Same Shop'
    assert client.post('/api/stalls', headers=HEADERS,
                       json={'name': 'same shop', 'location': 'Other'}).status_code == 409
    other = shop(client, 'Other shop')
    assert client.put(f'/api/stalls/{other["id"]}', headers=HEADERS,
                      json={'name': 'SAME SHOP', 'location': 'Other'}).status_code == 409
    assert client.get(f'/api/stalls/{other["id"]}').json()['name'] == 'Other shop'


def test_nonexistent_shop_does_not_create_or_move_a_menu_item(client):
    assert client.post('/api/menu-items', headers=HEADERS, json=meal(999)).status_code == 404
    stall = shop(client)
    item_id = client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id'])).json()['id']
    assert client.put(f'/api/menu-items/{item_id}', headers=HEADERS, json=meal(999)).status_code == 404
    assert client.get(f'/api/menu-items/{item_id}').json()['stall_id'] == stall['id']


@pytest.mark.parametrize('method,path,payload', [
    ('put', '/api/stalls/999', {'name': 'Missing', 'location': 'Gate'}),
    ('delete', '/api/stalls/999', None),
    ('put', '/api/menu-items/999', meal(1)),
    ('delete', '/api/menu-items/999', None),
])
def test_missing_records_are_404(client, method, path, payload):
    assert client.request(method, path, headers=HEADERS, json=payload).status_code == 404


def test_budget_matches_updated_price(client):
    stall = shop(client)
    item_id = client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id'])).json()['id']
    client.put(f'/api/menu-items/{item_id}', headers=HEADERS, json=meal(stall['id'], price='75.51'))
    assert client.get('/api/menu-items?budget=75.50').json() == []
    assert len(client.get('/api/menu-items?budget=75.51').json()) == 1


def test_shop_rename_and_location_change_preserve_menu_assignment(client):
    first = shop(client, 'First shop')
    second = shop(client, 'Second shop')
    for stall in (first, second):
        assert client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id'])).status_code == 201
    assert client.put(f'/api/stalls/{first["id"]}', headers=HEADERS,
                      json={'name': 'Renamed shop', 'location': 'New landmark'}).status_code == 200
    items = client.get('/api/menu-items').json()
    first_item = next(item for item in items if item['stall_id'] == first['id'])
    second_item = next(item for item in items if item['stall_id'] == second['id'])
    assert first_item['stall_name'] == 'Renamed shop'
    assert first_item['location'] == 'New landmark'
    assert second_item['stall_name'] == 'Second shop'
    assert second_item['location'] == 'Test landmark'


def test_empty_shops_are_visible_without_invented_menu_records(client):
    stall = shop(client, 'Menu pending')
    assert client.get('/api/stalls').json()[0]['id'] == stall['id']
    assert client.get('/api/menu-items').json() == []


def test_valid_admin_token_is_verified_with_provider(client):
    assert client.get('/api/admin/me', headers=HEADERS).json() == {'role': 'admin'}
    auth.httpx.get.assert_called_once_with(
        'https://test-project.supabase.co/auth/v1/user',
        headers={'apikey': 'sb_publishable_test', 'Authorization': 'Bearer test-access-token'}, timeout=10)


def test_signed_in_non_admin_cannot_write_even_with_admin_metadata(client, monkeypatch):
    auth.httpx.get.return_value = httpx.Response(200, json={
        'id': 'another-user', 'user_metadata': {'role': 'admin'}, 'role': 'admin',
    })
    response = client.post('/api/stalls', headers=HEADERS,
                           json={'name': 'Forbidden', 'location': 'Gate'})
    assert response.status_code == 403
    assert client.get('/api/stalls').json() == []


@pytest.mark.parametrize('status,expected', [(401, 401), (403, 401), (429, 503), (500, 503)])
def test_identity_provider_errors_are_safe(client, status, expected):
    auth.httpx.get.return_value = httpx.Response(status, text='private provider error')
    response = client.get('/api/admin/me', headers=HEADERS)
    assert response.status_code == expected
    assert 'private' not in response.text


@pytest.mark.parametrize('body', ['not json', '[]', '{}', '{"id": null}'])
def test_malformed_identity_response_fails_closed(client, body):
    auth.httpx.get.return_value = httpx.Response(200, text=body)
    assert client.get('/api/admin/me', headers=HEADERS).status_code == 503


def test_identity_timeout_fails_closed(client):
    auth.httpx.get.side_effect = httpx.ReadTimeout('private connection details')
    response = client.get('/api/admin/me', headers=HEADERS)
    assert response.status_code == 503
    assert 'private' not in response.text


@pytest.mark.parametrize('key', ['', 'sb_secret_private', 'header.' + base64.urlsafe_b64encode(
    json.dumps({'role': 'service_role'}).encode()).decode().rstrip('=') + '.signature'])
def test_auth_config_never_exposes_secret_keys(client, monkeypatch, key):
    monkeypatch.setattr(auth.settings, 'supabase_publishable_key', SecretStr(key))
    response = client.get('/api/admin/auth-config')
    assert response.status_code == 503
    assert 'publishable_key' not in response.text
    auth.httpx.get.assert_not_called()


def test_missing_auth_configuration_disables_writes_but_not_public_browsing(client, monkeypatch):
    monkeypatch.setattr(auth.settings, 'admin_user_id', '')
    assert client.get('/api/admin/me', headers=HEADERS).status_code == 503
    assert client.get('/api/menu-items').status_code == 200
    assert client.get('/api/stalls').status_code == 200


def test_public_auth_config_contains_only_public_connection_details(client):
    response = client.get('/api/admin/auth-config')
    assert response.status_code == 200
    assert response.headers['cache-control'] == 'no-store'
    assert response.json() == {'url': 'https://test-project.supabase.co',
                               'publishable_key': 'sb_publishable_test'}


def test_browser_can_preflight_authenticated_mutations(client):
    response = client.options('/api/menu-items/1', headers={
        'Origin': auth.settings.frontend_origin,
        'Access-Control-Request-Method': 'PUT',
        'Access-Control-Request-Headers': 'authorization,content-type',
    })
    assert response.status_code == 200
    assert 'PUT' in response.headers['access-control-allow-methods']


def test_foreign_keys_enabled_in_normal_sqlite_engine():
    engine = make_engine('sqlite://')
    with engine.connect() as connection:
        from sqlalchemy import text
        assert connection.scalar(text('PRAGMA foreign_keys')) == 1
    engine.dispose()
