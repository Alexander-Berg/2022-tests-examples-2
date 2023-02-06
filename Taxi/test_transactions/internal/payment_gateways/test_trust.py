# pylint: disable=too-many-lines
import abc
import contextlib
import dataclasses
import datetime
import itertools
from typing import Any
from typing import List
from typing import Optional

import asynctest
import pytest

from taxi.billing.util import dates as billing_dates

from test_transactions import helpers
from transactions.clients.trust import rest_client
from transactions.clients.trust import service_details
from transactions.internal import basket
from transactions.internal import handling
from transactions.internal.payment_gateways import trust
from transactions.internal.payment_gateways.compensation import (
    trust as trust_compensation,
)
from transactions.models import const
from transactions.models import fields
from transactions.models import gateway_features
from transactions.models import notify
from transactions.models import wrappers

_TRANSACTION_UID = '123456'
_NOW = datetime.datetime(2020, 1, 11)
_TRUST_CLEAR_TS = '1612278708.909'
_TRUST_CLEAR_TIME = datetime.datetime(2021, 2, 2, 15, 11, 48, 909000)


@dataclasses.dataclass(frozen=True)
class Refund:
    # pylint: disable=invalid-name
    id: str
    status: str
    receipt: Optional[str]
    trust_response: Optional[dict] = None
    trust_receipt: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Transaction:
    # pylint: disable=invalid-name
    id: str
    status: str
    attempts: Optional[int]
    eta: Optional[datetime.datetime]
    has_new_receipts: bool
    receipt: Optional[str]
    clearing_receipt: Optional[str]
    refunds: List[Refund]
    trust_receipt: Optional[str] = None
    trust_clearing_receipt: Optional[str] = None
    initial_sum: Optional[int] = None


@dataclasses.dataclass(frozen=True)
class FetchLostAndFoundSetup:
    context: Any
    check_basket_mock: Any
    mock_trust_check_basket_full: Any
    start_refund_mock: Any
    check_refund_mock: Any
    transactions_field: str


@pytest.mark.filldb(
    orders='for_test_start_new_transaction',
    eda_invoices='for_test_start_new_transaction',
)
@pytest.mark.parametrize(
    'testcase_json, ',
    [
        'start_new_transaction_card.json',
        'start_new_transaction_coop_account.json',
    ],
)
async def test_start_new_transaction(
        db,
        stq3_context,
        eda_stq3_context,
        load_py_json,
        trust_create_basket,
        trust_create_order,
        trust_refunds,
        personal_tins_bulk_retrieve,
        personal_phones_retrieve,
        mock_get_service_order,
        *,
        testcase_json,
):
    testcase = load_py_json(testcase_json)
    payment_type = const.PaymentType(testcase['payment_type'])
    to_hold = basket.Basket.make_from_sum_items(testcase['to_hold'])
    to_refund = basket.Basket.make_from_sum_items(testcase['to_refund'])

    expected_taxi_basket_requests = testcase['expected_taxi_basket_requests']
    expected_taxi_order_requests = testcase['expected_taxi_order_requests']
    expected_taxi_refunds_requests = testcase['expected_taxi_refunds_requests']
    expected_eda_basket_requests = testcase['expected_eda_basket_requests']
    expected_eda_order_requests = testcase['expected_eda_order_requests']
    expected_eda_refunds_requests = testcase['expected_eda_refunds_requests']

    personal_tins_bulk_retrieve()
    personal_phones_retrieve()

    tests = (
        (
            stq3_context,
            expected_taxi_basket_requests,
            expected_taxi_order_requests,
            expected_taxi_refunds_requests,
            'taxi',
        ),
        (
            eda_stq3_context,
            expected_eda_basket_requests,
            expected_eda_order_requests,
            expected_eda_refunds_requests,
            'eda',
        ),
    )
    for (
            context,
            expected_basket_requests,
            expected_order_requests,
            expected_refunds_requests,
            suffix,
    ) in tests:
        for request in expected_order_requests:
            mock_get_service_order(
                request['order_id'], 'error', 'order_not_found',
            )
        create_basket = trust_create_basket()
        create_order = trust_create_order()
        refunds = trust_refunds()
        gateway = trust.TrustGateway(['card'], stq3_context)
        invoice_id = testcase['invoice_id'] + '_' + suffix
        invoice_data = await context.transactions.invoices.find_one(invoice_id)
        assert invoice_data is not None
        invoice = wrappers.make_invoice(
            invoice_data, fields=context.transactions.fields,
        )

        features = asynctest.Mock(spec=gateway_features.Features)
        tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
        await gateway.start_new_transaction(
            invoice=invoice,
            to_hold=to_hold,
            to_refund=to_refund,
            payment_type=payment_type,
            features=features,
            tlog_notifier=tlog_notifier,
            context=context,
        )
        actual_order_requests = sorted(
            create_order.requests, key=lambda x: x['order_id'],
        )
        assert create_basket.requests == expected_basket_requests
        assert actual_order_requests == expected_order_requests
        assert refunds.requests == expected_refunds_requests
        assert not features.method_calls
        assert not tlog_notifier.method_calls


