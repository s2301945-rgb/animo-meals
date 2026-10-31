from sqlalchemy import create_engine, event
import re
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


def make_engine(url, schema=''):
    if schema and (not re.fullmatch('[a-z_][a-z0-9_]*', schema) or url.startswith('sqlite')):
        raise ValueError('A valid PostgreSQL schema is required.')
    engine = create_engine(
        url,
        connect_args={'check_same_thread': False} if url.startswith('sqlite') else {},
        pool_pre_ping=True,
    )
    if url.startswith('sqlite'):
        @event.listens_for(engine, 'connect')
        def enable_foreign_keys(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
    elif schema:
        @event.listens_for(engine, 'connect')
        def select_schema(connection, _):
            connection.execute(f'SET SESSION search_path TO "{schema}"')
            connection.commit()
    return engine


engine = make_engine(settings.database_url, settings.database_schema)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session
