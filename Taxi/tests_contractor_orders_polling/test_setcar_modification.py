import json

import pytest

from tests_contractor_orders_polling import utils


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'feature_pay_type_hide_polling': '9.07'},
        },
    },
    SETCAR_REMOVE_PAY_TYPE_FOR_CLIENT=['none', 'undefined'],
)
@pytest.mark.translations(
    taximeter_messages={
        'subvention_declined_reason': {
            'ru': 'фоллбечный ключ с параметром: %(param1)s',
        },
    },
)
@pytest.mark.redis_store(
    ['set', 'Order:SetCar:Driver:Reserv:MD5:999:888', 'SETCAR-ETAG'],
    ['sadd', 'Order:SetCar:Driver:Reserv:Items999:888', 'order0'],
    [
        'hmset',
        'Order:SetCar:Items:999',
        {
            'order0': json.dumps(
                {
                    'provider': 2,
                    'address_from': {'Street': 'somewhere1', 'House': '123'},
                    'address_to': {'Street': 'somewhere2', 'House': '234'},
                    'route_points': [
                        {'Street': 's1', 'House': 'h1'},
                        {'Street': 's2', 'House': 'h2'},
                        {'Street': 's3'},
                    ],
                    'show_address': True,
                    'base_price': {'driver': {}, 'user': {}},
                    'driver_fixed_price': {'show': True},
                    'fixed_price': {'show': True},
                    'subvention': {
                        'disabled_rules': [
                            {
                                'declined_reasons': [
                                    {
                                        'key': 'some_key',
                                        'reason': 'some_reason',
                                        'parameters': {'param1': 'p1_value'},
                                    },
                                ],
                            },
                        ],
                    },
                    'waiting_mode': 'something',
                    'client_geo_sharing': 'something',
                    'pay_type': 0,
                    'type_name': 'Яндекс.Корпоративный',
                },
            ),
        },
    ],
)
async def test_setcar_modifications_generic_path(
        taxi_contractor_orders_polling,
):
    response = await taxi_contractor_orders_polling.get(
        utils.HANDLER_URL, headers=utils.HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['setcar']['order0'] == {
        'provider': 2,
        'address_from': {'Street': 'somewhere1, 123'},
        'address_to': {'Street': 'somewhere2, 234'},
        'route_points': [
            {'Street': 's1, h1'},
            {'Street': 's2, h2'},
            {'Street': 's3'},
        ],
        'show_address': True,
        'base_price': {'driver': {}, 'user': {}},
        'driver_fixed_price': {'show': True},
        'fixed_price': {'show': True},
        'subvention': {
            'disabled_rules': [
                {
                    'declined_reasons': [
                        'фоллбечный ключ с параметром: p1_value',
                    ],
                },
            ],
        },
        'type_name': 'Яндекс.Безналичный',
    }