@pytest.mark.filldb(
    orders='for_test_start_transaction_with_transaction_payload',
)
async def test_start_transaction_with_transaction_payload(
        stq3_context,
        db,
        trust_create_basket,
        trust_create_order,
        trust_refunds,
        personal_tins_bulk_retrieve,
        personal_phones_retrieve,
        mock_get_service_order,
):
    payment_type = const.PaymentType('card')
    to_hold = basket.Basket.make_from_sum_items(
        {'ride': '10.123', 'tips': '1'},
    )
    personal_tins_bulk_retrieve()
    personal_phones_retrieve()
    trust_create_basket()
    trust_create_order()
    trust_refunds()
    mock_get_service_order('<alias_id>', 'error', 'order_not_found')
    mock_get_service_order('<alias_id>_tips', 'error', 'order_not_found')
    gateway = trust.TrustGateway(['card'], stq3_context)
    invoice_data = await stq3_context.transactions.invoices.find_one(
        '<invoice_id>',
    )
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    processing = await gateway.start_new_transaction(
        invoice=invoice,
        to_hold=to_hold,
        to_refund=basket.Basket({}),
        payment_type=payment_type,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    assert len(processing.invoice.data['billing_tech']['transactions']) == 1
    transaction = processing.invoice.data['billing_tech']['transactions'][0]
    assert transaction['transaction_payload'] == {'key_1': 'value_1'}


@pytest.fixture(name='trust_create_basket')
def _trust_create_basket(mockserver):
    class _DoMock:
        def __init__(self):
            self.requests = []

            @mockserver.json_handler('/trust-payments/v2/payments/')
            def _handler(request):
                self.requests.append(request.json)
                resp_body = {
                    'status': 'success',
                    'purchase_token': 'trust-basket-token',
                    'trust_payment_id': 'trust-payment-id',
                }
                return mockserver.make_response(status=200, json=resp_body)

    return _DoMock


@pytest.fixture(name='trust_refunds')
def _trust_refunds(mockserver):
    class _DoMock:
        def __init__(self):
            self.requests = []

            @mockserver.json_handler('/trust-payments/v2/refunds/')
            def _handler(request):
                assert request.headers['X-Uid'] == '123456'
                self.requests.append(request.json)
                resp_body = {
                    'status': 'success',
                    'trust_refund_id': 'trust-refund-id',
                }
                return mockserver.make_response(status=200, json=resp_body)

    return _DoMock


@pytest.fixture(name='trust_create_order')
def _trust_create_order(mockserver):
    class _DoMock:
        def __init__(self):
            self.requests = []

            @mockserver.json_handler('/trust-payments/v2/orders/')
            def _handler(request):
                self.requests.append(request.json)
                resp_body = {
                    'status': 'success',
                    'status_code': 'created',
                    'order_id': request.json.get('order_id') or '<order_id>',
                }
                return mockserver.make_response(status=200, json=resp_body)

    return _DoMock


@pytest.mark.filldb(
    orders='for_test_card_validity_updated',
    eda_invoices='for_test_card_validity_updated',
)
@pytest.mark.parametrize('is_eda, suffix', [(False, 'taxi'), (True, 'eda')])
@pytest.mark.parametrize(
    'trust_response, current_card_validity,'
    'taxi_expected_card_updates, eda_expected_card_updates',
    [
        (
            {
                'payment_resp_code': 'done',
                'payment_method': 'card',
                'payment_status': 'authorized',
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_resp_desc': '',
            },
            True,
            [],
            [],
        ),
        (
            {
                'payment_resp_code': 'expired_card',
                'payment_method': 'card',
                'payment_status': 'not_authorized',
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_resp_desc': 'ActionCode [101] - [expired_card]',
            },
            False,
            [],
            [],
        ),
        (
            {
                'payment_resp_code': 'expired_card',
                'payment_method': 'card',
                'payment_status': 'not_authorized',
                'status': 'success',
                'purchase_token': 'trust-basket-token',
                'payment_resp_desc': 'ActionCode [101] - [expired_card]',
            },
            True,
            [{'yandex_uid': '123', 'card_id': 'card-1324', 'valid': False}],
            [],
        ),
        (
            {
                'payment_resp_desc': 'Card is blocked, reason: RC=41, reason=',
                'payment_resp_code': 'restricted_card',
                'uid': '501652192',
                'payment_method': 'card',
                'payment_status': 'not_authorized',
                'purchase_token': 'trust-basket-token',
                'status': 'success',
            },
            True,
            [{'yandex_uid': '123', 'card_id': 'card-1324', 'valid': False}],
            [],
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_card_validity_updated(
        eda_stq3_context,
        stq3_context,
        db,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        cardstorage_update_card,
        cardstorage_card,
        is_eda,
        suffix,
        trust_response,
        current_card_validity,
        taxi_expected_card_updates,
        eda_expected_card_updates,
):
    context = eda_stq3_context if is_eda else stq3_context

    mock_trust_check_basket(
        purchase_token=trust_response['purchase_token'],
        payment_status=trust_response['payment_status'],
        expect_headers={'X-Uid': _TRANSACTION_UID},
        resp_body=trust_response,
    )
    mock_trust_check_basket_full(
        purchase_token=trust_response['purchase_token'],
        payment_status=trust_response['payment_status'],
        expect_headers={'X-Uid': _TRANSACTION_UID},
        resp_body=trust_response,
    )
    card_updates = []
    cardstorage_update_card(requests=card_updates)
    cardstorage_card(valid=current_card_validity)

    invoice_id = '<invoice_id>' + '_' + suffix
    invoice_data = await context.transactions.invoices.find_one(invoice_id)
    invoice = wrappers.make_invoice(
        invoice_data, fields=context.transactions.fields,
    )
    gateway = trust.TrustGateway(['card'], context)
    with contextlib.suppress(rest_client.StatusError):
        await gateway.check_pending_transactions(
            invoice=invoice,
            context=context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )

    if is_eda:
        assert card_updates == eda_expected_card_updates
    else:
        assert card_updates == taxi_expected_card_updates


@pytest.mark.parametrize(
    'invoice_json, payment_type, trust_details, '
    'transaction_payload, client_exists, expected',
    [
        (
            'pass_params_invoice.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TaxiTrustDetails(),
            None,
            True,
            {
                'payload': {
                    'tariff_class': 'econom',
                    'order_id': 'some_order_id',
                    'alias_id': 'some_alias_id',
                    'oebs_mvp_id': 'some_oebs_mvp_id',
                    'service_id': '124',
                },
            },
        ),
        (
            'pass_params_invoice.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TaxiTrustDetails(),
            None,
            False,
            {'some_key': 'some_value'},
        ),
        (
            'pass_params_invoice.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TrustDetails(),
            None,
            True,
            {'some_key': 'some_value'},
        ),
        (
            'pass_params_invoice.json',
            const.PaymentType.CARD,
            service_details.TaxiTrustDetails(),
            None,
            True,
            {'some_key': 'some_value'},
        ),
        pytest.param(
            'pass_params_invoice_w_wallet_payload.json',
            const.PaymentType.CARD,
            service_details.TrustDetails(),
            None,
            True,
            {'some_key': 'some_value'},
            id='If invoice has wallet_payload, card gets ordinary pass params',
        ),
        pytest.param(
            # If invoice has wallet_payload, wallet gets pass params with
            # wallet payload
            'pass_params_invoice_w_wallet_payload.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TrustDetails(),
            None,
            True,
            {'payload': {'some_wallet_key': 'some_wallet_value'}},
            id=(
                'If invoice has wallet_payload, wallet gets pass params with '
                'wallet payload'
            ),
        ),
        pytest.param(
            'pass_params_invoice_w_wallet_payload.json',
            const.PaymentType.CARD,
            service_details.TaxiTrustDetails(),
            None,
            True,
            {'some_key': 'some_value'},
            id=(
                'If taxi invoice has wallet_payload, card gets ordinary pass '
                'params'
            ),
        ),
        pytest.param(
            'pass_params_invoice_w_wallet_payload.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TaxiTrustDetails(),
            None,
            True,
            {
                'payload': {
                    'tariff_class': 'econom',
                    'order_id': 'some_order_id',
                    'alias_id': 'some_alias_id',
                    'oebs_mvp_id': 'some_oebs_mvp_id',
                    'service_id': '124',
                },
            },
            id=(
                'If taxi invoice has wallet_payload, wallet gets custom taxi '
                'pass params '
            ),
        ),
        pytest.param(
            'pass_params_invoice_w_wallet_without_performer_payload.json',
            const.PaymentType.PERSONAL_WALLET,
            service_details.TaxiTrustDetails(),
            {
                'alias_id': 'payload_alias_id',
                'tariff_class': 'payload_tariff_class',
            },
            True,
            {
                'payload': {
                    'tariff_class': 'payload_tariff_class',
                    'order_id': 'some_order_id',
                    'alias_id': 'payload_alias_id',
                    'oebs_mvp_id': 'some_oebs_mvp_id',
                    'service_id': '124',
                },
            },
            id='should take tariff_class & alias_id from transaction_payload',
        ),
    ],
)
async def test_get_pass_params(
        mock_taxi_agglomerations,
        stq3_context,
        load_py_json,
        invoice_json,
        payment_type,
        trust_details,
        transaction_payload,
        client_exists,
        expected,
):
    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def get_mvp_oebs_id(request):
        # pylint: disable=unused-variable
        expected_dt = datetime.datetime(
            2000, 1, 1, tzinfo=datetime.timezone.utc,
        )
        assert request.args['tariff_zone'] == 'moscow'
        assert billing_dates.parse_datetime(request.args['dt']) == expected_dt
        return {'oebs_mvp_id': 'some_oebs_mvp_id'}

    client = (
        stq3_context.clients.taxi_agglomerations if client_exists else None
    )
    invoice = _load_invoice(load_py_json, stq3_context, invoice_json)
    actual = await trust.get_pass_params(
        invoice=invoice,
        payment_type=payment_type,
        trust_details=trust_details,
        maybe_agglomerations_client=client,
        billing_payments_service_id=124,
        transaction_payload=transaction_payload,
    )
    assert actual == expected


def _make_invoice_for_select_transactions():
    data = {
        'billing_tech': {
            'transactions': [
                {
                    'purchase_token': 'trust',
                    'payment_method_type': 'card',
                    'trust_payment_id': '',
                },
                {
                    'purchase_token': 'psp',
                    'payment_method_type': 'card',
                    'psp_external_id': 'psp_id',
                    'trust_payment_id': '',
                },
            ],
        },
        'invoice_payment_tech': {},
    }
    return wrappers.make_invoice(data, fields=fields.TaxiOrderFields())


@pytest.mark.parametrize(
    'invoice, expected_ids',
    [
        pytest.param(
            _make_invoice_for_select_transactions(),
            ['trust'],
            id='it should ignore psp transactions',
        ),
    ],
)
def test_select_trust_transactions(invoice, expected_ids):
    transactions = trust.select_trust_transactions(invoice)
    actual_ids = _select_ids(transactions)
    assert actual_ids == expected_ids


@pytest.mark.parametrize(
    'invoice, expected_ids',
    [
        pytest.param(
            _make_invoice_for_select_transactions(),
            ['trust'],
            id='it should ignore psp transactions',
        ),
    ],
)
def test_select_transactions_for_refund(invoice, expected_ids):
    transactions = trust.select_transactions_for_refund(
        invoice, const.PaymentType.CARD,
    )
    actual_ids = _select_ids(transactions)
    assert actual_ids == expected_ids


def _select_ids(transactions: List[wrappers.Transaction]) -> List[str]:
    return [tx.external_payment_id for tx in transactions]


def _load_invoice(load_py_json, stq3_context, invoice_json):
    invoice_data = load_py_json(invoice_json)
    return wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )


def _receipt_testcase(id, transaction, version, eta, changes):
    # pylint: disable=invalid-name,redefined-builtin
    return pytest.param(
        [transaction],
        version,
        eta,
        [dataclasses.replace(transaction, **changes)],
        id=id,
    )


def _transaction_from_stub(changes, initial_sum=1990000):
    transaction = Transaction(
        id='1',
        status='clear_success',
        attempts=None,
        eta=None,
        has_new_receipts=False,
        receipt='receipt-url',
        clearing_receipt='clearing-receipt-url',
        refunds=[
            Refund(
                id='1', status='refund_success', receipt='refund-receipt-url',
            ),
        ],
        initial_sum=initial_sum,
    )
    return dataclasses.replace(transaction, **changes)


@pytest.mark.parametrize(
    'transactions, expected_version, expected_eta, expected_transactions',
    [
        # All receipts are present, unset eta & attempts and return None
        _receipt_testcase(
            'no-missing-receipts',
            transaction=_transaction_from_stub(
                dict(attempts=123, eta=datetime.datetime(2020, 1, 11, 1)),
            ),
            version=2,
            eta=None,
            changes=dict(attempts=None, eta=None),
        ),
        # Old transaction without initial-sum, do nothing and return None
        _receipt_testcase(
            'no-initial-sum',
            transaction=_transaction_from_stub(dict(initial_sum=None)),
            version=1,
            eta=None,
            changes=dict(),
        ),
        # No receipt & no eta. Set eta and return it
        _receipt_testcase(
            'no-receipt-no-attempts',
            transaction=_transaction_from_stub(dict(receipt=None)),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(
                attempts=1, eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            ),
        ),
        # No receipt & eta has not come yet. Return eta
        _receipt_testcase(
            'no-receipt-eta-is-in-future',
            transaction=_transaction_from_stub(
                dict(
                    receipt=None, eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
                ),
            ),
            version=1,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(),
        ),
        # No receipt & eta has come, but there's no receipt in Trust yet.
        # Increment attempts, set & return new eta
        _receipt_testcase(
            'no-receipt-no-receipt-in-trust-yet',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    receipt=None,
                    trust_clearing_receipt='clearing-receipt-url',
                ),
            ),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            changes=dict(
                attempts=2, eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            ),
        ),
        # No receipt & eta has come, and receipt is in Trust.
        # Unset attempts & eta, store new receipt, mark transaction with
        # 'has new receipts' flag, return eta=None
        _receipt_testcase(
            'no-receipt-receipt-is-in-trust',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    receipt=None,
                    trust_receipt='receipt-url',
                    trust_clearing_receipt='clearing-receipt-url',
                ),
            ),
            version=2,
            eta=None,
            changes=dict(
                attempts=None,
                eta=None,
                has_new_receipts=True,
                receipt='receipt-url',
            ),
        ),
        # No clearing receipt & no eta. Set eta and return it
        _receipt_testcase(
            'no-clearing-receipt-no-attempts',
            transaction=_transaction_from_stub(dict(clearing_receipt=None)),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(
                attempts=1, eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            ),
        ),
        # No clearing_receipt & eta has not come yet. Return eta
        _receipt_testcase(
            'no-clearing-receipt-eta-is-in-future',
            transaction=_transaction_from_stub(
                dict(
                    clearing_receipt=None,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
                ),
            ),
            version=1,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(),
        ),
        # No receipt & eta has come, but there's no receipt in Trust yet.
        # Increment attempts, set & return new eta
        _receipt_testcase(
            'no-clearing-receipt-no-receipt-in-trust-yet',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    clearing_receipt=None,
                    trust_receipt='receipt-url',
                ),
            ),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            changes=dict(
                attempts=2, eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            ),
        ),
        # No clearing receipt & eta has come, and clearing receipt is in Trust.
        # Unset attempts & eta, store new clearing receipt, mark transaction
        # with 'has new receipts' flag, return eta=None
        _receipt_testcase(
            'no-clearing-receipt-receipt-is-in-trust',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    clearing_receipt=None,
                    trust_receipt='receipt-url',
                    trust_clearing_receipt='clearing-receipt-url',
                ),
            ),
            version=2,
            eta=None,
            changes=dict(
                attempts=None,
                eta=None,
                has_new_receipts=True,
                clearing_receipt='clearing-receipt-url',
            ),
        ),
        # Successful refund with chargeback, do nothing and return None
        _receipt_testcase(
            'refund-chargeback',
            transaction=_transaction_from_stub(
                dict(
                    refunds=[
                        Refund(
                            id='1',
                            status='refund_success',
                            receipt=None,
                            trust_response={
                                'status': 'error',
                                'status_desc': (
                                    'Invalid payment state [ChargeBack]'
                                ),
                            },
                        ),
                    ],
                ),
            ),
            version=1,
            eta=None,
            changes=dict(),
        ),
        # No refund receipt & no eta. Set eta and return it
        _receipt_testcase(
            'no-refund-receipt-no-attempts',
            transaction=_transaction_from_stub(
                dict(
                    refunds=[
                        Refund(id='1', status='refund_success', receipt=None),
                    ],
                ),
            ),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(
                attempts=1, eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            ),
        ),
        # No clearing_receipt & eta has not come yet. Return eta
        _receipt_testcase(
            'no-refund-receipt-eta-is-in-future',
            transaction=_transaction_from_stub(
                dict(
                    refunds=[
                        Refund(id='1', status='refund_success', receipt=None),
                    ],
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
                ),
            ),
            version=1,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 2),
            changes=dict(),
        ),
        # No receipt & eta has come, but there's no receipt in Trust yet.
        # Increment attempts, set & return new eta
        _receipt_testcase(
            'no-refund-receipt-no-receipt-in-trust-yet',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    refunds=[
                        Refund(id='1', status='refund_success', receipt=None),
                    ],
                    trust_receipt='receipt-url',
                ),
            ),
            version=2,
            eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            changes=dict(
                attempts=2, eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
            ),
        ),
        # No clearing receipt & eta has come, and clearing receipt is in Trust.
        # Unset attempts & eta, store new clearing receipt, mark transaction
        # with 'has new receipts' flag, return eta=None
        _receipt_testcase(
            'no-refund-receipt-receipt-is-in-trust',
            transaction=_transaction_from_stub(
                dict(
                    attempts=1,
                    eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                    refunds=[
                        Refund(
                            id='1',
                            status='refund_success',
                            receipt=None,
                            trust_receipt='refund-receipt-url',
                        ),
                    ],
                ),
            ),
            version=2,
            eta=None,
            changes=dict(
                attempts=None,
                eta=None,
                has_new_receipts=True,
                refunds=[
                    Refund(
                        id='1',
                        status='refund_success',
                        receipt='refund-receipt-url',
                    ),
                ],
            ),
        ),
        # When receipts are missing from multiple transactions, pick nearest
        # eta for next attempt
        pytest.param(
            [
                _transaction_from_stub(
                    dict(
                        attempts=1,
                        eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                        receipt=None,
                        trust_clearing_receipt='clearing-receipt-url',
                    ),
                ),
                _transaction_from_stub(
                    dict(
                        id='2',
                        attempts=2,
                        eta=datetime.datetime(2020, 1, 11, 0, 0, 0),
                        receipt=None,
                        trust_clearing_receipt='clearing-receipt-url',
                    ),
                ),
            ],
            2,
            datetime.datetime(2020, 1, 11, 0, 0, 4),
            [
                _transaction_from_stub(
                    dict(
                        attempts=2,
                        eta=datetime.datetime(2020, 1, 11, 0, 0, 4),
                        receipt=None,
                        trust_clearing_receipt='clearing-receipt-url',
                    ),
                ),
                _transaction_from_stub(
                    dict(
                        id='2',
                        attempts=3,
                        eta=datetime.datetime(2020, 1, 11, 0, 0, 8),
                        receipt=None,
                        trust_clearing_receipt='clearing-receipt-url',
                    ),
                ),
            ],
            id='pick-nearest-eta',
        ),
    ],
)
@pytest.mark.now('2020-01-11T00:00:00')
@pytest.mark.config(
    TRANSACTIONS_RETRIEVE_FISCAL_RECEIPT_BACKOFF={'min': 2, 'max': 1800},
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.filldb(orders='for_test_check_receipts')
async def test_check_receipts(
        stq3_context,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_check_refund,
        _patch_random,
        transactions,
        expected_version,
        expected_eta,
        expected_transactions,
):
    updated = datetime.datetime(2020, 1, 10)  # before 'now'
    invoice_id = 'for_test_check_receipts'
    collection = stq3_context.transactions.invoices
    for transaction in transactions:
        mock_trust_check_basket(
            purchase_token=transaction.id,
            payment_status=_get_payment_status(transaction.status),
            status='success',
            receipt=transaction.trust_receipt,
            clearing_receipt=transaction.trust_clearing_receipt,
            expect_headers={'X-Uid': _TRANSACTION_UID},
        )
        mock_trust_check_basket_full(
            purchase_token=transaction.id,
            payment_status=_get_payment_status(transaction.status),
            status='success',
            receipt=transaction.trust_receipt,
            clearing_receipt=transaction.trust_clearing_receipt,
            expect_headers={'X-Uid': _TRANSACTION_UID},
        )
        for refund in transaction.refunds:
            mock_trust_check_refund(
                trust_refund_id=refund.id,
                receipt=refund.trust_receipt,
                expect_headers={'X-Uid': _TRANSACTION_UID},
            )
    await _set_transactions(invoice_id, collection, transactions, updated)
    invoice = await _get_invoice(invoice_id, stq3_context)
    gateway = trust.TrustGateway(['card'], stq3_context)
    invoice, eta = await gateway.check_for_new_fiscal_receipts(
        invoice=invoice, context=stq3_context, log_extra=None,
    )
    assert invoice['billing_tech']['version'] == expected_version
    actual_transactions = _get_actual_transactions(invoice)
    expected_transactions = _strip_trust_settings(expected_transactions)
    assert _updated_has_not_changed(invoice, updated)
    assert actual_transactions == expected_transactions
    assert eta == expected_eta


def _gen_set_clear_time_from_trust_cases():
    @dataclasses.dataclass(frozen=True)
    class _Outcome:
        clear_ts: Optional[str]
        expected_cleared: datetime.datetime

    def _gen_cases(
            transactions_type: str,
            initial_statuses: List[str],
            trust_statuses: List[str],
            outcomes: List[_Outcome],
    ):
        case_inputs = itertools.product(
            initial_statuses, trust_statuses, outcomes,
        )
        result = []
        for case_input in case_inputs:
            initial_status, trust_status, outcome = case_input
            result.append(
                (
                    transactions_type,
                    initial_status,
                    trust_status,
                    outcome.clear_ts,
                    outcome.expected_cleared,
                ),
            )
        return result

    outcomes_with_enabled_usage = [
        _Outcome(_TRUST_CLEAR_TS, _TRUST_CLEAR_TIME),
        _Outcome(None, _NOW),
    ]

    transactions_cases = _gen_cases(
        transactions_type='transactions',
        initial_statuses=['hold_pending', 'clear_pending', 'hold_init'],
        trust_statuses=['cleared'],
        outcomes=outcomes_with_enabled_usage,
    )
    compensations_cases_with_config = _gen_cases(
        transactions_type='compensations',
        initial_statuses=['compensation_pending'],
        trust_statuses=['cleared', 'refunded'],
        outcomes=outcomes_with_enabled_usage,
    )
    return transactions_cases + [
        pytest.param(*case) for case in compensations_cases_with_config
    ]


@pytest.mark.parametrize(
    'transactions_type, initial_status, trust_status, clear_ts, '
    'expected_cleared',
    [*_gen_set_clear_time_from_trust_cases()],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(orders='for_test_set_clear_time_from_trust')
@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_set_clear_time_from_trust(
        stq3_context,
        now,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_pay_basket,
        get_gateway_wrapper,
        transactions_type,
        initial_status,
        trust_status,
        clear_ts,
        expected_cleared,
):
    expected_status = {
        'transactions': 'clear_success',
        'compensations': 'compensation_success',
    }[transactions_type]
    cleared_field = {
        'transactions': 'cleared',
        'compensations': 'compensation_made_at',
    }[transactions_type]
    invoice_id = 'for_test_set_clear_time_from_trust'
    collection = stq3_context.transactions.invoices
    transaction = _transaction_from_stub(changes=dict(status=initial_status))
    await _set_transactions(
        invoice_id=invoice_id,
        collection=collection,
        transactions=[transaction],
        updated=now,
        transactions_type=transactions_type,
    )
    mock_trust_check_basket(
        purchase_token=transaction.id,
        payment_status=trust_status,
        clear_ts=clear_ts,
    )
    mock_trust_check_basket_full(
        purchase_token=transaction.id,
        payment_status=trust_status,
        clear_ts=clear_ts,
    )
    mock_trust_pay_basket(
        purchase_token=transaction.id,
        payment_status=trust_status,
        clear_ts=clear_ts,
    )
    invoice = await _get_invoice(invoice_id, stq3_context)
    await get_gateway_wrapper(transactions_type).check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    invoice = await _get_invoice(invoice_id, stq3_context)
    transaction = invoice['billing_tech'][transactions_type][0]
    assert transaction['status'] == expected_status
    assert transaction[cleared_field] == expected_cleared


@pytest.mark.parametrize(
    'test_data_path',
    [
        'cases/successful_clear.json',
        'cases/successful_refund.json',
        'cases/successful_compensation.json',
        'cases/successful_compensation_refund.json',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(orders='for_test_flag_for_tlog_notification')
async def test_flag_for_tlog_notification(
        stq3_context,
        load_py_json,
        now,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_check_refund,
        get_gateway_wrapper,
        test_data_path,
):
    test_data = load_py_json(test_data_path)
    mock_trust_check_basket(
        purchase_token='purchase-token', payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='purchase-token', payment_status='cleared',
    )
    mock_trust_check_refund(
        trust_refund_id='trust-refund-id', expect_headers={'X-Uid': '123'},
    )
    invoice = await _get_invoice(test_data['invoice_id'], stq3_context)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    gateway_wrapper = get_gateway_wrapper(test_data['transactions_type'])
    await gateway_wrapper.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert tlog_notifier.flag_for_notification.call_count == 1
    call_args, call_kwargs = tlog_notifier.flag_for_notification.call_args
    assert not call_kwargs
    upd_set, prefix, transaction = call_args
    expected_call = test_data['expected_call']
    assert isinstance(upd_set, dict)
    assert prefix == expected_call['prefix']
    helpers.match_dict(
        a_dict=transaction, template=expected_call['transaction'],
    )


@pytest.mark.parametrize(
    'test_case_path',
    [
        'cases/do_refund_pending.json',
        'cases/check_refund_pending.json',
        'cases/do_refund_success_with_create_ts.json',
        'cases/check_refund_success_with_create_ts.json',
        'cases/compensation_do_refund_pending.json',
        'cases/compensation_check_refund_pending.json',
        'cases/compensation_do_refund_success_with_create_ts.json',
        'cases/compensation_check_refund_success_with_create_ts.json',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(orders='for_test_fetch_lost_and_found')
async def test_fetch_lost_and_found_on_refund(
        load_py_json, now, setup_fetch_lost_and_found_test, test_case_path,
):
    """
    Test that lost and found data (refund create_ts, basket terminal ID) is
    fetched on refunds
    """
    test_case = load_py_json(test_case_path)
    await _check_fetch_lost_and_found_on_refund(
        setup_fetch_lost_and_found_test,
        check_basket_response=test_case['check_basket_response'],
        start_refund_status=test_case['start_refund_status'],
        check_refund_status=test_case['check_refund_status'],
        transactions_type=test_case['transactions_type'],
        invoice_id=test_case['invoice_id'],
        transactions=test_case.get('transactions'),
        compensations=test_case.get('compensations'),
        expected_check_basket_times_called=(
            test_case['expected_check_basket_times_called']
        ),
        expected_start_refund_times_called=(
            test_case['expected_start_refund_times_called']
        ),
        expected_check_refund_times_called=(
            test_case['expected_check_refund_times_called']
        ),
        expected_transaction_status=test_case['expected_transaction_status'],
        expected_refund_status=test_case['expected_refund_status'],
        expected_refund_made_at=test_case['expected_refund_made_at'],
        expected_terminal_id=test_case['expected_terminal_id'],
    )


@pytest.mark.parametrize('expected_terminal_id', [None, 42])
@pytest.mark.parametrize(
    'test_case_path',
    [
        'cases/do_refund_pending.json',
        'cases/check_refund_pending.json',
        'cases/do_refund_success.json',
        'cases/check_refund_success.json',
        'cases/compensation_do_refund_pending.json',
        'cases/compensation_check_refund_pending.json',
        'cases/compensation_do_refund_success.json',
        'cases/compensation_check_refund_success.json',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(orders='for_test_fetch_lost_and_found')
async def test_fetch_terminal_id_on_refund(
        load_py_json,
        now,
        setup_fetch_lost_and_found_test,
        test_case_path,
        expected_terminal_id,
):
    test_case = load_py_json(test_case_path)
    if expected_terminal_id is None:
        check_basket_response = load_py_json(
            'data/check_basket_response_no_terminal_id.json',
        )
    else:
        check_basket_response = load_py_json(
            'data/check_basket_response_with_terminal_id.json',
        )
    await _check_fetch_lost_and_found_on_refund(
        setup_fetch_lost_and_found_test,
        check_basket_response=check_basket_response,
        start_refund_status=test_case['start_refund_status'],
        check_refund_status=test_case['check_refund_status'],
        transactions_type=test_case['transactions_type'],
        invoice_id=test_case['invoice_id'],
        transactions=test_case.get('transactions'),
        compensations=test_case.get('compensations'),
        expected_check_basket_times_called=(
            test_case['expected_check_basket_times_called']
        ),
        expected_start_refund_times_called=(
            test_case['expected_start_refund_times_called']
        ),
        expected_check_refund_times_called=(
            test_case['expected_check_refund_times_called']
        ),
        expected_transaction_status=test_case['expected_transaction_status'],
        expected_refund_status=test_case['expected_refund_status'],
        expected_refund_made_at=test_case['expected_refund_made_at'],
        expected_terminal_id=expected_terminal_id,
    )


@pytest.mark.parametrize(
    'check_basket_response_path',
    [
        'data/no_refunds_field.json',
        'data/refund_missing.json',
        'data/no_create_ts.json',
    ],
)
@pytest.mark.parametrize(
    'test_case_path',
    [
        'cases/do_refund.json',
        'cases/check_refund.json',
        'cases/compensation_do_refund.json',
        'cases/compensation_check_refund.json',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.filldb(orders='for_test_fetch_lost_and_found')
async def test_fetch_create_ts_error_on_refund(
        load_py_json,
        now,
        setup_fetch_lost_and_found_test,
        test_case_path,
        check_basket_response_path,
):
    test_case = load_py_json(test_case_path)
    check_basket_response = load_py_json(check_basket_response_path)
    await _check_fetch_lost_and_found_on_refund(
        setup_fetch_lost_and_found_test,
        check_basket_response=check_basket_response,
        start_refund_status=test_case['start_refund_status'],
        check_refund_status=test_case['check_refund_status'],
        transactions_type=test_case['transactions_type'],
        invoice_id=test_case['invoice_id'],
        transactions=test_case.get('transactions'),
        compensations=test_case.get('compensations'),
        expected_check_basket_times_called=(
            test_case['expected_check_basket_times_called']
        ),
        expected_start_refund_times_called=(
            test_case['expected_start_refund_times_called']
        ),
        expected_check_refund_times_called=(
            test_case['expected_check_refund_times_called']
        ),
        expected_transaction_status=test_case['expected_transaction_status'],
        expected_refund_status=test_case['expected_refund_status'],
        expected_refund_made_at=_NOW,
        expected_terminal_id=42,
    )


@pytest.mark.parametrize(
    'testcase_json, ',
    [
        'full_cancel_and_unhold_disabled.json',
        'full_cancel_and_unhold_enabled.json',
        'partial_cancel_and_unhold_enabled.json',
        'full_cancel_with_previous_resize_and_unhold_enabled.json',
        'full_cancel_without_initial_sum_and_unhold_enabled.json',
    ],
)
@pytest.mark.filldb(orders='for_test_unhold')
async def test_start_unhold(
        patch, stq3_context, load_py_json, *, testcase_json,
):
    testcase = load_py_json(testcase_json)
    gateway = trust.TrustGateway(['card'], stq3_context)
    features = asynctest.Mock(spec=gateway_features.Features)
    features.use_trust_unhold_on_full_cancel.side_effect = (
        lambda external_payment_id, uid: testcase['unhold_enabled']
    )
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    await gateway.start_new_transaction(
        invoice=invoice,
        to_hold=basket.Basket({}),
        to_refund=basket.Basket.make_from_sum_items(testcase['to_refund']),
        payment_type=const.PaymentType('card'),
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    assert features.use_trust_unhold_on_full_cancel.call_count == (
        testcase['expected_use_trust_unhold_on_full_cancel_call_count']
    )
    assert not tlog_notifier.method_calls
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction['status'] == testcase['expected_transaction_status']


@pytest.mark.parametrize(
    'testcase_json, ',
    [
        'trust_status_payment_status_updated.json',
        'trust_status_already_unheld.json',
        'trust_status_already_sbp_unheld.json',
        'trust_status_unexpected_status.json',
    ],
)
@pytest.mark.filldb(orders='for_test_unhold')
async def test_unhold_init(
        stq3_context, load_py_json, patch, mock_trust_unhold, *, testcase_json,
):
    testcase = load_py_json(testcase_json)
    unhold_mock = mock_trust_unhold(
        purchase_token='purchase-token', status_code=testcase['trust_status'],
    )
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    gateway = trust.TrustGateway(['card'], stq3_context)
    await gateway.check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    assert unhold_mock.times_called == 1
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction['status'] == testcase['expected_transaction_status']


@pytest.mark.parametrize(
    'testcase_json, ',
    ['trust_status_canceled.json', 'trust_status_unexpected_status.json'],
)
@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.filldb(orders='for_test_unhold')
@pytest.mark.now(_NOW.isoformat())
async def test_unhold_pending(
        stq3_context,
        load_py_json,
        patch,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        *,
        testcase_json,
):
    testcase = load_py_json(testcase_json)
    check_basket_mock = mock_trust_check_basket(
        purchase_token='purchase-token',
        payment_status=testcase['trust_status'],
    )
    check_basket_full_mock = mock_trust_check_basket_full(
        purchase_token='purchase-token',
        payment_status=testcase['trust_status'],
    )
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    gateway = trust.TrustGateway(['card'], stq3_context)
    await gateway.check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    assert check_basket_mock.times_called == 1
    if testcase['trust_status'] == 'canceled':
        assert check_basket_full_mock.times_called == 1
    else:
        assert check_basket_full_mock.times_called == 0
    invoice = await _get_invoice(testcase['invoice_id'], stq3_context)
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction['status'] == testcase['expected_transaction_status']
    expected_unheld_time = testcase['expected_unheld_time']
    if expected_unheld_time is None:
        assert 'unheld' not in transaction
    else:
        assert transaction['unheld'] == expected_unheld_time


@pytest.mark.filldb(orders='for_test_unhold')
@pytest.mark.now(_NOW.isoformat())
async def test_unhold_clear(stq3_context):
    invoice_id = 'unhold-clear-init-invoice-id'
    invoice = await _get_invoice(invoice_id, stq3_context)
    gateway = trust.TrustGateway(['card'], stq3_context)
    await gateway.check_pending_transactions(
        invoice=invoice,
        context=stq3_context,
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
    )
    invoice = await _get_invoice(invoice_id, stq3_context)
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 1
    transaction = transactions[0]
    assert transaction['status'] == 'clear_success'
    assert transaction['cleared'] == _NOW


async def _check_fetch_lost_and_found_on_refund(
        setup_function,
        check_basket_response: dict,
        start_refund_status: str,
        check_refund_status: str,
        transactions_type: str,
        invoice_id: str,
        transactions: Optional[List[dict]],
        compensations: Optional[List[dict]],
        expected_check_basket_times_called: int,
        expected_start_refund_times_called: int,
        expected_check_refund_times_called: int,
        expected_transaction_status: str,
        expected_refund_status: str,
        expected_refund_made_at: Optional[datetime.datetime],
        expected_terminal_id: Optional[int],
):
    setup = await setup_function(
        check_basket_response=check_basket_response,
        start_refund_status=start_refund_status,
        check_refund_status=check_refund_status,
        transactions_type=transactions_type,
        invoice_id=invoice_id,
        transactions=transactions,
        compensations=compensations,
    )
    assert (
        setup.check_basket_mock.times_called
        == expected_check_basket_times_called
    )
    assert (
        setup.start_refund_mock.times_called
        == expected_start_refund_times_called
    )
    assert (
        setup.check_refund_mock.times_called
        == expected_check_refund_times_called
    )
    invoice = await _get_invoice(invoice_id, setup.context)
    actual_transactions = invoice['billing_tech'][setup.transactions_field]
    assert len(actual_transactions) == 1
    transaction = actual_transactions[0]
    assert transaction['status'] == expected_transaction_status
    assert transaction.get('terminal_id') == expected_terminal_id
    assert len(transaction['refunds']) == 1
    refund = transaction['refunds'][0]
    assert refund['status'] == expected_refund_status
    assert refund.get('refund_made_at') == expected_refund_made_at


@pytest.fixture(name='setup_fetch_lost_and_found_test')
def _setup_fetch_lost_and_found_test(
        stq3_context,
        now,
        mockserver,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_start_refund,
        mock_trust_check_refund,
        get_gateway_wrapper,
):
    async def do_setup(
            check_basket_response: dict,
            start_refund_status: str,
            check_refund_status: str,
            transactions_type: str,
            invoice_id: str,
            transactions: Optional[List[dict]],
            compensations: Optional[List[dict]],
    ) -> FetchLostAndFoundSetup:
        @mockserver.json_handler(
            '/trust-payments/v2/payment_status/purchase-token/',
        )
        def mock_trust_check_basket(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'purchase-token',
                'payment_status': 'cleared',
            }
            resp_body.update(check_basket_response)
            return mockserver.make_response(status=200, json=resp_body)

        @mockserver.json_handler('/trust-payments/v2/payments/purchase-token/')
        def mock_trust_check_basket_full(request):
            resp_body = {
                'status': 'success',
                'purchase_token': 'purchase-token',
                'payment_status': 'cleared',
            }
            resp_body.update(check_basket_response)
            return mockserver.make_response(status=200, json=resp_body)

        start_refund_mock = mock_trust_start_refund(
            status=start_refund_status, trust_refund_id='trust-refund-id',
        )
        check_refund_mock = mock_trust_check_refund(
            status=check_refund_status, trust_refund_id='trust-refund-id',
        )
        collection = stq3_context.transactions.invoices
        transactions_field = transactions_type
        transactions = {
            'transactions': transactions,
            'compensations': compensations,
        }[transactions_field]
        assert transactions is not None
        await collection.update_one(
            {'_id': invoice_id},
            {'$set': {f'billing_tech.{transactions_field}': transactions}},
        )
        invoice = await _get_invoice(invoice_id, stq3_context)
        gateway_wrapper = get_gateway_wrapper(transactions_type)
        await gateway_wrapper.check_pending_transactions(
            invoice=invoice,
            context=stq3_context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )

        return FetchLostAndFoundSetup(
            context=stq3_context,
            check_basket_mock=mock_trust_check_basket,
            mock_trust_check_basket_full=mock_trust_check_basket_full,
            start_refund_mock=start_refund_mock,
            check_refund_mock=check_refund_mock,
            transactions_field=transactions_field,
        )

    return do_setup


async def _set_transactions(
        invoice_id,
        collection,
        transactions,
        updated,
        transactions_type: str = 'transactions',
):
    transactions_for_update = []
    for a_transaction in transactions:
        transactions_for_update.append(
            _make_transaction_for_update(
                a_transaction, updated, transactions_type,
            ),
        )
    transactions_key = f'billing_tech.{transactions_type}'
    await collection.update_one(
        {'_id': invoice_id},
        {'$set': {transactions_key: transactions_for_update}},
    )


def _make_transaction_for_update(
        transaction: Transaction, updated, transactions_type: str,
):
    body = {
        'billing_response': {'fiscal_status': 'inprogress'},
        'purchase_token': transaction.id,
        'refunds': [
            _make_refund_for_update(refund, updated)
            for refund in transaction.refunds
        ],
        'request_id': f'request-id-{transaction.id}',
        'status': transaction.status,
        'has_new_fiscal_receipts': transaction.has_new_receipts,
        'sum': {'ride': 1980000},
        'trust_payment_id': 'trust-payment-id-{transaction.id}',
        'updated': updated,
    }
    if transactions_type == 'transactions':
        body['card_owner_uid'] = _TRANSACTION_UID
        body['payment_method_type'] = 'googlepay'
    elif transactions_type == 'compensations':
        body['owner_uid'] = _TRANSACTION_UID
    else:
        raise RuntimeError(f'Unknown transactions type {transactions_type}')
    if transaction.initial_sum is not None:
        body['initial_sum'] = {'ride': transaction.initial_sum}

    if transaction.receipt is not None:
        body['billing_response']['fiscal_receipt_url'] = transaction.receipt
    if transaction.clearing_receipt is not None:
        body['billing_response'][
            'fiscal_receipt_clearing_url'
        ] = transaction.clearing_receipt
    if transaction.attempts is not None:
        body['fiscal_receipts_attempts'] = transaction.attempts
    if transaction.eta is not None:
        body['fiscal_receipts_attempt_eta'] = transaction.eta
    return body


def _make_refund_for_update(refund, updated):
    body = {
        'billing_response': refund.trust_response or {},
        'status': refund.status,
        'trust_refund_id': refund.id,
        'updated': updated,
    }
    if refund.receipt is not None:
        body['billing_response']['fiscal_receipt_url'] = refund.receipt
    return body


def _make_refund(body):
    return Refund(
        id=body['trust_refund_id'],
        status=body['status'],
        receipt=body['billing_response'].get('fiscal_receipt_url'),
    )


def _make_transaction(body):
    initial_sum = body.get('initial_sum', {}).get('ride')
    return Transaction(
        id=body['purchase_token'],
        status=body['status'],
        attempts=body.get('fiscal_receipts_attempts'),
        eta=body.get('fiscal_receipts_attempt_eta'),
        has_new_receipts=body['has_new_fiscal_receipts'],
        receipt=body['billing_response'].get('fiscal_receipt_url'),
        clearing_receipt=body['billing_response'].get(
            'fiscal_receipt_clearing_url',
        ),
        refunds=[_make_refund(refund_body) for refund_body in body['refunds']],
        initial_sum=initial_sum,
    )


def _get_actual_transactions(invoice):
    transactions = []
    for transaction_body in invoice['billing_tech']['transactions']:
        transactions.append(_make_transaction(transaction_body))
    return transactions


async def _get_invoice(invoice_id, context):
    collection = context.transactions.invoices
    invoice_data = await collection.find_one({'_id': invoice_id})
    return wrappers.make_invoice(
        invoice_data, fields=context.transactions.fields,
    )


def _updated_has_not_changed(invoice, updated) -> bool:
    for transaction in invoice['billing_tech']['transactions']:
        if transaction['updated'] != updated:
            return False
        for refund in transaction['refunds']:
            if refund['updated'] != updated:
                return False
    return True


@pytest.fixture
def _patch_random(patch):
    @patch('random.random')
    def random():
        return 0.5

    return random


def _strip_trust_settings(transactions):
    result = []
    for transaction in transactions:
        refunds = [
            dataclasses.replace(
                refund, trust_receipt=None, trust_response=None,
            )
            for refund in transaction.refunds
        ]
        result.append(
            dataclasses.replace(
                transaction,
                refunds=refunds,
                trust_receipt=None,
                trust_clearing_receipt=None,
            ),
        )
    return result


def _get_payment_status(status):
    if status == 'clear_success':
        return 'cleared'
    raise ValueError(f'Unknown status {status}')


class _GatewayWrapper(abc.ABC):
    async def check_pending_transactions(
            self, invoice, context, tlog_notifier,
    ):
        raise NotImplementedError


class TrustGateway(_GatewayWrapper):
    async def check_pending_transactions(
            self, invoice, context, tlog_notifier,
    ):
        gateway = trust.TrustGateway(['card'], context)
        await gateway.check_pending_transactions(
            invoice=invoice, context=context, tlog_notifier=tlog_notifier,
        )


class TrustCompensationGateway(_GatewayWrapper):
    async def check_pending_transactions(
            self, invoice, context, tlog_notifier,
    ):
        gateway = trust_compensation.TrustGateway(['card'], context)
        await gateway.check_pending_compensations(
            invoice=invoice,
            compensations=invoice.compensations,
            context=context,
            counter=handling.AttemptsCounter(),
            tlog_notifier=tlog_notifier,
            log_extra=None,
        )


@pytest.fixture(name='get_gateway_wrapper')
async def _get_gateway_wrapper():
    def _get(transactions_type) -> _GatewayWrapper:
        if transactions_type == 'transactions':
            return TrustGateway()
        error_msg = f'Unknown transactions type {transactions_type}'
        assert transactions_type == 'compensations', error_msg
        return TrustCompensationGateway()

    return _get


@pytest.mark.filldb(orders='for_test_check_pending_transactions')
@pytest.mark.parametrize(
    'clear_basket_response,expected_status,expected_exception',
    [
        pytest.param(
            {'status': 'success'},
            'has_pending',
            contextlib.nullcontext(),
            marks=pytest.mark.config(
                TRANSACTIONS_CLEAR_ATTEMPTS_BACKOFF={
                    'min_interval': 2,
                    'max_interval': 1800,
                    'max_attempts': 10,
                },
            ),
        ),
        pytest.param(
            {'status': 'error', 'status_code': 'Server error'},
            'no_pending',
            contextlib.nullcontext(),
            marks=pytest.mark.config(
                TRANSACTIONS_CLEAR_ATTEMPTS_BACKOFF={
                    'min_interval': 2,
                    'max_interval': 1800,
                    'max_attempts': 10,
                },
            ),
        ),
        pytest.param(
            {'status': 'error', 'status_code': 'Server error'},
            'no_pending',
            pytest.raises(RuntimeError),
            marks=pytest.mark.config(
                TRANSACTIONS_CLEAR_ATTEMPTS_BACKOFF={
                    'min_interval': 2,
                    'max_interval': 1800,
                    'max_attempts': 0,
                },
            ),
        ),
    ],
)
@pytest.mark.now('2022-05-30T14:00:00')
async def test_check_pending_transactions_backoff(
        stq3_context,
        mockserver,
        clear_basket_response,
        expected_status,
        expected_exception,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/trust-payments/v2/payments/purchase-token/clear/',
    )
    async def mock_trust_clear_basket(request):
        return clear_basket_response

    invoice = await _get_invoice('invoice-id', stq3_context)
    gateway = trust.TrustGateway(['card'], stq3_context)
    with expected_exception:
        actual_status = await gateway.check_pending_transactions(
            invoice=invoice,
            context=stq3_context,
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        )
        assert actual_status == expected_status
