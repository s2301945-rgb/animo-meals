"""Provision only the application's public photo bucket and admin-only insert policy."""
from uuid import UUID
import argparse

from sqlalchemy import create_engine, text

from app.config import settings


def main():
    admin_id = str(UUID(settings.admin_user_id))
    if not settings.database_url.startswith('postgresql'):
        raise ValueError('Supabase PostgreSQL settings are required.')
    engine = create_engine(settings.database_url, connect_args={'connect_timeout': 10})
    bucket = settings.image_storage_bucket
    policy_name = 'animomeals_admin_image_insert' + ('_staging' if bucket.endswith('-staging') else '')
    with engine.begin() as connection:
        connection.execute(text('''
            INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
            VALUES (:bucket, :bucket, true, 2097152, ARRAY['image/webp'])
            ON CONFLICT (id) DO NOTHING
        '''), {'bucket': bucket})
        policy = connection.scalar(text("SELECT 1 FROM pg_policies WHERE schemaname='storage' AND tablename='objects' AND policyname=:policy"), {'policy': policy_name})
        if not policy:
            connection.execute(text(f'''
                CREATE POLICY {policy_name} ON storage.objects
                FOR INSERT TO authenticated WITH CHECK (
                    bucket_id = '{bucket}'
                    AND (SELECT auth.uid()) = '{admin_id}'::uuid
                    AND (storage.foldername(name))[1] = '{admin_id}'
                )
            '''))
    engine.dispose()
    print('Photo bucket configured. Public photo viewing; uploads restricted to the configured administrator.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--staging', action='store_true')
    if parser.parse_args().staging:
        settings.image_storage_bucket = 'animo-meals-images-staging'
    try:
        main()
    except Exception as error:
        print(f'Photo storage setup failed ({type(error).__name__}). Check private project settings.')
        raise SystemExit(1) from None
