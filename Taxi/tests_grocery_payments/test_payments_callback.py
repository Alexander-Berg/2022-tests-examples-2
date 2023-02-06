import pytest

from . import consts
from . import pytest_marks


MODE = 'result'
PURCHASE_TOKEN = 'some-p-token'
TRUST_REFUND_ID = 'some-refund-id'


@pytest.fixture(name='grocery_payments_callback')
def _grocery_payments_callback(taxi_grocery_payments):
    async def _inner(invoice_id, status_code=200):

        response = await taxi_grocery_payments.post(
            f'/payments/v1/trust-callback/{invoice_id}',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=f'mode={MODE}'
            f'&purchase_token={PURCHASE_TOKEN}'
            f'&trust_refund_id={TRUST_REFUND_ID}',
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest_marks.INVOICE_ORIGINATORS
async def test_proxy_to_transactions(
        grocery_payments_callback, transactions, grocery_orders, originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.payment_callback.check(
        invoice_id=invoice_id,
        id_namespace=consts.SERVICE,
        mode=MODE,
        purchase_token=PURCHASE_TOKEN,
        trust_refund_id=TRUST_REFUND_ID,
    )
    await grocery_payments_callback(invoice_id)

    assert transactions.payment_callback.times_called == 1
