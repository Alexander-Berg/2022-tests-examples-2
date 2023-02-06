import copy

import pytest

HEADERS = {'Accept-Language': 'ru'}
ESTIMATE_REQUEST = {
    'sender_info': {
        'yandex_uid': 'yandex_uid_1',
        'personal_phone_id': 'personal_phone_id_1',
        'name': 'Petr',
        'payment': {'type': 'card', 'payment_method_id': 'card-X1232'},
        'partner_tag': 'boxberry',
    },
    'items': [
        {
            'size': {'length': 0.3, 'width': 0.3, 'height': 0.5},
            'weight': 7,
            'quantity': 1,
        },
    ],
    'route_points': [
        {'coordinates': [37.1, 55.1]},
        {'coordinates': [37.2, 55.3]},
        {'coordinates': [37.3, 55.4]},
    ],
}


@pytest.mark.parametrize(
    'expected_user_agent',
    (
        pytest.param(
            None,
            marks=[pytest.mark.config(CARGO_TARIFF_CLASS_TO_USER_AGENT={})],
        ),
        pytest.param(
            'express_execution',
            marks=[
                pytest.mark.config(
                    CARGO_TARIFF_CLASS_TO_USER_AGENT={
                        'express': 'express_execution',
                    },
                ),
            ],
        ),
    ),
)
async def test_success(
        mockserver,
        taxi_cargo_matcher,
        get_currency_rules,
        expected_user_agent,
        mock_int_api_profile,
):
    mock_int_api_profile.expected_request = {
        'user': {
            'personal_phone_id': 'personal_phone_id_1',
            'yandex_uid': 'yandex_uid_1',
        },
        'sourceid': 'cargo_c2c',
    }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        if expected_user_agent:
            assert request.headers['User-Agent'] == expected_user_agent
        assert request.json == {
            'sourceid': 'cargo_c2c',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_1',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {'payment_method_id': 'card-X1232', 'type': 'card'},
            'requirements': {'door_to_door': True},
            'partner_tag': 'boxberry',
            'route': [[37.1, 55.1], [37.2, 55.3], [37.3, 55.4]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': get_currency_rules,
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    response = await taxi_cargo_matcher.post(
        '/v1/estimate', json=ESTIMATE_REQUEST, headers=HEADERS,
    )
    assert response.status_code == 200, response.json()
    assert response.json() == {
        'offer': {
            'offer_id': 'taxi_offer_id_1',
            'price': '999.001',
            'price_raw': 999,
        },
        'taxi_class': 'express',
        'zone_id': 'moscow',
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
            'text': 'руб.',
        },
        'taxi_requirements': {'door_to_door': True},
    }


async def test_item_not_fit(mockserver, taxi_cargo_matcher):
    request = copy.deepcopy(ESTIMATE_REQUEST)
    request['items'][0]['size']['length'] = 100
    response = await taxi_cargo_matcher.post(
        '/v1/estimate', json=request, headers=HEADERS,
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'estimating_failed',
        'message': 'estimating.too_large_item',
    }


async def test_no_items_size(
        mockserver,
        taxi_cargo_matcher,
        mock_int_api_profile,
        get_currency_rules,
):
    mock_int_api_profile.expected_request = {
        'sourceid': 'cargo_c2c',
        'user': {
            'personal_phone_id': 'personal_phone_id_1',
            'yandex_uid': 'yandex_uid_1',
        },
    }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': get_currency_rules,
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    request = copy.deepcopy(ESTIMATE_REQUEST)
    del request['items'][0]['size']
    del request['items'][0]['weight']
    response = await taxi_cargo_matcher.post(
        '/v1/estimate', json=request, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {
        'offer': {
            'offer_id': 'taxi_offer_id_1',
            'price': '999.001',
            'price_raw': 999,
        },
        'taxi_class': 'express',
        'zone_id': 'moscow',
        'currency_rules': {
            'code': 'RUB',
            'sign': '₽',
            'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
            'text': 'руб.',
        },
        'taxi_requirements': {'door_to_door': True},
    }
