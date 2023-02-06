import pytest

import tests_candidates.helpers


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
async def test_shifts(
        taxi_candidates, driver_positions, mockserver, grocery_depots,
):
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
                        'shift_status': 'closed',
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
                    {
                        'performer_id': 'dbid0_uuid3',
                        'shift_id': '19954',
                        'shift_status': 'waiting',
                        'started_at': '2020-07-28T09:10:00Z',
                        'closes_at': '2020-07-28T09:20:12Z',
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
            {'dbid_uuid': 'dbid0_uuid3', 'position': [37.630971, 55.743789]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'filters': ['grocery/shifts'],
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['67890', '67891']},
                },
            },
        },
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={  # filter out closed and not-started shifts
            'drivers': [
                {'dbid': 'dbid0', 'uuid': 'uuid1'},
                {'dbid': 'dbid0', 'uuid': 'uuid2'},
            ],
        },
    )
    assert actual == expected

    request_body['order']['request']['shift']['zone_group']['required_ids'] = [
        '67890',
    ]

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(),
        expected={'drivers': [{'dbid': 'dbid0', 'uuid': 'uuid1'}]},
    )
    assert actual == expected


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['express']},
        'grocery': {'classes': ['express']},
    },
)
async def test_incompatible_classes(
        taxi_candidates, driver_positions, mockserver,
):
    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts/v1/updates',
    )
    def _grocery_shifts_journal(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'shifts': [
                        {
                            'store_id': 'asdfghjkl',
                            'courier_id': 'dbid0_uuid0',
                            'shift_id': '19950',
                            'store_external_id': '12345',
                            'status': 'closed',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                        },
                        {
                            'store_id': 'asdfghjkl',
                            'courier_id': 'dbid0_uuid1',
                            'shift_id': '19950',
                            'store_external_id': '67890',
                            'status': 'in_progress',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                        },
                        {
                            'store_id': 'asdfghjkl',
                            'courier_id': 'dbid0_uuid1',
                            'shift_id': '19950',
                            'store_external_id': '67890',
                            'status': 'waiting',
                            'started_at': '2020-07-28T09:10:00Z',
                            'closes_at': '2020-07-28T09:20:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:10:12Z',
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
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'filters': ['grocery/shifts'],
        'allowed_classes': ['econom', 'vip', 'uberblack'],
        'order': {'request': {'shift': {'type': 'grocery'}}},
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
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
