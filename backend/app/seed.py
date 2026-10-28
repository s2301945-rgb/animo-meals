"""Load fictional demonstration records. Run after applying migrations."""
from decimal import Decimal

from sqlalchemy import select

from app.database import SessionLocal
from app.models import MenuItem, Stall

DEMO_MENU = [
    ('Demo • Rice & Co.', 'Ground floor · Zone A', [
        ('Chicken adobo with rice', 'Slow-simmered chicken with steamed rice.', '75', 'Main dish'),
        ('Vegetable rice bowl', 'Mixed vegetables over steamed rice.', '55', 'Main dish'),
        ('Bottled water', 'A simple drink to complete your lunch.', '15', 'Drink'),
        ('Extra rice', 'One serving of steamed rice.', '15', 'Side'),
    ]),
    ('Demo • Bowl Corner', 'Ground floor · Zone B', [
        ('Chicken teriyaki bowl', 'Chicken, teriyaki-style sauce, and rice.', '85', 'Main dish'),
        ('Tofu rice bowl', 'Tofu and vegetables with rice.', '65', 'Main dish'),
        ('Iced tea', 'A chilled tea drink.', '20', 'Drink'),
    ]),
    ('Demo • Snack Stop', 'Ground floor · Zone C', [
        ('Egg sandwich', 'An egg sandwich for a lighter break.', '40', 'Snack'),
        ('Banana bread', 'One slice of banana bread.', '30', 'Snack'),
        ('Calamansi drink', 'A refreshing citrus drink.', '25', 'Drink'),
    ]),
]


def seed():
    added = 0
    with SessionLocal.begin() as session:
        for name, location, items in DEMO_MENU:
            stall = session.scalar(select(Stall).where(Stall.name == name))
            if stall is None:
                stall = Stall(name=name, location=location)
                session.add(stall)
                session.flush()
            for title, description, price, category in items:
                exists = session.scalar(select(MenuItem.id).where(
                    MenuItem.stall_id == stall.id, MenuItem.name == title
                ))
                if exists is None:
                    session.add(MenuItem(stall_id=stall.id, name=title,
                                         description=description, price=Decimal(price),
                                         category=category, is_available=True))
                    added += 1
    print(f'Demonstration menu ready. Added {added} items.')


if __name__ == '__main__':
    seed()
