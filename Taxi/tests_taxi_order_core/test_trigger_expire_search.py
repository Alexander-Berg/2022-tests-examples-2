import datetime

import bson
import pytest


_NOW = datetime.datetime.fromisoformat('2021-04-13T13:04:58.101')


@pytest.mark.now(f'{_NOW.isoformat()}Z')
async def test_expire_search_run(stq, stq_runner, mockserver, mongodb):
    @mockserver.handler('/order-core/internal/processing/v1/event/expire')
    def post_event(req):
        assert req.query['order_id'] == order_id
        assert 'due' not in req.query
        body = bson.BSON(req.get_data()).decode()
        update = body['extra_update']['$set']
        assert update == {
            'status': 'finished',
            'order.user_fraud': False,
            'order.status': 'finished',
            'order.taxi_status': 'expired',
            'order.status_updated': _NOW,
        }
        assert body['event_extra_payload'] == {'s': 'finished', 't': 'expired'}
        assert body['fields'] == []
        assert body['filter'] == {'processing.version': 3}
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode({}),
        )

    order_id = 'order_1'
    args = [order_id, ['search_expire']]

    move_past = datetime.datetime(2020, 4, 13, 13, 4, 58)
    proc_update = {
        '$set': {
            'order.request.due': move_past,
            'order.created': move_past,
            'created': move_past,
            'order_info.statistics.status_updates.0.c': move_past,
        },
    }
    mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    # when run expire, do not reschedule
    assert not stq.process_trigger.times_called
    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'search_expire' not in proc.get('trigger', {}).get('s', {})

    assert post_event.times_called == 1


@pytest.mark.now(f'{_NOW.isoformat()}Z')
@pytest.mark.config(
    DA_SOON_SEARCH_EXPIRATION_SECONDS=600,
    DA_SOON_SEARCH_EXPIRATION_SECONDS_CHILDCHAIR=660,
    SVO_EXPIRATION_TIME=440,
    CODE_DISPATCH_ORDER_EXPIRE_TIME=770,
    CODE_DISPATCH_PROCESSING_ENABLED=True,
    DA_EXACT_SEARCH_EXPIRATION_SECONDS=22,
    DELAYED_SEARCH_EXPIRATION_SECONDS=33,
    DA_EXACT_AUTOREORDER_MAX_DUE_SHIFT_SECONDS=13,
    DELAYED_AUTOREORDER_MAX_DUE_SHIFT_SECONDS=22,
)
@pytest.mark.parametrize(
    'proc_update, expected_delay',
    [
        ({'$set': {'order.status': 'assigned'}}, None),
        (None, 500000),  # regular soon order
        (  # with lookup_ttl
            {'$set': {'order.request.lookup_ttl': 200}},
            100000,
        ),
        (
            # active auction with lookup ttl
            {
                '$set': {
                    'auction': {'change_ts': _NOW, 'iteration': 1},
                    'order.request.lookup_ttl': 200,
                },
            },
            200000,
        ),
        (
            # inactive auction with lookup ttl
            {
                '$set': {
                    'auction': {'change_ts': _NOW, 'iteration': 0},
                    'order.request.lookup_ttl': 200,
                },
            },
            100000,
        ),
        (  # dispatch-check-in after check-in without lookup ttl
            {'$set': {'dispatch_check_in': {'check_in_time': _NOW}}},
            500000,
        ),
        (  # dispatch-check-in after check-in with lookup ttl
            {
                '$set': {
                    'dispatch_check_in': {'check_in_time': _NOW},
                    'order.request.lookup_ttl': 200,
                },
            },
            200000,
        ),
        (  # dispatch-check-in before check-in
            {'$set': {'dispatch_check_in': {'check_in_time': None}}},
            500000,
        ),
        ({'$set': {'order.svo_car_number': '1234'}}, 340000),  # svo
        (  # by code-dispatch
            {'$set': {'extra_data.code_dispatch.code': 1234}},
            670000,
        ),
        (  # with child chair
            {'$set': {'order.request.requirements': {'childchair': {}}}},
            560000,
        ),
        ({'$set': {'order._type': 'urgent'}}, 28000),  # regular not soon
        (  # lookup_ttl
            {
                '$set': {
                    'order.request.lookup_ttl': 100,
                    'order._type': 'urgent',
                },
            },
            150000,
        ),
        (  # delayed
            {
                '$set': {
                    'order.request.is_delayed': True,
                    'order._type': 'urgent',
                },
            },
            17000,
        ),
        (  # autoreorder
            {
                '$set': {'order._type': 'urgent'},
                '$push': {
                    'order_info.statistics.status_updates': {
                        'c': _NOW,
                        'q': 'autoreorder',
                    },
                },
            },
            41000,
        ),
        (  # delayed && autoreorder
            {
                '$set': {
                    'order.request.is_delayed': True,
                    'order._type': 'urgent',
                },
                '$push': {
                    'order_info.statistics.status_updates': {
                        'c': _NOW,
                        'q': 'autoreorder',
                    },
                },
            },
            39000,
        ),
    ],
)
async def test_expire_search_eta(
        stq, stq_runner, mongodb, proc_update, expected_delay,
):
    order_id = 'order_1'
    args = [order_id, ['search_expire']]

    if proc_update is not None:
        mongodb.order_proc.update({'_id': order_id}, proc_update)

    await stq_runner.process_trigger.call(task_id=order_id, args=args)
    if expected_delay is None:
        assert not stq.process_trigger.times_called
    else:
        next_call = stq.process_trigger.next_call()
        eta = _NOW + datetime.timedelta(milliseconds=expected_delay)
        assert next_call['eta'] == eta

    proc = mongodb.order_proc.find_one({'_id': order_id})
    assert 'search_expire' not in proc.get('trigger', {}).get('s', {})
