import pytest

import tests_candidates.helpers


@pytest.mark.config(
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['lavka']},
    },
)
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
                            'zone_group_id': '67890',
                            'meta_group_id': '67890',
                            'status': 'in_progress',
                            'started_at': '2020-07-28T08:47:00Z',
                            'closes_at': '2020-07-28T09:07:12Z',
                            'paused_at': None,
                            'unpauses_at': None,
                            'updated_ts': '2020-07-28T09:07:12Z',
                            'is_high_priority': True,
                        },
                        {
                            'courier_id': 'dbid0_uuid2',
                            'eats_courier_id': '12',
                            'shift_id': '19950',
                            'zone_id': '6341',
                            'zone_group_id': '67891',
                            'meta_group_id': '67891',
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
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'filters': ['partners/eats_shifts'],
        'order': {
            'request': {
                'shift': {
                    'type': 'eats',
                    'zone_group': {'required_ids': ['67890', '67891']},
                },
            },
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
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['lavka']},
    },
)
@pytest.mark.parametrize(
    'allow_missing, required_ids, uuids',
    [
        (True, [], ['uuid0']),
        (True, ['123'], ['uuid0', 'uuid1']),
        (False, ['123'], ['uuid1']),
    ],
)
async def test_allow_missing(
        taxi_candidates,
        driver_positions,
        allow_missing,
        required_ids,
        uuids,
        mockserver,
):
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
                            'status': 'in_progress',
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
                            'zone_group_id': '123',
                            'meta_group_id': '123',
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
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 10,
        'max_distance': 100000,
        'point': [37.630971, 55.743789],
        'filters': ['partners/eats_shifts'],
        'order': {
            'request': {
                'shift': {
                    'type': 'eats',
                    'zone_group': {
                        'required_ids': required_ids,
                        'allow_missing': allow_missing,
                    },
                },
            },
        },
    }

    expected_drivers = [{'dbid': 'dbid0', 'uuid': uuid} for uuid in uuids]

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    actual, expected = tests_candidates.helpers.normalize(
        actual=response.json(), expected={'drivers': expected_drivers},
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
                            'zone_group_id': '67890',
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
        'filters': ['partners/eats_shifts'],
        'allowed_classes': ['econom', 'vip', 'uberblack'],
        'order': {'request': {'shift': {'type': 'eats'}}},
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
