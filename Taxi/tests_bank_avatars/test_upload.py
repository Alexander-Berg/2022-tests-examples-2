# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_avatars_plugins.generated_tests import *

import pytest
import aiohttp

IMAGES_HOST = 'avatars.mdst.yandex.net'


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=IMAGES_HOST)
async def test_ok_with_name(taxi_bank_avatars, mockserver, avatars_mds_mock):

    image_name = 'image_name'
    group_id = 123
    image_body = b'JPEG123, image body'

    avatars_mds_mock.set_group_id(group_id)

    with aiohttp.MultipartWriter('form-data') as data:
        payload = aiohttp.payload.BytesPayload(
            image_body, headers={'Content-Type': 'image/jpg'},
        )
        payload.set_content_disposition('form-data', name='image')
        data.append_payload(payload)

        payload = aiohttp.payload.StringPayload(image_name)
        payload.set_content_disposition('form-data', name='image_name')
        data.append_payload(payload)

    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
    }

    response = await taxi_bank_avatars.post(
        '/v1/avatars/v1/upload', data=data, headers=headers,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_named_handler.has_calls
    assert (
        response.json().get('image_url')
        == f'{IMAGES_HOST}/get-fintech/{group_id}/{image_name}/'
    )


@pytest.mark.config(BANK_AVATARS_IMAGES_HOST=IMAGES_HOST)
async def test_ok_without_name(
        taxi_bank_avatars, mockserver, avatars_mds_mock,
):

    image_name = 'image_name'
    group_id = 123
    image_body = b'JPEG123, image body'

    avatars_mds_mock.set_group_id(group_id)
    avatars_mds_mock.set_image_name(image_name)

    with aiohttp.MultipartWriter('form-data') as data:
        payload = aiohttp.payload.BytesPayload(
            image_body, headers={'Content-Type': 'image/jpg'},
        )
        payload.set_content_disposition('form-data', name='image')
        data.append_payload(payload)

    headers = {
        'Content-Type': 'multipart/form-data; boundary=' + data.boundary,
    }

    response = await taxi_bank_avatars.post(
        '/v1/avatars/v1/upload', data=data, headers=headers,
    )

    assert response.status_code == 200
    assert avatars_mds_mock.put_unnamed_handler.has_calls
    assert (
        response.json().get('image_url')
        == f'{IMAGES_HOST}/get-fintech/{group_id}/{image_name}/'
    )
