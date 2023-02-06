import pytest

import tests_candidates.helpers


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['lavka']},
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
async def test_shifts(taxi_candidates, driver_positions, mockserver):
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
                            'started_at': '2021-11-17T12:07:12Z',
                            'closes_at': '2021-11-17T12:12:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2021-11-17T12:07:12Z',
                            'is_high_priority': False,
                        },
                        {
                            'courier_id': 'dbid0_uuid1',
                            'eats_courier_id': '11',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': '67890',
                            'meta_group_id': '67890',
                            'status': 'in_progress',
                            'started_at': '2021-11-17T12:07:12Z',
                            'closes_at': '2021-11-17T12:14:12Z',
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
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'zone_id': 'moscow',
        'filters': ['eats/shift_ends_soon'],
        'allowed_classes': ['econom', 'vip', 'uberblack'],
        'order': {
            'calc': {'time': 600},
            'request': {'shift': {'type': 'eats'}},
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
