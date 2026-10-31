"""Admin-only image validation, normalization and Supabase Storage upload."""
from io import BytesIO
import ssl
from typing import Annotated, Literal
from uuid import uuid4
import warnings

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.admin import commit, find
from app.auth import auth_config, bearer, require_admin
from app.database import get_session
from app.models import MenuItem, Stall

router = APIRouter()
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_STORED_BYTES = 2 * 1024 * 1024
TYPES = {'image/jpeg': 'JPEG', 'image/png': 'PNG', 'image/webp': 'WEBP'}


def normalize_image(data, content_type):
    if content_type not in TYPES:
        raise HTTPException(415, 'Choose a JPEG, PNG or WebP photo.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(BytesIO(data)) as photo:
                if photo.format != TYPES[content_type]:
                    raise ValueError('Image format mismatch')
                if photo.width * photo.height > 16_000_000:
                    raise HTTPException(422, 'Choose a photo smaller than 16 megapixels.')
                photo.load()
                mode = 'RGBA' if photo.mode in ('RGBA', 'LA') or 'transparency' in photo.info else 'RGB'
                clean = ImageOps.exif_transpose(photo).convert(mode)
                clean.thumbnail((1600, 1600))
                output = BytesIO()
                clean.save(output, format='WEBP', quality=85)
        result = output.getvalue()
        if len(result) > MAX_STORED_BYTES:
            raise HTTPException(413, 'This photo is too large after processing. Choose a smaller image.')
        return result
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError,
            Image.DecompressionBombWarning):
        raise HTTPException(422, 'The file is not a valid supported photo.') from None


async def store_image(data, path, token):
    url, key = auth_config()
    try:
        async with httpx.AsyncClient(verify=ssl.create_default_context(), timeout=30) as client:
            response = await client.post(
                f'{url}/storage/v1/object/animo-meals-images/{path}',
                content=data,
                headers={'apikey': key, 'Authorization': f'Bearer {token}',
                         'Content-Type': 'image/webp', 'Cache-Control': '3600'},
            )
    except httpx.HTTPError:
        raise HTTPException(503, 'Photo storage is temporarily unavailable. Please try again.') from None
    if response.status_code not in (200, 201):
        raise HTTPException(503, 'Photo upload failed. Check the storage setup and try again.')
    return f'{url}/storage/v1/object/public/animo-meals-images/{path}'


@router.post('/api/{kind}/{record_id}/image')
async def upload_record_image(
    kind: Literal['stalls', 'menu-items'], record_id: int, request: Request,
    session: Annotated[Session, Depends(get_session)],
    admin_id: Annotated[str, Depends(require_admin)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
):
    record = find(session, Stall if kind == 'stalls' else MenuItem, record_id)
    content_type = request.headers.get('content-type', '').split(';')[0].strip().lower()
    if content_type not in TYPES:
        raise HTTPException(415, 'Choose a JPEG, PNG or WebP photo.')
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, 'Photos must be 5 MB or smaller.')
        data.extend(chunk)
    image = normalize_image(data, content_type)
    path = f'{admin_id}/{kind}/{record_id}/{uuid4().hex}.webp'
    image_url = await store_image(image, path, credentials.credentials)
    record.image_url = image_url
    commit(session)
    return {'image_url': image_url}
