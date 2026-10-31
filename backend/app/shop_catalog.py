"""Add the five user-supplied shops without inventing meals or replacing admin edits."""
from sqlalchemy import select

from app.database import SessionLocal
from app.models import Stall

SHOPS = [
    ('Maria Rosa', 'Location to be confirmed'),
    ('Pritong Manok', 'USLS Stingers'),
    ('Nene’s', 'In front of Gate 5'),
    ('Crazy Crunch', 'Ground floor, MM Building'),
    ('Lola Barbz', 'The Agora'),
]


def seed_shops():
    added = 0
    with SessionLocal.begin() as session:
        for name, location in SHOPS:
            if session.scalar(select(Stall.id).where(Stall.name == name)) is None:
                session.add(Stall(name=name, location=location))
                added += 1
    print(f'Shop catalog ready. Added {added} shops; no menu items were created.')


if __name__ == '__main__':
    seed_shops()
