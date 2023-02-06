import datetime

import pytest


async def test_stq_order_send(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq.json')
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


async def test_stq_order_send_cancel(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq_with_cancel.json')
    assert len(events['events']) == 3

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 3
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1121', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 2
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_arrival_112', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_order_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 0


async def test_stq_order_send_only_create(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq_only_create.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1121', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 0


async def test_stq_order_send_only_cancel(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time,
):
    events = load_json('events_stq_only_cancel.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_order_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_scheduler.times_called == 0


async def test_stq_order_send_calculate_sent_time(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time, pgsql,
):
    events = load_json('events_stq_sent_time.json')
    assert len(events['events']) == 3
    mocked_time.set(datetime.datetime(2021, 2, 1, 13, 59))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 3
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 2
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_1', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_2', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 3
    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 20, 0, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    check_creation_reasons(tasks[0][2])


async def test_stq_order_send_part_events(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time, pgsql,
):
    events = load_json('events_stq_part_one_create.json')
    assert len(events['events']) == 1
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 0
    mocked_time.sleep(600)
    events = load_json('events_stq_part_one_departure.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='departure_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 0
    mocked_time.sleep(600)

    events = load_json('events_stq_part_one_arrival.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='arrival_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 18, 30, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    check_creation_reasons(tasks[0][2])

    events = load_json('events_stq_part_one_cancel.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 18, 30, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    assert tasks[0][1] is True
    check_creation_reasons(tasks[0][2])


@pytest.mark.parametrize(
    'sent_time',
    [
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 18, 30, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_subtraction_default.json',
                ),
            ),
        ),
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 18, 30, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_subtraction_disabled.json',
                ),
            ),
        ),
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 18, 36, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_subtraction_different_delta.json',
                ),
            ),
        ),
    ],
)
async def test_stq_order_send_with_exp(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        pgsql,
        sent_time,
):
    events = load_json('events_stq_part_one_create.json')
    assert len(events['events']) == 1
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 0
    mocked_time.sleep(600)
    events = load_json('events_stq_part_one_departure.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='departure_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 0
    mocked_time.sleep(600)

    events = load_json('events_stq_part_one_arrival.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='arrival_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == sent_time
    assert tasks[0][1] is False
    check_creation_reasons(tasks[0][2])

    events = load_json('events_stq_part_one_cancel.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][1] is True
    check_creation_reasons(tasks[0][2])


async def test_stq_order_send_immediately(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time, pgsql,
):
    events = load_json('events_immediately_schema.json')
    assert len(events['events']) == 1

    cur_datetime = datetime.datetime(
        2021, 1, 1, 15, 3, tzinfo=datetime.timezone.utc,
    )
    mocked_time.set(cur_datetime)

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order_1', kwargs=stq_task['kwargs'],
    )
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)
    assert len(tasks) == 1
    assert tasks[0][3] >= cur_datetime
    assert tasks[0][3] < cur_datetime + datetime.timedelta(0, 10)


async def test_stq_order_send_unconditional(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time, pgsql,
):
    events = load_json('events_stq_unconditional_create.json')
    assert len(events['events']) == 1
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 19, 30, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    assert tasks[0][1] is False
    check_creation_reasons(tasks[0][2])

    mocked_time.sleep(600)

    events = load_json('events_stq_unconditional_departure.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='departure_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 2

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 18, 45, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    assert tasks[0][1] is False
    check_creation_reasons(tasks[0][2])

    events = load_json('events_stq_unconditional_cancel.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 2

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][1] is True
    check_creation_reasons(tasks[0][2])


async def test_stq_order_send_skip_sent_orders(
        taxi_eats_order_send, stq, stq_runner, load_json, mocked_time, pgsql,
):
    events = load_json('events_stq_sent_time.json')
    assert len(events['events']) == 3
    mocked_time.set(datetime.datetime(2021, 2, 1, 13, 59))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    add_sending_task_with_history(pgsql, 1)

    assert stq.eats_order_send_scheduler.times_called == 3
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_order', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 2
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_1', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='update_courier_2', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_scheduler.times_called == 0
    assert stq.eats_order_send_sender.times_called == 0


@pytest.mark.parametrize(
    ['sent_time_one', 'sent_time_two'],
    [
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 19, 30, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2021, 2, 1, 18, 45, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_unconditional_default.json',
                ),
            ),
        ),
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 19, 30, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2021, 2, 1, 18, 45, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_unconditional_disabled.json',
                ),
            ),
        ),
        pytest.param(
            datetime.datetime(
                2021, 2, 1, 19, 42, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            datetime.datetime(
                2021, 2, 1, 18, 57, 0, 10000, tzinfo=datetime.timezone.utc,
            ),
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_unconditional_different_delta.json',
                ),
            ),
        ),
    ],
)
async def test_stq_order_send_unconditional_with_exp(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        pgsql,
        sent_time_one,
        sent_time_two,
):
    events = load_json('events_stq_unconditional_create.json')
    assert len(events['events']) == 1
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='create_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 1
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == sent_time_one
    assert tasks[0][1] is False
    check_creation_reasons(tasks[0][2])

    mocked_time.sleep(600)

    events = load_json('events_stq_unconditional_departure.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='departure_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 2

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == sent_time_two
    assert tasks[0][1] is False
    check_creation_reasons(tasks[0][2])

    events = load_json('events_stq_unconditional_cancel.json')
    assert len(events['events']) == 1

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )
    assert response.status == 204

    assert stq.eats_order_send_scheduler.times_called == 1
    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='cancel_token', kwargs=stq_task['kwargs'],
    )
    mocked_time.sleep(1)
    assert stq.eats_order_send_sender.times_called == 2

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][1] is True
    check_creation_reasons(tasks[0][2])


