# pylint: disable=too-many-lines
# pylint: disable=unused-variable

import hashlib

from aiohttp import web
import pytest

from taxi.clients import experiments3

from orderhistory.utils import experiments


CORE_EATS_HANDLER_FALLBACK = (
    'handler.eats-orderhistory./internal-api/v1/orders/retrieve-POST.fallback'
)


def _default_handle_oh(request, load_json, expected_request, response):
    if isinstance(expected_request, str):
        expected_request = load_json(expected_request)
    assert request.json == expected_request
    return web.json_response(load_json(response))


def _default_handle_eats_oh(request, load_json, expected_request, response):
    return _default_handle_oh(request, load_json, expected_request, response)


async def _request_item(
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
        '/4.0/orderhistory/v2/item',
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
        json={
            'service': service,
            'flavor': flavor,
            'order_id': '777',
            **extra_json,
        },
    )


async def test_wrong_service(taxi_orderhistory_web):
    response = await _request_item(taxi_orderhistory_web, 'nonexistent')

    assert response.status == 400
    data = await response.json()
    assert data['details']['reason'] == (
        'Invalid value for service: \'nonexistent\' must be one of '
        '[\'taxi\', \'eats\', \'grocery\', '
        '\'qr_pay\', \'drive\', \'scooters\', \'wind\', \'shuttle\', '
        '\'market\', \'delivery\', \'market_locals\']'
    )


@pytest.mark.parametrize(
    'ridehistory_resp, expected_resp',
    [
        ('ridehistory_resp_simple.json', 'expected_resp_taxi_order_id.json'),
        (
            'ridehistory_resp_wo_image_tag.json',
            'expected_resp_wo_image_tag.json',
        ),
    ],
)
async def test_taxi_item(
        taxi_orderhistory_web,
        mock_ridehistory,
        load_json,
        ridehistory_resp,
        expected_resp,
):
    @mock_ridehistory('/v2/item')
    async def handler_ridehistory(request):
        return _default_handle_oh(
            request,
            load_json,
            'ridehistory_expected_req_image_tags.json',
            ridehistory_resp,
        )

    response = await _request_item(
        taxi_orderhistory_web,
        'taxi',
        extra_json={
            'service_request': {
                'taxi': {
                    'image_tags': {'skin_version': '6', 'size_hint': 9999},
                },
            },
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)


async def test_ridehistory_not_found(
        taxi_orderhistory_web, mockserver, mock_ridehistory,
):
    @mock_ridehistory('/v2/item')
    async def handler_ridehistory(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'order_not_found', 'message': 'Order not found'},
        )

    response = await _request_item(
        taxi_orderhistory_web,
        'taxi',
        extra_json={
            'service_request': {
                'taxi': {
                    'image_tags': {'skin_version': '6', 'size_hint': 9999},
                },
            },
        },
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No such order',
    }


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS={
        '__default__': 'test',
        'eats': 'eats_image_tag',
    },
)
async def test_eats_item(
        taxi_orderhistory_web, mock_eats_orderhistory_py3, load_json,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_order_id.json',
            'eats_oh_resp_order_id.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'eats')

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_eats_order_id.json',
    )


@pytest.mark.config(QR_ORDERHISTORY_ENABLED=True)
@pytest.mark.parametrize(
    'expected_status',
    (
        pytest.param(200, id='normal work'),
        pytest.param(404, id='order not found'),
    ),
)
async def test_qr_item(
        taxi_orderhistory_web,
        mock_iiko_integration,
        mockserver,
        load_json,
        expected_status,
):
    @mock_iiko_integration('/iiko-integration/v1/orderhistory/order')
    async def handler_qr(request):
        if expected_status == 404:
            return mockserver.make_response(
                status=404,
                json={'code': 'order_not_found', 'message': 'Order not found'},
            )
        assert request.args['order_id'] == '777'
        assert request.headers['X-Request-Language'] == 'ru'
        assert request.headers['X-Yandex-UID'] == 'uid0'
        assert request.headers['X-YaTaxi-Bound-Uids'] == 'uid1,uid2,uid3'
        return load_json('qr_oh_resp_order.json')

    response = await _request_item(taxi_orderhistory_web, 'qr_pay')

    assert response.status == expected_status
    if expected_status == 200:
        assert await response.json() == load_json(
            'expected_resp_qr_order.json',
        )


@pytest.mark.parametrize(
    'service, error_message',
    [
        pytest.param(
            'taxi',
            'Taxi orderhistory disabled',
            marks=pytest.mark.config(TAXI_ORDERHISTORY_ENABLED=False),
        ),
        pytest.param(
            'grocery',
            'Grocery orderhistory disabled',
            marks=pytest.mark.config(EATS_ORDERHISTORY_ENABLED=False),
        ),
        pytest.param(
            'qr_pay',
            'QR orderhistory disabled',
            marks=pytest.mark.config(QR_ORDERHISTORY_ENABLED=False),
        ),
    ],
)
async def test_service_turned_off(
        taxi_orderhistory_web, service, error_message,
):
    response = await _request_item(taxi_orderhistory_web, service)

    assert response.status == 500
    assert await response.json() == {
        'code': 'SERVICE_DISABLED',
        'message': error_message,
    }


