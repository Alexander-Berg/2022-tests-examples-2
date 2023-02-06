import contextlib
import datetime
import logging

import asynctest
import pytest

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.internal import compensations_handler
from transactions.internal import handling
from transactions.internal.payment_gateways.compensation import interface
from transactions.models import invoices
from transactions.models import notify
from transactions.models import wrappers
from transactions.stq import compensation_events_handler
from transactions.stq import watchdog_events_handler

_WATCHDOG_LOGGER = 'transactions.stq.watchdog_events_handler'


@pytest.mark.parametrize(
    'testcase_json, ',
    [
        'test_round_sums.json',
        'test_sums_already_rounded.json',
        'test_round_sums_dry_run.json',
        'test_round_sums_disabled.json',
        'test_round_sums_dry_run_disabled.json',
    ],
)
@pytest.mark.now('2020-09-07T00:00:00')
@pytest.mark.filldb(orders='for_test_round_sums')
async def test_round_sums(stq3_context, load_py_json, *, testcase_json):
    testcase = load_py_json(testcase_json)
    collection = stq3_context.transactions.invoices
    enabled = testcase['enabled']
    dry_run = testcase['dry_run']
    stq3_context.config.TRANSACTIONS_REPAIR_COMPENSATION_SUMS_ENABLED = enabled
    stq3_context.config.TRANSACTIONS_REPAIR_COMPENSATION_SUMS_DRY_RUN = dry_run
    invoice_data = await collection.find_one({'_id': testcase['invoice_id']})
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    processing = await compensations_handler.process_compensations(
        invoice=invoice,
        context=stq3_context,
        operation=invoices.find_last_active_operation(invoice),
        counter=handling.AttemptsCounter(),
        tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
        log_extra=None,
    )
    invoice = processing.invoice
    compensations = invoice['billing_tech']['compensations']
    assert len(compensations) == 1
    compensation = compensations[0]
    assert len(compensation['refunds']) == 1
    refund = compensation['refunds'][0]
    assert compensation['sum'] == testcase['expected_sum']
    assert compensation['numeric_sum'] == testcase['expected_numeric_sum']
    assert refund['sum'] == testcase['expected_refund_sum']
    assert refund['numeric_sum'] == testcase['expected_refund_numeric_sum']
    assert invoice['billing_tech']['version'] == testcase['expected_version']


