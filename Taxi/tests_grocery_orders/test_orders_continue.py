import pytest

from . import models


POSTPONED_FLOW = 'postponed_order_no_payment_flow_v1'


@pytest.mark.parametrize(
    'status',
    [
        'postponed',
        'assembling',
        'assembled',
        'delivering',
        'closed',
        'pending_cancel',
        'canceled',
    ],
)
async def test_200(taxi_grocery_orders, pgsql, processing, status):
    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    idempotency_token = 'idempotency_token'

    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=models.OrderState(wms_reserve_status='success'),
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        timeslot_request_kind=timeslot_request_kind,
        grocery_flow_version=POSTPONED_FLOW,
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/continue',
        json={
            'order_id': order.order_id,
            'request_source': 'grocery_dispatch',
        },
        headers={'X-Idempotency-Token': idempotency_token},
    )

    assert response.status_code == 200

    events = list(processing.events(scope='grocery', queue='processing'))

    if status == 'postponed':
        assert len(events) == 1
        assert events[0].payload == {
            'flow_version': POSTPONED_FLOW,
            'order_id': order.order_id,
            'order_version': 0,
            'reason': 'assemble_ready',
        }
    else:
        assert events == []


@pytest.mark.parametrize(
    'status', ['checked_out', 'draft', 'reserving', 'reserved'],
)
async def test_400(taxi_grocery_orders, pgsql, processing, status):
    timeslot_start = '2020-03-13T09:50:00+00:00'
    timeslot_end = '2020-03-13T17:50:00+00:00'
    timeslot_request_kind = 'wide_slot'

    idempotency_token = 'idempotency_token'

    order = models.Order(
        pgsql=pgsql,
        status=status,
        state=models.OrderState(wms_reserve_status='success'),
        timeslot_start=timeslot_start,
        timeslot_end=timeslot_end,
        timeslot_request_kind=timeslot_request_kind,
        grocery_flow_version=POSTPONED_FLOW,
    )

    response = await taxi_grocery_orders.post(
        '/internal/v1/orders/v1/continue',
        json={
            'order_id': order.order_id,
            'request_source': 'grocery_dispatch',
        },
        headers={'X-Idempotency-Token': idempotency_token},
    )

    assert response.status_code == 400

    events = list(processing.events(scope='grocery', queue='processing'))
    assert events == []
