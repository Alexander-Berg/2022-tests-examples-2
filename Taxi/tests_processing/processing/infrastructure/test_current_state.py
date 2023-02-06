import pytest


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
async def test_get_current_state(
        processing, taxi_processing, use_ydb, use_fast_flow,
):
    item_id = '123123123'
    queue = processing.testsuite.example

    async def _get_state():
        get_params = {'item_id': item_id, 'allow_restore': False}
        resp = await taxi_processing.get(
            '/v1/testsuite/example/current-state', params=get_params,
        )
        assert resp.status_code == 200
        return resp.json()['current-state']

    # initial state
    await queue.send_event(item_id, {'is-create': True})
    assert await _get_state() == {'foo': 42, 'bar': 100500, 'counter': '+'}

    # modifier
    await queue.send_event(
        item_id, {'is-create': False, 'new-foo': 'alice', 'new-bar': 'bob'},
    )
    assert await _get_state() == {
        'foo': 'alice',
        'bar': 'bob',
        'counter': '++',
    }


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
async def test_get_current_state_step_by_step(
        processing, taxi_processing, use_ydb, use_fast_flow,
):
    item_id = '123123123'
    queue = processing.testsuite.example

    async def _get_state(terminal_event_id):
        get_params = {
            'item_id': item_id,
            'allow_restore': False,
            'terminal-event-id': terminal_event_id,
        }
        resp = await taxi_processing.get(
            '/v1/testsuite/example/current-state', params=get_params,
        )
        assert resp.status_code == 200
        return resp.json()['current-state']

    # send events
    event_id1 = await queue.send_event(item_id, {'is-create': True})
    event_id2 = await queue.send_event(
        item_id, {'is-create': False, 'new-foo': 'alice', 'new-bar': 'bob'},
    )

    # check the states
    assert await _get_state(event_id1) == {
        'foo': 42,
        'bar': 100500,
        'counter': '+',
    }
    assert await _get_state(event_id2) == {
        'foo': 'alice',
        'bar': 'bob',
        'counter': '++',
    }


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
async def test_get_current_state_no_item(
        taxi_processing, use_ydb, use_fast_flow,
):
    resp = await taxi_processing.get(
        '/v1/testsuite/example/current-state',
        params={'item_id': '123123123', 'allow_restore': False},
    )
    assert resp.status_code == 404
    assert resp.json()['code'] == 'no_such_item'


@pytest.mark.processing_queue_config(
    'queue.yaml', scope='testsuite', queue='example',
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
async def test_get_current_state_no_queue(
        taxi_processing, use_ydb, use_fast_flow,
):
    resp = await taxi_processing.get(
        '/v1/foo/bar/current-state',
        params={'item_id': '123123123', 'allow_restore': False},
    )
    assert resp.status_code == 400
    assert resp.json()['code'] == 'no_such_queue'


@pytest.mark.processing_queue_config(
    'queue-keys-reasons.yaml', scope='testsuite', queue='example',
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
async def test_current_state_reasons(
        processing, taxi_processing, use_ydb, use_fast_flow,
):
    item_id = '123123123'
    queue = processing.testsuite.example

    async def _get_state():
        get_params = {'item_id': item_id, 'allow_restore': False}
        resp = await taxi_processing.get(
            '/v1/testsuite/example/current-state', params=get_params,
        )
        assert resp.status_code == 200
        return resp.json()['current-state']

    await queue.send_event(
        item_id, {'is-create': True, 'reason': 'reason-handle'},
    )
    assert await _get_state() == {'event-reason': 'reason-handle'}
