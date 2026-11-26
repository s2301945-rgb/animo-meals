"""Prove existing saved boxes remain readable after the quantity migration."""
import os
from pathlib import Path
import subprocess
import sys


def test_existing_box_migrates_with_one_portion_and_keeps_its_snapshot(tmp_path):
    code = '''
from alembic import command
from alembic.config import Config
from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models import SavedPlan
from app.plans import output

config = Config('alembic.ini')
command.upgrade(config, '0003')
with engine.begin() as connection:
    connection.execute(text("INSERT INTO saved_plans (id,owner_hash,title,budget,created_at) VALUES (1,:owner,'Old lunch',100,'2026-11-01 12:00:00')"), {'owner': 'a'*64})
    connection.execute(text("INSERT INTO saved_plan_items (plan_id,name,shop_name,location,price) VALUES (1,'Historical meal','Historical shop','Old location',50.50)"))
command.upgrade(config, 'head')
with SessionLocal() as session:
    plan = output(session.get(SavedPlan, 1))
    assert plan['version'] == 1
    assert plan['total'] == '50.50' and plan['remaining'] == '49.50'
    assert plan['items'][0]['quantity'] == 1
    assert plan['items'][0]['menu_item_id'] is None
    assert plan['items'][0]['name'] == 'Historical meal'
'''
    env = {**os.environ, 'DATABASE_URL': 'sqlite:///' + (tmp_path / 'old-box.db').as_posix(),
           'DATABASE_SCHEMA': '', 'APP_ENV': 'test', 'GROQ_API_KEY': ''}
    env.pop('SSLKEYLOGFILE', None)
    result = subprocess.run([sys.executable, '-c', code], cwd=Path(__file__).parents[1],
                            env=env, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
