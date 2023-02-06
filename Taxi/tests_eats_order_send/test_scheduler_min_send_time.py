import datetime

import pytest


@pytest.mark.parametrize(
    ['send_time', 'events_file'],
    [
        pytest.param(
            datetime.datetime(
                2021,
                1,
                8,
                21,
                30,
                0,
                10000,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)),
            ),
            'min_send_time_feature/events_time_not_set.json',
            marks=(
                pytest.mark.experiments3(
                    filename='min_send_time_feature/exp3_enabled.json',
                ),
            ),
            id='Time not set, exp enabled',
        ),
        pytest.param(
            datetime.datetime(
                2021,
                1,
                8,
                21,
                30,
                0,
                10000,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)),
            ),
            'min_send_time_feature/events_time_set.json',
            marks=(
                pytest.mark.experiments3(
                    filename='min_send_time_feature/exp3_disabled.json',
                ),
            ),
            id='Time set, exp disabled',
        ),
        pytest.param(
            datetime.datetime(
                2021,
                1,
                8,
                21,
                40,
                0,
                10000,
                tzinfo=datetime.timezone(datetime.timedelta(seconds=10800)),
            ),
            'min_send_time_feature/events_time_set.json',
            marks=(
                pytest.mark.experiments3(
                    filename='min_send_time_feature/exp3_enabled.json',
                ),
            ),
            id='Feature active',
        ),
    ],
)
async def test_stq_order_send_min_send_time(
        taxi_eats_order_send,
        stq,
        stq_runner,
        load_json,
        mocked_time,
        pgsql,
        events_file,
        send_time,
):
    events = load_json(events_file)
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
    tasks = get_sending_tasks(pgsql)

    assert tasks[0][3] == send_time
    assert tasks[0][1] is False


def get_sending_tasks(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, is_canceled, reasons, planned_on
        FROM eats_order_send.sending_tasks""",
    )
    return list(cursor)
