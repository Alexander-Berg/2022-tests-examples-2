import pytest


@pytest.fixture(autouse=True)
def eats_shifts_journal(mockserver):
    @mockserver.json_handler(
        '/eats-performer-shifts/internal/eats-performer-shifts/v1/courier-shift-states/updates',  # noqa: E501
    )
    def _eats_shifts_journal(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'shifts': [
                        {
                            'courier_id': 'dbid0_uuid0',
                            'eats_courier_id': '10',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': None,
                            'meta_group_id': None,
                            'status': 'closed',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': False,
                        },
                        {
                            'courier_id': 'dbid0_uuid1',
                            'eats_courier_id': '11',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': None,
                            'meta_group_id': '67890',
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


async def test_fetching_eats_shifts_basic(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    expected_eats_shift_value = {
        'shift_id': '19950',
        'zone_id': '6341',
        'status': 'closed',
        'started_at': '2020-07-28T08:47:00+0000',
        'closes_at': '2020-07-28T09:07:12+0000',
        'updated_ts': '2020-07-28T09:07:12+0000',
        'is_high_priority': False,
        'meta_group_id': None,
        'zone_group_id': None,
    }
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'data_keys': ['eats_shift'],
    }
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 3
    driver_found = False
    for driver in drivers:
        if driver['id'] != 'dbid0_uuid0':
            continue
        assert 'eats_shift' in driver
        assert driver['eats_shift'] == expected_eats_shift_value
        driver_found = True
    assert driver_found


async def test_filter_eats_shifts_profiles(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    expected_eats_shift_value = {
        'shift_id': '19950',
        'zone_id': '6341',
        'status': 'closed',
        'started_at': '2020-07-28T08:47:00+0000',
        'closes_at': '2020-07-28T09:07:12+0000',
        'updated_ts': '2020-07-28T09:07:12+0000',
        'is_high_priority': False,
        'meta_group_id': None,
        'zone_group_id': None,
    }
    request_body = {
        'data_keys': ['eats_shift'],
        'driver_ids': [{'dbid': 'dbid0', 'uuid': 'uuid0'}],
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    driver_found = False
    for driver in drivers:
        if driver['id'] != 'dbid0_uuid0':
            continue
        assert 'eats_shift' in driver
        assert driver['eats_shift'] == expected_eats_shift_value
        driver_found = True
    assert driver_found
