import copy
import datetime

import pytest


_NOW_STR = '2021-04-12T12:55:00.125'
_NOW = datetime.datetime.fromisoformat(_NOW_STR)
_TASK_ID = '_task_id'
_PROCAAS_EVENT = {
    'event_id': 'event_id',
    'created': '2021-08-27T09:36:24.982105+00:00',
    'handled': True,
    'payload': {'q': 'create', 'event-index': 0},
}


@pytest.mark.now(_NOW_STR)
async def test_processing_starter_all_processed(stq, stq_runner, mockserver):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        orders.remove(req.query['item_id'])
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    orders = {'order_1', 'order_2', 'order_3', 'order_legacy'}

    await stq_runner.processing_starter.call(task_id=_TASK_ID)
    next_call = stq.processing_starter.next_call()
    assert next_call['id'] == _TASK_ID
    assert next_call['eta'] == _NOW + datetime.timedelta(seconds=10)

    assert events.times_called == 4
    assert create_event.times_called == 4
    assert not orders


@pytest.mark.now(_NOW_STR)
async def test_processing_starter_all_throw(stq, stq_runner, mockserver):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        orders.remove(req.query['item_id'])
        return mockserver.make_response(
            status=400,
            json={'code': 'race_condition', 'message': 'it happens'},
        )

    orders = {'order_1', 'order_2', 'order_3', 'order_legacy'}

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert stq.processing_starter.times_called == 1
    assert events.times_called == 4
    assert create_event.times_called == 4
    assert not orders


@pytest.mark.now(_NOW_STR)
async def test_processing_starter_second_throws(stq, stq_runner, mockserver):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        orders.remove(req.query['item_id'])
        if len(orders) == 1:
            return mockserver.make_response(
                status=400,
                json={'code': 'race_condition', 'message': 'it happens'},
            )
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    orders = {'order_1', 'order_2', 'order_3', 'order_legacy'}

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert stq.processing_starter.times_called == 1
    assert events.times_called == 4
    assert create_event.times_called == 4
    assert not orders


@pytest.mark.now(_NOW_STR)
@pytest.mark.config(ORDER_CORE_STQ_PROCESSING_STARTER_DELAY=10000)
@pytest.mark.parametrize(
    'updated_seconds_ago, times_called_expected',
    [
        ([11, 11, 11], 4),
        ([11, 11, 10], 3),
        ([11, 10, 10], 2),
        ([10, 10, 9], 1),
    ],
)
async def test_processing_starter_delay(
        stq,
        stq_runner,
        mockserver,
        mongodb,
        updated_seconds_ago,
        times_called_expected,
):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    orders = ['order_1', 'order_2', 'order_3']

    for order_id, seconds in zip(orders, updated_seconds_ago):
        mongodb.order_proc.update(
            {'_id': order_id},
            {'$set': {'updated': _NOW - datetime.timedelta(seconds=seconds)}},
        )

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert events.times_called == times_called_expected
    assert create_event.times_called == times_called_expected


@pytest.mark.now(_NOW_STR)
@pytest.mark.parametrize(
    'restart',
    [
        pytest.param(False),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_STQ_PROCESSING_STARTER_RESTART=True,
                ),
            ],
        ),
    ],
)
async def test_processing_starter_restart(
        stq, stq_runner, mockserver, restart,
):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(
            status=200,
            json={
                'events': [
                    {
                        'event_id': '123456',
                        'created': '2021-02-27T09:43:06+03:00',
                        'handled': True,
                        'payload': {'event-index': 0},
                    },
                ],
            },
        )

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert events.times_called == 4
    assert create_event.times_called == (4 if restart else 0)


@pytest.mark.now(_NOW_STR)
@pytest.mark.config(ORDER_CORE_STQ_PROCESSING_STARTER_RESTART=True)
@pytest.mark.parametrize(
    'restart_limit',
    [
        pytest.param(
            i,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_STQ_PROCESSING_STARTER_RESTART_LIMIT=i,
                ),
            ],
        )
        for i in [1, 2, 5]
    ],
)
async def test_processing_starter_restart_limit_not_restarting(
        stq, stq_runner, mockserver, restart_limit,
):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(
            status=200, json={'events': procaas_events},
        )

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    procaas_events = [
        copy.deepcopy(_PROCAAS_EVENT) for _ in range(restart_limit)
    ]
    for i in range(restart_limit):
        procaas_events[i]['payload']['q'] = 'restart-processing'
        procaas_events[i]['payload']['event-index'] = i

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert events.times_called == 4
    assert create_event.times_called == 0


@pytest.mark.now(_NOW_STR)
@pytest.mark.config(ORDER_CORE_STQ_PROCESSING_STARTER_RESTART=True)
@pytest.mark.parametrize(
    'restart_limit',
    [
        pytest.param(
            i,
            marks=[
                pytest.mark.config(
                    ORDER_CORE_STQ_PROCESSING_STARTER_RESTART_LIMIT=i,
                ),
            ],
        )
        for i in [1, 2, 5]
    ],
)
async def test_processing_starter_restart_limit_restarting(
        stq, stq_runner, mockserver, restart_limit,
):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(
            status=200, json={'events': procaas_events},
        )

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    procaas_events = [
        copy.deepcopy(_PROCAAS_EVENT) for _ in range(2 * restart_limit)
    ]
    for i in range(1, len(procaas_events)):
        procaas_events[i]['payload']['event-index'] = i
        procaas_events[i]['payload']['q'] = 'restart-processing'
        if i == restart_limit:
            procaas_events[i]['payload']['q'] = 'driving'

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert events.times_called == 4
    assert create_event.times_called == 4


@pytest.mark.now(_NOW_STR)
async def test_processing_starter_super_legacy(stq, stq_runner, mockserver):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        orders.remove(req.query['item_id'])
        return mockserver.make_response(
            status=200, json={'event_id': 'event_id'},
        )

    orders = {'order_1', 'order_2', 'order_3', 'order_legacy'}

    await stq_runner.processing_starter.call(task_id=_TASK_ID)
    next_call = stq.processing_starter.next_call()
    assert next_call['id'] == _TASK_ID
    assert next_call['eta'] == _NOW + datetime.timedelta(seconds=10)

    assert events.times_called == 4
    assert create_event.times_called == 4
    assert not orders


@pytest.mark.now(_NOW_STR)
@pytest.mark.config(ORDER_CORE_STQ_PROCESSING_STARTER_RESTART=True)
@pytest.mark.parametrize('create_status', [200, 409])
async def test_processing_starter_basic(stq_runner, mockserver, create_status):
    @mockserver.handler('/processing/v1/taxi/orders/events')
    def events(req):
        return mockserver.make_response(status=200, json={'events': []})

    @mockserver.handler('/processing/v1/taxi/orders/create-event')
    def create_event(req):
        assert req.json['q'] != 'restart-processing'
        body = {'event_id': 'event_id'}
        if create_status == 409:
            body = {'code': 'race_condition', 'message': 'it happens'}
        return mockserver.make_response(status=create_status, json=body)

    await stq_runner.processing_starter.call(task_id=_TASK_ID)

    assert events.times_called == 4
    assert create_event.times_called == 4
