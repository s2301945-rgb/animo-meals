"""Provision only the application's public photo bucket and admin-only insert policy."""
from uuid import UUID

from sqlalchemy import create_engine, text

from app.config import settings


def main():
    admin_id = str(UUID(settings.admin_user_id))
    if not settings.database_url.startswith('postgresql'):
        raise ValueError('Supabase PostgreSQL settings are required.')
    engine = create_engine(settings.database_url, connect_args={'connect_timeout': 10})
    with engine.begin() as connection:
        connection.execute(text('''
            INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            VALUES ('animo-meals-images', 'animo-meals-images', true, 2097152, ARRAY['image/webp'])
            ON CONFLICT (id) DO NOTHING
        '''))
        policy = connection.scalar(text("SELECT 1 FROM pg_policies WHERE schemaname='storage' AND tablename='objects' AND policyname='animomeals_admin_image_insert'"))
        if not policy:
            connection.execute(text(f'''
                CREATE POLICY animomeals_admin_image_insert ON storage.objects
                FOR INSERT TO authenticated WITH CHECK (
                    bucket_id = 'animo-meals-images'
                    AND (SELECT auth.uid()) = '{admin_id}'::uuid
                    AND (storage.foldername(name))[1] = '{admin_id}'
                )
            '''))
    engine.dispose()
    print('Photo bucket configured. Public photo viewing; uploads restricted to the configured administrator.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Photo storage setup failed ({type(error).__name__}). Check private project settings.')
        raise SystemExit(1) from None
