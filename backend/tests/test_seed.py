from decimal import Decimal

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import sessionmaker

from app import seed
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
