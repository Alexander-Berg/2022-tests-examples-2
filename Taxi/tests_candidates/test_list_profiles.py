import pytest


import tests_candidates.helpers


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'data_keys': []}, 400),
        (
            {
                'tl': [36.464186, 56.286216],
                'br': [39.438735, 54.985976],
                'data_keys': [],
            },
            200,
        ),
    ],
)
async def test_response_code(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == response_code


async def test_response_format(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'data_keys': ['car_classes'],
    }
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 3
    assert set(['id', 'uuid', 'dbid', 'position', 'car_classes']) == set(
        drivers[0].keys(),
    )


async def test_with_filters(taxi_candidates, driver_positions):
    await driver_positions(
        [
            # inside search area, free
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            # outside search area
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.512910, 55.997496]},
            # inside search area, on order
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'search_area': [
            [37.309394, 55.914744],
            [37.884803, 55.911659],
            [37.942481, 55.520175],
            [37.242102, 55.499913],
            [37.309394, 55.914744],
        ],
        'only_free': True,
        'data_keys': ['car_classes'],
    }
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    driver = drivers[0]
    assert driver['uuid'] == 'uuid0'


@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': False,
        'Москва': True,
    },
)
async def test_list_profiles_filtration(
        taxi_candidates, driver_positions, mockserver, load_binary,
):
    @mockserver.json_handler('/driver-weariness/v1/tired-drivers')
    def _tired_drivers(request):
        return {
            'items': [
                {
                    'unique_driver_id': '56f968f07c0aa65c44998e4b',
                    'tired_status': 'hours_exceed',
                    'block_till': '1970-01-01T00:00:00.0+0000',
                    'block_time': '1970-01-01T00:00:00.0+0000',
                },
            ],
        }

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]}],
    )
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'search_area': [
            [37.309394, 55.914744],
            [37.884803, 55.911659],
            [37.942481, 55.520175],
            [37.242102, 55.499913],
            [37.309394, 55.914744],
        ],
        'only_free': True,
        'data_keys': ['car_classes'],
    }

    response = await taxi_candidates.post('list-profiles', json=request_body)

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert len(json['drivers']) == 1

    request_body['filtration'] = 'base'
    response = await taxi_candidates.post('list-profiles', json=request_body)

    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    assert not json['drivers']


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['lavka']},
    },
)
async def test_with_shifts(taxi_candidates, driver_positions, mockserver):
    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _mock_courier_shift_states(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'shifts': [
                        {
                            'courier_id': 'dbid0_uuid0',
                            'eats_courier_id': '10',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': 'abc',
                            'meta_group_id': 'abc',
                            'status': 'closed',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': False,
                        },
                        {
                            'courier_id': 'dbid0_uuid2',
                            'eats_courier_id': '11',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': 'def',
                            'meta_group_id': 'def',
                            'status': 'in_progress',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': True,
                        },
                    ],
                    'cursor': '1',
                },
            }
        return {'data': {'shifts': [], 'cursor': '1'}}

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'data_keys': ['eats_shift'],
        'order': {'request': {'shift': {'type': 'eats'}}},
    }
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == 200

    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {
                    'dbid': 'dbid0',
                    'uuid': 'uuid2',
                    'eats_shift': {'shift_id': '19950'},
                },
            ],
        },
    )
    assert actual == expected
