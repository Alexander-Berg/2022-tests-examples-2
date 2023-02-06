# pylint: disable=unused-variable

from aiohttp import web
import pytest


def _default_handle_oh(request, load_json, expected_request, response):
    if isinstance(expected_request, str):
        expected_request = load_json(expected_request)
    assert request.json == expected_request
    return web.json_response(load_json(response))


async def _request_receipts(
        taxi_orderhistory_web,
        service,
        extra_headers=None,
        extra_json=None,
        flavor=None,
):
    if not extra_headers:
        extra_headers = {}
    if not extra_json:
        extra_json = {}
    return await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/receipts',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android,app_brand=some_brand',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            **extra_headers,
        },
        json={'service': service, 'order_id': '777', **extra_json},
    )


async def test_wrong_service(taxi_orderhistory_web):
    response = await _request_receipts(taxi_orderhistory_web, 'nonexistent')

    assert response.status == 400
    data = await response.json()
    assert data['details']['reason'] == (
        'Invalid value for service: \'nonexistent\' must be one of '
        '[\'taxi\', \'eats\', \'grocery\', '
        '\'qr_pay\', \'drive\', \'scooters\', \'wind\', \'shuttle\', '
        '\'market\', \'delivery\', \'market_locals\']'
    )


async def test_taxi_receipts(
        taxi_orderhistory_web, mock_ridehistory, load_json,
):
    @mock_ridehistory('/v2/receipts')
    async def handler_ridehistory(request):
        return _default_handle_oh(
            request,
            load_json,
            'expected_request_taxi.json',
            'receipts_response.json',
        )

    response = await _request_receipts(taxi_orderhistory_web, 'taxi')

    assert response.status == 200
    assert await response.json() == load_json('expected_response.json')


@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_receipts(
        taxi_orderhistory_web, mock_ridehistory, load_json, mockserver,
):
    @mockserver.json_handler('/cargo-c2c/orderhistory/v1/receipts')
    def _mock_cargo_c2c(request):
        return _default_handle_oh(
            request,
            load_json,
            'expected_request_delivery.json',
            'receipts_response.json',
        )

    response = await _request_receipts(taxi_orderhistory_web, 'delivery')

    assert response.status == 200
    assert await response.json() == load_json('expected_response.json')
