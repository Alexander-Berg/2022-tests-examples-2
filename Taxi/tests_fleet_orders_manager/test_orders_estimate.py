import pytest

from tests_fleet_orders_manager import common

ENDPOINT = 'fleet/fleet-orders-manager/v1/orders/estimate'
REQUEST_BODY = {
    'phone_pd_id': 'id_+7123',
    'route': [{'geopoint': [1.0, 12.0]}, {'geopoint': [1.2, 11.8]}],
    'due': '2021-04-29T07:48:47.487+0000',
    'forced_fixprice': '100.0',
    'requirements': [{'id': 'meeting_arriving', 'type': 'boolean'}],
}

ESTIMATE_OK_RESPONSE = {
    'currency_rules': {
        'code': 'OMR',
        'sign': '﷼',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'OMR',
    },
    'is_fixed_price': True,
    'offer': '4f57e20c7cc8ea8a5e0b380ed00acdd0',
    'service_levels': [
        {
            'class': 'econom',
            'cost_message_details': {
                'cost_breakdown': [
                    {
                        'display_amount': '10 $SIGN$$CURRENCY$, ~0 мин в пути',
                        'display_name': 'cost',
                    },
                ],
            },
            'details_tariff': [
                {'type': 'price', 'value': 'от 10 $SIGN$$CURRENCY$'},
            ],
            'estimated_waiting': {'message': 'Мало свободных машин'},
            'is_fixed_price': True,
            'price': '10 $SIGN$$CURRENCY$',
            'price_raw': 10.0,
            'min_price': 10.0,
            'time': '0 мин',
            'time_raw': 0,
        },
        {
            'class': 'comfort',
            'cost_message_details': {
                'cost_breakdown': [
                    {
                        'display_amount': '20 $SIGN$$CURRENCY$, ~0 мин в пути',
                        'display_name': 'cost',
                    },
                ],
            },
            'details_tariff': [
                {'type': 'price', 'value': 'от 20 $SIGN$$CURRENCY$'},
            ],
            'estimated_waiting': {'message': 'Мало свободных машин'},
            'is_fixed_price': True,
            'price': '20 $SIGN$$CURRENCY$',
            'min_price': 20.0,
            'time': '0 мин',
            'time_raw': 0,
        },
    ],
    'user_id': 'b5cfdff704264db6bcc5e513d631d4a4',
}

# not sure if this response possible
ESTIMATE_OK_NO_TARIFFS = {
    'currency_rules': {
        'code': 'OMR',
        'sign': '﷼',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'OMR',
    },
    'is_fixed_price': True,
    'offer': '4f57e20c7cc8ea8a5e0b380ed00acdd0',
    'service_levels': [],
    'user_id': 'b5cfdff704264db6bcc5e513d631d4a4',
}

EXPECTED_ESTIMATE_REQUEST = {
    'user': {'personal_phone_id': 'id_+7123', 'user_id': 'user_id_id_+7123'},
    'payment': {'type': 'cash'},
    'requirements': {'meeting_arriving': True},
    'all_classes': True,
    'selected_class': '',
    'route': [[1.0, 12.0], [1.2, 11.8]],
    'format_currency': True,
    'due': '2021-04-29T07:48:47.487+00:00',
    'white_label_requirements': {
        'dispatch_requirement': 'only_source_park',
        'source_park_id': 'park_id',
        'forced_fixprice': 100.0,
    },
}


@pytest.mark.parametrize(
    'orders_estimate_response, expected_code, expected_body',
    [
        pytest.param(
            {'json': ESTIMATE_OK_RESPONSE, 'status': 200},
            200,
            {
                'currency_code': 'OMR',
                'is_fixed_price': False,
                'class_estimates': [
                    {
                        'class_id': 'econom',
                        'is_fixed_price': True,
                        'min_price': 10.0,
                        'price_raw': 10.0,
                        'time_raw': 0.0,
                    },
                    {
                        'class_id': 'comfort',
                        'is_fixed_price': True,
                        'min_price': 20.0,
                        'time_raw': 0.0,
                    },
                ],
            },
            id='all ok',
        ),
        pytest.param(
            {'json': ESTIMATE_OK_NO_TARIFFS, 'status': 200},
            400,
            {
                'code': 'SERVICE_IS_UNAVAILABLE_IN_AREA',
                'message': 'SERVICE_IS_UNAVAILABLE_IN_AREA',
            },
            id='no tariffs',
        ),
        pytest.param(
            {'json': {}, 'status': 404},
            400,
            {'code': 'RECORD_NOT_FOUND', 'message': 'RECORD_NOT_FOUND'},
            id='no tariff zone',
        ),
    ],
)
async def test(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
        orders_estimate_response,
        expected_code,
        expected_body,
):
    @mockserver.json_handler('/integration-api/v1/orders/estimate')
    def _mock_orders_estimate(request):
        return mockserver.make_response(**orders_estimate_response)

    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY, headers=headers,
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body

    assert _mock_orders_estimate.times_called == 1
    orders_estimate_request = _mock_orders_estimate.next_call()['request']
    assert orders_estimate_request.json == EXPECTED_ESTIMATE_REQUEST
    assert (
        orders_estimate_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )
    assert orders_estimate_request.headers['Accept-Language'] == 'de'


REQUEST_BODY_BAD_PRICE = {
    'phone_pd_id': 'id_+7123',
    'route': [{'geopoint': [1.0, 12.0]}, {'geopoint': [2.0, 13.0]}],
    'due': '2021-04-29T07:48:47.487+0000',
    'forced_fixprice': 'not_a_number',
    'requirements': [],
}


async def test_non_numeric_forced_fixprice(
        mockserver,
        taxi_fleet_orders_manager,
        fleet_parks_dispatch_requirements,
        fleet_parks_list,
        v1_profile,
):
    headers = {**common.YA_USER_HEADERS, 'X-Park-Id': 'park_id'}
    response = await taxi_fleet_orders_manager.post(
        ENDPOINT, json=REQUEST_BODY_BAD_PRICE, headers=headers,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'NON_NUMERIC_FORCED_FIXPRICE',
        'message': 'NON_NUMERIC_FORCED_FIXPRICE',
    }
