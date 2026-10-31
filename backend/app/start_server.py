"""Run migrations and start the hosted API without printing connection secrets."""
import os
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.engine import make_url
import uvicorn

from app.config import BACKEND_DIR, settings
from app.database import engine


def main():
    environment = os.getenv('APP_ENV', getattr(settings, 'app_env', 'development'))
    if environment == 'staging':
        role = make_url(settings.database_url).username or ''
        if (not settings.database_url.startswith('postgresql')
                or role.split('.')[0] != 'animomeals_staging'
                or settings.database_schema != 'animomeals_staging'
                or settings.image_storage_bucket != 'animo-meals-images-staging'):
            print('Staging startup stopped: use the restricted staging database and photo bucket.', flush=True)
            return 1
        try:
            with engine.connect() as connection:
                identity = connection.execute(text('SELECT current_user, current_schema()')).one()
                if tuple(identity) != ('animomeals_staging', 'animomeals_staging'):
                    print('Staging startup stopped: database isolation check failed.', flush=True)
                    return 1
        except Exception:
            print('Staging startup stopped: could not verify the isolated database.', flush=True)
            return 1
    if environment == 'production':
        if not settings.database_url.startswith('postgresql'):
            print('Startup stopped: configure the production PostgreSQL DATABASE_URL.', flush=True)
            return 1
        if not settings.frontend_origin.startswith('https://'):
            print('Startup stopped: FRONTEND_ORIGIN must be the HTTPS frontend address.', flush=True)
            return 1
        if (getattr(settings, 'database_schema', '') or
                getattr(settings, 'image_storage_bucket', 'animo-meals-images') != 'animo-meals-images'):
            print('Production startup stopped: staging settings are not allowed.', flush=True)
            return 1
    try:
        command.upgrade(Config(str(BACKEND_DIR / 'alembic.ini')), 'head')
    except Exception as error:
        print(f'Database migration failed ({type(error).__name__}). Check private hosting configuration.', flush=True)
        return 1
    print('Database migration is current. Starting AnimoMeals API.', flush=True)
    uvicorn.run('app.main:app', host='127.0.0.1' if environment == 'staging' else '0.0.0.0', port=int(os.getenv('PORT', '8000')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
