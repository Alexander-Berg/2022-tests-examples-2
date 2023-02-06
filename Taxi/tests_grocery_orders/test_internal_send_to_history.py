import pytest

from . import helpers


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize(
    'event,status_change,order_state',
    [
        ('reserving', 'reserving', 'created'),
        ('approving', 'reserved', 'created'),
        ('request', 'assembling', 'assembling'),
        ('processing', 'assembling', 'assembling'),
        ('complete', 'assembling', 'assembling'),
        ('dispatched', 'delivering', 'delivering'),
    ],
)
async def test_send_nonfinal_status(
        taxi_grocery_orders,
        processing,
        grocery_order_log,
        event,
        status_change,
        order_state,
):
    order_id = 'some-id'
    grocery_order_log.set_order_id_response(order_id)
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={'order_id': order_id, 'event': event},
    )

    assert response.status_code == 200

    notification_result = _get_last_processing_events(
        processing, order_id, count=1, queue='processing_non_critical',
    )[0]
    assert notification_result == {
        'order_id': order_id,
        'reason': 'status_change',
        'status_change': status_change,
        'order_log_info': {'order_state': order_state, 'order_type': 'eats'},
    }


@pytest.mark.now('2020-11-12T13:00:50.283761+00:00')
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize(
    'event,status_change,order_state',
    [
        ('arrived', 'closed', 'closed'),
        ('failed', 'canceled', 'canceled'),
        ('canceled', 'canceled', 'canceled'),
    ],
)
async def test_send_final_status(
        taxi_grocery_orders,
        processing,
        grocery_order_log,
        event,
        status_change,
        order_state,
):
    order_id = 'some-id'
    grocery_order_log.set_order_id_response(order_id)
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={'order_id': order_id, 'event': event},
    )

    assert response.status_code == 200

    notification_result = _get_last_processing_events(
        processing, order_id, count=1, queue='processing_non_critical',
    )[0]
    assert notification_result == {
        'order_id': order_id,
        'reason': 'status_change',
        'status_change': status_change,
        'order_log_info': {
            'order_state': order_state,
            'order_type': 'eats',
            'order_finished_date': '2020-11-12T13:00:50.283761+00:00',
        },
    }


@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize(
    'event,eda_event,status_change,order_state',
    [
        ('complete', 'ARRIVED_TO_CUSTOMER', 'delivering', 'delivering'),
        ('complete', 'CUSTOMER_NO_SHOW', 'delivering', 'delivering'),
        ('complete', 'ORDER_TAKEN', 'delivering', 'delivering'),
        ('complete', 'PICKUP', 'delivering', 'delivering'),
    ],
)
async def test_send_eda_nonfinal_status(
        taxi_grocery_orders,
        processing,
        grocery_order_log,
        event,
        eda_event,
        status_change,
        order_state,
):
    order_id = 'some-id'
    grocery_order_log.set_order_id_response(order_id)
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={'order_id': order_id, 'event': event, 'eda_event': eda_event},
    )

    assert response.status_code == 200

    notification_result = _get_last_processing_events(
        processing, order_id, count=1, queue='processing_non_critical',
    )[0]
    assert notification_result == {
        'order_id': order_id,
        'reason': 'status_change',
        'status_change': status_change,
        'order_log_info': {'order_state': order_state, 'order_type': 'eats'},
    }


@pytest.mark.now('2020-11-12T13:00:50.283761+00:00')
@pytest.mark.config(GROCERY_ORDERS_SEND_STATUS_CHANGE_EVENT=True)
@pytest.mark.parametrize(
    'event,eda_event,status_change,order_state',
    [
        ('complete', 'DELIVERED', 'closed', 'closed'),
        ('complete', 'CANCELLED', 'canceled', 'canceled'),
    ],
)
async def test_send_eda_final_status(
        taxi_grocery_orders,
        processing,
        grocery_order_log,
        event,
        eda_event,
        status_change,
        order_state,
):
    order_id = 'some-id'
    grocery_order_log.set_order_id_response(order_id)
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={'order_id': order_id, 'event': event, 'eda_event': eda_event},
    )

    assert response.status_code == 200

    notification_result = _get_last_processing_events(
        processing, order_id, count=1, queue='processing_non_critical',
    )[0]
    assert notification_result == {
        'order_id': order_id,
        'reason': 'status_change',
        'status_change': status_change,
        'order_log_info': {
            'order_state': order_state,
            'order_type': 'eats',
            'order_finished_date': '2020-11-12T13:00:50.283761+00:00',
        },
    }


async def test_not_found(taxi_grocery_orders, processing, grocery_order_log):
    order_id = 'some-id'
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={
            'order_id': order_id,
            'event': 'complete',
            'eda_event': 'DELIVERED',
        },
    )

    assert response.status_code == 404


async def test_bad_request(taxi_grocery_orders, processing, grocery_order_log):
    order_id = 'some-id'
    response = await taxi_grocery_orders.post(
        '/internal/v1/send-to-history',
        json={'order_id': order_id, 'event': {}, 'eda_event': {}},
    )

    assert response.status_code == 400


def _get_last_processing_events(
        processing, order_id, count=1, queue='processing-non-critical',
):
    return helpers.get_last_processing_payloads(
        processing, order_id, queue, count,
    )
