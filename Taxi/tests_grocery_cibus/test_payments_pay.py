import datetime

import pytest

from . import consts
from . import models

ITEMS = [models.make_transaction_item('item-1', '100')]
DEAL_PRICE = 100


@pytest.fixture(name='grocery_cibus_pay')
async def _grocery_cibus_pay(taxi_grocery_cibus):
    async def _do(status_code=200, **kwargs):
        body = {
            'invoice_id': consts.ORDER_ID,
            'payment_id': consts.TRANSACTION_ID,
            'token': consts.DEFAULT_TOKEN,
            'items': ITEMS,
            **kwargs,
        }

        response = await taxi_grocery_cibus.post(
            '/cibus/payments/v1/pay', json=body,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


@pytest.fixture(name='testpoint_upsert_transaction')
def _testpoint_upsert_transaction(testpoint):
    @testpoint('upsert_transaction')
    def _inner(_):
        pass

    return _inner


async def test_basic(grocery_cibus_pay, grocery_cibus_db):
    invoice_id = consts.ORDER_ID
    transaction_id = consts.TRANSACTION_ID

    response = await grocery_cibus_pay(
        invoice_id=invoice_id, payment_id=transaction_id,
    )
    assert response == {'status': 'pending'}

    transaction = grocery_cibus_db.load_transaction(invoice_id, transaction_id)
    assert transaction.invoice_id == invoice_id
    assert transaction.transaction_id == transaction_id
    assert transaction.transaction_type == models.TransactionType.payment
    assert transaction.items == ITEMS
    assert transaction.status == models.TransactionStatus.pending
    assert transaction.error_code is None


async def test_second_payment(
        grocery_cibus_pay, grocery_cibus_db, testpoint_upsert_transaction,
):
    transaction = models.Transaction(
        transaction_id='some-another',
        transaction_type=models.TransactionType.payment,
    )
    grocery_cibus_db.insert_transaction(transaction)

    response = await grocery_cibus_pay()
    assert response['status'] == 'fail'
    assert response['error_code'] == 'declined'

    assert testpoint_upsert_transaction.times_called == 0


@pytest.mark.parametrize(
    'status',
    [models.TransactionStatus.success, models.TransactionStatus.fail],
)
@pytest.mark.parametrize('error_code', [None, 'error'])
async def test_terminal_state(
        grocery_cibus_pay, grocery_cibus_db, status, error_code,
):
    transaction = models.Transaction(status=status, error_code=error_code)
    grocery_cibus_db.insert_transaction(transaction)

    response = await grocery_cibus_pay()
    assert response.get('status') == status.value
    assert response.get('error_code') == error_code

    new_transaction = grocery_cibus_db.load_transaction(
        transaction.invoice_id, transaction.transaction_id,
    )
    assert transaction == new_transaction


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('has_payment', [False, True])
async def test_pending_payment(
        grocery_cibus_pay,
        grocery_cibus_db,
        testpoint_upsert_transaction,
        has_payment,
):
    status = models.TransactionStatus.pending
    transaction = models.Transaction(
        transaction_type=models.TransactionType.payment, status=status,
    )
    grocery_cibus_db.insert_transaction(transaction)

    if has_payment:
        payment = models.Payment(status=models.PaymentStatus.init)
        grocery_cibus_db.insert_payment(payment)

    response = await grocery_cibus_pay()
    assert response['status'] == status.value
    assert testpoint_upsert_transaction.times_called == 0


@pytest.mark.now(consts.NOW)
async def test_pending_payment_timeout(
        grocery_cibus_pay,
        grocery_cibus_db,
        grocery_cibus_configs,
        testpoint_upsert_transaction,
):
    timeout = 30
    grocery_cibus_configs.set_payment_timeout(timeout)

    transaction = models.Transaction(
        transaction_type=models.TransactionType.payment,
        status=models.TransactionStatus.pending,
        created=consts.NOW_DT - datetime.timedelta(minutes=timeout),
    )
    grocery_cibus_db.insert_transaction(transaction)

    response = await grocery_cibus_pay()
    assert response['status'] == 'fail'
    assert response['error_code'] == 'payment_timeout'
    assert testpoint_upsert_transaction.times_called == 1


@pytest.mark.parametrize(
    'payment_extra, expected_response',
    [
        (dict(status=models.PaymentStatus.success), dict(status='success')),
        (
            dict(
                status=models.PaymentStatus.success, deal_price=DEAL_PRICE + 1,
            ),
            dict(status='fail', error_code=consts.ERROR_LOGIC),
        ),
        (
            dict(status=models.PaymentStatus.canceled),
            dict(status='fail', error_code='payment_canceled'),
        ),
        (
            dict(status=models.PaymentStatus.fail),
            dict(status='fail', error_code='declined'),
        ),
        (
            dict(
                status=models.PaymentStatus.fail,
                error_code='budget_limit',
                error_desc='budget_limit extended',
            ),
            dict(
                status='fail',
                error_code='budget_limit',
                error_desc='budget_limit extended',
            ),
        ),
    ],
)
async def test_payment_status(
        grocery_cibus_pay,
        grocery_cibus_db,
        testpoint_upsert_transaction,
        payment_extra,
        expected_response,
):
    payment_extra = {'deal_price': DEAL_PRICE, **payment_extra}

    payment = models.Payment(**payment_extra)
    grocery_cibus_db.insert_payment(payment)

    response = await grocery_cibus_pay()
    assert response == expected_response
    assert testpoint_upsert_transaction.times_called == 1
