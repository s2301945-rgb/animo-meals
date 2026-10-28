from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / '.env', extra='ignore')
    database_url: str = f'sqlite:///{(BACKEND_DIR / "animomeals.db").as_posix()}'
    frontend_origin: str = 'http://localhost:5173'


settings = Settings()
