import pytest

from eats_corp_orders.stq import payment_callback


@pytest.mark.parametrize(
    'action, status, order_status',
    [
        ('purchase', 'confirmed', 'completed'),
        ('purchase', 'rejected', 'failed'),
    ],
)
async def test_success(
        stq3_context,
        stq,
        order_id,
        mock_eats_payments_py3,
        load_json,
        check_redis_array,
        check_order_status_db,
        terminal_id,
        idempotency_key,
        action,
        status,
        order_status,
):
    @mock_eats_payments_py3('/v1/orders/close')
    async def close_handler(request):
        assert request.json == {'id': order_id}
        return {}

    await payment_callback.task(stq3_context, order_id, action, status)

    check_redis_array(
        f'payment_{terminal_id}_{idempotency_key}',
        load_json(f'{status}.json'),
    )
    check_order_status_db(order_id, order_status)
    assert not stq.eats_corp_orders_nowait_callback.has_calls

    if status == 'confirmed':
        assert close_handler.has_calls
        assert stq.eats_corp_orders_billing_events.has_calls
        assert not stq.eats_corp_orders_cancel.has_calls
    elif status == 'rejected':
        assert not close_handler.has_calls
        assert not stq.eats_corp_orders_billing_events.has_calls
        assert stq.eats_corp_orders_cancel.has_calls


@pytest.mark.config(
    EATS_CORP_ORDERS_PAYMENT_SETTINGS={
        '__default__': {
            'payment_enabled': True,
            'wait_for_payment_result': True,
        },
        'terminal_id': {
            'payment_enabled': True,
            'wait_for_payment_result': True,
            'nowait': True,
        },
    },
)
async def test_nowait(stq3_context, stq, order_id, mock_eats_payments_py3):
    @mock_eats_payments_py3('/v1/orders/close')
    async def _handler(request):
        return {}

    await payment_callback.task(
        stq3_context, order_id, 'purchase', 'confirmed',
    )
    assert stq.eats_corp_orders_nowait_callback.has_calls


@pytest.mark.parametrize(
    'order_id, action, status',
    [
        ('not_existing_order_id', 'purchase', 'confirmed'),
        ('order_id', 'purchase', 'wrong_status'),
    ],
)
async def test_raises_exception(
        stq3_context,
        check_redis_array,
        terminal_id,
        idempotency_key,
        order_id,
        action,
        status,
):
    with pytest.raises(Exception):
        await payment_callback.task(stq3_context, order_id, action, status)

    check_redis_array(f'payment_{terminal_id}_{idempotency_key}', [])


@pytest.mark.parametrize(
    'order_id, action, status', [('order_id', 'not_purchase', 'confirmed')],
)
async def test_exits_if_action_not_purchase(
        stq3_context,
        check_redis_array,
        terminal_id,
        idempotency_key,
        order_id,
        action,
        status,
):
    await payment_callback.task(stq3_context, order_id, action, status)

    check_redis_array(f'payment_{terminal_id}_{idempotency_key}', [])
