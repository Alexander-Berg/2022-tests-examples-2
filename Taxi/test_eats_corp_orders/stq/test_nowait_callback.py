from eats_corp_orders.internal import constants
from eats_corp_orders.stq import nowait_callback


async def test_nowait_callback_terminal(
        stq3_context,
        order_id,
        mock_premium_bonus,
        idempotency_key,
        cancel_token,
):
    @mock_premium_bonus('/v1/payment/cb')
    async def handler(request):
        return {'success': True}

    await nowait_callback.task(
        stq3_context,
        originator=constants.Originator.terminal,
        order_id=order_id,
        idempotency_key=idempotency_key,
        cancel_token=cancel_token,
        status=constants.PaymentStatus.new.value,
    )
    assert handler.has_calls


async def test_nowait_callback_cheque(
        stq3_context,
        order_id,
        mock_premium_bonus,
        idempotency_key,
        cancel_token,
):
    await nowait_callback.task(
        stq3_context,
        originator=constants.Originator.cheque,
        order_id=order_id,
        idempotency_key=idempotency_key,
        cancel_token=cancel_token,
        status=constants.PaymentStatus.new.value,
    )