async def test_order_not_found_eats(
        taxi_orderhistory_web, load_json, mock_eats_orderhistory_py3,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_order_id.json',
            'empty_resp.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'eats')

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No such order',
    }


@pytest.mark.parametrize('fired_fallbacks', [[CORE_EATS_HANDLER_FALLBACK], []])
async def test_fallback(
        taxi_orderhistory_web,
        load_json,
        mock_fallbacks,
        mock_eats_orderhistory_error,
        fired_fallbacks,
):
    await mock_fallbacks(fired_fallbacks)

    response = await _request_item(taxi_orderhistory_web, 'eats')

    assert response.status == 500
    assert await response.json() == load_json(
        'expected_resp_eats_grocery_fallback_not_fired.json',
    )


@pytest.mark.parametrize(
    [
        'drive_resp',
        'expected_resp',
        'expected_resp_status',
        'expected_error_counts',
    ],
    [
        (
            'drive_item_basic.json',
            'expected_resp_drive_order_id_basic.json',
            200,
            {},
        ),
        (
            'drive_item_cancelled.json',
            'expected_resp_drive_order_id_cancelled.json',
            200,
            {},
        ),
        ('drive_item_broken_view.json', None, 500, {'deser_ViewsItem': 1}),
        (
            'drive_item_outofrange_view.json',
            None,
            500,
            {'prepare_order_full': 1},
        ),
    ],
)
@pytest.mark.config(
    DRIVE_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
)
async def test_drive_item(
        web_app_client,
        web_app,
        get_stats_by_label_values,
        load_json,
        mock_yandex_drive,
        drive_resp,
        expected_resp_status,
        expected_resp,
        expected_error_counts,
):
    @mock_yandex_drive('/sessions/item')
    def _handler_drive(request):
        assert request.args['lang'] == 'ru'
        assert request.headers['X-Ya-User-Ticket'] == 'some-user-ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'uid0').hexdigest()
        )
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return load_json(drive_resp)

    response = await _request_item(
        web_app_client,
        'drive',
        extra_headers={'x-ya-user-ticket': 'some-user-ticket'},
    )

    assert response.status == expected_resp_status

    if expected_resp_status == 200:
        assert await response.json() == load_json(expected_resp)

    stats = get_stats_by_label_values(
        web_app['context'],
        {'sensor': 'orderhistory.drive.response_parsing_failure'},
    )
    error_counts = {s['labels']['type']: s['value'] for s in stats}
    assert error_counts == expected_error_counts


@pytest.mark.parametrize(
    [
        'scooters_resp',
        'expected_resp',
        'expected_resp_status',
        'expected_error_counts',
    ],
    [
        (
            'scooters_item_basic.json',
            'expected_resp_scooters_order_id_basic.json',
            200,
            {},
        ),
        ('drive_item_broken_view.json', None, 500, {'deser_ViewsItem': 1}),
        (
            'drive_item_outofrange_view.json',
            None,
            500,
            {'prepare_order_full': 1},
        ),
    ],
)
@pytest.mark.config(
    DRIVE_ORDERHISTORY_ENABLED=True,
    SCOOTERS_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
)
async def test_scooters_item(
        web_app_client,
        web_app,
        patch,
        get_stats_by_label_values,
        load_json,
        mock_scooter_backend_sessions,
        scooters_resp,
        expected_resp_status,
        expected_resp,
        expected_error_counts,
):
    @mock_scooter_backend_sessions('/sessions/item')
    def _handler_scooter_backend(request):
        assert request.args['lang'] == 'ru'
        assert request.headers['X-Ya-User-Ticket'] == 'some-user-ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'uid0').hexdigest()
        )
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        return load_json(scooters_resp)

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_SCOOTERS_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
        ]

    response = await _request_item(
        web_app_client,
        'scooters',
        extra_headers={'x-ya-user-ticket': 'some-user-ticket'},
    )

    assert response.status == expected_resp_status

    if expected_resp_status == 200:
        assert await response.json() == load_json(expected_resp)

    stats = get_stats_by_label_values(
        web_app['context'],
        {'sensor': 'orderhistory.scooters.response_parsing_failure'},
    )
    error_counts = {s['labels']['type']: s['value'] for s in stats}
    assert error_counts == expected_error_counts


