# pylint: disable=line-too-long
# flake8: noqa
import asynctest
import pytest
from transactions.internal import basket
from transactions.internal.payment_gateways.psp import gateway
from transactions.models import const
from transactions.models import gateway_features
from transactions.models import notify
from transactions.models import wrappers
from transactions.internal import transaction_statuses


@pytest.fixture(name='psp_payment_authorized_events_flow')
def _psp_payment_authorized_events_flow(load_py_json):
    return [
        {'request_id': '456', 'response': []},
        load_py_json('only_intent_created_event.json'),
        load_py_json('intent_and_payment_created_events.json'),
        load_py_json('payment_authorized_events.json'),
    ]


@pytest.fixture(name='intent_created_response')
def _intent_created_response(load_py_json):
    return load_py_json('intent_created_response.json')


@pytest.fixture(name='refund_created_response')
def _refund_created_response(load_py_json):
    return load_py_json('refund_created_response.json')


@pytest.fixture(name='events_response')
def _events_response(load_py_json):
    return load_py_json('events_response.json')


@pytest.fixture(name='psp_create_auth_event_sequence_mock')
def _psp_create_auth_event_sequence_mock(
        mockserver, psp_payment_authorized_events_flow,
):
    class _DoMock:
        def __init__(self):
            self.resp_index = 0

            @mockserver.json_handler('psp/events')
            def _handler():
                resp_body = psp_payment_authorized_events_flow[self.resp_index]
                self.resp_index = min(
                    self.resp_index + 1,
                    len(psp_payment_authorized_events_flow) - 1,
                )
                return mockserver.make_response(status=200, json=resp_body)

    return _DoMock


@pytest.fixture(name='psp_create_intent')
def _psp_create_intent(mockserver, load_py_json, intent_created_response):
    class _DoMock:
        def __init__(self):
            self.requests = []

            @mockserver.json_handler('psp/intents')
            def _handler(request):
                self.requests.append(request.json)
                return mockserver.make_response(
                    status=200, json=intent_created_response,
                )

    return _DoMock


@pytest.fixture(name='psp_create_refund')
def _psp_create_refund(mockserver, load_py_json, refund_created_response):
    class _DoMock:
        def __init__(self):
            @mockserver.json_handler('psp/refunds')
            def _handler(request):
                return mockserver.make_response(
                    status=200, json=refund_created_response,
                )

    return _DoMock


@pytest.fixture(name='psp_get_events')
def _psp_get_events(mockserver, load_py_json, events_response):
    class _DoMock:
        def __init__(self):
            @mockserver.json_handler('psp/events')
            def _handler(request):
                return mockserver.make_response(
                    status=200, json=events_response,
                )

    return _DoMock


