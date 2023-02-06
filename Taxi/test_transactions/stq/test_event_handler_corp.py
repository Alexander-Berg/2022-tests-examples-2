import datetime

import pytest

from taxi.util import dates
from taxi.util import unused

from test_transactions import helpers
from transactions.internal.payment_gateways import corp as corp_gateway
from transactions.stq import events_handler

# mocks consts
INVOICE_ID = '111111-222222'
OPERATION_ID = 'create:55555555555555555555555555555555'
OPERATION_ID_REFUND = 'create:66666666666666666666666666666666'
OPERATION_ID_FULL_REFUND = 'create:77777777777777777777777777777777'
X_YA_REQUEST_ID = '99999999999999999999999999999999'

# corp-billing consts
SUCCESS = 'SUCCESS'
FAIL = 'FAIL'
TECHNICAL_ERROR = 'TECHNICAL_ERROR'
INVALID_PAYMENT_METHOD = 'INVALID_PAYMENT_METHOD'

_NOW_DATETIME = datetime.datetime(
    2019, 6, 3, 12, 0, tzinfo=datetime.timezone.utc,
)
_NOW = _NOW_DATETIME.isoformat()

# transactions consts
STQ_ETA = datetime.datetime(1970, 1, 1, 0, 0)  # always in past
DONE = 'done'
CLEAR_SUCCESS = 'clear_success'
FAILED = 'failed'
CLEAR = 'clear'

OPERATION_FINISH = 'operation_finish'
TRANSACTION_CLEAR = 'transaction_clear'


