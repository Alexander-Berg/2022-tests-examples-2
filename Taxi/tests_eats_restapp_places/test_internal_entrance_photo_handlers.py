from typing import Dict
from typing import Optional

import aiohttp
import pytest

PLACE_ID = 1
TEST_IMAGENAME_HASH = '67989d5d7592478a98e102a64248035a'
TEST_GROUP_ID = 3738224
TEST_IMAGE_WIDTH = 1600
TEST_IMAGE_HEIGHT = 1200


@pytest.fixture(name='build_photo_file_request')
def _build_photo_file_request():
    def get_content_type(name: str, format_: str) -> Optional[str]:
        if name == 'file':
            return 'application/octet-stream'
        if name == 'string':
            return None
        if format_ == 'swagger':
            return 'text/plain'
        if name == 'int-required':
            return 'application/rare'
        return 'text/plain'

    def inner(
            args: Dict[str, Dict[str, object]], format_: str,
    ) -> Dict[str, object]:
        with aiohttp.MultipartWriter('form-data') as data:
            for name, dct in args.items():
                for type_, value in dct.items():
                    if not isinstance(value, bytes):
                        value = str(value).encode('utf-8')
                    content_type = get_content_type(type_, format_)
                    payload = aiohttp.payload.BytesPayload(
                        value, content_type=content_type,
                    )
                    payload.set_content_disposition('form-data', name=name)
                    if content_type is None:
                        del payload.headers['Content-Type']
                    data.append_payload(payload)

        return {
            'headers': {
                'Content-Type': (
                    'multipart/form-data; boundary=' + data.boundary
                ),
            },
            'data': data,
        }

    return inner


@pytest.fixture(name='mock_mds_avatar_200')
def _mock_mds_avatar_200(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_mds_avatar(request, imagename):
        return mockserver.make_response(
            status=200,
            json={
                'imagename': TEST_IMAGENAME_HASH,
                'group-id': TEST_GROUP_ID,
                'meta': {'orig-format': 'jpeg'},
                'sizes': {
                    'orig': {
                        'width': TEST_IMAGE_WIDTH,
                        'height': TEST_IMAGE_HEIGHT,
                        'path': '',
                    },
                },
            },
        )


@pytest.fixture(name='mock_mds_avatar_400')
def _mock_mds_avatar_400(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_mds_avatar(request, imagename):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'error request'},
        )


@pytest.fixture(name='mock_mds_avatar_500')
def _mock_mds_avatar_500(mockserver, request):
    @mockserver.json_handler(
        r'/avatars-mds/put-eda/(?P<imagename>\w+)', regex=True,
    )
    def _mock_mds_avatar(request, imagename):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': 'internal error'},
        )


async def test_entrance_photo_happy_path(
        mockserver,
        taxi_eats_restapp_places,
        build_photo_file_request,
        mock_mds_avatar_200,
):
    photo_weight = 130
    use_entrance_photo = False
    response = await taxi_eats_restapp_places.post(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
        **build_photo_file_request(
            {
                'weight': {'int': photo_weight},
                'use_entrance_photo': {'bool': use_entrance_photo},
                'image': {'file': '358232113523'},
            },
            'openapi',
        ),
    )
    assert response.status_code == 201
    assert response.json() == {
        'entrance_photo_url': (
            'http://avatars.mds.yandex.net/get-eda/{0}/{1}/{2}x{3}'.format(
                TEST_GROUP_ID,
                TEST_IMAGENAME_HASH,
                TEST_IMAGE_WIDTH,
                TEST_IMAGE_HEIGHT,
            )
        ),
    }

    response = await taxi_eats_restapp_places.get(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
    )
    assert response.status_code == 200
    response_json = response.json()
    url = 'http://avatars.mds.yandex.net/get-eda/{0}/{1}/{2}x{3}'.format(
        TEST_GROUP_ID,
        TEST_IMAGENAME_HASH,
        TEST_IMAGE_WIDTH,
        TEST_IMAGE_HEIGHT,
    )

    assert response_json == {
        'entrances_photos_info': [
            {
                'use_entrance_photo': use_entrance_photo,
                'weight': photo_weight,
                'url': url,
                'status': 'approved',
            },
        ],
    }

    response = await taxi_eats_restapp_places.delete(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
    )
    assert response.status_code == 204
    response = await taxi_eats_restapp_places.get(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
    )
    assert response.status_code == 200
    for info in response_json['entrances_photos_info']:
        info['status'] = 'deleted'
    assert response.json() == response_json


async def test_set_entrance_photo_avatar_400(
        taxi_eats_restapp_places,
        build_photo_file_request,
        mock_mds_avatar_400,
):
    response = await taxi_eats_restapp_places.post(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
        **build_photo_file_request(
            {
                'weight': {'int': 10},
                'use_entrance_photo': {'bool': True},
                'image': {'file': '3248347284'},
            },
            'openapi',
        ),
    )
    assert response.status_code == 500


async def test_set_entrance_photo_avatar_500(
        taxi_eats_restapp_places,
        build_photo_file_request,
        mock_mds_avatar_500,
):
    response = await taxi_eats_restapp_places.post(
        '/internal/places/entrance-photo?place_id={}'.format(PLACE_ID),
        **build_photo_file_request(
            {
                'weight': {'int': 5},
                'use_entrance_photo': {'bool': False},
                'image': {'file': '2138912941035743895734895798'},
            },
            'openapi',
        ),
    )
    assert response.status_code == 500


async def test_set_entrance_photo_delete_404(
        taxi_eats_restapp_places,
        build_photo_file_request,
        mock_mds_avatar_500,
):
    response = await taxi_eats_restapp_places.delete(
        '/internal/places/entrance-photo?place_id={}&url={}'.format(
            PLACE_ID,
            'http://avatars.mds.yandex.net/get-eda/no_group_id/no_guid/no_wxh',
        ),
    )
    assert response.status_code == 404
