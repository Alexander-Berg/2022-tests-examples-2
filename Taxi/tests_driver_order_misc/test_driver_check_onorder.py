import pytest

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
ORDER_ID = 'order_id'


@pytest.mark.redis_store(
    [
        'sadd',
        f'Order:SetCar:Driver:Reserv:Items{PARK_ID}:{DRIVER_ID}',
        ORDER_ID,
    ],
)
async def test_ok(taxi_driver_order_misc):
    response = await taxi_driver_order_misc.post(
        '/driver-order-misc/v1/check-on-order',
        json={
            'drivers': [
                {'park_id': PARK_ID, 'driver_profile_id': DRIVER_ID},
                {'park_id': 'unknown', 'driver_profile_id': 'unknown'},
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'drivers': [
            {
                'park_id': PARK_ID,
                'driver_profile_id': DRIVER_ID,
                'on_order': True,
            },
            {
                'park_id': 'unknown',
                'driver_profile_id': 'unknown',
                'on_order': False,
            },
        ],
    }
