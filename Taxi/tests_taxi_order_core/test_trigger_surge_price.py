import datetime

import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'proc_update, push_new_suggestion, suggestions_size',
    (
        # no suggestion in proc
        (None, True, 1),
        # no spr, do not need to make suggestion
        ({'$unset': {'order.request.spr': True}}, False, 0),
        # already have suggestion, but for another generation, make new one
        (
            {
                '$push': {
                    'reorder.suggestions': {
                        'generation': 2,
                        'request': {'sp': 1.7},
                    },
                },
            },
            True,
            2,
        ),
        # already have suggestion, but with another sp, make new one
        (
            {
                '$push': {
                    'reorder.suggestions': {
                        'generation': 1,
                        'request': {'sp': 1.6},
                    },
                },
            },
            True,
            2,
        ),
        # already have actual suggestion, do not edit it
        (
            {
                '$push': {
                    'reorder.suggestions': {
                        'generation': 1,
                        'request': {'sp': 1.7},
                    },
                },
            },
            False,
            1,
        ),
    ),
)
async def test_surge_price_run(
        stq,
        stq_runner,
        mongodb,
        proc_update,
        push_new_suggestion,
        suggestions_size,
):
    order_id = 'order_1'
    args = [order_id, ['surgeprice']]
    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert proc['trigger']['s']['surgeprice']['last_called'] == _NOW

    assert len(proc['reorder']['suggestions']) == suggestions_size
    if push_new_suggestion:
        new_suggestion = proc['reorder']['suggestions'][-1]
        suggestion_id = new_suggestion.pop('id')
        assert suggestion_id.find('-') == -1
        assert suggestion_id.count('0') < 16
        assert new_suggestion == {
            'type': 'forced_surge',
            'generation': 1,
            'params': {'c': _NOW - datetime.timedelta(seconds=100)},
            'request': {'sp': 1.7},
        }
    next_call = stq.process_trigger.next_call()
    assert next_call['id'] == order_id
    assert next_call['eta'] == _NOW + datetime.timedelta(seconds=60)


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.parametrize(
    'proc_update, expected_delay',
    [
        ({'$set': {'order.status': 'assigned'}}, None),
        ({'$set': {'order.request.sp': 1.7}}, None),
        ({'$unset': {'lookup': True}}, None),
        (None, 60),
        ({'$unset': {'trigger.s.surgeprice': True}}, 60),
        (
            {
                '$unset': {'trigger.s.surgeprice': True},
                '$set': {
                    'order._type': 'urgent',
                    'order.request.due': _NOW + datetime.timedelta(
                        seconds=1300,
                    ),
                },
            },
            100,
        ),
    ],
)
async def test_surge_price_eta(
        stq, stq_runner, mongodb, proc_update, expected_delay,
):
    order_id = 'order_1'
    args = [order_id, ['surgeprice']]

    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    if expected_delay is None:
        assert not stq.process_trigger.times_called
    else:
        next_call = stq.process_trigger.next_call()
        eta = _NOW + datetime.timedelta(seconds=expected_delay)
        assert next_call['eta'] == eta
