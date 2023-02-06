import datetime

import pytest

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.stq import events_handler

_NOW_DATETIME = datetime.datetime(2019, 6, 3, 12, 0)
_NOW = _NOW_DATETIME.isoformat()

COMMON_ORDER_ID = 'common_order_id'
EXTERNAL_PAYMENT_ID = 'tr1234'

SYSTEM_COMMON_ITEM_ID = f'system/common_item_id_{EXTERNAL_PAYMENT_ID}'


@pytest.fixture
def _prepare(personal_phones_retrieve, personal_emails_retrieve):
    def _inner():
        personal_phones_retrieve()
        personal_emails_retrieve()

    return _inner


@pytest.fixture
def _mock_trust_payments(mockserver):
    class Context:
        def __init__(self):
            self.amount = None
            self.times_called = 0

        def check_amount(self, amount):
            self.amount = amount

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def _mock_trust_create_basket(request):
        amount = request.json['amount']
        assert amount == context.amount
        context.times_called += 1
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
        }

    context = Context()

    return context


@pytest.fixture
def _mock_trust_refunds(mockserver):
    class Context:
        def __init__(self):
            self.amount = None
            self.times_called = 0

        def check_amount(self, amount):
            self.amount = amount

    @mockserver.json_handler('/trust-payments/v2/refunds/')
    def _mock_trust_create_refund(request):
        assert 'orders' in request.json
        orders = request.json['orders']
        assert len(orders) == 1
        order = orders[0]
        assert order['order_id'] == COMMON_ORDER_ID
        assert order['delta_amount'] == context.amount
        context.times_called += 1
        return {'status': 'success', 'trust_refund_id': 'trust-refund-id'}

    context = Context()

    return context


@pytest.fixture
def _mock_trust_status_full(mockserver):
    class Context:
        def __init__(self):
            self.times_called = 0

    @mockserver.json_handler(
        f'/trust-payments/v2/payments/{EXTERNAL_PAYMENT_ID}/',
    )
    def _mock_trust_status_full(request):
        context.times_called += 1
        return {
            'status': 'success',
            'orders': [{'order_id': COMMON_ORDER_ID}],
            'payment_status': 'authorized',
        }

    context = Context()

    return context


@pytest.fixture
def _mock_trust_resize(mockserver):
    class Context:
        def __init__(self):
            self.amount = None
            self.times_called = 0

        def check_amount(self, amount):
            self.amount = amount

    @mockserver.json_handler(
        (
            f'/trust-payments/v2/payments/{EXTERNAL_PAYMENT_ID}/'
            f'orders/{COMMON_ORDER_ID}/resize'
        ),
    )
    def _mock_trust_resize(request):
        assert request.json['amount'] == context.amount
        context.times_called += 1
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    context = Context()

    return context


@pytest.mark.now(_NOW)
async def test_hold(
        stq3_context: stq_context.Context, _mock_trust_payments, _prepare, stq,
):
    _prepare()
    _mock_trust_payments.check_amount('300')

    invoice_id = 'pending_invoice'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_payments.times_called == 1


@pytest.mark.now(_NOW)
async def test_refund(
        stq3_context: stq_context.Context,
        _mock_trust_status_full,
        _mock_trust_refunds,
        _prepare,
        stq,
):
    _prepare()
    _mock_trust_refunds.check_amount('70')

    invoice_id = 'clear_success'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_status_full.times_called == 1
    assert _mock_trust_refunds.times_called == 1

    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice is not None
    service_orders = invoice['billing_tech']['service_orders']
    assert SYSTEM_COMMON_ITEM_ID in service_orders
    assert service_orders[SYSTEM_COMMON_ITEM_ID] == COMMON_ORDER_ID


@pytest.mark.now(_NOW)
async def test_refund_common_order_id(
        stq3_context: stq_context.Context,
        _mock_trust_status_full,
        _mock_trust_refunds,
        _prepare,
        stq,
):
    _prepare()
    _mock_trust_refunds.check_amount('70')

    invoice_id = 'clear_success_common_order_id'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_status_full.times_called == 0
    assert _mock_trust_refunds.times_called == 1


@pytest.mark.now(_NOW)
async def test_resize(
        stq3_context: stq_context.Context,
        _mock_trust_status_full,
        _mock_trust_resize,
        _prepare,
        stq,
):
    _prepare()
    _mock_trust_resize.check_amount('160')

    invoice_id = 'hold_resize'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_status_full.times_called == 1
    assert _mock_trust_resize.times_called == 1

    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice is not None
    service_orders = invoice['billing_tech']['service_orders']
    assert SYSTEM_COMMON_ITEM_ID in service_orders
    assert service_orders[SYSTEM_COMMON_ITEM_ID] == COMMON_ORDER_ID


@pytest.mark.now(_NOW)
async def test_resize_common_order_id(
        stq3_context: stq_context.Context,
        _mock_trust_status_full,
        _mock_trust_resize,
        _prepare,
        stq,
):
    _prepare()
    _mock_trust_resize.check_amount('160')

    invoice_id = 'hold_resize_common_order_id'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_status_full.times_called == 0
    assert _mock_trust_resize.times_called == 1


@pytest.mark.now(_NOW)
async def test_no_items(
        stq3_context: stq_context.Context, _mock_trust_payments, _prepare, stq,
):
    _prepare()

    invoice_id = 'pending_invoice_no_items'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert _mock_trust_payments.times_called == 0


async def _run_task(context, invoice_id, queue='transactions_events'):
    await events_handler.task(
        context,
        helpers.create_task_info(queue=queue),
        invoice_id,
        log_extra=None,
    )
