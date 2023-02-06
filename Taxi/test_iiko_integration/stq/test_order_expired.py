import pytest

from iiko_integration.stq import order_expired


@pytest.mark.parametrize(
    'kwargs, exp_status',
    [
        pytest.param({'invoice_id': 'invoice_01'}, 'EXPIRED', id='expired'),
        pytest.param(
            {'invoice_id': 'invoice_02'}, 'PAYMENT_CONFIRMED', id='skip',
        ),
        pytest.param(
            {
                'order_id': '01',
                'restaurant_status': 'WAITING_FOR_CONFIRMATION',
                'invoice_status': 'HELD',
            },
            'EXPIRED',
            id='expired with status',
        ),
        pytest.param(
            {
                'order_id': '02',
                'restaurant_status': 'WAITING_FOR_CONFIRMATION',
                'invoice_status': 'CLEARED',
            },
            'PAYMENT_CONFIRMED',
            id='skip with status',
        ),
        pytest.param(
            {
                'order_id': '03',
                'restaurant_status': 'PENDING',
                'invoice_status': 'INIT',
            },
            'EXPIRED',
            id='expired pending',
        ),
        pytest.param(
            {
                'order_id': '04',
                'restaurant_status': 'PENDING',
                'invoice_status': 'INIT',
            },
            'PENDING',
            id='invoice status changed',
        ),
    ],
)
async def test_stq_order_expired(stq3_context, mockserver, kwargs, exp_status):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        assert queue_name == 'payments_eda_cancel_order'

    await order_expired.task(context=stq3_context, **kwargs)

    order_id = kwargs.get('order_id')
    invoice_id = kwargs.get('invoice_id')

    if order_id:
        order_cor = stq3_context.order_manager.get_order(order_id)
    elif invoice_id:
        order_cor = stq3_context.order_manager.get_order_by_invoice(
            invoice_id=invoice_id,
        )
    else:
        assert False

    order = await order_cor

    assert order.status.restaurant_status.value == exp_status