@pytest.mark.filldb(orders='for_test_start_new_transaction')
@pytest.mark.parametrize(
    'testcase_json, ', ['start_new_transaction_card.json'],
)
@pytest.mark.config(
    TRANSACTIONS_PSP_GATEWAY_CONFIG={
        'payment_auth_timeout_days': 1,
        'payment_capture_timeout_days': 2,
        'intent_timeout_days': 30,
    },
    TRANSACTIONS_PSP_PAYMENT_METADATA={
        'payment_method': 'card-x5049e1e094a8a4077ced9586',
        'card_token': 'AY4aa4yc0GIoVzAR2W228OfOx/WP64N1ZHcHDk5BTsbNhXd8F89vbC9CGjWB7ymyBO6ZkGCV/h69q8/ibMb//YE=',
        'expiration_month': '12',
        'expiration_year': '2024',
        'cardholder': 'CARD HOLDER',
    },
    TRANSACTIONS_PSP_POS={
        'taxi': {'card': 'yandex_taxi_card_rub_payment_any_bank'},
    },
    TRANSACTIONS_BILLING_SERVICE_TOKENS={
        'card': {
            'billing_api_key': 'taxifee_8c7078d6b3334e03c1b4005b02da30f4',
            'billing_payments_service_id': 124,
            'cardstorage_service_type': 'card',
        },
    },
)
async def test_psp_happy_path_hold(
        db,
        stq3_context,
        load_py_json,
        psp_create_intent,
        psp_create_auth_event_sequence_mock,
        personal_tins_bulk_retrieve,
        personal_phones_retrieve,
        mock_cardstorage_payment_methods,
        *,
        testcase_json,
):
    personal_tins_bulk_retrieve()
    testcase = load_py_json(testcase_json)
    payment_type = const.PaymentType(testcase['payment_type'])
    to_hold = basket.Basket.make_from_sum_items(testcase['to_hold'])
    to_refund = basket.Basket.make_from_sum_items(testcase['to_refund'])

    expected_intent_requests = testcase['expected_taxi_create_intent_requests']
    create_intent = psp_create_intent()
    psp_create_auth_event_sequence_mock()

    psp_gateway = gateway.PSPGateway(stq3_context)
    invoice_id = testcase['invoice_id'] + '_' + 'taxi'
    invoice_data = await stq3_context.transactions.invoices.find_one(
        invoice_id,
    )
    assert invoice_data is not None
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    await psp_gateway.start_new_transaction(
        invoice=invoice,
        to_hold=to_hold,
        to_refund=to_refund,
        payment_type=payment_type,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_INIT

    # Hold
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert check_result == transaction_statuses.CHECKED_HAS_PENDING
    assert invoice.transactions[0].status == transaction_statuses.HOLD_PENDING
    assert len(create_intent.requests) == len(expected_intent_requests)
    for i, request in enumerate(create_intent.requests):
        compare_intent_requests(request, expected_intent_requests[i])

    # Got no events
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_PENDING
    assert check_result == transaction_statuses.CHECKED_HAS_PENDING

    # Got intent created event
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_PENDING
    assert check_result == transaction_statuses.CHECKED_HAS_PENDING

    # Got payment created event
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_PENDING
    assert check_result == transaction_statuses.CHECKED_HAS_PENDING

    # Got payment authorized event
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_SUCCESS
    assert check_result == transaction_statuses.CHECKED_HAS_REFRESHED

    # Got payment authorized event
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert invoice.transactions[0].status == transaction_statuses.HOLD_SUCCESS
    assert invoice.transactions[0].data['terminal_id'] == 666
    assert check_result == transaction_statuses.CHECKED_NO_PENDING


def compare_intent_requests(lhs: dict, rhs: dict):
    lhs_request = lhs.get('params', {})
    rhs_request = rhs.get('params', {})
    assert lhs_request.get('cost') == rhs_request.get('cost')
    assert lhs_request.get('service_id') == rhs_request.get('service_id')
    assert lhs_request.get('uid') == rhs_request.get('uid')
    compare_intent_payments(lhs_request, rhs_request)


def compare_intent_payments(lhs: dict, rhs: dict):
    assert len(lhs.get('payments', [])) == len(rhs.get('payments', []))

    for i, lhs_payment in enumerate(lhs.get('payments', [])):
        rhs_payment = rhs['payments'][i]
        lhs_payment = {
            key: lhs_payment[key]
            for key in lhs_payment
            if key
            not in [
                'uid',
                'external_id',
                'payment_session_id',
                'authorization_due_date',
            ]
        }
        rhs_payment = {
            key: rhs_payment[key]
            for key in rhs_payment
            if key
            not in [
                'uid',
                'external_id',
                'payment_session_id',
                'authorization_due_date',
            ]
        }
        lhs_payment.get('flow', {}).get('hold', {}).pop('due_date', None)
        rhs_payment.get('flow', {}).get('hold', {}).pop('due_date', None)
        assert lhs_payment == rhs_payment


@pytest.fixture(name='mock_cardstorage_payment_methods')
def _mock_cardstorage_payment_methods(mock_cardstorage):
    @mock_cardstorage('/v1/payment_methods')
    def _payment_methods(request):
        return {
            'available_cards': [
                {
                    'card_id': '1324',
                    'psp_payment_method_id': 'some_psp_payment_method_id',
                    'billing_card_id': '1324',
                    'currency': 'RUB',
                    'permanent_card_id': '',
                    'expiration_month': 12,
                    'expiration_year': 2025,
                    'number': '123456****8911',
                    'owner': 'abc',
                    'possible_moneyless': False,
                    'region_id': '225',
                    'regions_checked': [],
                    'system': 'visa',
                    'valid': True,
                    'bound': True,
                    'unverified': False,
                    'busy': False,
                    'busy_with': [],
                    'from_db': False,
                },
            ],
        }


@pytest.mark.parametrize(
    'testcase_json, ', ['full_cancel.json', 'partial_cancel.json'],
)
@pytest.mark.filldb(orders='for_test_resize')
async def test_start_resize(
        patch, stq3_context, load_py_json, *, testcase_json,
):
    testcase = load_py_json(testcase_json)
    psp_gateway = gateway.PSPGateway(stq3_context)
    invoice_id = testcase['invoice_id']
    invoice_data = await stq3_context.transactions.invoices.find_one(
        invoice_id,
    )
    assert invoice_data is not None
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    await psp_gateway.start_new_transaction(
        invoice=invoice,
        to_hold=basket.Basket({}),
        to_refund=basket.Basket.make_from_sum_items(testcase['to_refund']),
        payment_type=const.PaymentType('card'),
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    assert (
        invoice.transactions[0].status
        == testcase['expected_transaction_status']
    )


@pytest.mark.filldb(orders='for_test_refund')
@pytest.mark.parametrize('testcase_json, ', ['start_new_refund.json'])
async def test_start_refund(
        db,
        stq3_context,
        load_py_json,
        personal_tins_bulk_retrieve,
        personal_phones_retrieve,
        psp_create_refund,
        psp_get_events,
        *,
        testcase_json,
):
    personal_tins_bulk_retrieve()
    psp_create_refund()
    testcase = load_py_json(testcase_json)
    payment_type = const.PaymentType(testcase['payment_type'])
    to_hold = basket.Basket.make_from_sum_items(testcase['to_hold'])
    to_refund = basket.Basket.make_from_sum_items(testcase['to_refund'])

    psp_gateway = gateway.PSPGateway(stq3_context)
    invoice_id = testcase['invoice_id']
    invoice_data = await stq3_context.transactions.invoices.find_one(
        invoice_id,
    )
    assert invoice_data is not None
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    features = asynctest.Mock(spec=gateway_features.Features)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    await psp_gateway.start_new_transaction(
        invoice=invoice,
        to_hold=to_hold,
        to_refund=to_refund,
        payment_type=payment_type,
        features=features,
        tlog_notifier=tlog_notifier,
        context=stq3_context,
    )
    assert (
        invoice.transactions[0].status == transaction_statuses.REFUND_PENDING
    )
    assert invoice.transactions[0].refunds[0]['status'] == 'refund_pending'

    psp_get_events()
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert check_result == transaction_statuses.CHECKED_HAS_PENDING
    assert (
        invoice.transactions[0].status == transaction_statuses.REFUND_WAITING
    )
    assert invoice.transactions[0].refunds[0]['status'] == str(
        transaction_statuses.REFUND_WAITING,
    )

    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert check_result == transaction_statuses.CHECKED_HAS_REFRESHED
    assert invoice.transactions[0].status == transaction_statuses.CLEAR_SUCCESS
    assert invoice.transactions[0].refunds[0]['status'] == str(
        transaction_statuses.REFUND_SUCCESS,
    )


@pytest.mark.parametrize(
    'invoice_id, events_json, expected_status',
    [
        pytest.param(
            'hold_pending_invoice_id',
            'payment_hold_fail_events.json',
            'hold_fail',
            id='it should move hold_pending to hold_fail',
        ),
        pytest.param(
            'clear_pending_invoice_id',
            'payment_clear_fail_events.json',
            'clear_fail',
            id='it should move clear_pending to clear_fail',
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_transaction_fail')
async def test_transaction_fail(
        invoice_id,
        events_json,
        expected_status,
        stq3_context,
        mockserver,
        load_py_json,
):
    @mockserver.json_handler('psp/events')
    def _handler():
        return mockserver.make_response(
            status=200, json=load_py_json(events_json),
        )

    psp_gateway = gateway.PSPGateway(stq3_context)
    tlog_notifier = asynctest.Mock(spec=notify.TlogNotifier)
    invoice = await _fetch_invoice(invoice_id, stq3_context)
    check_result = await psp_gateway.check_pending_transactions(
        invoice=invoice, context=stq3_context, tlog_notifier=tlog_notifier,
    )
    assert check_result
    invoice_after = await _fetch_invoice(invoice_id, stq3_context)
    actual_status = invoice_after['billing_tech']['transactions'][0]['status']
    assert actual_status == expected_status


async def _fetch_invoice(invoice_id, stq3_context):
    invoice_data = await stq3_context.transactions.invoices.find_one(
        invoice_id,
    )
    assert invoice_data, f'invoice with id={invoice_id} was not found'
    return wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
