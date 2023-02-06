import datetime

import pytest


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='processing',
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
async def test_sequence(
        processing, now, stq, mocked_time, use_ydb, use_fast_flow,
):
    queue = processing.testsuite.processing
    item_id = '1'

    first_eta = now + datetime.timedelta(minutes=1)
    second_eta = now + datetime.timedelta(minutes=5)

    await queue.send_event(item_id, {'kind': 'create'})
    await queue.send_event(item_id, {}, eta=first_eta)
    await queue.send_event(item_id, {}, eta=second_eta)
    with stq.flushing():
        await queue.call(item_id)
        call = stq['testsuite_processing'].next_call()
        assert call['eta'] == first_eta

    mocked_time.sleep(100)
    with stq.flushing():
        await queue.call(item_id)
        call = stq['testsuite_processing'].next_call()
        assert call['eta'] == second_eta


@pytest.mark.parametrize(
    'fail_at_b,b_time_shift,expected_order',
    [
        (True, 5, ['a', 'b', 'b', 'c']),
        (False, 5, ['a', 'b', 'c']),
        (True, 0, ['a', 'c', 'b', 'b']),
        (False, 0, ['a', 'c', 'b']),
    ],
)
@pytest.mark.processing_queue_config(
    'for-determinism.yaml', scope='testsuite', queue='processing',
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
async def test_ensure_determinism(
        processing,
        stq,
        mocked_time,
        testpoint,
        fail_at_b,
        b_time_shift,
        expected_order,
        use_ydb,
        use_fast_flow,
):
    queue = processing.testsuite.processing
    item_id = '1'
    state = {'exec-order': [], 'fail_at_b': fail_at_b}

    @testpoint('event-processed')
    def _event_processed_tp(data):
        reason = data['extra-data']['reason']
        state['exec-order'].append(reason)
        if reason == 'b' and state['fail_at_b']:
            return {'simulated-error': 'test fail at event "b"'}
        return {}

    eta = mocked_time.now() + datetime.timedelta(minutes=b_time_shift)

    await queue.send_event(item_id, {'kind': 'create'})
    await queue.send_event(item_id, {'kind': 'a'})
    await queue.send_event(item_id, {'kind': 'c'}, eta=eta)
    await queue.send_event(
        item_id, {'kind': 'b'}, expect_fail=state['fail_at_b'],
    )

    state['fail_at_b'] = False
    mocked_time.sleep(b_time_shift * 60)

    with stq.flushing():
        await queue.call(item_id, expect_fail=state['fail_at_b'])

    assert state['exec-order'] == expected_order
