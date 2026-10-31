"""Run both local staging services; Ctrl+C stops them without touching development."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    backend = ROOT / 'backend'
    python = backend / ('.venv/Scripts/python.exe' if os.name == 'nt' else '.venv/bin/python')
    node = shutil.which('node') or ('C:/Program Files/nodejs/node.exe' if os.name == 'nt' else '')
    vite = ROOT / 'frontend/node_modules/vite/bin/vite.js'
    if not (backend / '.env.staging').exists() or not python.exists() or not vite.exists():
        print('Configure staging and install dependencies first. See STAGING.md.')
        return 1
    for port in (8003, 5177):
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', port)) == 0:
                print(f'Port {port} is already in use. Staging may already be running.')
                return 1
    logs = ROOT / '.staging-run'
    logs.mkdir(exist_ok=True)
    env = dict(os.environ)
    # Do not allow inherited development/production variables to override staging files.
    for key in ('DATABASE_URL', 'DATABASE_SCHEMA', 'IMAGE_STORAGE_BUCKET', 'FRONTEND_ORIGIN',
                'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY', 'ADMIN_USER_ID', 'GROQ_API_KEY',
                'SSLKEYLOGFILE', 'VITE_API_BASE_URL', 'VITE_APP_ENV'):
        env.pop(key, None)
    env.update(ANIMOMEALS_ENV_FILE='.env.staging', APP_ENV='staging', PORT='8003')
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    children = []
    with (logs / 'api.log').open('w') as api_log, (logs / 'frontend.log').open('w') as frontend_log:
        try:
            children.append(subprocess.Popen([str(python), '-m', 'app.start_server'], cwd=backend,
                env=env, stdout=api_log, stderr=subprocess.STDOUT, creationflags=flags))
            children.append(subprocess.Popen([node, str(vite), '--host', '127.0.0.1', '--port', '5177',
                '--strictPort', '--mode', 'staging'], cwd=ROOT / 'frontend', env=env,
                stdout=frontend_log, stderr=subprocess.STDOUT, creationflags=flags))
            print('Staging site: http://127.0.0.1:5177', flush=True)
            print('Staging admin: http://127.0.0.1:5177/#admin', flush=True)
            print('Ctrl+C stops staging. Logs: .staging-run/', flush=True)
            while all(child.poll() is None for child in children):
                time.sleep(1)
            print('A staging service stopped. Check the local staging logs.')
        except KeyboardInterrupt:
            print('Stopping staging.')
        finally:
            for child in children:
                if child.poll() is None:
                    child.terminate()
            for child in children:
                child.wait(timeout=10)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
