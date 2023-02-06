from . import consts
from . import helpers
from . import models

CREATE_OPERATION_ID = f'{consts.OPERATION_CREATE}:{consts.OPERATION_ID}'

DEFAULT_OPERATION = helpers.make_operation(
    id=CREATE_OPERATION_ID, status='processing',
)


async def test_tracking_update(
        run_user_actions_callback,
        grocery_orders,
        transactions,
        grocery_payments_tracking,
):
    redirect_url = 'some_url'
    operation_id = CREATE_OPERATION_ID

    transaction = helpers.make_transaction(
        payment_type=models.PaymentType.card.value,
        operation_id=operation_id,
        status='hold_pending',
    )

    transaction['3ds'] = {'redirect_url': redirect_url, 'status': 'status'}

    grocery_payments_tracking.update.check(
        order_id=consts.ORDER_ID,
        payload={'type': 'card', 'redirect_url': redirect_url},
    )

    transactions.retrieve.mock_response(
        operations=[DEFAULT_OPERATION], transactions=[transaction],
    )

    await run_user_actions_callback(
        operation_id=operation_id,
        notification_type=consts.X3DS_NOTIFICATION_TYPE,
    )

    assert grocery_payments_tracking.update.times_called == 1
