"""Create an isolated staging schema/role; save its password only in ignored settings."""
import json
import secrets

from dotenv import dotenv_values, set_key
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from app.config import BACKEND_DIR, settings

ROLE = 'animomeals_staging'
SCHEMA = 'animomeals_staging'


def main():
    target = BACKEND_DIR / '.env.staging'
    if target.exists():
        previous = dotenv_values(target)
        if previous.get('DATABASE_SCHEMA') != SCHEMA:
            raise ValueError('Review existing staging configuration before continuing.')
        print('Existing staging settings retained; no credentials were rotated.')
        return
    source = make_url(settings.database_url)
    if source.get_backend_name() != 'postgresql' or not settings.admin_user_id:
        raise ValueError('Configure the existing Supabase project and administrator first.')
    password = secrets.token_urlsafe(36)
    engine = create_engine(source, connect_args={'connect_timeout': 10})
    with engine.begin() as connection:
        if connection.scalar(text('SELECT 1 FROM pg_roles WHERE rolname=:role'), {'role': ROLE}):
            raise ValueError('Reserved staging role already exists; do not overwrite its credential.')
        # Identifiers are constants; the generated password contains only URL-safe characters.
        connection.execute(text(f"CREATE ROLE {ROLE} LOGIN PASSWORD '{password}' NOINHERIT NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS"))
        connection.execute(text(f'CREATE SCHEMA {SCHEMA}'))
        connection.execute(text(f'REVOKE ALL ON SCHEMA {SCHEMA} FROM PUBLIC'))
        connection.execute(text(f'GRANT USAGE, CREATE ON SCHEMA {SCHEMA} TO {ROLE}'))
        connection.execute(text(f'ALTER ROLE {ROLE} SET search_path TO {SCHEMA}'))
        connection.execute(text(f'GRANT CONNECT ON DATABASE postgres TO {ROLE}'))
    engine.dispose()
    project_suffix = source.username.partition('.')[2]
    staging_url = source.set(username=ROLE + (f'.{project_suffix}' if project_suffix else ''), password=password)
    values = {
        'APP_ENV': 'staging', 'DATABASE_URL': staging_url.render_as_string(hide_password=False),
        'DATABASE_SCHEMA': SCHEMA, 'FRONTEND_ORIGIN': 'http://127.0.0.1:5177',
        'IMAGE_STORAGE_BUCKET': 'animo-meals-images-staging',
        'SUPABASE_URL': settings.supabase_url,
        'SUPABASE_PUBLISHABLE_KEY': settings.supabase_publishable_key.get_secret_value(),
        'ADMIN_USER_ID': settings.admin_user_id, 'GROQ_API_KEY': '',
    }
    for key, value in values.items():
        set_key(target, key, value)
    (BACKEND_DIR.parent / 'frontend/.env.staging').write_text(
        'VITE_API_BASE_URL=http://127.0.0.1:8003\nVITE_APP_ENV=staging\n', encoding='utf-8')
    print(json.dumps({'staging_configured': True, 'credentials_saved_privately': True,
                      'schema': SCHEMA, 'production_records_changed': False}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Staging setup failed ({type(error).__name__}). No connection credentials were printed.')
        raise SystemExit(1) from None
