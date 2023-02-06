import pytest

from . import consts
from . import models

ITEMS = [models.make_transaction_item('item-1', '100')]
DEAL_PRICE = 100

DEFAULT_PAYMENT = models.Payment(
    status=models.PaymentStatus.success,
    deal_price=DEAL_PRICE,
    deal_id=consts.DEAL_ID,
)


@pytest.fixture(name='grocery_cibus_refund')
async def _grocery_cibus_refund(taxi_grocery_cibus):
    async def _do(status_code=200, **kwargs):
        body = {
            'invoice_id': consts.ORDER_ID,
            'refund_id': consts.TRANSACTION_ID,
            'token': consts.DEFAULT_TOKEN,
            'items': ITEMS,
            **kwargs,
        }

        response = await taxi_grocery_cibus.post(
            '/cibus/payments/v1/refund', json=body,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


async def test_basic(grocery_cibus_refund, grocery_cibus_db, cibus):
    invoice_id = consts.ORDER_ID
    transaction_id = consts.TRANSACTION_ID

    payment = DEFAULT_PAYMENT
    grocery_cibus_db.insert_payment(payment)

    response = await grocery_cibus_refund()
    assert response == {'status': 'success'}

    transaction = grocery_cibus_db.load_transaction(invoice_id, transaction_id)
    assert transaction.invoice_id == invoice_id
    assert transaction.transaction_id == transaction_id
    assert transaction.transaction_type == models.TransactionType.refund
    assert transaction.items == ITEMS
    assert transaction.status == models.TransactionStatus.success
    assert transaction.error_code is None


@pytest.mark.parametrize('status', list(models.TransactionStatus))
@pytest.mark.parametrize('error_code', [None, 'error'])
async def test_idempotency(
        grocery_cibus_refund, grocery_cibus_db, status, error_code,
):
    transaction = models.Transaction(
        status=status,
        error_code=error_code,
        transaction_type=models.TransactionType.refund,
    )
    grocery_cibus_db.insert_transaction(transaction)

    response = await grocery_cibus_refund()
    assert response.get('status') == status.name
    assert response.get('error_code') == error_code

    new_transaction = grocery_cibus_db.load_transaction(
        transaction.invoice_id, transaction.transaction_id,
    )
    assert transaction == new_transaction


async def test_payment_not_found(grocery_cibus_refund):
    response = await grocery_cibus_refund()
    assert response['status'] == 'fail'
    assert response['error_code'] == 'payment_not_found'


@pytest.mark.parametrize(
    'payment_extra, expected_response',
    [
        (
            dict(status=models.PaymentStatus.init),
            dict(status='fail', error_code=consts.ERROR_LOGIC),
        ),
        (
            dict(status=models.PaymentStatus.canceled),
            dict(status='fail', error_code=consts.ERROR_LOGIC),
        ),
        (
            dict(status=models.PaymentStatus.fail),
            dict(status='fail', error_code=consts.ERROR_LOGIC),
        ),
        (
            dict(
                status=models.PaymentStatus.success, deal_price=DEAL_PRICE + 1,
            ),
            dict(status='fail', error_code='declined'),
        ),
        (
            dict(status=models.PaymentStatus.success, deal_id=None),
            dict(status='fail', error_code=consts.ERROR_LOGIC),
        ),
    ],
)
async def test_refund_status(
        grocery_cibus_refund,
        grocery_cibus_db,
        payment_extra,
        expected_response,
):
    payment_extra = {'deal_price': DEAL_PRICE, **payment_extra}

    payment = models.Payment(**payment_extra)
    grocery_cibus_db.insert_payment(payment)

    response = await grocery_cibus_refund()
    assert response == expected_response


async def test_cancel(grocery_cibus_refund, grocery_cibus_db, cibus):
    payment = DEFAULT_PAYMENT
    grocery_cibus_db.insert_payment(payment)

    cibus.get_token.check(
        synonym=payment.yandex_uid,
        ext_info=None,
        headers={
            'Authorization': consts.CIBUS_API_SECRET,
            'Application-Id': consts.APPLICATION_ID,
        },
    )
    cibus.cancel_payment.check(
        deal_id=payment.deal_id,
        reference_id=payment.invoice_id,
        headers={
            'Authorization': consts.DEFAULT_TOKEN,
            'Application-Id': consts.APPLICATION_ID,
        },
    )

    response = await grocery_cibus_refund()
    assert response['status'] == 'success'

    assert cibus.get_token.times_called == 1
    assert cibus.cancel_payment.times_called == 1

    payment_new = grocery_cibus_db.load_payment(payment.invoice_id)
    assert payment_new.deal_id is None
    assert payment_new.status == models.PaymentStatus.canceled


async def test_cancel_failed(grocery_cibus_refund, grocery_cibus_db, cibus):
    cibus_code = 307
    cibus_msg = 'some error desc'
    payment = DEFAULT_PAYMENT
    grocery_cibus_db.insert_payment(payment)

    cibus.cancel_payment.mock_response(code=cibus_code, msg=cibus_msg)

    response = await grocery_cibus_refund()
    assert response['status'] == 'fail'
    assert response['error_code'] == 'cibus_error'
    assert (
        response['error_desc'] == f'CibusError [{cibus_code}] - [{cibus_msg}]'
    )

    payment_new = grocery_cibus_db.load_payment(payment.invoice_id)
    assert payment == payment_new
