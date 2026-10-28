"""Restricted backend command for one real provider call; no public AI endpoint."""
import argparse
from datetime import datetime, timezone
import getpass
import json
from pathlib import Path
import subprocess

from dotenv import set_key
from pydantic import SecretStr

from app.ai import AIError, extract_preferences
from app.config import BACKEND_DIR, Settings

SAMPLE = (
    'I have 100 pesos. I want a non-spicy chicken meal with a drink, '
    'preferably from one stall. No pork.'
)


def main():
    parser = argparse.ArgumentParser(description='Verify one backend Groq extraction request.')
    parser.add_argument('--configure', action='store_true', help='Enter a key privately and save after success.')
    parser.add_argument('--output', type=Path, help='Save non-secret verification evidence to this file.')
    args = parser.parse_args()
    config = Settings()
    env_file = BACKEND_DIR / '.env'
    if args.configure:
        if env_file.is_symlink() or subprocess.run(
            ['git', '-C', str(BACKEND_DIR.parent), 'ls-files', '--error-unmatch', 'backend/.env'],
            capture_output=True,
        ).returncode == 0:
            print('Stopped: environment file must be untracked and must not be a symbolic link.')
            return 1
        print('Paste your Groq key here, not in chat. Input stays hidden.')
        key = getpass.getpass('Groq API key: ').strip()
        if not key:
            print('Cancelled: no key entered.')
            return 1
        config.groq_api_key = SecretStr(key)
    try:
        result = extract_preferences(SAMPLE, config)
    except AIError as error:
        print(f'AI test failed ({error.code}): {error}')
        print('No automatic retries or new credentials were saved.')
        return 1
    if args.configure:
        set_key(str(env_file), 'GROQ_API_KEY', config.groq_api_key.get_secret_value())
        set_key(str(env_file), 'GROQ_MODEL', config.groq_model)
        print('Saved Groq settings in the ignored backend/.env file.')
    evidence = {
        'verified_at_utc': datetime.now(timezone.utc).isoformat(),
        'provider': 'Groq', 'model': config.groq_model,
        'status': 'real_provider_response_validated', 'sample_input': SAMPLE,
        'extracted_preferences': result.model_dump(),
        'note': 'A successful smoke test does not establish general extraction accuracy.',
    }
    print(json.dumps(evidence, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (KeyboardInterrupt, EOFError):
        print('\nCancelled.')
        raise SystemExit(1)
