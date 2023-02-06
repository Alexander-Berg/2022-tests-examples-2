# pylint: disable=import-only-modules
from copy import deepcopy

import pytest

BODY = {
    'zone': 'moscow',
    'requested_categories': ['econom', 'business'],
    'due': '2020-03-28T12:00:00+0000',
    'timezone': '+0000',
    'payment_info': {'type': 'card', 'method_id': 'card-x123123'},
    'user_info': {
        'yandex_uid': '111111',
        'phone_id': 'phone_id',
        'has_plus': True,
        'has_cashback_plus': True,
    },
}


def get_request_from_mock(mock):
    assert mock.has_calls
    return mock.next_call()['request'].json


@pytest.mark.config(
    CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': True},
    CASHBACK_RATES_USED_TARIFFS_BY_FINTECH=['econom'],
)
@pytest.mark.parametrize('fintech_amount', [pytest.param(5), pytest.param(0)])
async def test_rates_by_fintech(
        taxi_cashback_rates, mockserver, fintech_amount,
):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator/v1/calculate',
    )
    def _mock_balances(request):
        return {
            'cashback_rule': {
                'percent': {'amount': str(fintech_amount)},
                'max_amount': '15',
                'rule_ids': ['some_rule', 'some_rule_2'],
            },
        }

    body = deepcopy(BODY)
    body['payment_info']['type'] = 'yandex_card'

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200

    content = response.json()
    assert content == {
        'rates': {
            'econom': {
                'transaction_payload': {
                    'rule_ids': ['some_rule', 'some_rule_2'],
                },
                'rates': [
                    {
                        'rate': fintech_amount / 100.0,
                        'max_value': 15,
                        'sponsor': 'fintech',
                    },
                ],
            },
        },
    }


@pytest.mark.config(
    CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': True},
    CASHBACK_RATES_USED_TARIFFS_BY_FINTECH=['econom'],
)
async def test_empty_rates_by_fintech(taxi_cashback_rates, mockserver):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator/v1/calculate',
    )
    def _mock_balances(request):
        return {}

    body = deepcopy(BODY)
    body['payment_info']['type'] = 'yandex_card'

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200

    content = response.json()
    assert content == {'rates': {}}


@pytest.mark.config(
    CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': True},
    MARKETING_CASHBACK_EXPERIMENTS=[
        'portal_cashback',
        'portal_cashback_2',
        'test_fintech_portal',
        'test_complements',
    ],
    CASHBACK_RATES_USED_TARIFFS_BY_FINTECH=['econom', 'business'],
)
@pytest.mark.experiments3(filename='exp_cashback_rates.json')
async def test_rates_by_fintech_with_marketing(
        taxi_cashback_rates, mockserver,
):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator/v1/calculate',
    )
    def _mock_balances(request):
        return {
            'cashback_rule': {
                'percent': {'amount': '5'},
                'max_amount': '15',
                'rule_ids': ['some_rule', 'some_rule_2'],
            },
        }

    body = deepcopy(BODY)
    body['payment_info']['type'] = 'yandex_card'
    body['requested_categories'].append('vip')
    body['payment_info']['complements'] = {
        'personal_wallet': {'balance': 250, 'method_id': 'personal_wallet_id'},
    }

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200

    content = response.json()
    assert content == {
        'rates': {
            'econom': {
                'transaction_payload': {
                    'rule_ids': ['some_rule', 'some_rule_2'],
                },
                'rates': [
                    {'rate': 0.05, 'max_value': 15, 'sponsor': 'fintech'},
                    {'rate': 0.04, 'sponsor': 'portal'},
                    {'rate': 0.09, 'sponsor': 'portal'},
                    {'rate': 0.09, 'sponsor': 'personal_wallet'},
                ],
            },
            'business': {
                'transaction_payload': {
                    'rule_ids': ['some_rule', 'some_rule_2'],
                },
                'rates': [
                    {'rate': 0.05, 'max_value': 15, 'sponsor': 'fintech'},
                    {'rate': 0.09, 'sponsor': 'portal'},
                    {'rate': 0.09, 'sponsor': 'personal_wallet'},
                ],
            },
            'vip': {'rates': [{'rate': 0.01, 'sponsor': 'portal'}]},
        },
    }


