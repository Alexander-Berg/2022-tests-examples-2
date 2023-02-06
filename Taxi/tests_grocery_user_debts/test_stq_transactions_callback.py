# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error

import datetime

from grocery_payments_shared import transactions as transactions_lib
import pytest

from . import consts
from . import models

TASK_ID = 'task_id'
PAYMENT_TYPE = 'card'
WALLET_PAYMENT_TYPE = 'personal_wallet'

CURRENCY = 'RUB'


AMOUNT_ITEM1 = 10
AMOUNT_ITEM2 = 20


@pytest.fixture
def _transactions(transactions):
    transactions.retrieve.mock_response(
        operations=[
            transactions_lib.make_operation(
                id=consts.DEBT_OPERATION_ID,
                sum_to_pay=[
                    {
                        'items': [
                            {
                                'amount': str(AMOUNT_ITEM1),
                                'item_id': 'item_id1',
                            },
                            {
                                'amount': str(AMOUNT_ITEM2),
                                'item_id': 'item_id2',
                            },
                        ],
                        'payment_type': 'card',
                    },
                ],
            ),
        ],
        transactions=[
            transactions_lib.make_transaction(
                operation_id=consts.DEBT_OPERATION_ID,
                status='hold_success',
                payment_type='card',
                sum=[
                    {'item_id': 'item_id1', 'amount': str(AMOUNT_ITEM1)},
                    {'item_id': 'item_id2', 'amount': str(AMOUNT_ITEM2)},
                ],
                held=consts.NOW,
            ),
        ],
        currency=CURRENCY,
    )


@pytest.mark.parametrize('transaction_status', ['clear_success', 'clear_fail'])
async def test_clear(
        run_transactions_callback,
        check_grocery_payments_transactions_callback,
        transaction_status,
        default_debt,
):
    task_kwargs = dict(
        task_id=TASK_ID,
        notification_type='transaction_clear',
        transactions=[_make_stq_transaction(transaction_status)],
    )

    await run_transactions_callback(**task_kwargs)

    check_grocery_payments_transactions_callback(**task_kwargs)


async def test_hold_success(
        run_transactions_callback,
        check_grocery_payments_transactions_callback,
        grocery_orders,
        processing,
        default_debt,
        _transactions,
):
    task_kwargs = dict(
        task_id=TASK_ID,
        notification_type='operation_finish',
        operation_status='done',
    )

    processing.debts.check(
        reason='set-status',
        debt=dict(debt_id=consts.DEBT_ID, status='cleared'),
        order=consts.ORDER_INFO,
        headers={
            'X-Idempotency-Token': (
                'set-status:cleared:' + consts.DEBT_OPERATION_ID
            ),
        },
    )

    await run_transactions_callback(**task_kwargs)

    check_grocery_payments_transactions_callback(**task_kwargs)


async def test_hold_fail(
        run_transactions_callback,
        check_grocery_payments_transactions_callback,
        grocery_orders,
        processing,
        transactions,
        default_debt,
):
    error_reason_code = 'error_reason_code'

    transactions.retrieve.mock_response(
        operations=[
            transactions_lib.make_operation(id='create'),
            transactions_lib.make_operation(
                id=consts.DEBT_OPERATION_ID + '/prev',
            ),
            transactions_lib.make_operation(
                id=consts.DEBT_OPERATION_ID,
                status='failed',
                sum_to_pay=[
                    dict(items=[], payment_type=WALLET_PAYMENT_TYPE),
                    dict(items=[], payment_type=PAYMENT_TYPE),
                ],
            ),
        ],
        transactions=[
            transactions_lib.make_transaction(
                operation_id=consts.DEBT_OPERATION_ID,
                status='hold_fail',
                payment_type=PAYMENT_TYPE,
                error_reason_code=error_reason_code,
            ),
            transactions_lib.make_transaction(
                operation_id=consts.DEBT_OPERATION_ID,
                status='hold_success',
                payment_type=WALLET_PAYMENT_TYPE,
                error_reason_code=error_reason_code,
            ),
        ],
    )

    attempt = 2
    debt_reason = models.debt_reason(
        payment_type=PAYMENT_TYPE,
        composite_payment_type=WALLET_PAYMENT_TYPE,
        error_reason_code=error_reason_code,
        is_technical_error=False,
        attempt=attempt,
    )

    processing.debts.check(
        reason='clear',
        debt=dict(
            debt_id=consts.DEBT_ID,
            idempotency_token=f'clear:{attempt}',
            reason=debt_reason,
            reason_code=f'clear_retry_{attempt}',
        ),
        order=consts.ORDER_INFO,
        headers={'X-Idempotency-Token': f'clear:{attempt}'},
    )

    task_kwargs = dict(
        stq_event_id=TASK_ID,
        notification_type='operation_finish',
        operation_status='failed',
        operation_id=consts.DEBT_OPERATION_ID,
    )

    await run_transactions_callback(**task_kwargs)

    assert processing.debts.times_called == 1
    assert transactions.retrieve.times_called == 1
    check_grocery_payments_transactions_callback(times_called=0)


async def test_debt_not_found(run_transactions_callback):
    await run_transactions_callback(expect_fail=True)


async def test_several_debts(
        run_transactions_callback,
        grocery_user_debts_db,
        grocery_orders,
        processing,
        default_debt,
        _transactions,
):
    grocery_user_debts_db.upsert(
        default_debt.copy(
            debt_id='prev_' + default_debt.debt_id,
            created=default_debt.created - datetime.timedelta(hours=1),
            status='cleared',
        ),
        default_debt.copy(
            debt_id='next_' + default_debt.debt_id,
            created=default_debt.created + datetime.timedelta(hours=1),
            status='init',
        ),
    )

    processing.debts.check(
        debt=dict(debt_id=default_debt.debt_id, status='cleared'),
    )

    await run_transactions_callback()


# Todo: https://st.yandex-team.ru/LAVKABACKEND-9138


@pytest.mark.parametrize('notify', [True, False])
@pytest.mark.config(GROCERY_USER_DEBTS_USER_NOTIFY_DELAY=60)
async def test_user_notification(
        run_transactions_callback,
        grocery_user_debts_configs,
        grocery_orders,
        processing,
        default_debt,
        _transactions,
        notify,
):
    grocery_user_debts_configs.grocery_user_debts_notify_user(enabled=notify)

    grocery_orders.order.update(
        created=consts.NOW,
        finish_started=(
            consts.NOW_DT - datetime.timedelta(hours=2)
        ).isoformat(),
    )
    order = grocery_orders.order

    order_id = order['order_id']

    processing.non_critical.check(
        reason='order_notification',
        order_id=order_id,
        code='debt_hold',
        headers={'X-Idempotency-Token': f'{order_id}-{consts.DEBT_ID}'},
        payload={
            'amount': str(AMOUNT_ITEM1 + AMOUNT_ITEM2),
            'currency': CURRENCY,
        },
    )

    await run_transactions_callback()

    assert processing.non_critical.times_called == int(notify)


def _make_stq_transaction(status):
    return {
        'external_payment_id': transactions_lib.EXTERNAL_PAYMENT_ID,
        'payment_type': PAYMENT_TYPE,
        'status': status,
    }