@pytest.mark.parametrize(
    'testcase_json',
    [
        'no_pending_compensations.json',
        'trust_pending_compensations.json',
        'tlog_pending_compensations.json',
        'trust_refreshed_no_pending_compensations.json',
        'tlog_refreshed_no_pending_compensations.json',
        'test_create_trust_compensation.json',
        'test_create_tlog_compensation.json',
        'test_create_trust_refund.json',
        'test_create_tlog_refund.json',
        'test_create_refund_compensation_not_found.json',
    ],
)
@pytest.mark.config(
    TRANSACTIONS_POLLING_BACKOFF_ALGO_ENABLED=True,
    TRANSACTIONS_POLLING_BACKOFF_ALGO={
        '__default__': {
            '__default__': {
                'data': {
                    'first_delays': [],
                    'max_delay': 1800,
                    'min_delay': 10,
                },
                'kind': 'exponential_backoff',
            },
        },
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-09-07T00:00:00')
@pytest.mark.filldb(orders='for_test_process_compensations')
async def test_process_compensations(
        stq3_context, load_py_json, patch, *, testcase_json,
):
    testcase = load_py_json(testcase_json)

    def _start_new_compensation(invoice, *args, **kwargs):
        return invoice, 0

    def _start_new_refund(invoice, *args, **kwargs):
        return invoice, 0

    def _mock_check_pending_compensations(refreshed):
        def _do_mock(invoice, *args, **kwargs):
            return invoice, refreshed

        return _do_mock

    trust_mock = asynctest.Mock(spec=interface.Gateway)
    tlog_mock = asynctest.Mock(spec=interface.Gateway)
    trust_mock.start_new_compensation.side_effect = _start_new_compensation
    tlog_mock.start_new_compensation.side_effect = _start_new_compensation
    trust_mock.start_new_refund.side_effect = _start_new_refund
    tlog_mock.start_new_refund.side_effect = _start_new_refund
    trust_mock.check_pending_compensations.side_effect = (
        _mock_check_pending_compensations(testcase['trust_refreshed'])
    )
    tlog_mock.check_pending_compensations.side_effect = (
        _mock_check_pending_compensations(testcase['tlog_refreshed'])
    )

    @patch(
        'transactions.internal.payment_gateways.compensation.selector.'
        'select_by_name',
    )
    def _select_by_name(name, context):
        if name == 'trust':
            return trust_mock
        if name == 'tlog':
            return tlog_mock
        raise RuntimeError('Unknown gateway, fix tests')

    @patch('random.shuffle')
    def _shuffle(array):
        array.sort()

    @patch('random.random')
    def _random():
        return 0.5

    collection = stq3_context.transactions.invoices
    await collection.update_one(
        {'_id': testcase['invoice_id']},
        {'$set': {'billing_tech.compensations': testcase['compensations']}},
    )
    invoice_data = await collection.find_one({'_id': testcase['invoice_id']})
    invoice = wrappers.make_invoice(
        invoice_data, fields=stq3_context.transactions.fields,
    )
    eta = None
    expected_error_message = testcase.get('expected_error_message')
    if expected_error_message is not None:
        expectation = pytest.raises(RuntimeError)
    else:
        expectation = contextlib.nullcontext()
    with expectation as error:
        processing = await compensations_handler.process_compensations(
            invoice=invoice,
            context=stq3_context,
            operation=invoices.Operation(
                parent_field='compensation_operations',
                index=0,
                values=testcase['operation'],
            ),
            counter=handling.AttemptsCounter(),
            tlog_notifier=asynctest.Mock(spec=notify.TlogNotifier),
            log_extra=None,
        )
        eta = processing.eta
    if error is not None:
        assert str(error.value) == expected_error_message
    assert eta == testcase['expected_eta']
    # pylint: disable=invalid-name
    actual_start_new_compensation_call_counts = {
        'trust': trust_mock.start_new_compensation.call_count,
        'tlog': tlog_mock.start_new_compensation.call_count,
    }
    # pylint: disable=invalid-name
    actual_start_new_refund_call_counts = {
        'trust': trust_mock.start_new_refund.call_count,
        'tlog': tlog_mock.start_new_refund.call_count,
    }
    # pylint: disable=invalid-name
    actual_check_pending_compensations_call_counts = {
        'trust': trust_mock.check_pending_compensations.call_count,
        'tlog': tlog_mock.check_pending_compensations.call_count,
    }
    assert actual_start_new_compensation_call_counts == (
        testcase['expected_start_new_compensation_call_counts']
    )
    assert actual_start_new_refund_call_counts == (
        testcase['expected_start_new_refund_call_counts']
    )
    assert actual_check_pending_compensations_call_counts == (
        testcase['expected_check_pending_compensations_call_counts']
    )


@pytest.mark.parametrize(
    'bp_admin_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                TRANSACTIONS_WATCHDOG_SEND_TO_BP_ADMIN=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_WATCHDOG_SEND_TO_BP_ADMIN=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'additional_arguments_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                TRANSACTIONS_ADDITIONAL_ARGUMENTS_ENABLED=True,
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TRANSACTIONS_ADDITIONAL_ARGUMENTS_ENABLED=False,
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'invoice_id, clear_result, payment_resp_code, transaction_status, '
    'expected_uid, is_failed_transaction',
    [
        (
            'refund_pending',
            'autorized',
            None,
            'autorized',
            'transaction-uid',
            True,
        ),
        (
            'compensation_pending',
            'autorized',
            None,
            'autorized',
            'transaction-uid',
            True,
        ),
        (
            'compensation_pending_ok',
            'autorized',
            None,
            'autorized',
            'transaction-uid',
            False,
        ),
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.filldb(orders='for_test_pending_tasks')
@pytest.mark.config(
    TRANSACTIONS_WATCHDOG_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_pending_tasks(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        invoice_id,
        clear_result,
        payment_resp_code,
        transaction_status,
        expected_uid,
        is_failed_transaction,
        additional_arguments_enabled,
        mock_bp_admin_v1_issue_register,
        bp_admin_enabled,
        caplog,
):
    caplog.set_level(logging.INFO, logger=_WATCHDOG_LOGGER)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/trust-payments/v2/refunds/refund1234/start/')
    async def mock_trust_start_refund(_request):
        assert 'X-Uid' in _request.headers
        assert _request.headers['X-Uid'] == 'transaction-uid'
        return {'status': clear_result, 'status_desc': 'some'}

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    async def mock_trust_check_basket(_request):
        assert _request.headers['X-Uid'] == expected_uid
        result = {
            'status': 'success',
            'payment_status': clear_result,
            'data': 'abcd',
            'terminal': {'id': 42},
        }
        if payment_resp_code is not None:
            result['payment_resp_code'] = payment_resp_code
        return result

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    async def mock_trust_check_basket_full(_request):
        assert _request.headers['X-Uid'] == expected_uid
        result = {
            'status': 'success',
            'payment_status': clear_result,
            'data': 'abcd',
            'terminal': {'id': 42},
        }
        if payment_resp_code is not None:
            result['payment_resp_code'] = payment_resp_code
        return result

    # check that pending transactions was planned to run later
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_compensation_events.times_called == 1
        task = stq.transactions_compensation_events.next_call()
        # check 10s offset from now for task eta for first reschedule
        assert task['eta'] == datetime.datetime(2020, 1, 1, 0, 0, 10)
        if is_failed_transaction:
            assert not stq.is_empty
            assert stq.transactions_watchdog.times_called == 1
            watchdog_task = stq.transactions_watchdog.next_call()
            assert watchdog_task
        else:
            assert stq.is_empty
            assert stq.transactions_watchdog.times_called == 0
        # check 10s offset from now for task eta for first reschedule
        assert task['eta'] == datetime.datetime(2020, 1, 1, 0, 0, 10)

    if is_failed_transaction:
        if bp_admin_enabled:
            mock_bp_admin_v1_issue_register()

        for event in watchdog_task['kwargs']['events']:
            assert event.get('amount')
            assert event.get('currency')

        with stq.flushing():
            await _run_watchdog_task(
                stq3_context,
                watchdog_task['kwargs']['events'],
                watchdog_task['kwargs']['invoice_id'],
            )

        if not bp_admin_enabled:
            records = [
                x.getMessage()
                for x in caplog.records
                if x.name == _WATCHDOG_LOGGER
            ]
            # we should see some watchdog log
            assert records


async def _run_task(stq3_context, invoice_id):
    await compensation_events_handler.task(
        stq3_context,
        helpers.create_task_info(queue='transactions_compensation_events'),
        invoice_id,
    )


async def _run_watchdog_task(
        stq3_context, events, invoice_id, queue='transactions_watchdog',
):
    await watchdog_events_handler.task(
        stq3_context, invoice_id, events, log_extra=None,
    )
