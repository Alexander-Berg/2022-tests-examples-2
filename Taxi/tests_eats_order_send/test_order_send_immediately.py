# flake8: noqa
# pylint: disable=import-error,wildcard-import


async def test_order_send_immediately_post(
        taxi_eats_order_send, pgsql, mock_core_send_to_place,
):
    mock_core_send_to_place(order_nr='777', sync=True, idempotency_key='1')
    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=777',
        headers={'X-Idempotency-Token': 'x_idempotency_token'},
    )
    assert response.status == 204
    check_database_data(pgsql)


async def test_order_send_immediately_post_idempotency(
        taxi_eats_order_send, pgsql, mock_core_send_to_place,
):
    mock_core_send_to_place(order_nr='777', sync=True, idempotency_key='1')
    # first request
    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=777',
        headers={'X-Idempotency-Token': 'x_idempotency_token'},
    )
    assert response.status == 204
    check_database_data(pgsql)

    # second request with the same idempotency token and the same order
    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=777',
        headers={'X-Idempotency-Token': 'x_idempotency_token'},
    )
    assert response.status == 204
    check_database_data(pgsql)

    # third request with the same idempotency token and other order
    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=999',
        headers={'X-Idempotency-Token': 'x_idempotency_token'},
    )
    assert response.status == 400
    check_database_data(pgsql)


async def test_order_send_immediately_post_repeat(
        taxi_eats_order_send, pgsql, add_sending, mock_core_send_to_place,
):
    mock_core_send_to_place(order_nr='777', sync=True, idempotency_key='2')

    # fill sending tables
    add_sending(True, SENDING_TASK)

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=777',
        headers={'X-Idempotency-Token': 'x_idempotency_token_new'},
    )
    assert response.status == 204

    # check_data
    assert get_events(pgsql) == [
        (
            '777',
            'send_immediately',
            'x_idempotency_token_new',
            {'event_type': 'send_immediately'},
        ),
    ]
    assert get_sending_tasks(pgsql) == [
        ('777', False, {'events': ['x_idempotency_token']}),
        ('777', False, {'events': ['x_idempotency_token_new']}),
    ]
    assert get_sending_history(pgsql) == [(1,), (2,)]


async def test_order_send_immediately_post_canceled(
        taxi_eats_order_send, pgsql, add_sending, mock_core_send_to_place,
):
    mock_core_send_to_place(order_nr='777', sync=True, idempotency_key='2')

    # fill sending tables
    add_sending(False, SENDING_TASK)

    response = await taxi_eats_order_send.post(
        '/internal/eats-order-send/v1/order/send-immediately?order_id=777',
        headers={'X-Idempotency-Token': 'x_idempotency_token_new'},
    )
    assert response.status == 204

    # check_data
    assert get_events(pgsql) == [
        (
            '777',
            'send_immediately',
            'x_idempotency_token_new',
            {'event_type': 'send_immediately'},
        ),
    ]
    assert get_sending_tasks(pgsql) == [
        ('777', True, {'events': ['x_idempotency_token']}),
        ('777', False, {'events': ['x_idempotency_token_new']}),
    ]
    assert get_sending_history(pgsql) == [(2,)]


def check_database_data(pgsql):
    assert get_events(pgsql) == [
        (
            '777',
            'send_immediately',
            'x_idempotency_token',
            {'event_type': 'send_immediately'},
        ),
    ]
    assert get_sending_tasks(pgsql) == [
        ('777', False, {'events': ['x_idempotency_token']}),
    ]
    assert get_sending_history(pgsql) == [(1,)]


SENDING_TASK = {
    'order_id': '777',
    'created_at': '2021-01-01T15:30:27.01+00:00',
    'planned_on': '2021-01-01T17:30:27.01+00:00',
    'sent_at': '2021-01-01T17:33:27.01+00:00',
    'is_canceled': False,
    'reasons': {'events': ['x_idempotency_token']},
}


def get_events(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, type, idempotency_token, payload
        FROM eats_order_send.events""",
    )
    return list(cursor)


def get_sending_tasks(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT order_id, is_canceled, reasons
        FROM eats_order_send.sending_tasks""",
    )
    return list(cursor)


def get_sending_history(pgsql):
    cursor = pgsql['eats_order_send'].cursor()
    cursor.execute(
        """SELECT task_id
        FROM eats_order_send.sending_history""",
    )
    return list(cursor)