@pytest.mark.config(CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': True})
@pytest.mark.experiments3(filename='exp_cashback_rates.json')
async def test_rates_by_fintech_request(taxi_cashback_rates, mockserver):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator/v1/calculate',
    )
    def _mock_balances(request):
        return {
            'cashback_rule': {
                'percent': {'amount': '5'},
                'max_amount': '15',
                'rule_ids': ['some_rule', 'some_rule_2'],
            },
        }

    body = deepcopy(BODY)
    body['payment_info']['type'] = 'yandex_card'

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200
    balances_request = get_request_from_mock(_mock_balances)

    assert balances_request['service_name'] == 'yataxi'
    assert balances_request['timestamp'] == '2020-03-28T12:00:00.0+00:00'
    assert balances_request['currency'] == 'RUB'
    assert balances_request['payment_method_id'] == 'card-x123123'


@pytest.mark.config(
    CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': True},
    MARKETING_CASHBACK_EXPERIMENTS=[
        'portal_cashback',
        'portal_cashback_2',
        'test_fintech_portal',
    ],
    CASHBACK_RATES_USED_TARIFFS_BY_FINTECH=['econom', 'business'],
)
@pytest.mark.experiments3(filename='exp_cashback_rates.json')
async def test_bad_rates_by_fintech_with_marketing(
        taxi_cashback_rates, mockserver,
):
    @mockserver.json_handler(
        '/bank-cashback-calculator/cashback-calculator/v1/calculate',
    )
    def _mock_balances(request):
        return mockserver.make_response(
            status=400,
            json={'code': 'Bad request', 'message': 'Message for bad request'},
        )

    body = deepcopy(BODY)
    body['payment_info']['type'] = 'yandex_card'
    body['requested_categories'].append('vip')

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200

    content = response.json()
    assert content == {
        'rates': {
            'econom': {
                'rates': [
                    {'rate': 0.04, 'sponsor': 'portal'},
                    {'rate': 0.09, 'sponsor': 'portal'},
                ],
            },
            'business': {'rates': [{'rate': 0.09, 'sponsor': 'portal'}]},
            'vip': {'rates': [{'rate': 0.01, 'sponsor': 'portal'}]},
        },
    }


POINT_A = [37.619046, 55.767843]
POINT_B = [37.588144, 55.733842]
POINT_NEAR_A = [37.620282, 55.767530]
POINT_NEAR_B = [37.586426, 55.734227]
POINT_OTHER = [39.642777, 60.734839]


@pytest.mark.experiments3(filename='exp_cashback_rates.json')
@pytest.mark.experiments3(filename='exp_favorite_route_cashback_enabled.json')
@pytest.mark.experiments3(
    filename='exp_favorite_route_availability_radius.json',
)
@pytest.mark.config(
    CASHBACK_RATES_ENABLED_CASHBACK_SOURCES={'fintech': False},
    MARKETING_CASHBACK_EXPERIMENTS=['test_favorite_route_cashback'],
)
@pytest.mark.parametrize(
    'waypoints, fav_route, expected_rates',
    [
        pytest.param(
            [POINT_A, POINT_B],
            [POINT_A, POINT_B],
            {
                'econom': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
                'business': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
            },
            id='favorite_route_exact_match',
        ),
        pytest.param(
            [POINT_NEAR_A, POINT_NEAR_B],
            [POINT_A, POINT_B],
            {
                'econom': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
                'business': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
            },
            id='favorite_route_in_radius_match',
        ),
        pytest.param(
            [POINT_NEAR_B, POINT_NEAR_A],
            [POINT_A, POINT_B],
            {
                'econom': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
                'business': {
                    'rates': [{'rate': 0.5, 'sponsor': 'favorite_route'}],
                },
            },
            id='favorite_route_another_way',
        ),
        pytest.param(
            [POINT_NEAR_A, POINT_NEAR_B], None, {}, id='no_favorite_route',
        ),
        pytest.param(
            [POINT_NEAR_A, POINT_OTHER],
            [POINT_A, POINT_B],
            {},
            id='not_favorite_route',
        ),
    ],
)
async def test_rates_by_favorite_route(
        taxi_cashback_rates, mockserver, waypoints, fav_route, expected_rates,
):
    @mockserver.json_handler('/userplaces/userplaces/v1/fav-route')
    def _mock_userplaces_fav_route(request):
        if not fav_route:
            return mockserver.make_response(status=404, json={'code': '404'})

        addresses = [
            {
                'point': route,
                'full_text': 'full_text',
                'short_text': 'short_text',
            }
            for route in fav_route
        ]

        fav_routes = [
            {
                'id': 'fav_route_id',
                'addresses': addresses,
                'allowed_to_change': True,
            },
        ]
        return {'fav_routes': fav_routes, 'max_num_of_fav_routes': 1}

    body = deepcopy(BODY)
    body['waypoints'] = waypoints

    response = await taxi_cashback_rates.post('/v2/rates', json=body)
    assert response.status_code == 200

    assert response.json()['rates'] == expected_rates
