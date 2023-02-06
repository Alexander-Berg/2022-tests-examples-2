import datetime
import json

import pytest


@pytest.mark.parametrize(
    'n_core, n_service',
    [
        pytest.param(
            0,
            1,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_use_eats_order_integration.json',
                ),
            ),
        ),
        pytest.param(
            1,
            0,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_not_use_eats_order_integration.json',
                ),
            ),
        ),
    ],
)
async def test_send_order(
        stq_runner,
        stq,
        pgsql,
        load_json,
        mock_core_send_to_place,
        n_core,
        n_service,
):
    order_nr = '1'
    add_data_in_db(pgsql, load_json, order_nr, 'payload.json', False)
    mock_send_order = mock_core_send_to_place(
        order_nr=order_nr, sync=False, idempotency_key=order_nr,
    )
    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr},
    )
    assert stq.eats_order_integration_send_order.times_called == n_service
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1
    assert mock_send_order.times_called == n_core


@pytest.mark.parametrize(
    'n_core, n_service',
    [
        pytest.param(
            0,
            1,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_use_eats_order_integration.json',
                ),
            ),
        ),
        pytest.param(
            1,
            0,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_not_use_eats_order_integration.json',
                ),
            ),
        ),
    ],
)
async def test_cancel_order(
        stq_runner, stq, pgsql, load_json, mock_core_cancel, n_core, n_service,
):
    order_nr = '1'
    add_data_in_db(pgsql, load_json, order_nr, 'payload.json', True)
    mock_cancel_order = mock_core_cancel(order_id=order_nr)
    await stq_runner.eats_order_send_sender.call(
        task_id=order_nr, kwargs={'order_id': order_nr, 'is_cancel': True},
    )
    assert stq.eats_order_integration_cancel_order.times_called == n_service
    sending_history_list = get_sending_history(pgsql)
    assert not sending_history_list
    assert mock_cancel_order.times_called == n_core


@pytest.mark.parametrize(
    'n_core, n_service',
    [
        pytest.param(
            0,
            1,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_use_eats_order_integration.json',
                ),
            ),
        ),
        pytest.param(
            1,
            0,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_not_use_eats_order_integration.json',
                ),
            ),
        ),
    ],
)
async def test_send_immediately(
        taxi_eats_order_send,
        stq,
        pgsql,
        load_json,
        mock_core_send_to_place,
        n_core,
        n_service,
):
    order_nr = '1'
    add_event(
        pgsql, order_nr, datetime.datetime.now(), load_json('payload.json'),
    )
    mock_send_order = mock_core_send_to_place(
        order_nr=order_nr, sync=True, idempotency_key=order_nr,
    )
    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=1',
        headers={'X-Idempotency-Token': 'x_idempotency_token'},
    )
    assert response.status == 204
    assert stq.eats_order_integration_send_order.times_called == n_service
    sending_history_list = get_sending_history(pgsql)
    assert len(sending_history_list) == 1
    assert mock_send_order.times_called == n_core


def add_data_in_db(pgsql, load_json, order_id, file, is_canceled):
    payload = load_json(file)
    add_event(pgsql, order_id, datetime.datetime(2021, 2, 1, 14, 00), payload)
    add_sending_task(
        pgsql, order_id, datetime.datetime(2021, 2, 1, 15, 00), is_canceled,
    )


def get_sending_history(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT sent_at, task_id
        FROM eats_order_send.sending_history""",
    )
    return list(cursor)


def add_event(pgsql, order_id, created_at, payload):
    cursor = pgsql['eats_order_send'].cursor()
    idempotency = 'create_order_{}'.format(order_id)
    insert_event = """INSERT INTO eats_order_send.events
    (order_id, type, created_at, idempotency_token, payload)
    VALUES (%s, %s, %s, %s, %s);"""
    cursor.execute(
        insert_event,
        [
            order_id,
            'create_order',
            created_at,
            idempotency,
            json.dumps(payload),
        ],
    )


def add_sending_task(pgsql, order_id, planned_on, is_canceled):
    cursor = pgsql['eats_order_send'].cursor()
    insert_task = """INSERT INTO eats_order_send.sending_tasks
        (order_id, planned_on, reasons, is_canceled)
        VALUES (%s, %s, %s, %s)"""
    cursor.execute(insert_task, [order_id, planned_on, '{}', is_canceled])
