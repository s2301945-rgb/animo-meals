"""Run migrations and start the hosted API without printing connection secrets."""
import os
import sys

from alembic import command
from alembic.config import Config
import uvicorn

from app.config import BACKEND_DIR, settings


def main():
    if os.getenv('APP_ENV') == 'production':
        if not settings.database_url.startswith('postgresql'):
            print('Startup stopped: configure the production PostgreSQL DATABASE_URL.', flush=True)
            return 1
        if not settings.frontend_origin.startswith('https://'):
            print('Startup stopped: FRONTEND_ORIGIN must be the HTTPS frontend address.', flush=True)
            return 1
    try:
        command.upgrade(Config(str(BACKEND_DIR / 'alembic.ini')), 'head')
    except Exception as error:
        print(f'Database migration failed ({type(error).__name__}). Check private hosting configuration.', flush=True)
        return 1
    print('Database migration is current. Starting AnimoMeals API.', flush=True)
    uvicorn.run('app.main:app', host='0.0.0.0', port=int(os.getenv('PORT', '8000')))
    return 0


if __name__ == '__main__':
    sys.exit(main())
