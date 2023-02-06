import datetime

import pytest


@pytest.mark.experiments3(filename='max_send_time_feature/exp3_disabled.json')
async def test_stq_order_send_max_send_time_disabled(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq_max_send_time_cancel.json')
    assert len(events['events']) == 2
    mocked_time.set(datetime.datetime(2021, 1, 1, 14, 0))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 2
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1121', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_arrival_112', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 2

    stq_task = stq.eats_order_send_sender.next_call()
    assert 'is_cancel' not in stq_task['kwargs']

    stq_task = stq.eats_order_send_sender.next_call()
    assert 'is_cancel' not in stq_task['kwargs']


@pytest.mark.experiments3(filename='max_send_time_feature/exp3_cancel.json')
async def test_stq_order_send_max_send_time_cancel(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq_max_send_time_cancel.json')
    assert len(events['events']) == 2
    mocked_time.set(datetime.datetime(2021, 1, 1, 14, 0))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 2
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1121', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_arrival_112', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 1

    stq_task = stq.eats_order_send_sender.next_call()
    assert 'is_cancel' in stq_task['kwargs']


@pytest.mark.experiments3(filename='max_send_time_feature/exp3_send.json')
async def test_stq_order_send_max_send_time_send(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        testpoint,
        experiments3,
):
    exp = load_json('exp3_subtraction_max_send_time_enabled.json')
    experiments3.add_experiments_json(exp)

    @testpoint('max_send_time_force_send')
    def max_send_time_force_send(data):
        return data

    events = load_json('events_stq_max_send_time_send.json')
    assert len(events['events']) == 2
    mocked_time.set(datetime.datetime(2021, 1, 1, 14, 0))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 2

    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1121', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1

    stq_task = stq.eats_order_send_scheduler.next_call()
    assert stq.eats_order_send_sender.times_called == 1

    assert max_send_time_force_send.times_called == 1
    send_time = max_send_time_force_send.next_call()['data']['send_time']

    assert events['events'][0].get('payload').get('max_send_time') == send_time
    assert 'is_cancel' not in stq_task['kwargs']