@pytest.mark.parametrize(
    ['expected_resp', 'expected_resp_status', 'expected_error_counts'],
    [('expected_resp_with_wind_scooters.json', 200, {})],
)
@pytest.mark.config(
    TAXI_ORDERHISTORY_ENABLED=False,
    WIND_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'ILS': {'__default__': 2, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$SIGN$$VALUE$ $CURRENCY$'}},
)
async def test_wind_item(
        web_app_client,
        web_app,
        patch,
        get_stats_by_label_values,
        load_json,
        mock_talaria_misc,
        expected_resp_status,
        expected_resp,
        expected_error_counts,
):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_SCOOTERS_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
        ]

    order_id = '777'

    @mock_talaria_misc('/talaria/v1/ride-history/item')
    async def _mock_talaria_ride_history_item(request):
        assert request.json == {
            'yandex_user_info': {
                'personal_phone_id': 'personal_phone_id',
                'yandex_uid': 'uid0',
            },
            'order_id': order_id,
        }
        return load_json('talaria_ride_history_resp_basic.json')

    response = await _request_item(
        web_app_client,
        'wind',
        extra_headers={'X-YaTaxi-User': 'personal_phone_id=personal_phone_id'},
    )

    assert response.status == expected_resp_status

    if expected_resp_status == 200:
        assert await response.json() == load_json(expected_resp)

    # stats = get_stats_by_label_values(
    #     web_app['context'],
    #     {'sensor': 'orderhistory.scooters.response_parsing_failure'},
    # )
    # error_counts = {s['labels']['type']: s['value'] for s in stats}
    # assert error_counts == expected_error_counts


@pytest.mark.parametrize(
    'expected_image_tag',
    [
        'nonexistent',
        pytest.param(
            'right_tag',
            marks=pytest.mark.config(
                ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
                    '__default__': 'right_tag',
                    'cash': {'image_tag': 'wrong_tag'},
                },
            ),
        ),
        pytest.param(
            'right_tag',
            marks=pytest.mark.config(
                ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
                    '__default__': 'wrong_tag',
                    'card': {'image_tag': 'right_tag'},
                },
            ),
        ),
        pytest.param(
            'right_tag',
            marks=pytest.mark.config(
                ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
                    '__default__': 'wrong_tag',
                    'card': {
                        'key': 'system',
                        'key_image_tags': {
                            'VISA': 'right_tag',
                            '__default__': 'wrong_tag',
                        },
                    },
                },
            ),
        ),
        pytest.param(
            'right_tag',
            marks=pytest.mark.config(
                ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
                    '__default__': 'wrong_tag',
                    'card': {
                        'key': 'system',
                        'key_image_tags': {
                            'MasterCard': 'wrong_tag',
                            '__default__': 'right_tag',
                        },
                    },
                },
            ),
        ),
        pytest.param(
            'right_tag',
            marks=pytest.mark.config(
                ORDERHISTORY_PAYMENT_METHOD_IMAGE_TAG={
                    '__default__': 'wrong_tag',
                    'card': {
                        'key': 'nonexistent',
                        'key_image_tags': {
                            'VISA': 'wrong_tag',
                            '__default__': 'right_tag',
                        },
                    },
                },
            ),
        ),
    ],
)
async def test_payment_method_image_tag(
        taxi_orderhistory_web, mock_ridehistory, load_json, expected_image_tag,
):
    @mock_ridehistory('/v2/item')
    async def handler_ridehistory(request):
        return _default_handle_oh(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_simple.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'taxi')

    assert response.status == 200
    data = await response.json()
    assert (
        data['order']['payment']['payment_method']['image_tag']
        == expected_image_tag
    )


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS={
        '__default__': 'test',
        'eats': 'eats_image_tag',
        '__brand_override__': {
            'some_brand': {'taxi': 'taxi_override', 'eats': 'eats_override'},
        },
    },
)
async def test_brand_image_tag_override(
        taxi_orderhistory_web, mock_eats_orderhistory_py3, load_json,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_order_id.json',
            'eats_oh_resp_order_id.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'eats')

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_brand_image_tag_override.json',
    )


@pytest.mark.config(
    GROCERY_ORDERHISTORY_ENABLED=True, EATS_ORDERHISTORY_ENABLED=False,
)
async def test_grocery_item(
        taxi_orderhistory_web, mock_grocery_order_log, load_json,
):
    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        assert (
            request.headers['X-Request-Application']
            == 'app_name=android,app_brand=some_brand'
        )
        return _default_handle_eats_oh(
            request,
            load_json,
            'grocery_oh_expected_req_order_id.json',
            'grocery_oh_resp_order_id.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'grocery')
    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_grocery_order_id.json',
    )


