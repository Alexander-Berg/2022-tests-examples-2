import datetime


async def test_stq_eats_order_send_sender(
        stq_runner, mocked_time, pgsql, mock_core_send_to_place,
):
    order_nr = 'some_order_nr'
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 15, 00), False,
    )
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))
    mock_core_send_to_place(
        order_nr=order_nr, sync=False, idempotency_key=order_nr,
    )

    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1


async def test_stq_eats_order_send_sender_canceled(
        stq_runner, mocked_time, pgsql,
):
    add_sending_task(pgsql, '1', datetime.datetime(2021, 2, 1, 15, 00), True)
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))

    await stq_runner.eats_order_send_sender.call(
        task_id='1', kwargs={'order_id': '1'},
    )
    sending_history_list = get_sending_history(pgsql)
    assert not sending_history_list


async def test_stq_eats_order_send_sender_multi(
        stq_runner, mocked_time, pgsql, mock_core_send_to_place,
):
    order_nr = 'some_order_nr'
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 15, 00), True,
    )
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 16, 00), True,
    )
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 17, 00), False,
    )
    mocked_time.set(datetime.datetime(2021, 2, 1, 17, 00))
    mock_core_send_to_place(
        order_nr=order_nr, sync=False, idempotency_key=order_nr,
    )

    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1


async def test_stq_eats_order_send_sender_multi_cancel(
        stq_runner, mocked_time, pgsql,
):
    order_nr = 'some_order_nr'
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 15, 00), True,
    )
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 16, 00), True,
    )
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 17, 00), True,
    )
    mocked_time.set(datetime.datetime(2021, 2, 1, 17, 00))

    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    sending_history_list = get_sending_history(pgsql)
    assert not sending_history_list


async def test_stq_eats_order_send_sender_retry(
        stq_runner, mocked_time, pgsql, mock_core_send_to_place,
):
    order_nr = 'some_order_nr'
    add_sending_task(
        pgsql, order_nr, datetime.datetime(2021, 2, 1, 15, 00), False,
    )
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))
    mock_core_send_to_place(
        order_nr=order_nr, sync=False, idempotency_key=order_nr,
    )

    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1
    mocked_time.sleep(1)
    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1


async def test_stq_full_send(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        pgsql,
        mock_core_send_to_place,
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
    mocked_time.set(datetime.datetime(2021, 2, 1, 19, 00))
    mock_core_send_to_place(order_nr='3', sync=False, idempotency_key='3')
    assert stq.eats_order_send_sender.times_called == 1

    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == datetime.datetime(
        2021, 2, 1, 18, 30, 0, 10000, tzinfo=datetime.timezone.utc,
    )
    assert tasks[0][1] is False

    sender_stq = stq.eats_order_send_sender.next_call()
    assert sender_stq['kwargs']['order_id'] == '3'
    await stq_runner.eats_order_send_sender.call(
        task_id='3', kwargs=sender_stq['kwargs'],
    )
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1


async def test_stq_eats_order_send_sender_cancel(
        stq_runner, mocked_time, pgsql, mock_core_cancel,
):
    order_nr = 'some_order_nr'
    mocked_time.set(datetime.datetime(2021, 2, 1, 15, 00))
    mock_cancel_order = mock_core_cancel(order_id=order_nr)

    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr, 'is_cancel': True},
    )

    assert mock_cancel_order.times_called == 1


def get_sending_tasks(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, is_canceled, reasons,planned_on
        FROM eats_order_send.sending_tasks""",
    )
    return list(cursor)


def get_sending_history(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT sent_at, task_id
        FROM eats_order_send.sending_history""",
    )
    return list(cursor)


def add_sending_task(pgsql, order_id, planned_on, is_canceled):
    cursor = pgsql['eats_order_send'].cursor()
    reasons = '\'{}\'::json'
    cursor.execute(
        f"""INSERT INTO eats_order_send.sending_tasks
        (order_id, planned_on, reasons, is_canceled)
        VALUES ('{order_id}', '{planned_on}', {reasons}, {is_canceled})""",
    )
