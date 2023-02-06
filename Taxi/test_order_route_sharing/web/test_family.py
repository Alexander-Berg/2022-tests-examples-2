# pylint: disable=redefined-outer-name,unused-argument
import json
import uuid

import pytest

from .. import helpers


ADMIN_PHONE_ID = '59d8cbad83ede0ee28d4a774'
ADMIN_NAME = 'Василий'


@pytest.fixture
def mock_user_api_search(mockserver, load_json):
    @mockserver.json_handler('/user-api/users/search')
    def _mock_users_search(request):
        assert request.json['yandex_uids'] == ['123123123']
        assert request.json['applications'] == ['android', 'iphone']
        assert request.json['fields'] == [
            '_id',
            'application_version',
            'application',
            'phone_id',
        ]

        return load_json('user_api_response.json')

    return _mock_users_search


@pytest.fixture
def mock_family(mockserver):
    @mockserver.json_handler('family/4.0/family/v1/route_sharing_members')
    def _mock_family(request):
        return {
            'members': [
                {
                    'yandex_uid': '123123123',
                    'name': ADMIN_NAME,
                    'role': 'owner',
                },
                {'yandex_uid': '123', 'name': 'Наталья', 'role': 'user'},
            ],
        }

    return _mock_family


async def _invoke_share_trip_request(
        taxi_order_route_sharing_web, sharing_key, value, status=200,
):
    response = await taxi_order_route_sharing_web.post(
        '/v1/share_with_family',
        headers={
            'X-Yandex-UID': '123',
            'X-YaTaxi-PhoneId': 'user_phone_id_1',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
        },
        json={
            'order_id': 'order_id_1',
            'sharing_key': sharing_key,
            'tariff_class': 'econom',
            'share_ride_with_family': {'value': value},
        },
    )
    assert response.status == status


async def _invoke_sharing_info_request(
        taxi_order_route_sharing_web, sharing_key,
) -> dict:
    response = await taxi_order_route_sharing_web.get(
        '/v1/sharing_info', params={'key': sharing_key},
    )
    assert response.status == 200

    json = await response.json()
    return json


async def _invoke_shared_orders_request(taxi_order_route_sharing_web) -> dict:
    response = await taxi_order_route_sharing_web.get(
        '/v1/shared_orders',
        headers={
            'X-YaTaxi-PhoneId': ADMIN_PHONE_ID,
            'X-Ya-Family-Role': 'owner',
        },
    )
    assert response.status == 200

    json = await response.json()
    return json


async def _invoke_info_request(taxi_order_route_sharing_web, sharing_key):
    response = await taxi_order_route_sharing_web.get(
        '/v1/info',
        params={'key': sharing_key, 'status': 'driving'},
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-PhoneId': ADMIN_PHONE_ID,
            'X-Ya-Family-Role': 'owner',
        },
    )
    assert response.status == 200

    json = await response.json()
    return json


async def test_share_with_family(
        taxi_order_route_sharing_web,
        mock_user_api_search,
        mock_family,
        pgsql,
        mockserver,
        load_json,
):  # pylint: disable=R0913
    await _invoke_share_trip_request(
        taxi_order_route_sharing_web, 'family_key_1', True,
    )

    item = helpers.select_by_order_id(pgsql, 'order_id_1')

    assert item.sharing_key == 'family_key_1'
    assert not item.finished_at
    assert item.application == 'android'
    assert item.tariff_class == 'econom'
    assert item.phone_ids == [ADMIN_PHONE_ID]
    assert item.user_exists
    assert item.admin_name == ADMIN_NAME
    assert item.sharing_on


@pytest.mark.parametrize(
    ['family_status', 'family_body', 'order_route_sharing_status'],
    [
        pytest.param(404, {}, 404, id='not found'),
        pytest.param(
            200,
            {
                'members': [
                    {
                        'yandex_uid': '123123123',
                        'name': ADMIN_NAME,
                        'role': 'user',
                    },
                    {'yandex_uid': '123', 'name': 'Наталья', 'role': 'user'},
                ],
            },
            500,
            id='no admin in members list',
        ),
    ],
)
async def test_share_with_family_failure(
        taxi_order_route_sharing_web,
        mockserver,
        family_status,
        family_body,
        order_route_sharing_status,
):
    @mockserver.json_handler('/family/4.0/family/v1/route_sharing_members')
    def _mock_family(request):
        return mockserver.make_response(
            json.dumps(family_body), status=family_status,
        )

    await _invoke_share_trip_request(
        taxi_order_route_sharing_web,
        uuid.uuid4().hex,
        True,
        status=order_route_sharing_status,
    )


@pytest.mark.pgsql(
    'order_route_sharing',
    files=[
        'pg_order_route_sharing.sql',
        'pg_order_route_sharing_family_rides.sql',
    ],
)
async def test_sharing_info_basic(
        taxi_order_route_sharing_web, mock_user_api_search, pgsql,
):
    json = await _invoke_sharing_info_request(
        taxi_order_route_sharing_web, 'key_1',
    )
    assert json == {
        'phone_ids': ['00aaaaaaaaaaaaaaaaaaaa01', '00aaaaaaaaaaaaaaaaaaaa02'],
        'family_info': {'admin_name': ADMIN_NAME, 'sharing_on': True},
    }


@pytest.mark.translations(
    client_messages={
        'shared_order.popup_family_ride_title.econom': {
            'ru': '{admin_name}, член семьи в поездке',
        },
        'shared_order.status_title.c2c.econom.driving': {
            'ru': 'Водитель едет к пассажиру',
        },
        'shared_order.status_title.c2c.econom.transporting.with_time': {
            'ru': 'Водитель выполняет заказ, осталось %(minutes_left)s мин',
        },
    },
)
async def test_family_flow(
        taxi_order_route_sharing_web, mock_user_api_search, pgsql, mockserver,
):
    family_calls_count = 0

    @mockserver.json_handler('/family/4.0/family/v1/route_sharing_members')
    def _mock_family(request):
        nonlocal family_calls_count
        family_calls_count += 1
        return {
            'members': [
                {
                    'yandex_uid': '123123123',
                    'name': ADMIN_NAME,
                    'role': 'owner',
                },
                {'yandex_uid': '123', 'name': 'Наталья', 'role': 'user'},
            ],
        }

    for iteration, value in enumerate([True, True, False, True]):
        await _invoke_share_trip_request(
            taxi_order_route_sharing_web, 'family_key_2', value,
        )
        sharing_info_resp = await _invoke_sharing_info_request(
            taxi_order_route_sharing_web, 'family_key_2',
        )
        assert sharing_info_resp == {
            'phone_ids': [ADMIN_PHONE_ID],
            'family_info': {'admin_name': ADMIN_NAME, 'sharing_on': value},
        }, 'Wrong /v1/sharing_info response, iteration: {}'.format(iteration)

        sharing_orders_resp = await _invoke_shared_orders_request(
            taxi_order_route_sharing_web,
        )
        assert len(sharing_orders_resp['shared_orders']) == (
            1 if value else 0
        ), 'Wrong /v1/shared_orders response, iteration: {}'.format(iteration)

        if sharing_orders_resp['shared_orders']:
            info_resp = await _invoke_info_request(
                taxi_order_route_sharing_web, 'family_key_2',
            )
            assert (
                info_resp['display_info']['popup_title']
                == f'{ADMIN_NAME}, член семьи в поездке'
            ), 'Wrong /v1/info response, iteration: {}'.format(iteration)

    assert family_calls_count == 4
