import pytest


@pytest.mark.parametrize(
    'params,expected',
    [
        (
            {'park_id': 'park_id_0', 'driver_id': 'driver_id_0'},
            {'has_finished': True},
        ),
        (
            {'park_id': 'park_id_1', 'driver_id': 'driver_id_3'},
            {'has_finished': True},
        ),
        (
            {'park_id': 'park_id_4', 'driver_id': 'driver_id__'},
            {'has_finished': False},
        ),
    ],
)
async def test_driver_orders_has_finished(
        taxi_driver_orders, fleet_parks_shard, params, expected,
):
    response = await taxi_driver_orders.get(
        'v1/driver/orders/has-finished', params=params,
    )
    assert response.status_code == 200
    assert expected == response.json()
