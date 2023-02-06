import datetime

import asynctest
import pytest

from transactions.internal.payment_gateways import agent
from transactions.models import const
from transactions.models import gateway_features
from transactions.models import notify
from transactions.models import wrappers
from . import helpers

_NOW = datetime.datetime(2020, 2, 7, 0, 0, 1)
_NOW_STR = _NOW.isoformat()


@pytest.mark.now(_NOW_STR)
@pytest.mark.parametrize(
    'invoice_id, expected_invoice_json, '
    'expected_flag_new_transaction_for_notification_call_count',
    [
        ('hold', 'expected_hold.json', 1),
        ('full-refund', 'expected_full_refund.json', 1),
        ('tips-refund', 'expected_tips_refund.json', 1),
        ('many-refunds', 'expected_many_refunds.json', 2),
    ],
)
@pytest.mark.filldb(orders='for_test_new_transaction')
async def test_new_transaction(
        invoice_id,
        expected_invoice_json,
        # pylint: disable=invalid-name
        expected_flag_new_transaction_for_notification_call_count,
        stq3_context,
        db,
        load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    to_hold, to_refund = invoice.calc_hold_resize_refund()
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    processing = await agent.AgentGateway().start_new_transaction(
        invoice=invoice,
        to_hold=helpers.first_basket(to_hold),
        to_refund=helpers.first_basket(to_refund),
        payment_type=const.PaymentType.AGENT,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    processing.invoice.pop('updated')
    expected_invoice = load_py_json(expected_invoice_json)
    assert processing.invoice.data == expected_invoice
    assert not features.method_calls
    assert tlog_notifier.flag_for_notification.call_count == 0
    assert tlog_notifier.flag_new_transaction_for_notification.call_count == (
        expected_flag_new_transaction_for_notification_call_count
    )


@pytest.mark.now(_NOW_STR)
@pytest.mark.filldb(orders='for_test_new_transaction')
async def test_new_transaction_with_transaction_payload(
        # pylint: disable=invalid-name
        stq3_context,
        db,
        load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': 'transaction_payload'}),
        fields=stq3_context.transactions.fields,
    )
    to_hold, to_refund = invoice.calc_hold_resize_refund()
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    processing = await agent.AgentGateway().start_new_transaction(
        invoice=invoice,
        to_hold=helpers.first_basket(to_hold),
        to_refund=helpers.first_basket(to_refund),
        payment_type=const.PaymentType.AGENT,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    processing.invoice.pop('updated')
    expected_invoice = load_py_json('expected_transaction_payload.json')
    assert processing.invoice.data == expected_invoice


async def test_check_pending_transactions(stq3_context):
    invoice = wrappers.make_invoice(
        {
            'billing_tech': {
                'transactions': [
                    {'payment_method_type': 'card', 'status': 'hold_init'},
                ],
            },
            'invoice_payment_tech': {'payments': []},
        },
        fields=stq3_context.transactions.fields,
    )
    actual_status = await agent.AgentGateway().check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    assert actual_status == 'no_pending'
