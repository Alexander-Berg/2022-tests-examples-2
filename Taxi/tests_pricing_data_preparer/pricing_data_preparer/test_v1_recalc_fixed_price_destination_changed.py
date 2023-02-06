# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines, import-error
# flake8: noqa F401
import pytest


from .plugins.mock_order_core import mock_order_core
from .plugins.mock_order_core import order_core
from pricing_extended.mock_router import yamaps_router, mock_yamaps_router


@pytest.mark.parametrize(
    'order_id, params, code, params_log, price_log',
    [
        (
            'normal_order',
            {
                'destinations': [[36.1, 60.1], [36.15, 60.1]],
                'current_driver_position': [36, 60],
            },
            200,
            {},
            {},
        ),
        (
            'normal_order',
            {
                'destinations': [[36.1, 60.1]],
                'current_driver_position': [36, 60],
            },
            200,
            {
                'driver': {
                    'new_base_price': {
                        'boarding': 89.0,
                        'destination_waiting': 0.0,
                        'distance': 0.8280000000000041,
                        'requirements': 0.0,
                        'time': 4.466666666666667,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                    'params': {
                        'distance_ab': 2046.0,
                        'distance_ac': 2046.0,
                        'distance_bc': 2046.0,
                        'distance_cb': 2046.0,
                        'distance_abf': 2046.0,
                        'distance_bfb': 2046.0,
                        'fixed_price_boarding': 100.0,
                        'fixed_price_distance': 100.0,
                        'fixed_price_time': 100.0,
                    },
                },
                'user': {
                    'new_base_price': {
                        'boarding': 89.0,
                        'destination_waiting': 0.0,
                        'distance': 0.8280000000000041,
                        'requirements': 0.0,
                        'time': 4.466666666666667,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                    'params': {
                        'distance_ab': 2046.0,
                        'distance_ac': 2046.0,
                        'distance_bc': 2046.0,
                        'distance_cb': 2046.0,
                        'distance_abf': 2046.0,
                        'distance_bfb': 2046.0,
                        'fixed_price_boarding': 150.0,
                        'fixed_price_distance': 150.0,
                        'fixed_price_time': 150.0,
                    },
                },
            },
            {
                'user': {
                    'price': 94.3,
                    'meta': {
                        'total_time': 307.0,
                        'waiting_time': 0.0,
                        'total_distance': 2046.0,
                        'waiting_in_destination_time': 0.0,
                        'waiting_in_transit_time': 0.0,
                    },
                },
                'driver': {
                    'price': 94.3,
                    'meta': {
                        'total_time': 307.0,
                        'waiting_time': 0.0,
                        'total_distance': 2046.0,
                        'waiting_in_destination_time': 0.0,
                        'waiting_in_transit_time': 0.0,
                    },
                },
            },
        ),
        (
            'normal_order',
            {'destinations': [[36.1, 60.1]]},
            200,
            {
                'driver': {
                    'new_base_price': {
                        'boarding': 89.0,
                        'destination_waiting': 0.0,
                        'distance': 0.8280000000000041,
                        'requirements': 0.0,
                        'time': 4.466666666666667,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                },
                'user': {
                    'new_base_price': {
                        'boarding': 89.0,
                        'destination_waiting': 0.0,
                        'distance': 0.8280000000000041,
                        'requirements': 0.0,
                        'time': 4.466666666666667,
                        'transit_waiting': 0.0,
                        'waiting': 0.0,
                    },
                },
            },
            {
                'driver': {
                    'meta': {
                        'total_distance': 2046.0,
                        'total_time': 307.0,
                        'waiting_in_destination_time': 0.0,
                        'waiting_in_transit_time': 0.0,
                        'waiting_time': 0.0,
                    },
                    'price': 94.3,
                },
                'user': {
                    'meta': {
                        'total_distance': 2046.0,
                        'total_time': 307.0,
                        'waiting_in_destination_time': 0.0,
                        'waiting_in_transit_time': 0.0,
                        'waiting_time': 0.0,
                    },
                    'price': 94.3,
                },
            },
        ),
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_change_destinations(
        taxi_pricing_data_preparer,
        order_id,
        params,
        code,
        params_log,
        price_log,
        order_core,
        mock_order_core,
        mock_yamaps_router,
        yamaps_router,
        testpoint,
):
    @testpoint('log_params')
    def tp_params_log(data):
        assert data == params_log

    @testpoint('log_prices')
    def tp_price_log(data):
        assert data == price_log

    response = await taxi_pricing_data_preparer.post(
        '/v1/recalc_fixed_price/destination_changed',
        params={'order_id': order_id},
        json=params,
    )
    assert response.status_code == code
    if len(params['destinations']) == 1:
        assert tp_params_log.times_called == 1
        assert tp_price_log.times_called == 1
    else:
        assert not tp_params_log.times_called
        assert not tp_price_log.times_called
