from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app import seed
from app import shop_catalog
from app.database import Base
from app.models import MenuItem, Stall


def test_demo_seed_adds_six_affordable_items_without_duplicates_or_overwrites(monkeypatch):
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(seed, 'SessionLocal', sessions)
    seed.seed()
    new_names = {'Egg fried rice', 'Pancit bihon', 'Mushroom rice bowl',
                 'Fish fillet with rice', 'Tuna pandesal', 'Cheese sandwich'}
    with sessions.begin() as session:
        assert session.scalar(select(func.count()).select_from(Stall)) == 3
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 16
        additions = session.scalars(select(MenuItem).where(MenuItem.name.in_(new_names))).all()
        assert len(additions) == 6
        assert all(item.is_available and item.price <= 75 and item.stall_id for item in additions)
        existing = session.scalar(select(MenuItem).where(MenuItem.name == 'Chicken adobo with rice'))
        existing.price = Decimal('76.00')
        existing.is_available = False
    seed.seed()
    with sessions() as session:
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 16
        existing = session.scalar(select(MenuItem).where(MenuItem.name == 'Chicken adobo with rice'))
        assert existing.price == Decimal('76.00')
        assert existing.is_available is False
    engine.dispose()


def test_real_shop_catalog_starts_with_blank_menus_and_preserves_admin_changes(monkeypatch):
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(shop_catalog, 'SessionLocal', sessions)
    shop_catalog.seed_shops()
    with sessions.begin() as session:
        stalls = session.scalars(select(Stall)).all()
        assert {stall.name: stall.location for stall in stalls} == dict(shop_catalog.SHOPS)
        assert len(stalls) == 5
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 0
        maria = session.scalar(select(Stall).where(Stall.name == 'Maria Rosa'))
        maria.location = 'Location later confirmed by administrator'
    shop_catalog.seed_shops()
    with sessions() as session:
        assert session.scalar(select(func.count()).select_from(Stall)) == 5
        assert session.scalar(select(func.count()).select_from(MenuItem)) == 0
        maria = session.scalar(select(Stall).where(Stall.name == 'Maria Rosa'))
        assert maria.location == 'Location later confirmed by administrator'
    engine.dispose()
