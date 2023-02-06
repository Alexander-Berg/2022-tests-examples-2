import datetime

import pytest

from . import consts
from . import helpers
from . import models
from .plugins import configs

ITEMS = [models.Item(item_id='444', quantity='1', price='300')]


@pytest.mark.parametrize(
    'clear_status, times_called',
    [(consts.CLEAR_SUCCESS, 1), (consts.CLEAR_FAILED, 0)],
)
@pytest.mark.now(consts.NOW)
async def test_notification_after_clear(
        grocery_orders,
        grocery_payments_configs,
        transactions,
        run_transactions_callback,
        check_cashback_stq_event,
        check_grocery_cashback_reward_stq_event,
        clear_status,
        times_called,
):
    transactions.retrieve.mock_response(
        status='cleared',
        transactions=[helpers.make_transaction(status=clear_status)],
    )

    await run_transactions_callback(
        notification_type=consts.TRANSACTION_CLEAR,
        transactions=[
            {
                'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
                'payment_type': 'card',
                'status': clear_status,
            },
        ],
    )

    if times_called == 0:
        check_cashback_stq_event(times_called=times_called)
    else:
        delay = consts.NOW_DT + datetime.timedelta(
            seconds=configs.CASHBACK_EVENT_DELAY_SECONDS,
        )
        check_cashback_stq_event(
            times_called=times_called,
            stq_event_id=f'{consts.SERVICE}_{consts.ORDER_ID}',
            order_id=consts.ORDER_ID,
            service=consts.SERVICE,
            eta=delay,
        )

        check_grocery_cashback_reward_stq_event(
            times_called=times_called,
            stq_event_id=f'{consts.SERVICE}_{consts.ORDER_ID}',
            order_id=consts.ORDER_ID,
        )


@pytest.mark.parametrize(
    'operation_type, times_called',
    [('create', 0), ('update', 0), ('cancel', 0), ('refund', 1)],
)
async def test_notification_after_refund(
        grocery_orders,
        transactions,
        run_transactions_callback,
        check_cashback_stq_event,
        operation_type,
        times_called,
):
    refund = helpers.make_refund(
        operation_id=_operation_id('refund'),
        status='refund_success',
        sum=models.to_transaction_items(ITEMS),
    )

    transactions.retrieve.mock_response(
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=consts.CLEAR_SUCCESS, refunds=[refund],
            ),
        ],
    )

    await run_transactions_callback(
        operation_id=_operation_id(operation_type),
        notification_type=consts.OPERATION_FINISH,
        transactions=[],
        operation_status='done',
    )

    check_cashback_stq_event(times_called=times_called)


@pytest.mark.parametrize(
    'operation_status, times_called',
    [(consts.OPERATION_DONE, 1), (consts.OPERATION_FAILED, 0)],
)
async def test_only_successful_refunds(
        grocery_orders,
        transactions,
        run_transactions_callback,
        check_cashback_stq_event,
        operation_status,
        times_called,
):
    refund = helpers.make_refund(
        operation_id=_operation_id('refund'),
        sum=models.to_transaction_items(ITEMS),
    )

    transactions.retrieve.mock_response(
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=consts.CLEAR_SUCCESS, refunds=[refund],
            ),
        ],
    )

    await run_transactions_callback(
        operation_id=_operation_id('refund'),
        notification_type=consts.OPERATION_FINISH,
        transactions=[],
        operation_status=operation_status,
    )

    check_cashback_stq_event(times_called=times_called)


@pytest.mark.parametrize('service_name', ['grocery', 'grocery_v2'])
async def test_order_calculator_service_name(
        grocery_orders,
        transactions,
        run_transactions_callback,
        check_cashback_stq_event,
        experiments3,
        service_name,
):
    experiments3.add_config(
        name='grocery_order_cashback_service',
        consumers=['grocery-payments'],
        default_value={'service': service_name},
    )

    transactions.retrieve.mock_response(
        status='cleared',
        transactions=[helpers.make_transaction(status=consts.CLEAR_SUCCESS)],
    )

    await run_transactions_callback(
        notification_type=consts.TRANSACTION_CLEAR,
        transactions=[
            {
                'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
                'payment_type': 'card',
                'status': consts.CLEAR_SUCCESS,
            },
        ],
    )

    check_cashback_stq_event(
        times_called=1,
        stq_event_id=f'{service_name}_{consts.ORDER_ID}',
        order_id=consts.ORDER_ID,
        service=service_name,
    )


def _operation_id(operation_type):
    return f'{operation_type}:123'
