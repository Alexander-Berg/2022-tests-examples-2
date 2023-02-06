import pytest

import tests_candidates.helpers


@pytest.fixture(autouse=True)
def mock_grocery_shifts(mockserver, grocery_depots):
    grocery_depots.add_depot(0, legacy_depot_id='12345')
    grocery_depots.add_depot(1, legacy_depot_id='67890')
    grocery_depots.add_depot(1, legacy_depot_id='67891')

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _grocery_shifts_info(request):
        by_depots = {
            # external_depot_id -> shift response
            '12345': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid0',
                        'shift_id': '19950',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
            '67890': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19951',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2020-07-28T09:07:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
            '67891': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid2',
                        'shift_id': '19953',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T09:10:00Z',
                        'closes_at': '2020-07-28T09:20:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
async def test_without_shift(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'filters': ['infra/meta_status_searchable'],
        'limit': 10,
        'point': [37.630971, 55.743789],
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200, response.text
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
            ],
        },
    )
    assert actual == expected


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
async def test_with_shift(taxi_candidates, driver_positions):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )
    request_body = {
        'geoindex': 'kdtree',
        'filters': ['infra/meta_status_searchable'],
        'limit': 10,
        'point': [37.630971, 55.743789],
        'order': {'request': {'shift': {'type': 'grocery'}}},
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200, response.text
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        },
    )
    assert actual == expected
