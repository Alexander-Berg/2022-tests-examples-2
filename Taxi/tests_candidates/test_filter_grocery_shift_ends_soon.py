import pytest

import tests_candidates.helpers


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['lavka']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
    ROUTER_SELECT=[
        {'routers': ['yamaps', 'tigraph']},
        {
            'ids': ['moscow'],
            'routers': ['linear-fallback', 'yamaps', 'tigraph'],
        },
    ],
)
@pytest.mark.now('2021-11-17T12:23:00+00:00')
async def test_shifts(
        taxi_candidates, driver_positions, mockserver, grocery_depots,
):
    grocery_depots.add_depot(0, legacy_depot_id='12345')

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
                        'closes_at': '2021-11-17T12:12:12Z',  # shift ends soon
                        'shift_type': 'wms',
                    },
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19949',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2021-11-17T12:14:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.630971, 55.743789]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.630971, 55.743789]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'zone_id': 'moscow',
        'filters': ['grocery/shift_ends_soon'],
        'allowed_classes': ['econom', 'vip', 'uberblack'],
        'order': {
            'calc': {'time': 600},
            'request': {'shift': {'type': 'grocery'}},
        },
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        },
    )
    assert actual == expected
