from io import BytesIO

from fastapi import HTTPException
from PIL import Image
import pytest

from app import images
from test_admin import HEADERS, client as client, meal, shop


def photo_bytes(format='PNG', size=(80, 50)):
    stream = BytesIO()
    Image.new('RGB', size, color='#35744a').save(stream, format=format)
    return stream.getvalue()


def record(client, kind):
    stall = shop(client)
    if kind == 'stalls':
        return stall['id']
    return client.post('/api/menu-items', headers=HEADERS, json=meal(stall['id'])).json()['id']


@pytest.mark.parametrize('kind', ['stalls', 'menu-items'])
def test_photo_upload_updates_the_record_and_can_be_removed(client, monkeypatch, kind):
    record_id = record(client, kind)
    uploaded = {}

    async def fake_storage(data, path, token):
        uploaded.update(data=data, path=path, token=token)
        return f'https://test-project.supabase.co/storage/v1/object/public/animo-meals-images/{path}'

    monkeypatch.setattr(images, 'store_image', fake_storage)
    response = client.post(f'/api/{kind}/{record_id}/image',
                           headers={**HEADERS, 'Content-Type': 'image/png'}, content=photo_bytes())
    assert response.status_code == 200
    result = response.json()['image_url']
    assert f'/{kind}/{record_id}/' in result
    assert client.get(f'/api/{kind}/{record_id}').json()['image_url'] == result
    assert uploaded['token'] == 'test-access-token'
    with Image.open(BytesIO(uploaded['data'])) as photo:
        assert photo.format == 'WEBP'
    if kind == 'stalls':
        payload = {'name': 'Test shop', 'location': 'Test landmark', 'image_url': None}
    else:
        payload = meal(client.get(f'/api/menu-items/{record_id}').json()['stall_id'], image_url=None)
    assert client.put(f'/api/{kind}/{record_id}', headers=HEADERS, json=payload).status_code == 200
    assert client.get(f'/api/{kind}/{record_id}').json()['image_url'] is None


@pytest.mark.parametrize('mime,body,expected', [
    ('image/svg+xml', b'<svg/>', 415),
    ('image/png', b'not a photo', 422),
    ('image/jpeg', photo_bytes('PNG'), 422),
    ('image/png', b'', 422),
    ('image/png', b'x' * (images.MAX_UPLOAD_BYTES + 1), 413),
])
def test_invalid_uploads_do_not_change_records(client, monkeypatch, mime, body, expected):
    record_id = record(client, 'stalls')

    async def unexpected_storage(*args):
        pytest.fail('Invalid uploads must never reach storage')

    monkeypatch.setattr(images, 'store_image', unexpected_storage)
    response = client.post(f'/api/stalls/{record_id}/image',
                           headers={**HEADERS, 'Content-Type': mime}, content=body)
    assert response.status_code == expected
    assert client.get(f'/api/stalls/{record_id}').json()['image_url'] is None


def test_anonymous_image_upload_is_rejected(client):
    assert client.post('/api/stalls/1/image', headers={'Content-Type': 'image/png'},
                       content=photo_bytes()).status_code == 401


def test_missing_record_does_not_upload(client):
    assert client.post('/api/stalls/999/image', headers={**HEADERS, 'Content-Type': 'image/png'},
                       content=photo_bytes()).status_code == 404


def test_storage_failure_keeps_the_existing_photo(client, monkeypatch):
    record_id = record(client, 'stalls')
    original = 'https://test-project.supabase.co/storage/v1/object/public/animo-meals-images/old.webp'
    client.put(f'/api/stalls/{record_id}', headers=HEADERS,
               json={'name': 'Test shop', 'location': 'Test landmark', 'image_url': original})

    async def failed_storage(*args):
        raise HTTPException(503, 'Photo storage is temporarily unavailable.')

    monkeypatch.setattr(images, 'store_image', failed_storage)
    response = client.post(f'/api/stalls/{record_id}/image',
                           headers={**HEADERS, 'Content-Type': 'image/png'}, content=photo_bytes())
    assert response.status_code == 503
    assert client.get(f'/api/stalls/{record_id}').json()['image_url'] == original


def test_non_storage_image_urls_are_rejected(client):
    assert client.post('/api/stalls', headers=HEADERS, json={
        'name': 'Bad photo', 'location': 'Gate', 'image_url': 'javascript:alert(1)',
    }).status_code == 422
    assert client.post('/api/stalls', headers=HEADERS, json={
        'name': 'Other source', 'location': 'Gate', 'image_url': 'https://other.example/photo.png',
    }).status_code == 422


def test_large_dimensions_are_resized_and_photo_metadata_is_removed():
    output = images.normalize_image(photo_bytes('JPEG', size=(3000, 2000)), 'image/jpeg')
    with Image.open(BytesIO(output)) as photo:
        assert photo.size == (1600, 1067)
        assert not photo.getexif()


def test_transparent_photo_keeps_its_alpha_channel():
    source = BytesIO()
    Image.new('RGBA', (10, 10), (10, 80, 20, 0)).save(source, format='PNG')
    output = images.normalize_image(source.getvalue(), 'image/png')
    with Image.open(BytesIO(output)) as photo:
        assert photo.mode == 'RGBA'
        assert photo.getpixel((0, 0))[3] == 0
