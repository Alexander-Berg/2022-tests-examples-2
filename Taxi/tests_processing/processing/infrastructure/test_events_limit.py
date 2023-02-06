import pytest


@pytest.mark.parametrize(
    'item_id,expected_limit',
    [
        pytest.param(
            '123123123_0',
            0,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-0',
                ),
            ],
        ),
        pytest.param(
            '123123123_1',
            1,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-1',
                ),
            ],
        ),
        pytest.param(
            '123123123_5',
            5,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-5',
                ),
            ],
        ),
        pytest.param(
            '123123123_5',
            3,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-5',
                ),
                pytest.mark.config(
                    PROCESSING_EVENTS_LIMITS={
                        '__default__': {'max-events-hard': 3},
                    },
                ),
            ],
        ),
        pytest.param(
            '123123123_5',
            5,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-5',
                ),
                pytest.mark.config(
                    PROCESSING_EVENTS_LIMITS={
                        '__default__': {'max-events-hard': 30},
                    },
                ),
            ],
        ),
        pytest.param(
            '123123123_5',
            3,
            marks=[
                pytest.mark.processing_queue_config(
                    'dummy-queue.yaml',
                    scope='testsuite',
                    queue='foo',
                    main_operator='main-5',
                ),
                pytest.mark.config(
                    PROCESSING_EVENTS_LIMITS={
                        '__default__': {'max-events-hard': 30},
                        'testsuite/foo': {'max-events-hard': 3},
                    },
                ),
            ],
        ),
    ],
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
async def test_create_event_limit(
        taxi_processing, pgsql, ydb, item_id, expected_limit, use_ydb,
):
    for i in range(max(1, expected_limit * 2)):
        resp = await taxi_processing.post(
            '/v1/testsuite/foo/create-event',
            params={'item_id': item_id},
            headers={'X-Idempotency-Token': f'event_{i}'},
            json={},
        )
        if i < expected_limit:
            assert resp.status_code == 200
        else:
            assert resp.status_code == 400
            assert resp.json()['code'] == 'too_many_events'
    resp = await taxi_processing.get(
        '/v1/testsuite/foo/events',
        params={
            'item_id': item_id,
            'allow_restore': False,
            'show_unapproached': True,
        },
    )
    assert resp.status_code == 400
    assert resp.json()['code'] == 'too_many_events'

    if not use_ydb:
        cursor = pgsql['processing_db'].cursor()
        cursor.execute(
            'SELECT COUNT(*) FROM processing.events WHERE item_id=%(item_id)s',
            {'item_id': item_id},
        )
        assert list(cursor)[0][0] == expected_limit
    else:
        db_name = '`events`'
        cursor = ydb.execute(
            'SELECT COUNT(*) AS cnt FROM {} where item_id="{}"'.format(
                db_name, item_id,
            ),
        )
        assert cursor[0].rows[0]['cnt'] == expected_limit


@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'dummy-queue.yaml', scope='testsuite', queue='foo', main_operator='main-5',
)
async def test_early_fail_on_limit_violation(
        taxi_processing, processing, testpoint, use_ydb,
):
    @testpoint('ProcessingNgQueue::HardlimitViolation')
    def early_quit_tp(data):
        pass

    # add event to reach limit
    item_id = '123123'
    for i in range(5):
        resp = await taxi_processing.post(
            '/v1/testsuite/foo/create-event',
            params={'item_id': item_id},
            headers={'X-Idempotency-Token': f'event_{i}'},
            json={},
        )
        assert resp.status_code == 200

    # will fail but not early
    resp = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id},
        headers={'X-Idempotency-Token': f'event_5'},
        json={},
    )
    assert resp.status_code == 400
    assert early_quit_tp.times_called == 0

    # will fail but not early
    await processing.testsuite.foo.call(item_id, expect_fail=True)
    assert early_quit_tp.times_called == 0

    # will fail early
    await processing.testsuite.foo.call(item_id, expect_fail=True)
    assert early_quit_tp.times_called == 1

    # will fail early
    resp = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id},
        headers={'X-Idempotency-Token': f'event_5'},
        json={},
    )
    assert resp.status_code == 400
    assert early_quit_tp.times_called == 2


@pytest.mark.parametrize(
    'use_ydb',
    [
        pytest.param(False),
        pytest.param(
            True, marks=[pytest.mark.experiments3(filename='use_ydb.json')],
        ),
    ],
)
@pytest.mark.processing_queue_config(
    'dummy-queue.yaml', scope='testsuite', queue='foo', main_operator='main-6',
)
@pytest.mark.config(
    PROCESSING_EVENTS_LIMITS={'__default__': {'max-events-hard': 3}},
)
async def test_early_fail_on_limit_violation_conflicts(
        taxi_processing, processing, testpoint, use_ydb,
):
    @testpoint('ProcessingNgQueue::HardlimitViolation')
    def early_quit_tp(data):
        pass

    item_id_fail = 'd9dde9159696126fad9569fe2e27dc33'
    item_id_ok = '0806256223a0327193afd6a00c4ba13b'

    events = [
        {'order_id': item_id_ok, 'reason': 'create'},
        {'order_id': item_id_fail, 'reason': 'create'},
        {'order_id': item_id_fail, 'reason': 'event_1'},
        {'order_id': item_id_fail, 'reason': 'event_2'},
    ]

    for event in events:
        resp = await taxi_processing.post(
            '/v1/testsuite/foo/create-event',
            params={'item_id': event['order_id']},
            headers={'X-Idempotency-Token': event['reason']},
            json={'q': event['reason']},
        )
        assert resp.status_code == 200

    # will fail but not early
    resp = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id_fail},
        headers={'X-Idempotency-Token': 'event_3'},
        json={},
    )
    assert resp.status_code == 400
    assert early_quit_tp.times_called == 0

    # will fail but not early
    await processing.testsuite.foo.call(
        item_id_fail, expect_fail=True, stq_queue='testsuite_foo',
    )
    assert early_quit_tp.times_called == 0

    # will fail early
    await processing.testsuite.foo.call(
        item_id_fail, expect_fail=True, stq_queue='testsuite_foo',
    )
    assert early_quit_tp.times_called == 1

    # will fail early
    resp = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id_fail},
        headers={'X-Idempotency-Token': f'event_4'},
        json={},
    )
    assert resp.status_code == 400
    assert early_quit_tp.times_called == 2

    # will not fail early
    resp = await taxi_processing.post(
        '/v1/testsuite/foo/create-event',
        params={'item_id': item_id_ok},
        headers={'X-Idempotency-Token': 'event_1'},
        json={},
    )
    assert resp.status_code == 200