async def test_stq_order_send_reschedule_on_not_found(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        taxi_config,
        testpoint,
):
    @testpoint('max_count_not_found_reschedule')
    def max_count_not_found_reschedule(data):
        pass

    taxi_config.set_values(
        {
            'EATS_ORDER_SEND_STQ_SETTINGS': {
                'stq_scheduler': {
                    'delay_open': 1000,
                    'delay_retry_lock': 200,
                    'not_found_max_reschedule_count': 1,
                },
                'stq_sender': {'delay_retry_lock': 200},
            },
        },
    )

    events = load_json('events_stq.json')
    mocked_time.set(datetime.datetime(2021, 1, 1, 14, 0))
    await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/event', events,
    )

    stq_task = stq.eats_order_send_scheduler.next_call()
    await stq_runner.eats_order_send_scheduler.call(
        task_id='wrong_task_id',
        reschedule_counter=1,
        kwargs=stq_task['kwargs'],
    )

    assert max_count_not_found_reschedule.times_called == 1


def check_creation_reasons(reasons):
    assert 'events' in reasons
    assert 'features' in reasons
    assert 'max_send_time_feature' in reasons['features']
    feat = reasons['features']['max_send_time_feature']
    assert 'enabled' in feat and 'delta' in feat and 'applied' in feat
    feat = reasons['features']['min_send_time_feature']
    assert 'min_send_time_feature' in reasons['features']
    assert 'enabled' in feat and 'applied' in feat
    assert 'deltas' in reasons
    assert 'delta_preparation_time' in reasons['deltas']
    assert 'delta_departure_time' in reasons['deltas']


def get_sending_tasks(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, is_canceled, reasons,planned_on
        FROM eats_order_send.sending_tasks""",
    )
    return list(cursor)


def add_sending_task_with_history(pgsql, order_id):
    cursor = pgsql['eats_order_send'].cursor()
    reasons = '\'{}\'::json'
    cursor.execute(
        f"""WITH ins_st AS (INSERT INTO eats_order_send.sending_tasks
        (order_id, planned_on, is_canceled, reasons) VALUES
        ({order_id}, 'NOW()', FALSE, {reasons}) RETURNING id)
INSERT INTO eats_order_send.sending_history (task_id, sent_at, created_at)
SELECT id, NOW(), NOW() FROM ins_st;""",
    )
