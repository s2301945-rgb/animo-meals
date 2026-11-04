from pathlib import Path
import os
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = os.getenv('ANIMOMEALS_ENV_FILE', '.env')
if ENV_FILE not in ('.env', '.env.staging'):
    raise RuntimeError('Select .env or .env.staging for backend configuration.')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ENV_FILE, extra='ignore')
    database_url: str = f'sqlite:///{(BACKEND_DIR / "animomeals.db").as_posix()}'
    frontend_origin: str = 'http://localhost:5173'
    groq_api_key: SecretStr = SecretStr('')
    groq_model: str = 'openai/gpt-oss-20b'
    supabase_url: str = ''
    app_env: Literal['development', 'test', 'staging', 'production'] = 'development'
    database_schema: str = ''
    image_storage_bucket: Literal['animo-meals-images', 'animo-meals-images-staging'] = 'animo-meals-images'


settings = Settings()
