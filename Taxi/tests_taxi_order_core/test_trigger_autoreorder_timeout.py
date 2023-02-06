import datetime

import bson
import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_autoreorder_timeout_run(stq, stq_runner, mockserver, mongodb):
    @mockserver.handler(
        '/order-core/internal/processing/v1/event/autoreorder_timeout',
    )
    def post_event(req):
        assert req.query['order_id'] == order_id
        assert 'due' not in req.query
        body = bson.BSON(req.get_data()).decode()
        assert body['extra_update'] == {}
        assert body['event_extra_payload'] == {}
        assert body['fields'] == []
        assert body['filter'] == {'processing.version': 3}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['autoreordertimeout']]

    move_past = datetime.datetime(2021, 4, 13, 13, 1, 58)
    proc_update = {'$push': {'autoreorder.decisions': {'created': move_past}}}
    mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    # when run autoreorder-timeout, do not reschedule
    assert not stq.process_trigger.times_called
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'autoreordertimeout' not in proc.get('trigger', {}).get('s', {})

    assert post_event.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'proc_update, expected_delay',
    [
        ({'$set': {'order.status': 'assigned'}}, None),
        ({'$set': {'order_info.statistics.status_updates': []}}, None),
        (
            {
                '$push': {
                    'order_info.statistics.status_updates': {
                        'c': _NOW,
                        'q': 'assigned',
                        's': 'assigned',
                    },
                },
            },
            None,
        ),
        (None, 5),
    ],
)
async def test_autoreorder_timeout_eta(
        stq, stq_runner, mongodb, proc_update, expected_delay,
):
    order_id = 'order_1'
    args = [order_id, ['autoreordertimeout']]

    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    if expected_delay is None:
        assert not stq.process_trigger.times_called
    else:
        next_call = stq.process_trigger.next_call()
        eta = _NOW + datetime.timedelta(seconds=expected_delay)
        assert next_call['eta'] == eta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'autoreordertimeout' not in proc.get('trigger', {}).get('s', {})
