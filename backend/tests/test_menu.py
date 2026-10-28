from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.main import app
from app.models import MenuItem, Stall


@pytest.fixture
def client():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        stall = Stall(name='Test stall', location='Test location')
        session.add(stall)
        session.flush()
        session.add_all([
            MenuItem(stall_id=stall.id, name='Exact budget meal', description='Test',
                     price=Decimal('75.50'), category='Main dish', is_available=True),
            MenuItem(stall_id=stall.id, name='Over budget meal', description=None,
                     price=Decimal('75.51'), category='Main dish', is_available=False),
        ])
        session.commit()

    def override_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    engine.dispose()


def test_menu_joins_stall_and_preserves_decimal_price(client):
    response = client.get('/api/menu-items')
    assert response.status_code == 200
    assert len(response.json()) == 2
    item = response.json()[0]
    assert item['stall_name'] == 'Test stall'
    assert item['price'] == '75.50'
    assert item['updated_at']


def test_budget_includes_exact_boundary_but_not_one_cent_more(client):
    data = client.get('/api/menu-items?budget=75.50').json()
    assert [item['name'] for item in data] == ['Exact budget meal']
    assert client.get('/api/menu-items?budget=1').json() == []


@pytest.mark.parametrize('budget', ['0', '-1', 'invalid', '10000.01', '75.501'])
def test_invalid_budget_is_rejected(client, budget):
    assert client.get('/api/menu-items', params={'budget': budget}).status_code == 422


def test_health_confirms_database(client):
    assert client.get('/api/health').json() == {'status': 'ok', 'database': 'connected'}


def test_database_failure_is_safe(client):
    def failed_session():
        raise SQLAlchemyError('private database connection details')
        yield

    app.dependency_overrides[get_session] = failed_session
    response = client.get('/api/menu-items')
    assert response.status_code == 503
    assert 'private' not in response.text
