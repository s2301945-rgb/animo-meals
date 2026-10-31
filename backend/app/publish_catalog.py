"""Back up production data and explicitly replace only recognized fictional seed shops."""
import argparse
import json

from sqlalchemy import delete, func, select, text

from app.config import BACKEND_DIR, settings
from app.database import SessionLocal, engine
from app.models import MenuItem, Stall
from app.seed import DEMO_MENU
from app.shop_catalog import SHOPS


def replace_demo_catalog(session):
    demo_names = {name: {item[0] for item in items} for name, _, items in DEMO_MENU}
    demo_stalls = session.scalars(select(Stall).where(Stall.name.in_(demo_names))).all()
    # Validate every target before deleting anything; unfamiliar menu records require review.
    for stall in demo_stalls:
        names = set(session.scalars(select(MenuItem.name).where(MenuItem.stall_id == stall.id)))
        if not names.issubset(demo_names[stall.name]):
            raise ValueError('A demonstration shop contains unfamiliar data. Review before publishing.')
    ids = [stall.id for stall in demo_stalls]
    removed_items = 0
    if ids:
        removed_items = session.execute(delete(MenuItem).where(MenuItem.stall_id.in_(ids))).rowcount
        session.execute(delete(Stall).where(Stall.id.in_(ids)))
    added = 0
    for name, location in SHOPS:
        if session.scalar(select(Stall.id).where(Stall.name == name)) is None:
            session.add(Stall(name=name, location=location))
            session.flush()
            added += 1
    return {'demo_shops_removed': len(ids), 'demo_items_removed': removed_items,
            'selected_shops_added': added}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    if not settings.database_url.startswith('postgresql') or settings.database_schema:
        raise ValueError('Use the existing production PostgreSQL configuration, not staging.')
    with engine.connect() as connection:
        assert connection.scalar(text('SELECT current_schema()')) == 'public'
        snapshot = {table: [dict(row) for row in connection.execute(
            text(f'SELECT * FROM public.{table} ORDER BY id')).mappings()]
                    for table in ('stalls', 'menu_items')}
    backup = BACKEND_DIR / '.production-backups/catalog-before-week2.json'
    backup.parent.mkdir(exist_ok=True)
    if not backup.exists():
        backup.write_text(json.dumps(snapshot, indent=2, default=str), encoding='utf-8')
    if not args.apply:
        print(json.dumps({'backup_saved': True, 'apply_requested': False,
                          'shops': len(snapshot['stalls']), 'menu_items': len(snapshot['menu_items'])}))
        return
    with SessionLocal.begin() as session:
        result = replace_demo_catalog(session)
        result.update(shops=session.scalar(select(func.count()).select_from(Stall)),
                      menu_items=session.scalar(select(func.count()).select_from(MenuItem)))
    print(json.dumps({'backup_saved': True, 'applied': True, **result}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Catalog publication stopped ({type(error).__name__}). Review the private backup and settings.')
        raise SystemExit(1) from None
