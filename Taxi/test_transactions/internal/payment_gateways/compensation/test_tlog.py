import contextlib

import asynctest
import pytest

from transactions.internal.payment_gateways.compensation import tlog
from transactions.models import compensation
from transactions.models import notify
from transactions.models import wrappers


@pytest.mark.parametrize(
    'testcase_json', ['start_new_compensation_rounded_amount.json'],
)
@pytest.mark.filldb(orders='for_test_tlog_gateway')
@pytest.mark.now('2020-09-07T00:00:00')
async def test_start_new_tlog_compensation(
        stq3_context, load_py_json, db, *, testcase_json,
):
    testcase = load_py_json(testcase_json)
    payment_request = compensation.Payment.from_dict(
        data=testcase,
        round_amount=stq3_context.transactions.trust_details.round_amount,
    )
    gateway = tlog.TlogGateway()
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': '<invoice_id>'}),
        fields=stq3_context.transactions.fields,
    )
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    invoice, _ = await gateway.start_new_compensation(
        invoice=invoice,
        operation_id=testcase['operation_id'],
        payment_request=payment_request,
        context=stq3_context,
        tlog_notifier=tlog_notifier,
        log_extra=None,
    )
    actual_compensations = invoice['billing_tech']['compensations']
    assert actual_compensations == testcase['expected_compensations']
    assert tlog_notifier.flag_for_notification.call_count == 0
    assert tlog_notifier.flag_new_transaction_for_notification.call_count == 1


@pytest.mark.parametrize(
    'testcase_json, expectation',
    [
        ('start_new_refund.json', contextlib.nullcontext()),
        ('start_new_too_large_refund.json', pytest.raises(RuntimeError)),
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_gateway')
@pytest.mark.now('2020-09-07T00:00:00')
async def test_start_new_tlog_refund(
        stq3_context, load_py_json, db, *, testcase_json, expectation,
):
    testcase = load_py_json(testcase_json)
    refund_request = compensation.Refund.from_dict(
        data=testcase,
        round_amount=stq3_context.transactions.trust_details.round_amount,
    )
    gateway = tlog.TlogGateway()
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': testcase['invoice_id']}),
        fields=stq3_context.transactions.fields,
    )
    compensation_to_refund = _select_compensation(
        invoice, refund_request.trust_payment_id,
    )
    with expectation as error:
        tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
        invoice, _ = await gateway.start_new_refund(
            invoice=invoice,
            operation_id=testcase['operation_id'],
            compensation=compensation_to_refund,
            refund_request=refund_request,
            context=stq3_context,
            tlog_notifier=tlog_notifier,
            log_extra=None,
        )
    if error is not None:
        assert str(error.value) == testcase['expected_error_message']
    actual_compensations = invoice['billing_tech']['compensations']
    assert actual_compensations == testcase['expected_compensations']
    assert tlog_notifier.flag_for_notification.call_count == 0
    assert tlog_notifier.flag_new_transaction_for_notification.call_count == (
        testcase['expected_flag_new_transaction_for_notification_call_count']
    )


def _select_compensation(
        invoice: wrappers.Invoice, trust_payment_id: str,
) -> wrappers.Compensation:
    for a_compensation in invoice.compensations:
        if a_compensation.external_payment_id == trust_payment_id:
            return a_compensation
    raise RuntimeError('No compensation found, fix tests')
