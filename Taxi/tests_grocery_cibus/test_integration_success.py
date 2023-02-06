import pytest

from . import consts
from . import headers
from . import models


@pytest.fixture(name='success_callback')
async def _success_callback(taxi_grocery_cibus):
    async def _do(
            deal_id=consts.DEAL_ID,
            status_code=200,
            token=consts.DEFAULT_TOKEN,
    ):
        response = await taxi_grocery_cibus.post(
            '/cibus/integration/v1/success',
            params={'token': token, 'deal_id': deal_id},
            headers=headers.DEFAULT_HEADERS,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


async def test_request_db(grocery_cibus_db, success_callback):
    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)
    deal_id = consts.DEAL_ID + 1

    for _ in range(2):
        await success_callback(deal_id=deal_id)
        result_payment = grocery_cibus_db.load_payment(payment.invoice_id)

        assert result_payment.status == models.PaymentStatus.success
        assert result_payment.deal_id == deal_id
        assert result_payment.error_code is None
        assert result_payment.error_desc is None


async def test_not_found(grocery_cibus_db, success_callback):
    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)

    await success_callback(status_code=404, token='some-another-token')
    result_payment = grocery_cibus_db.load_payment(payment.invoice_id)

    assert result_payment.status == models.PaymentStatus.init
    assert result_payment.deal_id is None
    assert result_payment.error_code is None
    assert result_payment.error_desc is None


async def test_deferred_cancel(
        grocery_cibus_db, success_callback, check_deferred_cancel_stq_event,
):
    payment = models.Payment()
    grocery_cibus_db.insert_payment(payment)

    await success_callback()

    check_deferred_cancel_stq_event(token=consts.DEFAULT_TOKEN)
