"""Developer-run dataset import. Dry run by default; never called by the website."""
import argparse
import json
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from sqlalchemy import select

from app.database import SessionLocal
from app.models import MenuItem, Stall
from app.recommendations import Budget
from app.shop_catalog import CATALOG_LOCATIONS

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class DatasetItem(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: Name
    price: Budget
    category: Literal['Main dish', 'Drink', 'Snack', 'Side']
    description: Annotated[str | None, StringConstraints(strip_whitespace=True, max_length=2000)] = None
    is_listed: Annotated[bool, Field(strict=True)] = True


class DatasetShop(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: str
    menu_items: list[DatasetItem] = Field(max_length=200)

    @field_validator('name')
    @classmethod
    def known_shop(cls, value):
        if value not in CATALOG_LOCATIONS:
            raise ValueError('Use a shop name from the catalog.')
        return value

    @field_validator('menu_items')
    @classmethod
    def unique_items(cls, items):
        names = [item.name.casefold() for item in items]
        if len(set(names)) != len(names):
            raise ValueError('Duplicate item name within a shop.')
        return items


class Dataset(BaseModel):
    model_config = ConfigDict(extra='forbid')
    shops: list[DatasetShop] = Field(min_length=1, max_length=len(CATALOG_LOCATIONS))

    @field_validator('shops')
    @classmethod
    def unique_shops(cls, shops):
        if len({shop.name for shop in shops}) != len(shops):
            raise ValueError('A shop may only occur once.')
        return shops


def apply_dataset(session, dataset):
    for source in dataset.shops:
        stall = session.scalar(select(Stall).where(Stall.name == source.name))
        if stall is None:
            stall = Stall(name=source.name, location=CATALOG_LOCATIONS[source.name])
            session.add(stall)
            session.flush()
        for entry in source.menu_items:
            item = session.scalar(select(MenuItem).where(MenuItem.stall_id == stall.id,
                                                        MenuItem.name == entry.name))
            if item is None:
                item = MenuItem(stall_id=stall.id)
                session.add(item)
            values = entry.model_dump()
            values['is_available'] = values.pop('is_listed')  # Legacy column means catalog inclusion.
            for key, value in values.items():
                setattr(item, key, value)
    # Caller commits one transaction. No deletion; omitted rows/photos/locations are preserved.


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dataset', type=Path)
    parser.add_argument('--apply', action='store_true', help='Write the validated dataset to the configured database.')
    args = parser.parse_args()
    if args.dataset.stat().st_size > 1_000_000:
        raise ValueError('Dataset is too large.')
    dataset = Dataset.model_validate_json(args.dataset.read_text(encoding='utf-8'))
    print(json.dumps({'valid': True, 'shops': len(dataset.shops),
                      'menu_items': sum(len(shop.menu_items) for shop in dataset.shops),
                      'mode': 'apply' if args.apply else 'dry_run'}))
    if args.apply:
        with SessionLocal.begin() as session:
            apply_dataset(session, dataset)
        print('Recorded menu dataset imported. No live-stock claim is made.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Import stopped ({type(error).__name__}). Check the dataset and private database settings.')
        raise SystemExit(1) from None
