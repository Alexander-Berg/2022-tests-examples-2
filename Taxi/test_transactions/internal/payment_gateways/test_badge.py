# pylint: disable=redefined-outer-name
import enum

from aiohttp import web
import asynctest
import pytest

from generated.clients import badgepay

from transactions.internal import transaction_statuses
from transactions.internal.payment_gateways import badge
from transactions.models import const
from transactions.models import gateway_features
from transactions.models import notify
from transactions.models import wrappers
from . import helpers


class ClientReaction(enum.Enum):
    SUCCESS = 'success'
    RAISE_SERVER_ERROR = 'server_error'
    RAISE_CLIENT_ERROR = 'client_error'


@pytest.fixture
def badgepay_client_reaction():
    return ClientReaction.SUCCESS


@pytest.fixture(autouse=True)
def badgepay_client(mock_badgepay, badgepay_client_reaction):
    actual_docs = []

    @mock_badgepay('/pg/eda/pay')
    async def _pg_eda_pay(request):
        nonlocal actual_docs
        actual_docs.append(request)

        if badgepay_client_reaction is ClientReaction.SUCCESS:
            return web.json_response(
                {
                    'status': 'OK',
                    'message': 'Подтверждено',
                    'orderStatus': 'Confirmed',
                },
                status=200,
            )
        if badgepay_client_reaction is ClientReaction.RAISE_SERVER_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Server error'}, status=500,
            )
        if badgepay_client_reaction is ClientReaction.RAISE_CLIENT_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Client error'}, status=400,
            )

    @mock_badgepay('/pg/eda/reverse')
    async def _pg_eda_reverse(request):
        nonlocal actual_docs
        actual_docs.append(request)
        if badgepay_client_reaction is ClientReaction.SUCCESS:
            return web.json_response(
                {
                    'status': 'OK',
                    'message': 'Сторнировано',
                    'orderStatus': 'Reversed',
                },
            )
        if badgepay_client_reaction is ClientReaction.RAISE_SERVER_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Server error'}, status=500,
            )
        if badgepay_client_reaction is ClientReaction.RAISE_CLIENT_ERROR:
            return web.json_response(
                {'status': 'ERROR', 'message': 'Client error'}, status=400,
            )

    return actual_docs


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, expected_invoice_json',
    [
        ('hold', 'expected_hold.json'),
        ('clear_success_refund', 'expected_refund_for_clear_success.json'),
        ('hold_success_refund', 'expected_refund_for_hold_success.json'),
        ('two_transactions_refund', 'expected_two_transactions_refund.json'),
    ],
)
@pytest.mark.filldb(orders='for_test_transaction_started')
async def test_transaction_started(
        invoice_id, expected_invoice_json, stq3_context, db, load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    to_hold, to_refund = invoice.calc_hold_resize_refund()
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    processing = await badge.BadgeGateway().start_new_transaction(
        invoice=invoice,
        to_hold=helpers.first_basket(to_hold),
        to_refund=helpers.first_basket(to_refund),
        payment_type=const.PaymentType.BADGE,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    processing.invoice.pop('updated')
    expected_invoice = load_py_json(expected_invoice_json)

    assert processing.invoice == expected_invoice
    assert not features.method_calls
    assert not tlog_notifier.method_calls


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.filldb(
    orders='for_test_transaction_started_with_transaction_payload',
)
async def test_transaction_started_with_transaction_payload(
        stq3_context, db, load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one(
            {'_id': 'transaction_with_transaction_payload'},
        ),
        fields=stq3_context.transactions.fields,
    )
    to_hold, to_refund = invoice.calc_hold_resize_refund()
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    processing = await badge.BadgeGateway().start_new_transaction(
        invoice=invoice,
        to_hold=helpers.first_basket(to_hold),
        to_refund=helpers.first_basket(to_refund),
        payment_type=const.PaymentType.BADGE,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    processing.invoice.pop('updated')
    expected_invoice = load_py_json('expected_transaction_payload.json')
    assert processing.invoice == expected_invoice


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, '
    'expected_invoice_json, '
    'expected_status, '
    'badgepay_client_reaction, ',
    [
        (
            'refund',
            'expected_cleared_refund.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'refund_without_wallet',
            'expected_cleared_refund_without_wallet.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'hold',
            'expected_success_hold.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'hold_without_wallet',
            'expected_success_hold_without_wallet.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'hold',
            'expected_failed_hold.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.RAISE_CLIENT_ERROR,
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
        badgepay_client_reaction,
        badgepay_client,
        db,
        load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    actual_status = await (
        badge.BadgeGateway().check_pending_transactions(
            invoice=invoice,
            context=stq3_context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )
    )
    assert actual_status == expected_status

    expected_invoice = load_py_json(expected_invoice_json)
    actual_invoice = await db.orders.find_one({'_id': invoice_id})
    actual_invoice.pop('updated')

    assert actual_invoice == expected_invoice


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, badgepay_client_reaction, ',
    [
        ('hold', ClientReaction.RAISE_SERVER_ERROR),
        ('refund', ClientReaction.RAISE_SERVER_ERROR),
        ('refund', ClientReaction.RAISE_CLIENT_ERROR),
    ],
)
@pytest.mark.filldb(orders='for_test_check_pending_transactions')
async def test_check_pending_transactions_raise_error(
        invoice_id,
        stq3_context,
        badgepay_client_reaction,
        badgepay_client,
        db,
        load_py_json,
):
    invoice = wrappers.make_invoice(
        await db.orders.find_one({'_id': invoice_id}),
        fields=stq3_context.transactions.fields,
    )
    with pytest.raises(badgepay.ClientException):
        await badge.BadgeGateway().check_pending_transactions(
            invoice=invoice,
            context=stq3_context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )


@pytest.mark.now('2020-02-07T00:00:01')
@pytest.mark.parametrize(
    'invoice_id, '
    'expected_invoice_json, '
    'expected_status, '
    'badgepay_client_reaction, ',
    [
        (
            'partial_refund',
            'expected_cleared_partial_refund.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
        (
            'partial_refund_after_partial_refund',
            'expected_cleared_partial_refund_after_partial_refund.json',
            transaction_statuses.CHECKED_HAS_REFRESHED,
            ClientReaction.SUCCESS,
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_partial_refunds')
async def test_partial_refunds(
        invoice_id,
        expected_status,
        expected_invoice_json,
        stq3_context,
        badgepay_client_reaction,
        badgepay_client,
        db,
        load_py_json,
):
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    for _ in range(2):
        invoice = wrappers.make_invoice(
            await db.orders.find_one({'_id': invoice_id}),
            fields=stq3_context.transactions.fields,
        )
        to_hold, to_refund = invoice.calc_hold_resize_refund()
        processing = await badge.BadgeGateway().start_new_transaction(
            invoice=invoice,
            to_hold=helpers.first_basket(to_hold),
            to_refund=helpers.first_basket(to_refund),
            payment_type=const.PaymentType.BADGE,
            features=features,
            tlog_notifier=tlog_notifier,
            context=stq3_context,
        )
        status = await (
            badge.BadgeGateway().check_pending_transactions(
                invoice=processing.invoice,
                context=stq3_context,
                tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
            )
        )
        assert status == expected_status

    expected_invoice = load_py_json(expected_invoice_json)
    actual_invoice = await db.orders.find_one({'_id': invoice_id})
    actual_invoice.pop('updated')

    assert actual_invoice == expected_invoice
    assert not features.method_calls
    assert not tlog_notifier.method_calls
