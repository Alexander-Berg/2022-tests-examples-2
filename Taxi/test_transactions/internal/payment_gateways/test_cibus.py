# pylint: disable=redefined-outer-name
import enum

from aiohttp import web
import asynctest
import pytest

from generated.clients import grocery_cibus

from transactions.internal import transaction_statuses
from transactions.internal.payment_gateways import cibus
from transactions.models import const
from transactions.models import gateway_features
from transactions.models import notify
from transactions.models import wrappers
from . import helpers


class ClientReaction(enum.Enum):
    SUCCESS = 'success'
    FAIL = 'fail'
    PENDING = 'pending'
    RAISE_SERVER_ERROR = 'server_error'


@pytest.fixture
def cibus_client_reaction():
    return ClientReaction.SUCCESS


@pytest.fixture(autouse=True)
def cibus_client(mock_grocery_cibus, cibus_client_reaction):
    actual_docs = []

    @mock_grocery_cibus('/cibus/payments/v1/pay')
    async def _payment_pay(request):
        nonlocal actual_docs
        actual_docs.append(request)

        if cibus_client_reaction in (
                ClientReaction.SUCCESS,
                ClientReaction.PENDING,
        ):
            return web.json_response(
                {'status': cibus_client_reaction.value}, status=200,
            )
        if cibus_client_reaction is ClientReaction.FAIL:
            return web.json_response(
                {
                    'status': cibus_client_reaction.value,
                    'error_code': 'payment_failed',
                    'error_desc': 'payment_failed desc',
                },
                status=200,
            )
        if cibus_client_reaction is ClientReaction.RAISE_SERVER_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Server error'}, status=500,
            )

    @mock_grocery_cibus('/cibus/payments/v1/refund')
    async def _payment_refund(request):
        nonlocal actual_docs
        actual_docs.append(request)

        if cibus_client_reaction in (
                ClientReaction.SUCCESS,
                ClientReaction.PENDING,
        ):
            return web.json_response(
                {'status': cibus_client_reaction.value}, status=200,
            )
        if cibus_client_reaction is ClientReaction.FAIL:
            return web.json_response(
                {
                    'status': cibus_client_reaction.value,
                    'error_code': 'refund_failed',
                    'error_desc': 'refund_failed desc',
                },
                status=200,
            )
        if cibus_client_reaction is ClientReaction.RAISE_SERVER_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Server error'}, status=500,
            )

    return actual_docs


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, ' 'expected_invoice_json, ' 'cibus_client_reaction',
    [
        ('hold', 'expected_new_hold.json', None),
        (
            'clear_success_refund',
            'expected_new_refund_pending.json',
            ClientReaction.PENDING,
        ),
        (
            'clear_success_refund',
            'expected_new_refund_success.json',
            ClientReaction.SUCCESS,
        ),
        (
            'clear_success_refund',
            'expected_new_refund_failed.json',
            ClientReaction.FAIL,
        ),
        (
            'hold_success_refund',
            'expected_new_refund_for_hold_success.json',
            ClientReaction.SUCCESS,
        ),
        (
            'two_transactions_refund',
            'expected_new_refund_with_two_transactions.json',
            ClientReaction.SUCCESS,
        ),
        (
            'partial_refund',
            'expected_new_partial_refund.json',
            ClientReaction.SUCCESS,
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_transaction_started')
async def test_transaction_started(
        invoice_id,
        expected_invoice_json,
        cibus_client_reaction,
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
    processing = await cibus.CibusGateway().start_new_transaction(
        invoice=invoice,
        to_hold=helpers.first_basket(to_hold),
        to_refund=helpers.first_basket(to_refund),
        payment_type=const.PaymentType.CIBUS,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    processing.invoice.pop('updated')
    expected_invoice = load_py_json(expected_invoice_json)

    assert processing.invoice.data == expected_invoice
    assert not features.method_calls
    assert not tlog_notifier.method_calls


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, '
    'expected_invoice_json, '
    'expected_status, '
    'cibus_client_reaction, ',
    [
        (
            'hold',
            'expected_hold_success.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'hold',
            'expected_hold_pending.json',
            transaction_statuses.CHECKED_HAS_PENDING,
            ClientReaction.PENDING,
        ),
        (
            'hold',
            'expected_hold_failed.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.FAIL,
        ),
        (
            'refund',
            'expected_refund_success.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'refund',
            'expected_refund_pending.json',
            transaction_statuses.CHECKED_HAS_PENDING,
            ClientReaction.PENDING,
        ),
        (
            'refund',
            'expected_refund_failed.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.FAIL,
        ),
        (
            'clear_init',
            'expected_clear_success.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_check_pending_transactions')
async def test_check_pending_transactions(
        invoice_id,
        expected_status,
        expected_invoice_json,
        stq3_context,
        cibus_client_reaction,
        db,
        load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    actual_status = await cibus.CibusGateway().check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    assert actual_status == expected_status

    expected_invoice = load_py_json(expected_invoice_json)
    actual_invoice = await db.orders.find_one({'_id': invoice_id})
    actual_invoice.pop('updated')

    assert actual_invoice == expected_invoice


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, cibus_client_reaction, ',
    [
        ('hold', ClientReaction.RAISE_SERVER_ERROR),
        ('refund', ClientReaction.RAISE_SERVER_ERROR),
    ],
)
@pytest.mark.filldb(orders='for_test_check_pending_transactions')
async def test_check_pending_transactions_raise_error(
        invoice_id, stq3_context, cibus_client_reaction, db, load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    with pytest.raises(grocery_cibus.ClientException):
        await cibus.CibusGateway().check_pending_transactions(
            invoice=invoice,
            context=stq3_context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )
