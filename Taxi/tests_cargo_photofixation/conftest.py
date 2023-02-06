import aiohttp
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from cargo_photofixation_plugins import *  # noqa: F403 F401


IMAGE_FILE_MOCK = b'IMAGE FILE MOCK'


class MultiPartRequest:
    def __init__(self, headers, data):
        self.headers = headers
        self.data = data


@pytest.fixture(name='build_default_headers')
def _build_default_headers():
    def wrapper():
        return {'Accept-Language': 'en-US;q=1, ru;q=0.8'}

    return wrapper


@pytest.fixture(name='build_photo_file_request')
def _build_photo_file_request(build_default_headers):
    def inner(photo_id, file):
        with aiohttp.MultipartWriter('form-data') as data:
            payload = aiohttp.payload.BytesPayload(
                file, headers={'Content-Type': 'image/jpeg'},
            )
            payload.set_content_disposition('form-data', name='file')
            data.append_payload(payload)

            payload = aiohttp.payload.StringPayload(photo_id)
            payload.set_content_disposition('form-data', name='photo_id')
            data.append_payload(payload)

        headers = build_default_headers()
        headers['Content-Type'] = (
            'multipart/form-data; boundary=' + data.boundary
        )

        return MultiPartRequest(headers, data)

    return inner


@pytest.fixture(name='default_image_file_mock')
def _default_image_file_mock():
    def wrapper():
        return IMAGE_FILE_MOCK

    return wrapper


@pytest.fixture(name='upload_order_photos')
async def _upload_order_photos(
        taxi_cargo_photofixation, build_photo_file_request,
):
    async def wrapper(cargo_order_id, claim_point_id, photos, files=None):
        if not files:
            files = [IMAGE_FILE_MOCK for _ in photos]
        order_photos = {
            'cargo_order_id': cargo_order_id,
            'claim_point_id': claim_point_id,
            'photos': photos,
        }
        response = await taxi_cargo_photofixation.post(
            '/v1/photos/init-uploading', order_photos,
        )
        assert response.status_code == 200
        for i, photo in enumerate(response.json()['photos']):
            file_request = build_photo_file_request(
                photo['photo_id'], files[i],
            )
            response = await taxi_cargo_photofixation.post(
                '/v1/photos/file',
                data=file_request.data,
                headers=file_request.headers,
            )
            assert response.status_code == 200

    return wrapper


@pytest.fixture
async def create_default_photos(taxi_cargo_photofixation, upload_order_photos):
    cargo_order_ids = [
        {'order': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'points': [1, 2, 3]},
        {'order': 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'points': [1, 2, 3]},
        {'order': 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'points': [1, 2, 3]},
    ]
    photos = [
        {'name': 'photo1.jpg', 'size': len(IMAGE_FILE_MOCK)},
        {'name': 'photo2.jpg', 'size': len(IMAGE_FILE_MOCK)},
        {'name': 'photo3.jpg', 'size': len(IMAGE_FILE_MOCK)},
    ]
    for item in cargo_order_ids:
        for photo in item['points']:
            await upload_order_photos(item['order'], photo, photos)
