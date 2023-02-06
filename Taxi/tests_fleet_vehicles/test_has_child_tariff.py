import pytest


DRIVERS = [
    {
        'params': {
            'park_id': 'aaa',
            'vehicle_id': 'aaa',
            'driver_profile_id': 'aaa',
        },
        'code': 404,
        'has_child_tariff': None,
        'id': 'Vehicle not in cache',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_without_chairs_or_boosters',
            'driver_profile_id': 'aaa',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'No chairs or booster in vehicle',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_confirmed_chairs',
            'driver_profile_id': 'aaa',
        },
        'code': 200,
        'has_child_tariff': True,
        'id': 'Vehicle has confirmed chairs',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_non_confirmed_chairs',
            'driver_profile_id': 'aaa',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Vehicle has non-confirmed chairs',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_driver_confirmed_chairs',
            'driver_profile_id': 'driver_with_confirmed_chairs',
        },
        'code': 200,
        'has_child_tariff': True,
        'id': 'Driver has confirmed chairs',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_driver_non_confirmed_chairs',
            'driver_profile_id': 'driver_with_non_confirmed_chairs',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Driver has non-confirmed chairs',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_confirmed_boosters',
            'driver_profile_id': 'aaa',
        },
        'code': 200,
        'has_child_tariff': True,
        'id': 'Vehicle has confirmed boosters',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_non_confirmed_boosters',
            'driver_profile_id': 'aaa',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Vehicle has non-confirmed boosters',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_driver_confirmed_boosters',
            'driver_profile_id': 'driver_with_confirmed_boosters',
        },
        'code': 200,
        'has_child_tariff': True,
        'id': 'Driver has confirmed boosters',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_driver_non_confirmed_boosters',
            'driver_profile_id': 'driver_with_non_confirmed_boosters',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Driver has non-confirmed boosters',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_confirmed_chairs',
            'driver_profile_id': 'driver_without_confirmed_chairs',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Vehicle has confirmed chairs, but driver has not',
    },
    {
        'params': {
            'park_id': 'park_for_child',
            'vehicle_id': 'car_with_confirmed_boosters',
            'driver_profile_id': 'driver_without_confirmed_boosters',
        },
        'code': 200,
        'has_child_tariff': False,
        'id': 'Vehicle has confirmed boosters, but driver has not',
    },
]


@pytest.mark.parametrize(
    'params,code,has_child_tariff',
    [
        pytest.param(
            driver['params'],
            driver['code'],
            driver['has_child_tariff'],
            id=driver['id'],
        )
        for driver in DRIVERS
    ],
)
async def test_has_child_tariff(
        taxi_fleet_vehicles, params, code, has_child_tariff,
):
    await taxi_fleet_vehicles.invalidate_caches(
        clean_update=True, cache_names=['child-seats-cache'],
    )

    response = await taxi_fleet_vehicles.get(
        '/v1/vehicles/driver/has-child-tariff', params=params,
    )
    assert response.status_code == code
    if code == 200:
        assert response.json() == {'has_child_tariff': has_child_tariff}


async def test_has_child_tariff_bulk(taxi_fleet_vehicles):
    await taxi_fleet_vehicles.invalidate_caches(
        clean_update=True, cache_names=['child-seats-cache'],
    )

    response = await taxi_fleet_vehicles.post(
        '/v1/vehicles/driver/has-child-tariff-bulk',
        json={'drivers': [driver['params'] for driver in DRIVERS]},
    )

    assert response.status_code == 200

    response_drivers = []
    for driver in DRIVERS:
        response_drivers.append(driver['params'])
        if driver['has_child_tariff'] is not None:
            response_drivers[-1]['has_child_tariff'] = driver[
                'has_child_tariff'
            ]

    assert response.json() == {'drivers': response_drivers}


async def test_has_child_tariff_bulk_too_big_request(taxi_fleet_vehicles):
    await taxi_fleet_vehicles.invalidate_caches(
        clean_update=True, cache_names=['child-seats-cache'],
    )

    response = await taxi_fleet_vehicles.post(
        '/v1/vehicles/driver/has-child-tariff-bulk',
        json={
            'drivers': [
                {
                    'park_id': 'aaa',
                    'vehicle_id': 'aaa',
                    'driver_profile_id': 'aaa',
                }
                for i in range(0, 1001)
            ],
        },
    )

    assert response.status_code == 400
