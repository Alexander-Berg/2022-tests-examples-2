import typing

import pytest

from taxi.clients import driver_photos
from taxi.models import image_typing


def _build_headers(
        _id: str = '', uid: str = '', base: typing.Dict[str, str] = None,
) -> typing.Dict[str, str]:
    headers = base.copy() if base else {}
    if _id:
        headers['X-YaTaxi-UserId'] = _id
    if uid:
        headers['X-Yandex-UID'] = uid
    return headers


GOOD_TAG = '97c3b1ffaebe4d489f3481d9f22308f17654813286d65ed88709972dffa08bf8'
GOOD_ORDER = '8c83b49edb274ce0992f337061047375'
GOOD_HEADERS = _build_headers('b300bda7d41b4bae8d58dfa93221ef16', '4003514353')


@pytest.mark.parametrize(
    ['performer_tag', 'order_id', 'expected_code', 'expected_response'],
    [
        ('bad_tag', GOOD_ORDER, 200, {}),
        (GOOD_TAG, 'bad_order', 200, {}),
        (GOOD_TAG, GOOD_ORDER, 200, {'photos': {}}),
    ],
)
async def test_orderperformerinfo(
        web_app_client,
        patch_driver_photos,
        performer_tag: str,
        order_id: str,
        expected_code: int,
        expected_response: typing.Dict[str, dict],
):
    patch_driver_photos()

    response = await web_app_client.get(
        '/4.0/orderperformerinfo',
        params={'performer_tag': performer_tag, 'order_id': order_id},
        headers=GOOD_HEADERS,
    )

    assert response.status == expected_code
    assert await response.json() == expected_response


@pytest.mark.config(
    DRIVER_INFO_DISPLAY_SETTINGS={'econom': {'return_profile_photo': True}},
)
async def test_profile_photo(web_app_client, patch_driver_photos):
    patch_driver_photos(
        [
            driver_photos.Photo('avatar_url', image_typing.ImageType.AVA),
            driver_photos.Photo('photo_url', image_typing.ImageType.PORTRAIT),
        ],
    )

    response = await web_app_client.get(
        '/4.0/orderperformerinfo',
        params={'performer_tag': GOOD_TAG, 'order_id': GOOD_ORDER},
        headers=GOOD_HEADERS,
    )

    assert response.status == 200
    assert await response.json() == {
        'photos': {
            'avatar_image': {
                'url': 'avatar_url',
                'url_parts': {'key': '', 'path': ''},
            },
            'profile_photo': {
                'url': 'photo_url',
                'url_parts': {'key': '', 'path': ''},
            },
        },
    }


@pytest.mark.parametrize(
    ['headers', 'expected_code', 'expected_response'],
    [
        (GOOD_HEADERS, 200, {'photos': {}}),
        (_build_headers(_id='bad_id', base=GOOD_HEADERS), 200, {}),
        (_build_headers(uid='bad_uid', base=GOOD_HEADERS), 200, {}),
    ],
)
async def test_auth(
        web_app_client,
        patch_driver_photos,
        headers: typing.Dict[str, str],
        expected_code: int,
        expected_response: typing.Dict[str, dict],
):
    patch_driver_photos()

    response = await web_app_client.get(
        '/4.0/orderperformerinfo',
        params={'performer_tag': GOOD_TAG, 'order_id': GOOD_ORDER},
        headers=headers,
    )

    assert response.status == expected_code
    assert await response.json() == expected_response


async def test_empty_for_client_exception(
        web_app_client, patch_driver_photos_raise,
):
    patch_driver_photos_raise()

    response = await web_app_client.get(
        '/4.0/orderperformerinfo',
        params={'performer_tag': GOOD_TAG, 'order_id': GOOD_ORDER},
        headers=GOOD_HEADERS,
    )

    assert response.status == 200
    assert await response.json() == {}
