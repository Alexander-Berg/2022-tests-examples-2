import uuid

import pytest


@pytest.mark.processing_queue_config(
    'testsuite-foo-basic.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_basic(taxi_processing, pgsql, use_ydb, use_fast_flow):
    item_id = '0'
    create_payload = {'kind': 'create'}
    user_payload = {'foo': 'bar', 'kind': 'user'}
    expect_archivable = False

    # create an item
    result = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id},
        headers={'X-Idempotency-Token': uuid.uuid4().hex},
        json=create_payload,
    )
    assert result.status_code == 200
    create_event_id = result.json()['event_id']
    await _check_archivable(
        pgsql, 'testsuite', 'foo', item_id, expect_archivable,
    )

    # insert user event
    result = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id},
        headers={'X-Idempotency-Token': uuid.uuid4().hex},
        json=user_payload,
    )
    assert result.status_code == 200
    user_event_id = result.json()['event_id']
    await _check_archivable(
        pgsql, 'testsuite', 'foo', item_id, expect_archivable,
    )

    # fetch events of item
    result = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={'item_id': item_id, 'show_unapproached': True},
    )
    assert result.status_code == 200
    body = result.json()
    assert len(body['events']) == 2
    assert body['events'][0]['event_id'] == create_event_id
    assert body['events'][0]['payload'] == create_payload
    assert body['events'][1]['event_id'] == user_event_id
    assert body['events'][1]['payload'] == user_payload


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_idemotency_with_writabillity(
        taxi_processing, use_ydb, use_fast_flow,
):
    for kind in ['create', 'whatever']:
        event_id = None
        for _ in range(2):
            result = await taxi_processing.post(
                '/v1/testsuite/foo/create-event',
                params={'item_id': '8b71bcdf54dabadeb53dacb2049ee83c'},
                headers={'X-Idempotency-Token': 'token' + kind},
                json={'kind': kind},
            )
            assert result.status_code == 200
            assert not event_id or event_id == result.json()['event_id']
            event_id = result.json()['event_id']


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'], dyn_table_data=['yt_events_data.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize('allow_restore', [True, False])
@pytest.mark.pgsql('processing_db', files=['testsuite-foo-db.sql'])
async def test_get_events_handler(taxi_processing, yt_apply, allow_restore):
    response = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={
            'item_id': '0123456789',
            'allow_restore': allow_restore,
            'show_unapproached': True,
        },
    )
    assert response.status_code == 200
    events = response.json()['events']
    assert len(events) == (3 if allow_restore else 1)
    if allow_restore:
        assert events[0]['event_id'] == 'abcdef000000'
        assert events[1]['event_id'] == 'abcdef000001'
        assert events[2]['event_id'] == 'abcdef000002'
    else:
        assert events[0]['event_id'] == 'abcdef000002'


@pytest.mark.yt(
    schemas=['yt_events_schema.yaml'],
    dyn_table_data=['yt_events_empty_data.yaml'],
)
@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize('allow_restore', [True, False])
async def test_get_events_handler_empty(
        taxi_processing, yt_apply, allow_restore,
):
    response = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={
            'item_id': '0123456789',
            'allow_restore': allow_restore,
            'show_unapproached': True,
        },
    )
    assert response.status_code == 200
    assert not response.json()['events']


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_get_events_handler_empty_ydb(taxi_processing, use_fast_flow):
    # no restore from yt for ydb
    response = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={'item_id': '0123456789', 'show_unapproached': True},
    )
    assert response.status_code == 200
    assert not response.json()['events']


@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
async def test_get_events_handler_bad_queue(
        taxi_processing, use_ydb, use_fast_flow,
):
    response = await taxi_processing.get(
        '/v1/bad/queue/events',
        params={'item_id': '0123456789', 'show_unapproached': True},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'no_such_queue'


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
async def test_order_key(taxi_processing, ydb, pgsql, use_ydb):
    event_ids = []

    result = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': 'baz'},
        headers={'X-Idempotency-Token': uuid.uuid4().hex},
        json={'kind': 'create'},
    )
    assert result.status_code == 200
    event_ids.append(result.json()['event_id'])

    for _ in range(10):
        result = await taxi_processing.post(
            '/v1/testsuite/foo/create-event',
            params={'item_id': 'baz'},
            headers={'X-Idempotency-Token': uuid.uuid4().hex},
            json={'kind': 'regular'},
        )
        assert result.status_code == 200
        event_ids.append(result.json()['event_id'])

    result = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={'item_id': 'baz', 'show_unapproached': True},
    )
    assert result.status_code == 200
    body = result.json()
    assert len(body['events']) == len(event_ids)
    assert event_ids == [i['event_id'] for i in body['events']]

    # ensure order_key values are sane
    stored_order_keys = {}
    expected_order_keys = {event_ids[i]: i for i in range(len(event_ids))}

    if use_ydb:
        db_name = '`events`'
        cursor = ydb.execute(
            'SELECT event_id, order_key FROM {} ORDER BY order_key ASC'.format(
                db_name,
            ),
        )
        stored_order_keys = {
            row['event_id'].decode('ascii'): row['order_key']
            for row in cursor[0].rows
        }
    else:
        cursor = pgsql['processing_db'].cursor()
        cursor.execute(
            'SELECT event_id, order_key FROM processing.events '
            'ORDER BY order_key ASC',
        )
        stored_order_keys = {
            item_id: order_key for item_id, order_key in cursor
        }

    assert expected_order_keys == stored_order_keys


