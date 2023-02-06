import datetime

import pytest


PARK_CREDENTIALS = {
    'clid': '999012',
    'apikey': 'd19a9b3b59424881b57adf5b0f367a2c',
}


@pytest.mark.parametrize(
    'payload,status,destinations_statuses',
    [
        ({'order_id': '1', 'points': []}, 200, []),
        ({'order_id': 'not_found', 'points': []}, 404, None),
        (
            {
                'order_id': '1',
                'points': [
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:00.0Z',
                        'passed': True,
                        'type': 'auto',
                    },
                ],
            },
            400,
            None,
        ),
        (
            {
                'order_id': '2',
                'points': [
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:00Z',
                        'passed': True,
                        'type': 'manual',
                    },
                ],
            },
            200,
            [{'updated': datetime.datetime(2010, 1, 1), 'passed': True}],
        ),
        (
            {'order_id': '2', 'points': []},
            200,
            [
                {
                    'updated': datetime.datetime(1970, 1, 1, 0, 0),
                    'passed': False,
                },
            ],
        ),
        (
            {
                'order_id': '2',
                'points': [
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:00Z',
                        'passed': True,
                        'type': 'manual',
                    },
                ],
            },
            200,
            [{'updated': datetime.datetime(2010, 1, 1), 'passed': True}],
        ),
        (
            {
                'order_id': '3',
                'points': [
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:00Z',
                        'passed': True,
                        'type': 'manual',
                    },
                ],
            },
            200,
            [
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 1),
                    'passed': False,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 2),
                    'passed': False,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 3),
                    'passed': False,
                },
            ],
        ),
        (
            {
                'order_id': '3',
                'points': [
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:10Z',
                        'passed': True,
                        'type': 'manual',
                    },
                ],
            },
            200,
            [
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 10),
                    'passed': True,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 2),
                    'passed': False,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 3),
                    'passed': False,
                },
            ],
        ),
        (
            {
                'order_id': '3',
                'points': [
                    {
                        'order': 2,
                        'arrival_time': '2010-01-01T00:00:10Z',
                        'passed': True,
                        'type': 'manual',
                    },
                ],
            },
            200,
            [
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 1),
                    'passed': False,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 10),
                    'passed': True,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 3),
                    'passed': False,
                },
            ],
        ),
        (
            {
                'order_id': '3',
                'points': [
                    {
                        'order': 2,
                        'arrival_time': '2010-01-01T00:00:10Z',
                        'passed': True,
                        'type': 'manual',
                    },
                    {
                        'order': 1,
                        'arrival_time': '2010-01-01T00:00:00Z',
                        'passed': True,
                        'type': 'manual',
                    },
                    {
                        'order': 3,
                        'arrival_time': '2010-01-01T00:00:15Z',
                        'passed': False,
                        'type': 'auto',
                    },
                ],
            },
            200,
            [
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 1),
                    'passed': False,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 10),
                    'passed': True,
                },
                {
                    'updated': datetime.datetime(2010, 1, 1, 0, 0, 15),
                    'passed': False,
                },
            ],
        ),
    ],
)
def test_updatepoints(
        payload, status, destinations_statuses, taxi_protocol, db,
):
    response = taxi_protocol.post(
        '1.x/updatepoints', json=payload, params=PARK_CREDENTIALS,
    )
    assert response.status_code == status
    if destinations_statuses is not None:
        proc = db.order_proc.find_one({'aliases.id': payload['order_id']})
        assert proc['destinations_statuses'] == destinations_statuses


@pytest.mark.parametrize('use_order_core', [False, True])
@pytest.mark.parametrize('events_enabled', [True, False])
@pytest.mark.parametrize(
    'point_aware_idempotency_token_enabled', [False, True],
)
def test_add_events(
        taxi_protocol,
        db,
        config,
        events_enabled,
        use_order_core,
        point_aware_idempotency_token_enabled,
        mock_order_core,
):
    config.set_values(
        {
            'UPDATEPOINTS_STATUS_UPDATE_EVENTS_ENABLED': events_enabled,
            'UPDATEPOINTS_POINT_AWARE_IDEMPOTENCY_TOKEN_ENABLED': (
                point_aware_idempotency_token_enabled
            ),
        },
    )
    if use_order_core:
        config.set_values(
            dict(PROCESSING_BACKEND_CPP_SWITCH=['update-points']),
        )
    payload = {
        'order_id': '2',
        'points': [
            {
                'order': 1,
                'arrival_time': '2010-01-01T00:00:00Z',
                'passed': True,
                'type': 'manual',
            },
        ],
    }
    response = taxi_protocol.post(
        '1.x/updatepoints', json=payload, params=PARK_CREDENTIALS,
    )

    assert response.status_code == 200

    if use_order_core and events_enabled:
        assert mock_order_core.post_event_times_called == 1
        return

    assert mock_order_core.post_event_times_called == 0

    proc = db.order_proc.find_one({'aliases.id': payload['order_id']})

    #  We can't mock $currentDate now, so check it separately
    now = datetime.datetime.utcnow()
    assert abs(now - proc['updated']) < datetime.timedelta(minutes=10)
    if events_enabled:
        assert proc['order']['version'] == 1
        assert proc['processing']['version'] == 1
        assert proc['processing']['need_start'] is True
        assert proc['order_info']['need_sync'] is True
        statuses = proc['order_info']['statistics']['status_updates']
        assert len(statuses) == 1
        assert statuses[0]['q'] == 'destinations_statuses_updated'
        assert statuses[0]['h'] is True
        assert abs(now - statuses[0]['c']) < datetime.timedelta(minutes=10)
    else:
        assert not proc['order'].get('version')
        assert not proc.get('processing')
        assert not proc.get('order_info')
