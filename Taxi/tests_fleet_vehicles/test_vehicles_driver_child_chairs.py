import json


import pytest


ENDPOINT = '/v1/vehicles/driver/child-chairs'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'


@pytest.mark.parametrize(
    'park_id, vehicle_id, child_chairs, diff, mock_times_called',
    [
        (
            'park1',
            'car1',
            {
                'boosters_count': 2,
                'chairs': [
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': False,
                    },
                ],
            },
            [{'field': 'DriverBoosters', 'old': '0', 'new': '2'}],
            1,
        ),
        (
            'park1',
            'car1',
            {
                'boosters_count': 0,
                'chairs': [
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': False,
                    },
                ],
            },
            None,
            0,
        ),
        (
            'park1',
            'car1',
            {'boosters_count': 0, 'chairs': []},
            [
                {
                    'field': 'DriverChairs',
                    'old': (
                        '[{"brand":"Other","categories":[1,2,3],'
                        '"isofix":false}]'
                    ),
                    'new': '[]',
                },
            ],
            1,
        ),
        (
            'park1',
            'car1',
            {
                'boosters_count': 1,
                'chairs': [
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': False,
                    },
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': False,
                    },
                ],
            },
            [
                {'field': 'DriverBoosters', 'old': '0', 'new': '1'},
                {
                    'field': 'DriverChairs',
                    'old': (
                        '[{"brand":"Other","categories":[1,2,3],'
                        '"isofix":false}]'
                    ),
                    'new': (
                        '[{"brand":"Other","categories":[1,2,3],'
                        '"isofix":false},{"brand":"Other",'
                        '"categories":[1,2,3],"isofix":false}]'
                    ),
                },
            ],
            1,
        ),
        (
            'park1',
            'car2',
            {
                'boosters_count': 0,
                'chairs': [
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': True,
                    },
                    {
                        'brand': 'Other',
                        'categories': [1, 2, 3],
                        'isofix': False,
                    },
                ],
            },
            [
                {
                    'field': 'DriverChairs',
                    'old': (
                        '[{"brand":"Other","categories":[1,2,3],'
                        '"isofix":false},{"brand":"Yandex",'
                        '"categories":[1,2,3],"isofix":true}]'
                    ),
                    'new': (
                        '[{"brand":"Other","categories":[1,2,3],'
                        '"isofix":false},{"brand":"Other",'
                        '"categories":[1,2,3],"isofix":true}]'
                    ),
                },
            ],
            1,
        ),
    ],
)
async def test_vehicles_driver_child_chairs(
        taxi_fleet_vehicles,
        mockserver,
        mongodb,
        park_id,
        vehicle_id,
        child_chairs,
        diff,
        mock_times_called,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': park_id,
            'change_info': {
                'object_id': vehicle_id,
                'object_type': 'MongoDB.Docs.Car.CarDoc',
                'diff': diff,
            },
            'author': {
                'dispatch_user_id': 'uuid1',
                'display_name': 'driver',
                'user_ip': '',
            },
        }

    old_car = mongodb.dbcars.find_one(
        {'park_id': park_id, 'car_id': vehicle_id},
        {'modified_date', 'updated_ts'},
    )

    response = await taxi_fleet_vehicles.put(
        ENDPOINT,
        params={
            'park_id': park_id,
            'driver_profile_id': 'uuid1',
            'vehicle_id': vehicle_id,
        },
        data=json.dumps(
            {
                'author': {
                    'consumer': 'driver-profile-view',
                    'identity': {
                        'type': 'driver',
                        'driver_profile_id': 'uuid1',
                    },
                },
                'child_chairs': child_chairs,
            },
        ),
    )

    assert response.status_code == 200
    assert _mock_change_logger.times_called == mock_times_called

    car = mongodb.dbcars.find_one(
        {'park_id': park_id, 'car_id': vehicle_id},
        {
            'driver_boosters',
            'driver_chairs',
            'driver_confirmed_boosters',
            'driver_confirmed_chairs',
            'modified_date',
            'updated_ts',
        },
    )
    assert car['driver_boosters']['uuid1'] == child_chairs['boosters_count']
    assert car['driver_confirmed_boosters']['uuid1'] == 0
    assert car['driver_chairs']['uuid1'] == child_chairs['chairs']
    assert car['driver_confirmed_chairs']['uuid1'] == []
    assert car['modified_date'] > old_car['modified_date']
    assert car['updated_ts'] > old_car['updated_ts']