@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_item(taxi_orderhistory_web, mock_cargo_c2c, load_json):
    @mock_cargo_c2c('/orderhistory/v1/item')
    async def handler_cargo_c2c(request):
        assert request.json == {'delivery_id': '777'}
        return {
            'delivery_id': '777',
            'created_at': '2019-07-22T13:44:34+00:00',
            'key': 'value',
        }

    response = await _request_item(taxi_orderhistory_web, 'delivery')
    assert response.status == 200
    assert await response.json() == load_json('expected_resp_delivery.json')


@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_legacy_item(
        taxi_orderhistory_web, mock_cargo_c2c, load_json,
):
    @mock_cargo_c2c('/orderhistory/v1/item')
    async def handler_cargo_c2c(request):
        assert request.json == {'delivery_id': '777'}
        return {
            'delivery_id': '777',
            'created_at': '2019-07-22T13:44:34+00:00',
            'key': 'value',
        }

    response = await _request_item(
        taxi_orderhistory_web, 'taxi', flavor='delivery',
    )
    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_delivery_legacy.json',
    )


@pytest.mark.config(GROCERY_ORDERHISTORY_ENABLED=True)
async def test_grocery_item_non_available_eats(
        taxi_orderhistory_web,
        mockserver,
        mock_eats_orderhistory_py3,
        mock_grocery_order_log,
        load_json,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return mockserver.make_response('internal error', status=500)

    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'grocery_oh_expected_req_order_id.json',
            'grocery_oh_resp_order_id.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'grocery')
    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_grocery_order_id.json',
    )


async def test_empty_order_id(taxi_orderhistory_web):
    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/item',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android,app_brand=some_brand',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'service': 'taxi', 'order_id': ''},
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No such order',
    }


@pytest.mark.config(SHUTTLE_ORDERHISTORY_ENABLED=True)
async def test_shuttle_item(taxi_orderhistory_web, mockserver, load_json):
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/item',
    )
    async def handler_shuttle_control(request):
        return _default_handle_oh(
            request,
            load_json,
            {'order_id': '777'},
            'shuttle_resp_simple.json',
        )

    response = await _request_item(taxi_orderhistory_web, 'shuttle')
    assert response.status == 200
    assert await response.json() == load_json('expected_resp_shuttle.json')


@pytest.mark.config(MARKET_ORDERHISTORY_ENABLED=True)
async def test_market_item(
        taxi_orderhistory_web, mock_market_orderhistory, load_json,
):
    @mock_market_orderhistory('/api/v1')
    async def handler_market(request):
        assert request.query['name'] == 'resolveGoOrderHistoryItem'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket_777'
        assert request.headers['Api-Platform'] == 'go_orderhistory'
        assert request.json == {'params': [{'orderId': 777}]}

        return load_json('market_resp_simple.json')

    response = await _request_item(
        taxi_orderhistory_web,
        'market',
        extra_headers={'X-Ya-User-Ticket': 'user_ticket_777'},
    )

    assert response.status == 200
    assert await response.json() == load_json('expected_resp_market.json')


@pytest.mark.config(MARKET_ORDERHISTORY_ENABLED=True)
@pytest.mark.parametrize(
    [
        'extra_headers',
        'market_resp',
        'exp_resp_code',
        'exp_resp',
        'exp_market_times_called',
    ],
    [
        (
            {'X-Ya-User-Ticket': 'user_ticket_777'},
            'market_resp_not_found.json',
            404,
            {'code': 'ORDER_NOT_FOUND', 'message': 'No such order'},
            1,
        ),
        (None, None, 500, None, 0),
        (
            {'X-Ya-User-Ticket': 'user_ticket_777'},
            'market_resp_broken.json',
            500,
            None,
            1,
        ),
    ],
)
async def test_market_item_fails(
        taxi_orderhistory_web,
        mock_market_orderhistory,
        load_json,
        extra_headers,
        market_resp,
        exp_resp_code,
        exp_resp,
        exp_market_times_called,
):
    @mock_market_orderhistory('/api/v1')
    async def handler_market(request):
        return load_json(market_resp)

    response = await _request_item(
        taxi_orderhistory_web, 'market', extra_headers=extra_headers,
    )

    assert response.status == exp_resp_code
    if exp_resp is not None:
        assert await response.json() == exp_resp

    assert handler_market.times_called == exp_market_times_called


@pytest.mark.config(MARKET_LOCALS_ORDERHISTORY_ENABLED=True)
async def test_market_locals_item(
        taxi_orderhistory_web, mockserver, load_json,
):
    @mockserver.json_handler('/market-locals-orderhistory/api/v1/order/get/yg')
    async def _handler(request):
        assert request.query['orderId'] == '777'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket_777'
        return load_json('market_locals_resp.json')

    response = await _request_item(
        taxi_orderhistory_web,
        'market_locals',
        extra_headers={'X-Ya-User-Ticket': 'user_ticket_777'},
    )

    assert response.status == 200

    assert await response.json() == load_json(
        'expected_resp_market_locals.json',
    )
