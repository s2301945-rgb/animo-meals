from decimal import Decimal

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app import seed
from app.database import Base
from app.models import MenuItem, Stall
from app.publish_catalog import replace_demo_catalog
from app.shop_catalog import SHOPS


@pytest.fixture
def sessions(monkeypatch):
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    monkeypatch.setattr(seed, 'SessionLocal', factory)
    seed.seed()
    yield factory
    engine.dispose()


def test_catalog_publication_replaces_demo_data_and_is_repeatable(sessions):
    with sessions.begin() as session:
        result = replace_demo_catalog(session)
        assert result == {'demo_shops_removed': 3, 'demo_items_removed': 16, 'selected_shops_added': 5}
    with sessions.begin() as session:
        assert set(session.scalars(select(Stall.name))) == {name for name, _ in SHOPS}
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 0
        assert replace_demo_catalog(session) == {'demo_shops_removed': 0, 'demo_items_removed': 0, 'selected_shops_added': 0}


def test_catalog_publication_preserves_non_demo_records_and_admin_edits(sessions):
    with sessions.begin() as session:
        stall = Stall(name='Maria Rosa', location='Administrator-confirmed location')
        session.add(stall)
        session.flush()
        session.add(MenuItem(stall_id=stall.id, name='Administrator-entered meal',
                             price=Decimal('65'), category='Main dish', is_available=True))
    with sessions.begin() as session:
        replace_demo_catalog(session)
    with sessions() as session:
        assert session.scalar(select(Stall).where(Stall.name == 'Maria Rosa')).location == 'Administrator-confirmed location'
        assert session.scalar(select(MenuItem)).name == 'Administrator-entered meal'


def test_unfamiliar_data_in_demo_shop_stops_publication_before_deletion(sessions):
    with sessions.begin() as session:
        stall = session.scalar(select(Stall))
        session.add(MenuItem(stall_id=stall.id, name='Unfamiliar record', price=Decimal('10'),
                             category='Snack', is_available=True))
    with sessions.begin() as session:
        with pytest.raises(ValueError):
            replace_demo_catalog(session)
        assert session.scalar(select(func.count()).select_from(Stall)) == 3
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 17