@pytest.mark.now(_NOW)
async def test_full_cycle(
        _close_order_handler,
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _clear_invoice,
        _full_refund_invoice,
        _exec_stq_until_no_tasks_left,
        _get_invoice,
):
    # create invoice doesn't start anything
    await _create_invoice()
    tasks = await _exec_stq_until_no_tasks_left()
    assert not _corp_ok_handler.times_called
    assert tasks.empty()

    # update invoice starts hold procedure, which ends with notification
    await _update_invoice()
    tasks = await _exec_stq_until_no_tasks_left()
    amount = _extract_amount(_corp_ok_handler.next_call()['request'])
    assert amount == '279.00'
    assert not _corp_ok_handler.times_called
    expected_args = [INVOICE_ID, OPERATION_ID, DONE, OPERATION_FINISH]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-1',
                'payment_type': 'corp',
                'status': 'hold_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    assert not tasks.payments_eda

    # clear just marks transaction cleared and notify payments-eda
    await _clear_invoice()
    tasks = await _exec_stq_until_no_tasks_left()
    assert not _corp_ok_handler.times_called
    expected_args = [
        INVOICE_ID,
        'create:55555555555555555555555555555555',
        DONE,
        TRANSACTION_CLEAR,
    ]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-1',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    assert not tasks.payments_eda

    # refund can be done on any sum
    refund_sum = '100.00'
    await _update_invoice(OPERATION_ID_REFUND, refund_sum)
    tasks = await _exec_stq_until_no_tasks_left()
    amount = _extract_amount(_corp_ok_handler.next_call()['request'])
    assert amount == refund_sum
    assert not _corp_ok_handler.times_called
    expected_args = [INVOICE_ID, OPERATION_ID_REFUND, DONE, OPERATION_FINISH]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-2',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    # clear starts automatically if any invoice transaction was cleared before
    expected_args = [INVOICE_ID, OPERATION_ID_REFUND, DONE, TRANSACTION_CLEAR]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-2',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    assert not tasks.payments_eda

    # refund must work with empty items list
    await _full_refund_invoice(OPERATION_ID_FULL_REFUND)
    tasks = await _exec_stq_until_no_tasks_left()
    amount = _extract_amount(_corp_ok_handler.next_call()['request'])
    assert amount == '0'
    assert not _corp_ok_handler.times_called
    expected_args = [
        INVOICE_ID,
        OPERATION_ID_FULL_REFUND,
        DONE,
        OPERATION_FINISH,
    ]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-3',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    # clear starts automatically if any invoice transaction was cleared before
    expected_args = [
        INVOICE_ID,
        OPERATION_ID_FULL_REFUND,
        DONE,
        TRANSACTION_CLEAR,
    ]
    expected_kwargs = {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-3',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }

    task = tasks.payments_eda.pop(0)
    assert task['args'] == expected_args
    assert task['kwargs'] == expected_kwargs
    assert not tasks.payments_eda

    invoice = await _get_invoice(INVOICE_ID)
    assert invoice['billing_tech']['transactions']
    for transaction in invoice['billing_tech']['transactions']:
        assert transaction['trust_payment_id']
        assert 'purchase_token' not in transaction


def _corp_billing_fail_resp(load_json):
    body = load_json('corp_billing_response.json')
    body['status']['code'] = FAIL
    return 200, body


def _corp_billing_tech_error_resp(load_json):
    body = load_json('corp_billing_response.json')
    body['status']['code'] = TECHNICAL_ERROR
    return 200, body


def _corp_billing_409_resp(load_json):
    body = {'code': 'INVALID_PAYMENT_METHOD', 'message': 'some text'}
    return 409, body


@pytest.mark.parametrize(
    'fail_resp_func',
    [
        _corp_billing_fail_resp,
        _corp_billing_tech_error_resp,
        _corp_billing_409_resp,
    ],
)
async def test_hold_fail_behaviour(
        _pay_order_handler,
        _create_invoice,
        _update_invoice,
        _exec_stq,
        load_json,
        fail_resp_func,
):
    handler = _pay_order_handler(*fail_resp_func(load_json))
    await _create_invoice()
    await _update_invoice()

    # call corp-billing which does reject operation
    tasks = await _exec_stq()
    assert len(tasks.transactions) == 1
    assert not tasks.payments_eda
    assert bool(handler.next_call())
    assert not handler.times_called

    # notify payments-eda about failed hold
    tasks = await _exec_stq()
    assert not tasks.transactions
    assert _extract_notify_status(tasks.payments_eda.pop(0)) == FAILED
    assert not tasks.payments_eda
    assert not handler.times_called


@pytest.mark.parametrize('code', [400, 401, 403, 500, 502, 503])
async def test_stq_fails_on_corp_billing_error(
        _pay_order_handler, _create_invoice, _update_invoice, _exec_stq, code,
):
    body = {}
    _handler = _pay_order_handler(code, body)
    unused.dummy(_handler)
    await _create_invoice()
    await _update_invoice()
    with pytest.raises(corp_gateway.ServerError):
        await _exec_stq()


async def test_hold_fail_on_invalid_pass_params(
        _corp_ok_handler, _create_invoice, _update_invoice, _exec_stq,
):
    await _create_invoice(pass_params={})
    await _update_invoice()
    tasks = await _exec_stq()

    # no calls to corp-billing
    assert not _corp_ok_handler.times_called
    # going call transactions again to notify payments-eda
    assert len(tasks.transactions) == 1
    assert not tasks.payments_eda

    # notify on hold fail
    tasks = await _exec_stq()
    assert _extract_notify_status(tasks.payments_eda.pop(0)) == FAILED

    # nothing left to do
    assert tasks.empty()


async def test_request_to_corp_billing(
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _exec_stq_until_no_tasks_left,
        load_json,
        now,
):
    await _create_invoice()
    await _update_invoice()
    await _exec_stq_until_no_tasks_left()

    request = _corp_ok_handler.next_call()['request']

    taken_request_body = request.json
    taken_request_body['transaction_created_at'] = dates.timestring(
        dates.parse_timestring(taken_request_body['transaction_created_at']),
    )

    expected_request_body = load_json('corp_billing_request.json')
    expected_request_body['transaction_created_at'] = dates.timestring(now)

    assert taken_request_body == expected_request_body


@pytest.mark.now(_NOW)
async def test_notifications(
        _close_order_handler,
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _clear_invoice,
        _exec_stq_until_no_tasks_left,
):
    await _create_invoice()
    await _update_invoice()
    tasks = await _exec_stq_until_no_tasks_left()
    await _clear_invoice()
    tasks.extend(await _exec_stq_until_no_tasks_left())

    task = tasks.payments_eda.pop(0)
    assert task['id'] == '%s:%s:%s:%s' % (
        INVOICE_ID,
        OPERATION_ID,
        DONE,
        OPERATION_FINISH,
    )
    assert task['args'] == [INVOICE_ID, OPERATION_ID, DONE, OPERATION_FINISH]

    assert task['kwargs'] == {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-1',
                'payment_type': 'corp',
                'status': 'hold_success',
            },
        ],
        'log_extra': None,
    }
    task = tasks.payments_eda.pop(0)

    assert task['id'] == '%s:%s:%s:%s' % (
        INVOICE_ID,
        OPERATION_ID,
        DONE,
        TRANSACTION_CLEAR,
    )
    assert task['args'] == [INVOICE_ID, OPERATION_ID, DONE, TRANSACTION_CLEAR]

    assert task['kwargs'] == {
        'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
        'transactions': [
            {
                'external_payment_id': 'corp-transaction-id-1',
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
        'log_extra': None,
    }

    assert not tasks.payments_eda


async def test_nothing_if_stq_called_twice_on_hold(
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _exec_stq_until_no_tasks_left,
):
    await _create_invoice()
    await _update_invoice()
    await _exec_stq_until_no_tasks_left()

    tasks = await _exec_stq_until_no_tasks_left()
    assert tasks.empty()


async def test_nothing_if_stq_called_twice_on_clear(
        _close_order_handler,
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _clear_invoice,
        _exec_stq_until_no_tasks_left,
):
    await _create_invoice()
    await _update_invoice()
    await _exec_stq_until_no_tasks_left()
    await _clear_invoice()
    await _exec_stq_until_no_tasks_left()

    tasks = await _exec_stq_until_no_tasks_left()
    assert tasks.empty()


async def test_keep_corp_response_on_clear(
        _close_order_handler,
        _corp_ok_handler,
        _create_invoice,
        _update_invoice,
        _clear_invoice,
        _exec_stq_until_no_tasks_left,
        _get_invoice,
):
    await _create_invoice()
    await _update_invoice()
    await _exec_stq_until_no_tasks_left()

    invoice = await _get_invoice(INVOICE_ID)
    old = invoice['billing_tech']['transactions'][0]['billing_response']

    await _clear_invoice()
    await _exec_stq_until_no_tasks_left()

    invoice = await _get_invoice(INVOICE_ID)
    new = invoice['billing_tech']['transactions'][0]['billing_response']

    # There is no api handler that returns billing response. Developers
    # should take it from db. So just check value in db, it must not be
    # changed after clear procedure.
    assert old == new


@pytest.fixture
def _create_invoice(load_json, now, _call_web):
    async def _wrapper(pass_params=None):
        request_body = load_json('request_invoice_create.json')
        request_body['invoice_due'] = dates.timestring(now)
        if pass_params is not None:
            request_body['pass_params'] = pass_params
        tasks_transactions = await _call_web('/invoice/create', request_body)
        assert not tasks_transactions

    return _wrapper


@pytest.fixture
def _update_invoice(load_json, _call_web):
    async def _wrapper(operation_id=None, update_sum=None):
        request_body = load_json('request_invoice_update.json')
        if operation_id is not None:
            request_body['operation_id'] = operation_id
        if update_sum is not None:
            request_body['items'][0]['amount'] = update_sum
        tasks_transactions = await _call_web('/invoice/update', request_body)
        assert len(tasks_transactions) == 1

    return _wrapper


@pytest.fixture
def _full_refund_invoice(load_json, _call_web):
    async def _wrapper(operation_id):
        request_body = load_json('request_invoice_full_refund.json')
        request_body['operation_id'] = operation_id
        tasks_transactions = await _call_web('/invoice/update', request_body)
        assert len(tasks_transactions) == 1

    return _wrapper


@pytest.fixture
def _clear_invoice(now, _call_web):
    async def _wrapper():
        clear_eta = dates.timestring(now)
        request_body = {'id': INVOICE_ID, 'clear_eta': clear_eta}
        tasks_transactions = await _call_web('/invoice/clear', request_body)
        assert len(tasks_transactions) == 1

    return _wrapper


@pytest.fixture
def _call_web(stq, eda_web_app_client):
    async def _wrapper(url_path, request_body):
        with stq.flushing():
            response = await eda_web_app_client.post(
                url_path, json=request_body,
            )
            assert response.status == 200
            assert (await response.json()) == {}

            tasks_transactions = _get_transactions_tasks(stq)
            assert stq.is_empty

        return tasks_transactions

    return _wrapper


@pytest.fixture
def _exec_stq_until_no_tasks_left(_exec_stq):
    async def _wrapper():
        tasks = await _exec_stq()

        no_new_tasks_left = False
        for _i in range(10):
            new_tasks = await _exec_stq()
            if new_tasks.empty():
                no_new_tasks_left = True
                break
            tasks.extend(new_tasks)
        assert no_new_tasks_left

        return tasks

    return _wrapper


@pytest.fixture
def _exec_stq(eda_stq3_context, stq, now):
    async def _wrapper():
        with stq.flushing():
            await events_handler.task(
                eda_stq3_context,
                helpers.create_task_info(queue='transactions_eda_events'),
                INVOICE_ID,
            )

            class Tasks:
                transactions = _get_transactions_tasks(stq)
                payments_eda = _get_payments_eda_tasks(stq)

                def extend(self, other):
                    self.transactions.extend(other.transactions)
                    self.payments_eda.extend(other.payments_eda)

                def empty(self):
                    return not self.transactions and not self.payments_eda

            assert stq.is_empty

        return Tasks()

    return _wrapper


@pytest.fixture
def _corp_ok_handler(_pay_order_handler, load_json):
    state = {'index': 1}
    corp_billing_response = load_json('corp_billing_response.json')

    def response(request):
        body = corp_billing_response.copy()
        body['transaction_id'] += '-%s' % str(state['index'])
        state['index'] += 1
        return body

    return _pay_order_handler(200, response)


@pytest.fixture
def _pay_order_handler(mockserver):
    def _wrapper(status, body):
        @mockserver.json_handler('/corp-billing/v1/pay-order/eats')
        def handler(request):
            resp_body = body(request) if callable(body) else body
            headers = {'X-YaRequestId': X_YA_REQUEST_ID}
            return mockserver.make_response(
                status=status, headers=headers, json=resp_body,
            )

        return handler

    return _wrapper


@pytest.fixture
def _close_order_handler(mockserver, load_json):
    @mockserver.json_handler('/corp-billing/v1/close-order/eats')
    def _handler(request):
        resp_body = load_json('corp_billing_response.json')
        headers = {'X-YaRequestId': X_YA_REQUEST_ID}
        return mockserver.make_response(
            status=200, headers=headers, json=resp_body,
        )


@pytest.fixture
def _get_invoice(eda_stq3_context):
    async def _wrapper(invoice_id):
        invoices = eda_stq3_context.transactions.invoices
        assert invoices.name == 'eda_invoices'
        invoice = await invoices.find_one({'_id': invoice_id})
        return invoice

    return _wrapper


def _get_transactions_tasks(stq):
    tasks = []
    while stq.transactions_eda_events.has_calls:
        task = stq.transactions_eda_events.next_call()
        # these params never changed
        assert task['id'] == INVOICE_ID
        assert task['eta'] == STQ_ETA
        assert task['args'] == [INVOICE_ID]
        assert task['queue'] == 'transactions_eda_events'
        tasks.append(task)
    return tasks


def _get_payments_eda_tasks(stq):
    tasks = []
    while stq.payments_eda_callback.has_calls:
        task = stq.payments_eda_callback.next_call()
        assert task['eta'] == STQ_ETA
        assert task['queue'] == 'payments_eda_callback'
        tasks.append(task)
    return tasks


def _extract_amount(request):
    taken_request_body = request.json
    return taken_request_body['products'][0]['amount']


def _extract_notify_status(eda_task):
    return eda_task['args'][2]
