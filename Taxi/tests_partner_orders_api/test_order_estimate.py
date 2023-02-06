import copy
import json

import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'int_api_paid_supply, partner_orders_api_paid_supply',
    [
        (
            {
                'enable_conditions': [
                    'change_payment_type_to_cashless',
                    'define_point_b',
                ],
                'free_cancel_timeout_sec': 180,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
            {
                'state': 'possible',
                'enable_conditions': [
                    'change_payment_type_to_cashless',
                    'define_point_b',
                ],
                'free_cancel_timeout_sec': 180,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
        ),
        (
            {
                'free_cancel_timeout_sec': 180,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
            {
                'state': 'enabled',
                'free_cancel_timeout_sec': 180,
                'paid_supply_price_raw': 40.0,
                'paid_supply_price': '40 руб.',
            },
        ),
        (None, None),
    ],
)
async def test_order_estimate_headers(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_paid_supply,
        partner_orders_api_paid_supply,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request.update(
            {'selected_class': 'econom', 'all_classes': True},
        )
        assert request.json == int_api_request
        int_api_response = load_json('int_api_response.json')
        if int_api_paid_supply is not None:
            service_levels = int_api_response.get('service_levels')
            for service_level in service_levels:
                service_level['paid_supply'] = int_api_paid_supply
        return int_api_response

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    expected_json = load_json('response.json')
    if partner_orders_api_paid_supply is not None:
        service_levels = expected_json.get('service_levels')
        for service_level in service_levels:
            service_level['paid_supply'] = partner_orders_api_paid_supply
    assert response.status_code == 200
    assert expected_json == response.json()

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate', json=request,
    )
    assert response.status_code == 400

    request_wrong_point = copy.deepcopy(request)
    request_wrong_point['route'][0] = [1.0, 1.0]
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request_wrong_point,
    )
    assert response.status_code == 404


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'overrides, code, error_response_json, '
    'int_api_request_overrides, ok_response_overrides',
    [
        (
            {'route': [[37.580165, 55.801424]]},
            200,
            {},
            {
                'route': [[37.580165, 55.801424]],
                'selected_class': 'econom',
                'all_classes': True,
            },
            {},
        ),
        (
            {'route': [[100, 100]]},
            404,
            {
                'code': 'ZONE_NOT_FOUND',
                'message': 'Can not find geozone for point [100, 100]',
            },
            {'selected_class': 'child_tariff'},
            {},
        ),
        (
            {'class': 'child_tariff', 'route': [[100, 100]]},
            404,
            {
                'code': 'ZONE_NOT_FOUND',
                'message': 'Can not find geozone for point [100, 100]',
            },
            {'selected_class': 'child_tariff'},
            {},
        ),
        (
            {'class': 'comfort'},
            404,
            {
                'code': 'CLASS_NOT_FOUND',
                'message': 'Class comfort not found for zone moscow',
            },
            {},
            {},
        ),
        (
            {
                'user': {
                    'agent_user_id': '241406a0972b4c4abbf5187e684f0061',
                    'phone': '+70001112233',
                    'type': 'individual',
                },
            },
            403,
            {
                'code': 'UNKNOWN_PHONE',
                'message': 'Phone +70001112233 not found',
            },
            {},
            {},
        ),
        (
            {
                'user': {
                    'agent_user_id': '241406a0972b4c4abbf5187e684f0061',
                    'phone': '+79179991122',
                    'type': 'individual',
                },
            },
            200,
            {},
            {
                'selected_class': 'econom',
                'all_classes': True,
                'user': {'phone': '+79179991122'},
            },
            {},
        ),
        (
            {'requirements': [{'name': 'unknown', 'unknown type': {}}]},
            404,
            {
                'code': 'WRONG_REQUIREMENTS',
                'message': 'Can\'t handle following requirements: {unknown}',
            },
            {'selected_class': 'econom', 'all_classes': True},
            {},
        ),
        (
            {
                'is_fixed_price': True,
                'route': [[37.580165, 55.801424], [37.590165, 55.811424]],
            },
            200,
            {},
            {
                'selected_class': 'econom',
                'all_classes': True,
                'route': [[37.580165, 55.801424], [37.590165, 55.811424]],
            },
            {},
        ),
        (
            {'route': [[37.580165, 55.801424], [37.590165, 55.811424]]},
            200,
            {},
            {'selected_class': 'econom', 'all_classes': True},
            {},
        ),
    ],
)
async def test_order_estimate_requests_format(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        overrides,
        code,
        error_response_json,
        int_api_request_overrides,
        ok_response_overrides,
):
    request = load_json('request.json')
    request.update(overrides)

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request.update(int_api_request_overrides)
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == code
    if code == 200:
        expected_response = load_json('response.json')
        expected_response.update(ok_response_overrides)
        assert response.json() == expected_response
    else:
        assert response.json() == error_response_json


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'request_params, response_params',
    [
        (
            {
                'fixed_price_requested': False,
                'offer': '5e5ffffbd0404e798b3b155f563c0877',
                'is_fixed_price': True,
                'service_levels_is_fixed_price': False,
                'valid_until': '2018-04-24T10:30:00+00:00',
            },
            {
                'is_fixed_price': False,
                'offer': None,
                'service_levels_is_fixed_price': False,
            },
        ),
        (
            {
                'fixed_price_requested': True,
                'offer': None,
                'is_fixed_price': False,
                'service_levels_is_fixed_price': True,
            },
            {
                'is_fixed_price': False,
                'offer': None,
                'service_levels_is_fixed_price': True,
            },
        ),
        (
            {
                'fixed_price_requested': True,
                'offer': '5e5ffffbd0404e798b3b155f563c0877',
                'is_fixed_price': True,
                'service_levels_is_fixed_price': True,
                'valid_until': '2018-04-24T10:30:00+00:00',
            },
            {
                'is_fixed_price': True,
                'offer': '5e5ffffbd0404e798b3b155f563c0877',
                'service_levels_is_fixed_price': True,
                'valid_until': '2018-04-24T10:30:00+00:00',
            },
        ),
        (
            {
                'fixed_price_requested': True,
                'offer': '5e5ffffbd0404e798b3b155f563c0877',
                'is_fixed_price': True,
                'service_levels_is_fixed_price': False,
            },
            {
                'is_fixed_price': True,
                'offer': '5e5ffffbd0404e798b3b155f563c0877',
                'service_levels_is_fixed_price': False,
            },
        ),
    ],
)
async def test_fixed_price(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        request_params,
        response_params,
):
    request = load_json('request.json')
    request['is_fixed_price'] = request_params['fixed_price_requested']

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        response = load_json('int_api_response.json')
        assert response['service_levels']
        response['service_levels'][0]['is_fixed_price'] = request_params[
            'service_levels_is_fixed_price'
        ]
        response['offer'] = request_params['offer']
        response['is_fixed_price'] = request_params['is_fixed_price']
        if request_params.get('valid_until') is not None:
            response['valid_until'] = request_params['valid_until']
        return response

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json.get('offer') == response_params.get('offer')
    assert response_json['is_fixed_price'] == response_params['is_fixed_price']
    assert response_json['service_levels']
    assert response_json['service_levels'][0][
        'is_fixed_price'
    ] == response_params.get('service_levels_is_fixed_price')
    if response_params.get('valid_until') is not None:
        assert response_json['valid_until'] == response_params['valid_until']
    else:
        assert 'valid_until' not in response_json


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'int_api_status, partner_status, response_json',
    [
        (
            400,
            400,
            {'code': 'BAD_REQUEST', 'message': 'Invalid request parameters'},
        ),
        (
            401,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (
            404,
            404,
            {
                'code': 'NOT_FOUND',
                'message': (
                    'Some data record not found or route cannot be constructed'
                ),
            },
        ),
        (
            406,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (
            429,
            429,
            {'code': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'},
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
async def test_order_estimate_forwarding_error_response(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        int_api_status,
        partner_status,
        response_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        return mockserver.make_response(
            json.dumps(ERROR_RESPONSE), status=int_api_status,
        )

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _user_phones_by_number(request):
        return load_json('user_phones_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_agent_payment(taxi_partner_orders_api, mockserver, load_json):
    request = load_json('request.json')
    request['payment']['type'] = 'agent'

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        assert request.json['payment']['type'] == 'agent'
        assert request.json['payment']['payment_method_id'] == 'agent_Gpartner'
        return load_json('int_api_response.json')

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _user_phones_by_number(request):
        return load_json('user_phones_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3_wrong_classes.json')
async def test_order_estimate_empty_service_levels(
        taxi_partner_orders_api, mockserver, load_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request.update(
            {'selected_class': 'econom', 'all_classes': True},
        )
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200
    r_json = response.json()
    assert not r_json['service_levels']


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.parametrize(
    ['is_expected_prices_enabled'],
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='experiments3_expected_prices_enabled.json',
                )
            ),
        ),
        pytest.param(
            False,
            marks=(pytest.mark.experiments3(filename='experiments3.json')),
        ),
    ],
)
async def test_forwarding_expected_classes(
        taxi_partner_orders_api,
        mockserver,
        is_expected_prices_enabled,
        load_json,
):
    request = load_json('request.json')
    request.update(
        {
            'expected_prices': [
                {'class': 'econom', 'price': 100},
                {'class': 'child_tariff', 'price': 200},
            ],
        },
    )

    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _order_estimate(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request.update(
            {'selected_class': 'econom', 'all_classes': True},
        )
        if is_expected_prices_enabled:
            assert 'expected_prices' in request.json
            assert request.json['expected_prices'] == [
                {'class': 'child_tariff', 'price': 200},
            ]
        else:
            assert 'expected_prices' not in request.json
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/estimate',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200
