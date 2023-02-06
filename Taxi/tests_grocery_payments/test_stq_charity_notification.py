import pytest

from . import consts
from . import helpers
from . import models

INVOICE_ID = models.InvoiceOriginator.helping_hand.prefix + consts.ORDER_ID


@pytest.mark.parametrize(
    'notification_type, operation_id, hh_operation, overload_sum_to_pay',
    [
        (consts.TRANSACTION_CLEAR, 'update:123', 'clear', None),
        (consts.OPERATION_FINISH, 'create:123', 'hold', None),
        (consts.OPERATION_FINISH, 'cancel:123', 'cancel', []),
        (consts.OPERATION_FINISH, f'{consts.DEBT_PREFIX}/1/1', 'hold', None),
        (consts.OPERATION_FINISH, f'{consts.DEBT_PREFIX}/1/2', 'cancel', []),
    ],
)
@pytest.mark.parametrize(
    'operation_status, hh_status',
    [(consts.OPERATION_DONE, 'success'), (consts.OPERATION_FAILED, 'failure')],
)
async def test_stq_callback_helping_hand(
        grocery_orders,
        transactions,
        run_transactions_callback,
        stq,
        notification_type,
        operation_id,
        operation_status,
        overload_sum_to_pay,
        hh_operation,
        hh_status,
):
    operation = helpers.make_operation(
        id=operation_id, status=operation_status,
    )
    if overload_sum_to_pay is not None:
        operation.update(sum_to_pay=overload_sum_to_pay)

    transactions.retrieve.mock_response(operations=[operation])

    await run_transactions_callback(
        invoice_id=INVOICE_ID,
        notification_type=notification_type,
        operation_id=operation_id,
        operation_status=operation_status,
    )

    assert stq.persey_payments_grocery_callback.times_called == 1

    args = stq.persey_payments_grocery_callback.next_call()
    _check_task_args(args, hh_operation, hh_status)


def _check_task_args(args, operation, status):
    assert args['id'] == f'{consts.ORDER_ID}-{operation}-{status}'

    kwargs = args['kwargs']
    kwargs.pop('log_extra')
    assert kwargs == {
        'order_id': consts.ORDER_ID,
        'operation': operation,
        'status': status,
    }
