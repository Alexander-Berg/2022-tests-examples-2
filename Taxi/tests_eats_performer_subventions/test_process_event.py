import pytest

STQ_SETTINGS = {'retries_timeout': 100, 'retries_count': 20}


@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_STQ_PROCESS_EVENT_RETRIES_SETTINGS=STQ_SETTINGS,
)
async def test_stq_order_events_created(stq_runner, db_select_orders):
    order_nr = 'order-nr'
    order_status = 'created'
    payment_type = 'payment-type'
    event = {
        'order_nr': order_nr,
        'order_status': order_status,
        'payment_type': payment_type,
    }

    await stq_runner.eats_performer_subventions_order_events.call(
        task_id='unique',
        kwargs={
            'order_nr': event['order_nr'],
            'order_status': event['order_status'],
            'payment_type': event['payment_type'],
        },
    )

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == 'created'
    assert order['payment_type'] == payment_type


@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_STQ_PROCESS_EVENT_RETRIES_SETTINGS=STQ_SETTINGS,
)
async def test_stq_order_client_events_wrong_event_order(
        stq_runner, db_select_orders,
):
    order_nr = 'order-nr'
    start_status = 'created'
    finish_status = 'finished'
    payment_type = 'payment-type'
    start_event = {
        'order_nr': order_nr,
        'order_status': start_status,
        'payment_type': payment_type,
    }
    finish_event = {
        'order_nr': order_nr,
        'order_status': finish_status,
        'payment_type': payment_type,
    }

    await stq_runner.eats_performer_subventions_order_events.call(
        task_id='unique',
        kwargs={
            'order_nr': finish_event['order_nr'],
            'order_status': finish_event['order_status'],
            'payment_type': finish_event['payment_type'],
        },
    )

    await stq_runner.eats_performer_subventions_order_events.call(
        task_id='unique',
        kwargs={
            'order_nr': start_event['order_nr'],
            'order_status': start_event['order_status'],
            'payment_type': start_event['payment_type'],
        },
    )

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == 'complete'
    assert order['payment_type'] == payment_type


@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_STQ_PROCESS_EVENT_RETRIES_SETTINGS=STQ_SETTINGS,
)
async def test_stq_order_events_changed(stq_runner, db_select_orders):
    order_nr = 'order-nr'
    start_status = 'created'
    finish_status = 'finished'
    payment_type = 'payment-type'
    start_event = {
        'order_nr': order_nr,
        'order_status': start_status,
        'payment_type': payment_type,
    }
    finish_event = {
        'order_nr': order_nr,
        'order_status': finish_status,
        'payment_type': payment_type,
    }

    await stq_runner.eats_performer_subventions_order_events.call(
        task_id='unique',
        kwargs={
            'order_nr': start_event['order_nr'],
            'order_status': start_event['order_status'],
            'payment_type': start_event['payment_type'],
        },
    )

    await stq_runner.eats_performer_subventions_order_events.call(
        task_id='unique',
        kwargs={
            'order_nr': finish_event['order_nr'],
            'order_status': finish_event['order_status'],
            'payment_type': finish_event['payment_type'],
        },
    )

    order = db_select_orders()[0]
    assert order['eats_id'] == order_nr
    assert order['order_status'] == 'complete'
    assert order['payment_type'] == payment_type
