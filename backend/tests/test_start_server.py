from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app import start_server


@pytest.fixture
def startup(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'production')
    monkeypatch.setattr(start_server, 'settings', SimpleNamespace(
        database_url='postgresql+psycopg://user:private@host/database',
        frontend_origin='https://example.vercel.app',
    ))
    migration = Mock()
    server = Mock()
    monkeypatch.setattr(start_server.command, 'upgrade', migration)
    monkeypatch.setattr(start_server.uvicorn, 'run', server)
    return migration, server


def test_production_refuses_local_database(startup):
    migration, server = startup
    start_server.settings.database_url = 'sqlite:///local.db'
    assert start_server.main() == 1
    migration.assert_not_called()
    server.assert_not_called()


def test_production_refuses_http_origin(startup):
    migration, server = startup
    start_server.settings.frontend_origin = 'http://localhost:5173'
    assert start_server.main() == 1
    migration.assert_not_called()
    server.assert_not_called()


def test_migration_failure_does_not_log_credentials(startup, capsys):
    migration, server = startup
    migration.side_effect = RuntimeError('private password in database error')
    assert start_server.main() == 1
    assert 'private password' not in capsys.readouterr().out
    server.assert_not_called()


def test_migrates_before_listening_on_host_port(startup, monkeypatch):
    migration, server = startup
    monkeypatch.setenv('PORT', '10000')
    assert start_server.main() == 0
    assert migration.call_args.args[1] == 'head'
    server.assert_called_once_with('app.main:app', host='0.0.0.0', port=10000)


def test_staging_refuses_a_production_database_before_migrations(startup, monkeypatch):
    migration, server = startup
    monkeypatch.setenv('APP_ENV', 'staging')
    assert start_server.main() == 1
    migration.assert_not_called()
    server.assert_not_called()


def test_production_refuses_staging_settings(startup):
    migration, server = startup
    start_server.settings.database_schema = 'animomeals_staging'
    assert start_server.main() == 1
    migration.assert_not_called()
    server.assert_not_called()


@pytest.mark.parametrize('identity', [
    ('postgres', 'public'), ('animomeals_staging', 'public'),
])
def test_staging_verifies_actual_database_identity(startup, monkeypatch, identity):
    migration, server = startup
    monkeypatch.setenv('APP_ENV', 'staging')
    start_server.settings.database_url = 'postgresql+psycopg://animomeals_staging.project:test@host/database'
    start_server.settings.database_schema = 'animomeals_staging'
    start_server.settings.image_storage_bucket = 'animo-meals-images-staging'
    engine = Mock()
    engine.connect.return_value.__enter__ = Mock(return_value=Mock())
    engine.connect.return_value.__exit__ = Mock(return_value=False)
    engine.connect.return_value.__enter__.return_value.execute.return_value.one.return_value = identity
    monkeypatch.setattr(start_server, 'engine', engine)
    assert start_server.main() == 1
    migration.assert_not_called()
    server.assert_not_called()
