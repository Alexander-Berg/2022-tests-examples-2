import pytest


DEPOT_ID = '12345'


@pytest.fixture(autouse=True)
def grocery_shifts_info(mockserver):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _grocery_shifts_journal(request):
        by_depots = {
            # external_depot_id -> shift response
            DEPOT_ID: {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid0',
                        'shift_id': '19950',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19949',
                        'shift_status': 'closed',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})


async def test_fetching_grocery_shifts_basic(
        taxi_candidates, driver_positions, grocery_depots,
):
    grocery_depots.add_depot(0, legacy_depot_id=DEPOT_ID)

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    expected_grocery_shift_value = {
        'shift_id': '19950',
        'status': 'in_progress',
        'started_at': '2020-07-28T08:47:00+0000',
        'closes_at': '2020-07-28T09:07:12+0000',
        'store_external_id': DEPOT_ID,
        'zone_group_id': DEPOT_ID,
    }
    request_body = {
        'tl': [36.464186, 56.286216],
        'br': [39.438735, 54.985976],
        'data_keys': ['grocery_shift'],
    }
    response = await taxi_candidates.post('list-profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 3
    driver_found = False
    for driver in drivers:
        if driver['id'] != 'dbid0_uuid0':
            assert 'grocery_shift' not in driver
        else:
            assert 'grocery_shift' in driver
            assert driver['grocery_shift'] == expected_grocery_shift_value
            driver_found = True
    assert driver_found


async def test_filter_grocery_shifts_profiles(
        taxi_candidates, driver_positions, grocery_depots,
):
    grocery_depots.add_depot(0, legacy_depot_id=DEPOT_ID)

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    expected_grocery_shift_value = {
        'shift_id': '19950',
        'status': 'in_progress',
        'started_at': '2020-07-28T08:47:00+0000',
        'closes_at': '2020-07-28T09:07:12+0000',
        'store_external_id': '12345',
        'zone_group_id': '12345',
    }
    request_body = {
        'data_keys': ['grocery_shift'],
        'driver_ids': [{'dbid': 'dbid0', 'uuid': 'uuid0'}],
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    driver = drivers[0]
    assert driver['id'] == 'dbid0_uuid0'
    assert driver['grocery_shift'] == expected_grocery_shift_value