async def _check_archivable(pgsql, scope, queue, item_id, expect):
    cursor = pgsql['processing_db'].cursor()
    cursor.execute(
        'SELECT is_archivable FROM processing.events '
        'WHERE scope=\'%s\' AND queue=\'%s\' AND item_id=\'%s\''
        % (scope, queue, item_id),
    )
    # NOTE: all is_archivable flags must be the same
    #       (i.e. whole item is archivable or not)
    assert all([is_archivable == expect for is_archivable, in cursor])


@pytest.mark.processing_queue_config(
    'testsuite-foo.yaml', scope='testsuite', queue='foo',
)
@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
async def test_extra_order_key(taxi_processing, ydb, pgsql, use_ydb):
    order_id = uuid.uuid4().hex
    events = [
        # extra_key, token, expected status, expected(key, extra_key)
        (0, f'{order_id}_e0', 200, (0, 0)),
        (1, f'{order_id}_e1', 200, (1, 1)),
        (2, f'{order_id}_e2', 200, (2, 2)),
        # commit nothing, return event_1_id
        (1, f'{order_id}_e1', 200, (1, 1)),
        # can't commit, extra_order_key=1 exists already
        (1, f'{order_id}_e10', 409, ()),
        # commit nothing, return event_2_id
        (3, f'{order_id}_e2', 200, (2, 2)),
        # can't commit, extra_order_key=4 with existed maximum 2
        (4, f'{order_id}_e4', 409, ()),
        # without extra_order_key we can commit anything
        (None, f'{order_id}_e10', 200, (3, None)),
        (3, f'{order_id}_e3', 200, (4, 3)),
        # now we can do it
        (4, f'{order_id}_e4', 200, (5, 4)),
    ]

    sent_events = dict()
    for event in events:
        params = {'item_id': order_id}
        if event[0] is not None:
            params['extra_order_key'] = event[0]
        result = await taxi_processing.post(
            '/v1/testsuite/foo/create-event',
            params=params,
            headers={'X-Idempotency-Token': event[1]},
            json={'kind': 'create'} if event[0] == 0 else {'kind': 'any'},
        )
        assert result.status_code == event[2]
        if result.status_code == 200:
            sent_events[result.json()['event_id']] = event[3]

        events_in_db = {}

        if use_ydb:
            db_name = '`events`'
            cursor = ydb.execute(
                """
                SELECT event_id, order_key, extra_order_key
                FROM {} ORDER BY order_key ASC
                """.format(
                    db_name,
                ),
            )
            events_in_db = {
                row['event_id'].decode('ascii'): (
                    row['order_key'],
                    row['extra_order_key'],
                )
                for row in cursor[0].rows
            }
        else:
            cursor = pgsql['processing_db'].cursor()
            cursor.execute(
                'SELECT event_id, order_key, extra_order_key '
                'FROM processing.events ORDER BY order_key ASC',
            )
            events_in_db = {
                id: (key, extra_key) for id, key, extra_key in cursor
            }
        assert sent_events == events_in_db

    result_events = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={'item_id': order_id, 'show_unapproached': True},
    )
    assert result_events.status_code == 200
    events = result_events.json()['events']
    assert len(events) == 6
    extra_order_keys = [ev.get('extra_order_key', 'null') for ev in events]
    assert extra_order_keys == [0, 1, 2, 'null', 3, 4]


@pytest.mark.experiments3(filename='use_ydb.json')
@pytest.mark.parametrize(
    'use_fast_flow',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='ydb_flow.json')],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'simple-example.yaml', scope='testsuite', queue='example',
)
async def test_need_start_set_in_ydb(processing, stq, ydb, use_fast_flow):
    with stq.flushing():
        event_id = await processing.testsuite.example.send_event(
            '1234567890', {'kind': 'create'},
        )
        cursor = ydb.execute(
            'SELECT * FROM `events` WHERE event_id="{}"'.format(event_id),
        )
        assert len(cursor) == 1
        row = cursor[0].rows[0]
        assert row['event_id'].decode('utf-8') == event_id
        assert (row['need_start']) or (row['need_start'] is None)
        # for some flows need_start is not set, so it may as well be NULL
