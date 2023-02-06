import typing

import pytest

from . import balance_client_id
from . import consts
from . import models

COUNTRY = models.Country.Russia

ITEM = models.Item(item_id='item-1', price='1', quantity='2')
CASHBACK_ITEM = models.Item(item_id='item-1', price='149', quantity='2')

CARD_SUM_TO_PAY = {
    'items': models.to_operation_items([ITEM]),
    'payment_type': 'card',
}

CASHBACK_SUM_TO_PAY = {
    'items': models.to_operation_items([CASHBACK_ITEM]),
    'payment_type': models.PaymentType.personal_wallet.value,
}


@pytest.fixture
def _run_stq(run_transactions_callback):
    async def _do(notification_type=consts.OPERATION_FINISH):
        await run_transactions_callback(
            notification_type=notification_type, transactions=[],
        )

    return _do


@balance_client_id.CONFIG
@pytest.mark.now(consts.NOW)
async def test_event_after_operation_finish(
        transactions,
        grocery_orders,
        check_eats_billing_callback_event,
        _run_stq,
):
    transactions.retrieve.mock_response(
        currency=COUNTRY.currency,
        sum_to_pay=[CARD_SUM_TO_PAY, CASHBACK_SUM_TO_PAY],
    )

    await _run_stq()

    check_eats_billing_callback_event(
        currency=COUNTRY.currency,
        event_at=consts.NOW,
        items=_items_to_eda_items([CASHBACK_ITEM], grocery_orders.order),
        order_id=consts.ORDER_ID,
        payment_type=models.PaymentType.personal_wallet.value,
        transaction_type='total',
    )


@balance_client_id.CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'notification_type, times_called',
    [(consts.OPERATION_FINISH, 1), (consts.TRANSACTION_CLEAR, 0)],
)
async def test_only_operation_finish(
        transactions,
        grocery_orders,
        check_eats_billing_callback_event,
        _run_stq,
        notification_type,
        times_called,
):
    transactions.retrieve.mock_response(
        currency=COUNTRY.currency,
        sum_to_pay=[CARD_SUM_TO_PAY, CASHBACK_SUM_TO_PAY],
    )

    transactions.retrieve.mock_response(
        sum_to_pay=[CARD_SUM_TO_PAY, CASHBACK_SUM_TO_PAY],
    )

    await _run_stq(notification_type=notification_type)

    check_eats_billing_callback_event(times_called=times_called)


@balance_client_id.CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'has_cashback_to_pay, times_called', [(True, 1), (False, 0)],
)
async def test_has_cashback_to_pay(
        transactions,
        grocery_orders,
        check_eats_billing_callback_event,
        _run_stq,
        has_cashback_to_pay,
        times_called,
):
    sum_to_pay = [CARD_SUM_TO_PAY]
    if has_cashback_to_pay:
        sum_to_pay.append(CASHBACK_SUM_TO_PAY)

    transactions.retrieve.mock_response(sum_to_pay=sum_to_pay)

    await _run_stq(notification_type=consts.OPERATION_FINISH)

    check_eats_billing_callback_event(times_called=times_called)


@balance_client_id.CONFIG
@pytest.mark.now(consts.NOW)
async def test_send_zero_items(
        transactions,
        grocery_orders,
        check_eats_billing_callback_event,
        _run_stq,
):
    cashback_items = [
        models.Item(item_id='item-1', price='123', quantity='3'),
        models.Item(item_id='item-2', price='0', quantity='3'),
        models.Item(item_id='item-2', price='10', quantity='0'),
    ]

    cashback_to_pay = {
        'items': models.to_operation_items(cashback_items),
        'payment_type': models.PaymentType.personal_wallet.value,
    }

    transactions.retrieve.mock_response(
        sum_to_pay=[CARD_SUM_TO_PAY, cashback_to_pay],
    )

    await _run_stq(notification_type=consts.OPERATION_FINISH)

    check_eats_billing_callback_event(
        items=_items_to_eda_items(cashback_items, grocery_orders.order),
    )


def _items_to_eda_items(items: typing.List[models.Item], order):
    result = []
    for item in models.to_sub_items(items):
        result.append(
            {
                'amount': item.amount,
                'balance_client_id': balance_client_id.MAPPING[COUNTRY],
                'item_id': item.item_id,
                'item_type': 'product',
                'place_id': order['depot']['id'],
            },
        )
    return result


def _operation_id(operation_type):
    return f'{operation_type}:123'
