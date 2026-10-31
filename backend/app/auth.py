"""Verify Supabase access tokens remotely and authorize one configured administrator."""
import base64
import json
from typing import Annotated
from urllib.parse import urlsplit

import httpx
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

bearer = HTTPBearer(auto_error=False)


def auth_config():
    url = settings.supabase_url.rstrip('/')
    parsed = urlsplit(url)
    key = settings.supabase_publishable_key.get_secret_value()
    public_key = key.startswith('sb_publishable_')
    if not public_key:
        try:
            payload = key.split('.')[1]
            public_key = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4))).get('role') == 'anon'
        except (ValueError, IndexError, AttributeError):
            public_key = False
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.path
            or parsed.query or parsed.fragment or parsed.username or not public_key
            or not settings.admin_user_id):
        raise HTTPException(503, 'Administrator sign-in is not configured yet.')
    return url, key


def require_admin(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    if not credentials or len(credentials.credentials) > 8192:
        raise HTTPException(401, 'Please sign in again.', headers={'WWW-Authenticate': 'Bearer'})
    url, key = auth_config()
    try:
        response = httpx.get(
            f'{url}/auth/v1/user',
            headers={'apikey': key, 'Authorization': f'Bearer {credentials.credentials}'},
            timeout=10,
        )
        if response.status_code in (401, 403):
            raise HTTPException(401, 'Your session has expired. Please sign in again.')
        if response.status_code != 200:
            raise HTTPException(503, 'Sign-in service is temporarily unavailable.')
        user = response.json()
        if not isinstance(user, dict) or not isinstance(user.get('id'), str):
            raise ValueError('Invalid identity response')
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, 'Sign-in service is temporarily unavailable.') from None
    # Never trust a client-supplied role, email or user_metadata flag.
    if user['id'] != settings.admin_user_id:
        raise HTTPException(403, 'This account does not have administrator access.')
    return user['id']
