import pytest

from . import consts
from . import models


async def test_transaction_success(
        run_deferred_cancel, check_deferred_cancel_stq_event, grocery_cibus_db,
):
    payment = models.Payment(status=models.PaymentStatus.success)
    grocery_cibus_db.insert_payment(payment)

    transaction = models.Transaction(status=models.TransactionStatus.success)
    grocery_cibus_db.insert_transaction(transaction)

    await run_deferred_cancel()

    check_deferred_cancel_stq_event(times_called=0)


async def test_transaction_pending(
        run_deferred_cancel, check_deferred_cancel_stq_event, grocery_cibus_db,
):
    payment = models.Payment(status=models.PaymentStatus.success)
    grocery_cibus_db.insert_payment(payment)

    transaction = models.Transaction(status=models.TransactionStatus.pending)
    grocery_cibus_db.insert_transaction(transaction)

    await run_deferred_cancel()

    check_deferred_cancel_stq_event(times_called=1)


async def test_transaction_fail(
        run_deferred_cancel,
        check_deferred_cancel_stq_event,
        grocery_cibus_db,
        cibus,
):
    payment = models.Payment(
        status=models.PaymentStatus.success, deal_id=consts.DEAL_ID,
    )
    grocery_cibus_db.insert_payment(payment)

    transaction = models.Transaction(status=models.TransactionStatus.fail)
    grocery_cibus_db.insert_transaction(transaction)

    cibus.get_token.check(synonym=payment.yandex_uid, ext_info=None)
    cibus.cancel_payment.check(
        deal_id=payment.deal_id, reference_id=payment.invoice_id,
    )

    await run_deferred_cancel()

    assert cibus.get_token.times_called == 1
    assert cibus.cancel_payment.times_called == 1

    payment_new = grocery_cibus_db.load_payment(payment.invoice_id)
    assert payment_new.deal_id is None
    assert payment_new.status == models.PaymentStatus.canceled

    check_deferred_cancel_stq_event(times_called=0)


async def test_payment_operation_not_exists(
        run_deferred_cancel, check_deferred_cancel_stq_event,
):
    await run_deferred_cancel()

    check_deferred_cancel_stq_event(times_called=0)


@pytest.mark.parametrize('status', list(models.PaymentStatus))
async def test_payment_operation_not_success(
        run_deferred_cancel,
        check_deferred_cancel_stq_event,
        grocery_cibus_db,
        status,
):
    payment = models.Payment(status=status)
    grocery_cibus_db.insert_payment(payment)

    await run_deferred_cancel()

    times_called = int(status == models.PaymentStatus.success)
    check_deferred_cancel_stq_event(times_called=times_called)
