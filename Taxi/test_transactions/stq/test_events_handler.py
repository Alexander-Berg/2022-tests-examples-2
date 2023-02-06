# pylint: disable=too-many-lines,redefined-outer-name,unused-variable
import contextlib
import copy
import datetime
import json
import logging
from typing import Any
from typing import Dict

from aiohttp import web
import freezegun
import pytest

from taxi.billing.util import eta as eta_util

from test_transactions import helpers
from transactions.clients.trust import rest_client
from transactions.generated.stq3 import stq_context
from transactions.internal import operations_handler
from transactions.internal.payment_gateways import exceptions
from transactions.internal.payment_gateways import trust
from transactions.models import invoice_operations
from transactions.models import invoices
from transactions.models import wrappers
from transactions.stq import events_handler
from transactions.stq import watchdog_events_handler
from . import _assertions

_NOW_DATETIME = datetime.datetime(2019, 6, 3, 12, 0)
_NOW = _NOW_DATETIME.isoformat()
_TERMINAL_CREATE_BASKET_ERROR = pytest.mark.config(
    TRANSACTIONS_CREATE_BASKET_TERMINAL_ERRORS=[
        {'status_code': 'shoop_da_whoop', 'status_desc': 'Firin my laser'},
    ],
)
_WATCHDOG_LOGGER = 'transactions.stq.watchdog_events_handler'

_OPERATION_TERMINATION_ENABLED = pytest.mark.config(
    TRANSACTIONS_OPERATION_TERMINATION_ENABLED={
        '__default__': False,
        'taxi': True,
    },
)
_LONG_OPERATION_TERMINATION_DELAY = pytest.mark.config(
    TRANSACTIONS_MAX_DELAY_BEFORE_OPERATION_TERMINATION={
        '__default__': 0,
        'refund': 1200,
    },
)
_SHORT_OPERATION_TERMINATION_DELAY = pytest.mark.config(
    TRANSACTIONS_MAX_DELAY_BEFORE_OPERATION_TERMINATION={
        '__default__': 0,
        'refund': 300,
    },
)

_POLLING_BACKOFF_ENABLED = pytest.mark.config(
    TRANSACTIONS_POLLING_BACKOFF_ALGO_ENABLED=True,
)
_POLLING_BACKOFF = pytest.mark.config(
    TRANSACTIONS_POLLING_BACKOFF_ALGO={
        '__default__': {
            '__default__': {
                'data': {
                    'first_delays': [10],
                    'max_delay': 1800,
                    'min_delay': 10,
                },
                'kind': 'exponential_backoff',
            },
        },
    },
)
_POLLING_BACKOFF_WITH_TAXI_OVERRIDE = pytest.mark.config(
    TRANSACTIONS_POLLING_BACKOFF_ALGO={
        '__default__': {
            '__default__': {
                'data': {
                    'first_delays': [10],
                    'max_delay': 1800,
                    'min_delay': 10,
                },
                'kind': 'exponential_backoff',
            },
        },
        'taxi': {
            '__default__': {
                'data': {
                    'first_delays': [10],
                    'max_delay': 1800,
                    'min_delay': 10,
                },
                'kind': 'exponential_backoff',
            },
            'trust:hold': {
                'kind': 'exponential_backoff',
                'data': {
                    'min_delay': 10,
                    'max_delay': 1800,
                    'first_delays': [8, 9],
                },
            },
        },
    },
)

_QUEUE_FOR_HOLD_TAXI = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': False}},
        'taxi': {'__default__': {'enabled': False}, 'hold': {'enabled': True}},
    },
)
_QUEUE_FOR_CLEAR_TAXI = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': False}},
        'taxi': {
            '__default__': {'enabled': False},
            'clear': {'enabled': True},
        },
    },
)
_QUEUE_FOR_EVERYTHING_TAXI = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': False}},
        'taxi': {'__default__': {'enabled': True}},
    },
)
_QUEUE_FOR_HOLD_EVERYWHERE = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {
            '__default__': {'enabled': False},
            'hold': {'enabled': True},
        },
    },
)
_QUEUE_FOR_EVERYTHING_EVERYWHERE = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': True}},
    },
)
_QUEUE_FOR_CLEAR_EDA = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': False}},
        'eda': {'__default__': {'enabled': False}, 'clear': {'enabled': True}},
    },
)
_QUEUE_FOR_HOLD_EDA = pytest.mark.config(
    TRANSACTIONS_PROCESSING_QUEUES_BY_STAGE_ENABLED={
        '__default__': {'__default__': {'enabled': False}},
        'eda': {'__default__': {'enabled': False}, 'hold': {'enabled': True}},
    },
)


@pytest.mark.config(
    TRANSACTIONS_TECHNICAL_ERROR_CODES_DEFAULT={
        'not_enough_funds': False,
        'tech_error': True,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
    TRANSACTIONS_ORIGINATORS={
        'taxi': {
            'processing': {
                'callback_queue': 'order_payment_result',
                'clear_result_callback_queue': 'order_payment_result',
                'user_action_required_callback_queues': [
                    'user_action_callback_queue',
                ],
                'priority': 1,
            },
        },
    },
)
@pytest.mark.parametrize(
    'order_not_found_error', [None, 'order_not_found', 'uid_not_found'],
)
@pytest.mark.parametrize(
    'hold_result,transaction_status,'
    'operation_status,payment_resp_code,'
    'is_technical_error,uantifraud_status,antifraud,num_antifraud_calls,'
    'extra_metrics',
    [
        pytest.param(
            'authorized',
            'hold_success',
            'done',
            None,
            False,
            'allow',
            {'response': {'status': 'allow'}, 'is_fraud': False},
            1,
            {
                'card_transactions_antifraud': 1,
                'card_transactions_antifraud_allow': 1,
            },
            marks=pytest.mark.config(
                TRANSACTIONS_ANTIFRAUD={'__default__': 1},
            ),
        ),
        pytest.param(
            'authorized',
            'hold_success',
            'done',
            None,
            False,
            'error',
            {'skip_reason': 'service_unavailable', 'is_fraud': False},
            3,
            {
                'card_transactions_antifraud': 1,
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_service-unavailable': 1,
            },
            marks=pytest.mark.config(
                TRANSACTIONS_ANTIFRAUD={'__default__': 1},
            ),
        ),
        (
            'not_authorized',
            'hold_fail',
            'failed',
            'not_enough_funds',
            False,
            'allow',
            {'is_fraud': False, 'skip_reason': 'disabled_by_config'},
            0,
            {
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_disabled-by-config': 1,
            },
        ),
        (
            'not_authorized',
            'hold_fail',
            'failed',
            'tech_error',
            True,
            'allow',
            {'is_fraud': False, 'skip_reason': 'disabled_by_config'},
            0,
            {
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_disabled-by-config': 1,
            },
        ),
    ],
)
@pytest.mark.now(_NOW)
# pylint: disable=too-many-locals,too-many-statements
async def test_basic_flow(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        hold_result,
        operation_status,
        transaction_status,
        payment_resp_code,
        is_technical_error,
        uantifraud_status,
        antifraud,
        num_antifraud_calls,
        extra_metrics,
        order_not_found_error,
        mock_experiments3,
        personal_phones_retrieve,
        personal_emails_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        cardstorage_update_card,
        cardstorage_card,
        mock_get_service_order,
        mock_uantifraud,
        mock_uuid4,
):
    personal_phones_retrieve()
    personal_emails_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    cardstorage_update_card()
    cardstorage_card()
    expected_headers = {'X-Uid': '123'}
    order_exists = order_not_found_error is None
    if order_exists:
        mock_get_service_order(
            '<alias_id>', 'success', '', expect_headers=expected_headers,
        )
    else:
        mock_get_service_order(
            '<alias_id>',
            'error',
            order_not_found_error,
            expect_headers=expected_headers,
        )

    @mockserver.json_handler('/trust-payments/v2/orders/')
    def mock_trust_create_order(request):
        assert request.headers['X-Uid'] == '123'
        return {
            'status': 'success',
            'status_code': 'created',
            'order_id': request.json['order_id'],
        }

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        orders = request.json['orders']
        assert len(orders) == 1
        assert orders[0]['price'] == '100.00'
        assert request.json['user_email'] == 'x@example.com'
        assert request.json['mit'] == {'create': True}
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
            'orders': [
                {'fiscal_inn': 'none'},
                {},
                {'fiscal_inn': '12345'},
                {'fiscal_inn': '67890'},
            ],
        }

    @mock_uantifraud('/v1/payment/check')
    def v1_payment_check(request):
        if uantifraud_status == 'error':
            return web.Response(status=500)
        return web.json_response({'status': uantifraud_status})

    collection = stq3_context.transactions.invoices

    # make sure we fill correct collection with test data.
    assert collection.name == 'orders'

    invoice_id = 'pending-invoice'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        task = stq.transactions_events.next_call()
        assert task == {
            'eta': datetime.datetime(1970, 1, 1, 0, 0),  # stq agent is weird
            'id': invoice_id,
            'args': [invoice_id],
            'kwargs': {'log_extra': None},
            'queue': 'transactions_events',
        }
        assert stq.is_empty

    assert v1_payment_check.times_called == num_antifraud_calls
    for _ in range(num_antifraud_calls):
        _assert_correct_call_to_uantifraud(v1_payment_check.next_call())
    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice is not None
    assert len(invoice['invoice_request']['operations']) == 1
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'processing'

    assert invoice['invoice_payment_tech']['sum_to_pay']['ride'] == '100'
    assert len(invoice['billing_tech']['transactions']) == 1
    assert invoice['billing_tech']['refresh_attempts_count'] == 0
    assert invoice['payment_tech']['hold_initiated'] is False
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['sum'] == {'ride': 1000000}
    assert transaction['card_billing_id'] == 'x1234'
    assert transaction['card_owner_uid'] == '123'
    assert transaction['card_payment_id'] == 'card-x1324'
    assert transaction['created'] is not None
    assert transaction['initial_sum'] == {'ride': 1000000}
    assert transaction['payment_method_type'] == 'card'
    assert transaction['refunds'] == []
    assert transaction['status'] == 'hold_init'
    assert transaction['purchase_token'] == 'trust-basket-token'
    assert transaction['antifraud'] == antifraud
    assert transaction['trust_payment_id'] == 'trust-payment-id'
    assert transaction['updated'] is not None

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/start/',
    )
    def mock_pay_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        return {
            'status': 'success',
            'payment_status': 'started',
            'data': 'abc',
            'orders': [
                {'fiscal_inn': 'none'},
                {},
                {'fiscal_inn': '12345'},
                {'fiscal_inn': '67890'},
            ],
        }

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task == {
            'eta': datetime.datetime(2019, 6, 3, 12, 0, 10),
            'id': invoice_id,
            'args': [invoice_id],
            'kwargs': {'log_extra': None},
            'queue': 'transactions_events',
        }
    invoice = await collection.find_one({'_id': invoice_id})
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_pending'
    assert transaction['billing_response'] == {
        'status': 'success',
        'payment_status': 'started',
        'data': 'abc',
        'orders': [
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345', 'fiscal_inn_pd_id': '0'},
            {'fiscal_inn': '67890', 'fiscal_inn_pd_id': '1'},
        ],
    }

    # check basket
    payment_status = None

    x3ds_info = {
        'status': 'some_status',
        'redirect_url': 'http://example.com/some_redirect_url',
        'process_url': 'http://example.com/some_process_url',
    }

    payment_form_info = {'_TARGET': 'http://example.com/some_process_url'}

    payment_url = 'http://example.com/some_payment_url'

    @mockserver.json_handler(
        '/trust-payments/v2/payment_status/trust-basket-token/',
    )
    def mock_check_basket(request):
        assert request.method == 'GET'
        response = {
            '3ds_transaction_info': x3ds_info,
            'payment_form': payment_form_info,
            'payment_url': payment_url,
            'status': 'success',
            'payment_status': payment_status,
            'purchase_token': 'purchase_token',
            'data': 'abcd',
            'payment_resp_code': payment_resp_code,
            'terminal': {'id': 42},
            'user_phone': '+70001234567',
            'user_email': 'vasya@example.com',
            'orders': [],
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/payments/trust-basket-token/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        response = {
            '3ds_transaction_info': x3ds_info,
            'payment_form': payment_form_info,
            'payment_url': payment_url,
            'status': 'success',
            'payment_status': payment_status,
            'purchase_token': 'purchase_token',
            'data': 'abcd',
            'payment_resp_code': payment_resp_code,
            'terminal': {'id': 42},
            'user_phone': '+70001234567',
            'user_email': 'vasya@example.com',
            'orders': [
                {'fiscal_inn': 'none'},
                {},
                {'fiscal_inn': '12345'},
                {'fiscal_inn': '67890'},
            ],
        }
        return response

    for (payment_status, transaction_response, start_new_task) in [
            ('started', 'hold_pending', True),
            (hold_result, transaction_status, False),
    ]:
        with stq.flushing():
            await _run_task(stq3_context, invoice_id)

            if start_new_task:
                assert stq.transactions_events.times_called == 1
                task = stq.transactions_events.next_call()
                assert task == {
                    'eta': datetime.datetime(2019, 6, 3, 12, 0, 10),
                    'id': invoice_id,
                    'args': [invoice_id],
                    'kwargs': {'log_extra': None},
                    'queue': 'transactions_events',
                }

                assert stq['user_action_callback_queue'].times_called == 2
                transaction_info = {
                    'external_payment_id': 'trust-basket-token',
                    'payment_type': 'card',
                    'status': transaction_response,
                    'payment_url': payment_url,
                    '3ds': x3ds_info,
                }

                task = stq['user_action_callback_queue'].next_call()
                await _check_user_action_callback(
                    invoice_id,
                    payment_resp_code,
                    task,
                    transaction_info,
                    '3ds_user_action_required',
                )

                task = stq['user_action_callback_queue'].next_call()
                await _check_user_action_callback(
                    invoice_id,
                    payment_resp_code,
                    task,
                    transaction_info,
                    'sbp_user_action_required',
                )

            else:
                # notifications
                assert stq.transactions_events.times_called == 1
                task = stq.transactions_events.next_call()
                assert task == {
                    'eta': datetime.datetime(1970, 1, 1, 0, 0),
                    'id': invoice_id,
                    'args': [invoice_id],
                    'kwargs': {'log_extra': None},
                    'queue': 'transactions_events',
                }
            assert stq.is_empty

        invoice = await collection.find_one({'_id': invoice_id})
        transaction = invoice['billing_tech']['transactions'][0]
        assert transaction['status'] == transaction_response
        assert transaction['3ds'] == x3ds_info
        assert (
            transaction['payment_form']['target']
            == payment_form_info['_TARGET']
        )
        assert transaction['payment_url'] == payment_url

        if start_new_task:
            assert transaction['is_technical_error'] is False
        else:
            assert transaction['is_technical_error'] is is_technical_error
        assert invoice['notifications'] == [
            {
                'type': '3ds_user_action_required',
                'operation_id': '1',
                'handled_at': datetime.datetime(2019, 6, 3, 12),
            },
            {
                'type': 'sbp_user_action_required',
                'operation_id': '1',
                'handled_at': datetime.datetime(2019, 6, 3, 12),
            },
        ]
        assert transaction['billing_response'] == {
            '3ds_transaction_info': x3ds_info,
            'payment_form': payment_form_info,
            'payment_url': payment_url,
            'status': 'success',
            'payment_status': payment_status,
            'purchase_token': 'purchase_token',
            'data': 'abcd',
            'payment_resp_code': payment_resp_code,
            'terminal': {'id': 42},
            'user_email': 'vasya@example.com',
            'user_email_pd_id': '4c3a6de6758742d0963496a9ac95663c',
            'user_phone': '+70001234567',
            'user_phone_pd_id': 'ef65e0f5b3274f7a9b8eb6bc7152b88f',
            'orders': [
                {'fiscal_inn': 'none'},
                {},
                {'fiscal_inn': '12345', 'fiscal_inn_pd_id': '0'},
                {'fiscal_inn': '67890', 'fiscal_inn_pd_id': '1'},
            ],
        }
        assert transaction['terminal_id'] == 42

    # notifications
    invoice = await collection.find_one({'_id': invoice_id})
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'processing'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        transaction_info = {
            'external_payment_id': 'trust-basket-token',
            'payment_type': 'card',
            'status': transaction_status,
            '3ds': x3ds_info,
            'payment_url': payment_url,
        }
        if is_technical_error:
            transaction_info['is_technical_error'] = True
        if payment_resp_code is not None:
            transaction_info['error_reason_code'] = payment_resp_code
        assert task == {
            'eta': datetime.datetime(1970, 1, 1, 0, 0),
            'id': f'{invoice_id}:1:{operation_status}:operation_finish',
            'args': [invoice_id, '1', operation_status, 'operation_finish'],
            'kwargs': {
                'created_at': _get_callback_created_at(_NOW_DATETIME),
                'transactions': [transaction_info],
                'payload': {'debt_id': 'some_debt_id', 'service': 'taxi'},
                'log_extra': None,
            },
            'queue': 'order_payment_result',
        }

    invoice = await collection.find_one({'_id': invoice_id})
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == operation_status
    assert invoice['billing_tech']['service_orders'] == {'ride': '<alias_id>'}

    # check stats
    if order_exists:
        assert mock_trust_create_order.times_called == 0
    else:
        assert mock_trust_create_order.times_called == 1
    assert mock_trust_create_basket.times_called == 1
    assert mock_pay_basket.times_called == 1
    assert mock_check_basket.times_called == 2  # hold_pending, hold_success
    await stq3_context.metrics.sync()
    await stq3_context.metrics.sync()  # check idempotency
    stat = await stq3_context.mongo.transactions_stat.find().to_list(None)
    assert len(stat) == 1

    if transaction_status == 'hold_success':
        metrics_transaction_status = 'success'
    else:
        if is_technical_error:
            metrics_transaction_status = 'technical-error'
        else:
            metrics_transaction_status = 'hold-fail'
    expected_metrics = {
        'card_methods_check-basket-light_success': (
            2
        ),  # hold_pending, hold_success
        'card_methods_check-basket_success': 1,  # hold_pending, hold_success
        'card_methods_create-basket_success': 1,
        'card_methods_get-order_success': 1,
        'card_methods_pay-basket_success': 1,
        f'card_transactions_{metrics_transaction_status}': 1,
        'card_methods_check-basket-light': 2,
        'card_methods_check-basket': 1,
        'card_methods_create-basket': 1,
        'card_methods_get-order': 1,
        'card_methods_pay-basket': 1,
        # payment type namespace
        f'card_card_transactions_{metrics_transaction_status}': 1,
    }
    expected_metrics.update(extra_metrics)
    if not order_exists:
        expected_metrics['card_methods_create-order_success'] = 1
        expected_metrics['card_methods_create-order'] = 1
    if payment_resp_code:
        metric_resp_code = payment_resp_code.replace('_', '-')
        expected_metrics[f'card_resp-codes_{metric_resp_code}'] = 1
        # payment type namespace
        expected_metrics[f'card_card_resp-codes_{metric_resp_code}'] = 1
    assert stat[0]['metrics'] == expected_metrics

    assert mock_experiments3.times_called > 0


async def _check_user_action_callback(
        invoice_id,
        payment_resp_code,
        task,
        transaction_info,
        notification_type,
):
    if payment_resp_code is not None:
        transaction_info['error_reason_code'] = payment_resp_code
    assert task == {
        'eta': datetime.datetime(1970, 1, 1, 0, 0),
        'id': f'{invoice_id}:1:processing:{notification_type}',
        'args': [invoice_id, '1', 'processing', notification_type],
        'kwargs': {
            'created_at': _get_callback_created_at(_NOW_DATETIME),
            'transactions': [transaction_info],
            'payload': {'debt_id': 'some_debt_id', 'service': 'taxi'},
            'log_extra': None,
        },
        'queue': 'user_action_callback_queue',
    }


@pytest.mark.config(
    TRANSACTIONS_TECHNICAL_ERROR_CODES_DEFAULT={
        'not_enough_funds': False,
        'tech_error': True,
    },
    TRANSACTIONS_FALLBACK_REFUNDABLE_HEADER_VALUES={
        'default_value': 'yes',
        'values': [{'payment_type': 'applepay', 'value': 'xpay'}],
    },
)
@pytest.mark.parametrize(
    'order_not_found_error', [None, 'order_not_found', 'uid_not_found'],
)
@pytest.mark.parametrize(
    'hold_result,transaction_status,'
    'operation_status,payment_resp_code,'
    'is_technical_error,uantifraud_status,antifraud,num_antifraud_calls,'
    'extra_metrics',
    [
        pytest.param(
            'authorized',
            'hold_success',
            'done',
            None,
            False,
            'allow',
            {'response': {'status': 'allow'}, 'is_fraud': False},
            1,
            {
                'card_transactions_antifraud': 1,
                'card_transactions_antifraud_allow': 1,
            },
            marks=pytest.mark.config(
                TRANSACTIONS_ANTIFRAUD={'__default__': 1},
            ),
        ),
        pytest.param(
            'authorized',
            'hold_success',
            'done',
            None,
            False,
            'error',
            {'skip_reason': 'service_unavailable', 'is_fraud': False},
            3,
            {
                'card_transactions_antifraud': 1,
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_service-unavailable': 1,
            },
            marks=pytest.mark.config(
                TRANSACTIONS_ANTIFRAUD={'__default__': 1},
            ),
        ),
        (
            'not_authorized',
            'hold_fail',
            'failed',
            'not_enough_funds',
            False,
            'allow',
            {'is_fraud': False, 'skip_reason': 'disabled_by_config'},
            0,
            {
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_disabled-by-config': 1,
            },
        ),
        (
            'not_authorized',
            'hold_fail',
            'failed',
            'tech_error',
            True,
            'allow',
            {'is_fraud': False, 'skip_reason': 'disabled_by_config'},
            0,
            {
                'card_transactions_antifraud-skipped': 1,
                'card_transactions_antifraud-skipped_disabled-by-config': 1,
            },
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_fallback_refundable_header(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        hold_result,
        operation_status,
        transaction_status,
        payment_resp_code,
        is_technical_error,
        uantifraud_status,
        antifraud,
        num_antifraud_calls,
        extra_metrics,
        order_not_found_error,
        mock_experiments3,
        personal_phones_retrieve,
        personal_emails_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        cardstorage_update_card,
        cardstorage_card,
        mock_get_service_order,
        mock_uantifraud,
        mock_uuid4,
):
    personal_phones_retrieve()
    personal_emails_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    cardstorage_update_card()
    cardstorage_card()
    expected_headers = {'X-Uid': '123'}
    order_exists = order_not_found_error is None
    if order_exists:
        mock_get_service_order(
            '<alias_id>', 'success', '', expect_headers=expected_headers,
        )
    else:
        mock_get_service_order(
            '<alias_id>',
            'error',
            order_not_found_error,
            expect_headers=expected_headers,
        )

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'xpay'
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token-applepay',
            'trust_payment_id': 'trust-payment-id',
        }

    invoice_id = 'pending-invoice-applepay'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _ensure_transactions_called(stq)

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token-applepay/start/',
    )
    def mock_pay_basket(request):
        assert request.headers['FallBackRefundable'] == 'xpay'
        return {
            'status': 'success',
            'payment_status': 'started',
            'data': 'abc',
        }

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _ensure_transactions_called(stq)

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token-applepay/clear/',
    )
    async def mock_trust_clear_basket(_request):
        assert _request.headers['FallBackRefundable'] == 'xpay'
        return {'status': 'success'}

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _ensure_transactions_called(stq)


@pytest.mark.now(_NOW)
async def test_recreate_service_orders(
        stq,
        stq3_context,
        mockserver,
        mock_get_service_order,
        personal_phones_retrieve,
        personal_emails_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        cardstorage_update_card,
        cardstorage_card,
):
    personal_phones_retrieve()
    personal_emails_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    cardstorage_update_card()
    cardstorage_card()
    expected_headers = {'X-Uid': '123'}
    mock_trust_get_order = mock_get_service_order(
        '<alias_id>',
        'error',
        'order_not_found',
        expect_headers=expected_headers,
    )

    @mockserver.json_handler('/trust-payments/v2/orders/')
    def mock_trust_create_order(request):
        assert request.headers['X-Uid'] == '123'
        assert request.json['product_id'] == '123'
        assert request.json['order_id'] == '<alias_id>'
        return {
            'status': 'success',
            'status_code': 'created',
            'order_id': request.json['order_id'],
        }

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        orders = request.json['orders']
        assert len(orders) == 1
        assert orders[0]['price'] == '100.00'
        assert request.json['user_email'] == 'x@example.com'
        return {'status': 'error', 'status_code': 'order_not_found'}

    collection = stq3_context.transactions.invoices

    # make sure we fill correct collection with test data.
    assert collection.name == 'orders'

    invoice_id = 'pending-invoice-with-saved-service-orders'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id

    invoice = await collection.find_one({'_id': invoice_id})
    assert not invoice['billing_tech']['transactions']
    assert invoice['billing_tech']['service_orders'] == {'ride': '<alias_id>'}
    assert mock_trust_get_order.times_called == 1
    assert mock_trust_create_order.times_called == 1


@pytest.mark.config(
    TRANSACTIONS_ANTIFRAUD={'__default__': 1},
    TRANSACTIONS_TECHNICAL_ERROR_CODES_DEFAULT={'blacklisted': False},
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_antifraud_block(
        stq,
        stq3_context,
        uantifraud_block,
        mock_get_service_order,
        personal_phones_retrieve,
        personal_emails_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        mock_uuid4,
):
    personal_phones_retrieve()
    personal_emails_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    mock_get_service_order('<alias_id>', 'success', '')
    collection = stq3_context.transactions.invoices

    # make sure we fill correct collection with test data.
    assert collection.name == 'orders'

    invoice_id = 'pending-invoice'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        task = stq.transactions_events.next_call()
        assert task == {
            'eta': datetime.datetime(1970, 1, 1, 0, 0),  # stq agent is weird
            'id': invoice_id,
            'args': [invoice_id],
            'kwargs': {'log_extra': None},
            'queue': 'transactions_events',
        }
        assert stq.is_empty

    assert uantifraud_block.times_called == 1
    _assert_correct_call_to_uantifraud(uantifraud_block.next_call())
    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice is not None
    assert len(invoice['invoice_request']['operations']) == 1
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'processing'

    assert invoice['invoice_payment_tech']['sum_to_pay']['ride'] == '100'
    assert len(invoice['billing_tech']['transactions']) == 1
    assert invoice['billing_tech']['refresh_attempts_count'] == 0
    assert invoice['payment_tech']['hold_initiated'] is False
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['sum'] == {'ride': 1000000}
    assert transaction['card_billing_id'] == 'x1234'
    assert transaction['card_owner_uid'] == '123'
    assert transaction['card_payment_id'] == 'card-x1324'
    assert transaction['created'] is not None
    assert transaction['initial_sum'] == {'ride': 1000000}
    assert transaction['payment_method_type'] == 'card'
    assert transaction['refunds'] == []
    assert transaction['status'] == 'hold_fail'
    assert transaction['purchase_token'] == 'pending-invoice/0'
    assert transaction['antifraud'] == {
        'response': {'status': 'block'},
        'is_fraud': True,
    }
    assert transaction['trust_payment_id'] == 'pending-invoice/0'
    assert transaction['billing_response'] == {
        'payment_resp_code': 'blacklisted',
        'payment_resp_desc': 'mlu af filters',
    }
    assert not transaction['is_technical_error']
    assert transaction['updated'] is not None

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 0
        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        transaction_info = {
            'external_payment_id': 'pending-invoice/0',
            'payment_type': 'card',
            'status': 'hold_fail',
            'error_reason_code': 'blacklisted',
        }
        assert task == {
            'eta': datetime.datetime(1970, 1, 1, 0, 0),
            'id': f'{invoice_id}:1:failed:operation_finish',
            'args': [invoice_id, '1', 'failed', 'operation_finish'],
            'kwargs': {
                'created_at': _get_callback_created_at(_NOW_DATETIME),
                'transactions': [transaction_info],
                'payload': {'debt_id': 'some_debt_id', 'service': 'taxi'},
                'log_extra': None,
            },
            'queue': 'order_payment_result',
        }

    invoice = await collection.find_one({'_id': invoice_id})
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'failed'
    assert invoice['billing_tech']['service_orders'] == {'ride': '<alias_id>'}

    await stq3_context.metrics.sync()
    await stq3_context.metrics.sync()  # check idempotency
    stat = await stq3_context.mongo.transactions_stat.find().to_list(None)
    assert len(stat) == 1

    expected_metrics = {
        'card_transactions_hold-fail': 1,
        'card_resp-codes_blacklisted': 1,
        'card_methods_get-order': 1,
        'card_methods_get-order_success': 1,
        'card_transactions_antifraud': 1,
        'card_transactions_antifraud_block': 1,
        # payment type namespace
        'card_card_transactions_hold-fail': 1,
        'card_card_resp-codes_blacklisted': 1,
    }
    assert stat[0]['metrics'] == expected_metrics


@pytest.fixture
def mock_trust_pay_basket_not_found(mockserver):
    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/start/')
    def mock_trust_pay_basket(request):
        assert request.headers['X-Uid'] == '123456'
        assert request.headers['FallBackRefundable'] == 'yes'
        text = json.dumps(
            {
                'status': 'error',
                'status_code': 'payment_not_found',
                'data': 'abc',
            },
            ensure_ascii=False,
        )
        return web.Response(
            text=text, status=404, content_type='application/json',
        )

    return mock_trust_pay_basket


@pytest.mark.config(
    BILLING_RECHECK_BASKET_ON_NOT_FOUND=False,
    BILLING_MAX_NOT_FOUND_BASKET_AGE=7200,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_handle_payment_not_found(
        stq3_context: stq_context.Context,
        mock_trust_pay_basket_not_found,
        mock_experiments3,
):
    invoice_id = 'hold-pending'

    collection = stq3_context.transactions.invoices

    await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_fail'
    assert transaction['billing_response'] == {
        'status': 'error',
        'status_code': 'payment_not_found',
    }

    # check stats
    assert mock_trust_pay_basket_not_found.times_called == 1
    await stq3_context.metrics.sync()
    stat = await stq3_context.mongo.transactions_stat.find_one()
    metric_namespace = invoice['invoice_request']['metric_namespaces'][0]
    assert stat['metrics'] == {
        'card_methods_pay-basket_error': 1,
        'card_transactions_hold-fail': 1,
        'card_resp-codes_payment-not-found': 1,
        f'card_{metric_namespace}_transactions_hold-fail': 1,
        f'card_{metric_namespace}_resp-codes_payment-not-found': 1,
        'card_methods_pay-basket': 1,
        # payment type namespace
        'card_card_transactions_hold-fail': 1,
        'card_card_resp-codes_payment-not-found': 1,
    }


@pytest.mark.parametrize(
    'invoice_id, expected_pending_ids',
    [
        pytest.param('noop-invoice', [], marks=[]),
        pytest.param(
            'noop-invoice',
            [],
            marks=[pytest.mark.config(BILLING_DO_NOT_CLEAR=True)],
        ),
        pytest.param(
            'noop-invoice',
            [],
            marks=[pytest.mark.config(BILLING_DO_NOT_PROCESS_DEBT=True)],
        ),
        pytest.param(
            'clear-invoice',
            ['transactions_events/clear-invoice'],
            marks=[pytest.mark.config(BILLING_DO_NOT_CLEAR=True)],
        ),
        pytest.param(
            'debt-invoice',
            ['transactions_events/debt-invoice'],
            marks=[pytest.mark.config(BILLING_DO_NOT_PROCESS_DEBT=True)],
        ),
        pytest.param(
            'noop-invoice',
            ['transactions_events/noop-invoice'],
            marks=[
                pytest.mark.config(BILLING_DO_NOT_PROCESS_TRANSACTIONS=True),
            ],
        ),
        pytest.param(
            'noop-invoice',
            ['transactions_events/noop-invoice'],
            marks=[pytest.mark.config(BILLING_DEBT_FALLBACK_ENABLED=True)],
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_fallbacks(
        stq3_context: stq_context.Context, invoice_id, expected_pending_ids,
):
    await _run_task(stq3_context, invoice_id)
    cursor = stq3_context.mongo.pending_transactions.find()
    pending = await cursor.to_list(None)
    pending_ids = [doc['_id'] for doc in pending]
    assert sorted(pending_ids) == sorted(expected_pending_ids)


@pytest.mark.parametrize(
    'invoice_id, expected_needs_notification',
    [('notify-invoice', False), ('notify-with-callbacks-invoice', False)],
)
@pytest.mark.now(_NOW)
async def test_notifications(
        stq3_context: stq_context.Context,
        stq,
        taxi_config,
        invoice_id,
        expected_needs_notification,
):
    await _run_task(stq3_context, invoice_id)
    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    operations = invoice['invoice_request']['operations']

    assert len(operations) == 1
    operation = operations[0]

    assert operation['needs_notification'] == expected_needs_notification

    assert stq.order_payment_result.times_called == 1
    base_call = {
        'queue': 'order_payment_result',
        'id': f'{invoice_id}:1:done:operation_finish',
        'args': [invoice_id, '1', 'done', 'operation_finish'],
        'kwargs': {
            'created_at': _get_callback_created_at(_NOW_DATETIME),
            'id_namespace': 'some_id_namespace',
            'transactions': [],
            'log_extra': None,
        },
        'eta': datetime.datetime(1970, 1, 1),
    }
    assert stq.order_payment_result.next_call() == base_call
    _check_callbacks(stq, operation, base_call)
    _check_extra_callbacks(stq, base_call, taxi_config)


def _check_callbacks(stq, operation, base_call):
    for callback in operation.get('callbacks', []):
        callback_queue = stq[callback['queue']]
        callback_call = _with_queue_and_payload(
            base_call, callback['queue'], callback.get('payload'),
        )
        assert callback_queue.times_called == 1
        assert callback_queue.next_call() == callback_call


def _check_extra_callbacks(stq, base_call, taxi_config, clear=False):
    originators_config = taxi_config.get('TRANSACTIONS_ORIGINATORS')
    config_field = (
        'extra_clear_result_callback_queues'
        if clear
        else 'extra_callback_queues'
    )
    callbacks_to_call = originators_config['taxi']['processing'].get(
        config_field, [],
    )
    for queue in callbacks_to_call:
        assert stq[queue].times_called == 1
        assert stq[queue].next_call() == {**base_call, 'queue': queue}


def _with_queue_and_payload(base_call, queue, payload):
    result = copy.deepcopy(base_call)
    result['queue'] = queue
    if payload is not None:
        result['kwargs']['payload'] = payload
    else:
        result['kwargs'].pop('payload', None)
    return result


@pytest.mark.config(
    BILLING_RECHECK_BASKET_ON_NOT_FOUND=True,
    BILLING_MAX_NOT_FOUND_BASKET_AGE=7200,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'invoice_id, expectation, expected_transaction_status, '
    'expected_billing_response, expected_metrics, expected_eta, '
    'expected_terminated_operations',
    [
        (
            'hold-pending',
            contextlib.nullcontext(),
            'hold_init',
            {'foo': 'bar'},
            {
                'card_methods_pay-basket_error': 1,
                'card_resp-codes_payment-not-found': 1,
                'card_isr_resp-codes_payment-not-found': 1,
                'card_methods_pay-basket': 1,
                # payment type namespace
                'card_card_resp-codes_payment-not-found': 1,
            },
            # Still has pending transactions - refresh at now() + delay
            datetime.datetime(2019, 6, 3, 12, 0, 10),
            [],
        ),
        (
            'hold-pending-old-not-found-transaction',
            contextlib.nullcontext(),
            'hold_fail',
            {'status': 'error', 'status_code': 'payment_not_found'},
            {
                'card_methods_pay-basket_error': 1,
                'card_transactions_hold-fail': 1,
                'card_resp-codes_payment-not-found': 1,
                'card_methods_pay-basket': 1,
                # payment type namespace
                'card_card_transactions_hold-fail': 1,
                'card_card_resp-codes_payment-not-found': 1,
            },
            # Transaction just updated its status - refresh now
            datetime.datetime(1970, 1, 1, 0, 0),
            [],
        ),
        pytest.param(
            'hold-pending-old-not-found-transaction',
            pytest.raises(trust.UnexpectedPaymentNotFoundError),
            'hold_init',
            {'foo': 'bar'},
            {
                'card_methods_pay-basket_error': 1,
                'card_resp-codes_payment-not-found': 1,
                'card_methods_pay-basket': 1,
                # payment type namespace
                'card_card_resp-codes_payment-not-found': 1,
            },
            None,  # ignored in test
            [],
            marks=pytest.mark.config(TRANSACTIONS_STATUS_CHANGES_ON_ERROR=[]),
        ),
        pytest.param(
            'hold-pending-old-not-found-transaction',
            pytest.raises(operations_handler.ProcessingTerminated),
            'hold_init',
            {'foo': 'bar'},
            {
                'card_methods_pay-basket_error': 1,
                'card_resp-codes_payment-not-found': 1,
                'card_methods_pay-basket': 1,
                # payment type namespace
                'card_card_resp-codes_payment-not-found': 1,
            },
            None,  # ignored in test
            [
                {
                    'id': '11111111111111111111111111111111',
                    'terminated_at': _NOW_DATETIME,
                    'termination_context': {
                        'error_kind': 'unexpected_payment_not_found',
                        'gateway_name': 'trust',
                        'gateway_response': {
                            'status': 'error',
                            'status_code': 'payment_not_found',
                            'status_desc': None,
                        },
                        'invoice_id': 'hold-pending-old-not-found-transaction',
                        'transaction_id': 'tr1234',
                        'transactions_scope': 'taxi',
                    },
                },
            ],
            marks=pytest.mark.config(
                TRANSACTIONS_STATUS_CHANGES_ON_ERROR=[],
                TRANSACTIONS_TERMINATE_ON_UNEXPECTED_PAYMENT_NOT_FOUND=True,
            ),
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_handle_payment_not_found_recheck(
        stq3_context: stq_context.Context,
        stq,
        mock_trust_pay_basket_not_found,
        mock_experiments3,
        mock_uuid4,
        invoice_id,
        expectation,
        expected_transaction_status,
        expected_billing_response,
        expected_metrics,
        expected_eta,
        expected_terminated_operations,
):
    collection = stq3_context.transactions.invoices

    with stq.flushing():
        with expectation:
            await _run_task(stq3_context, invoice_id)

            task = stq.transactions_events.next_call()
            assert task == {
                'eta': expected_eta,
                'id': invoice_id,
                'args': [invoice_id],
                'kwargs': {'log_extra': None},
                'queue': 'transactions_events',
            }
            assert stq.is_empty

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == expected_transaction_status
    assert transaction['billing_response'] == expected_billing_response

    # check stats
    assert mock_trust_pay_basket_not_found.times_called == 1
    await stq3_context.metrics.sync()
    stat = await stq3_context.mongo.transactions_stat.find_one()
    assert stat['metrics'] == expected_metrics

    # check terminated operations
    invoice_request = invoice['invoice_request']
    terminated_operations = invoice_request.get('terminated_operations', [])
    assert terminated_operations == expected_terminated_operations


@pytest.mark.config(
    TRANSACTIONS_TECHNICAL_ERROR_CODES_DEFAULT={'not_enough_funds': False},
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
    TRANSACTIONS_USE_TRANSACTION_ID_IN_CLEAR_CALLBACK={
        'taxi': {'card': True, '__default__': False},
        '__default__': {'__default__': False},
    },
)
@pytest.mark.parametrize(
    'invoice_id, clear_result, payment_resp_code, transaction_status, '
    'expected_uid',
    [
        (
            'hold-success-automatic-clear-delay',
            'cleared',
            None,
            'clear_success',
            '123456',
        ),
        ('hold-success', 'cleared', None, 'clear_success', 'transaction-uid'),
        (
            'hold-success',
            'not_authorized',
            'not_enough_funds',
            'clear_fail',
            'transaction-uid',
        ),
        (
            'hold-success-check-transaction-originator',
            'cleared',
            None,
            'clear_success',
            'transaction-uid',
        ),
    ],
)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_clear(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        taxi_config,
        invoice_id,
        clear_result,
        payment_resp_code,
        transaction_status,
        expected_uid,
):
    collection = stq3_context.transactions.invoices

    # move from hold_success to clear_init status
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['eta'] == datetime.datetime(1970, 1, 1, 0, 0)

    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice['billing_tech']['transactions'][0]['status'] == 'clear_init'

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/clear/')
    async def mock_trust_clear_basket(_request):
        assert _request.headers['X-Uid'] == expected_uid
        assert _request.headers['FallBackRefundable'] == 'yes'
        return {'status': 'success'}

    # move from clear_init to clear_pending status
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        _ensure_transactions_called(stq)

    invoice = await collection.find_one({'_id': invoice_id})
    assert (
        invoice['billing_tech']['transactions'][0]['status'] == 'clear_pending'
    )

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

    # done transaction clear
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        transaction_info = {
            'external_payment_id': 'tr1234',
            'payment_type': 'card',
            'status': transaction_status,
        }
        if payment_resp_code is not None:
            transaction_info['error_reason_code'] = payment_resp_code
        base_call = {
            'id': f'{invoice_id}:1:done:tr1234:transaction_clear',
            'args': [invoice_id, '1', 'done', 'transaction_clear'],
            'eta': datetime.datetime(1970, 1, 1),
            'queue': 'order_payment_result',
            'kwargs': {
                'created_at': {
                    '$date': (
                        datetime.datetime(
                            2020, 1, 1, tzinfo=datetime.timezone.utc,
                        ).timestamp()
                        * 1000
                    ),
                },
                'transactions': [transaction_info],
                'payload': {'debt_id': 'some_debt_id', 'service': 'taxi'},
                'log_extra': None,
            },
        }
        assert task == base_call
        operations = invoice['invoice_request']['operations']
        assert len(operations) == 1
        _check_callbacks(stq, operations[0], base_call)
        _check_extra_callbacks(stq, base_call, taxi_config, clear=True)
    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == transaction_status
    assert transaction['clear_notify_ts'] == now

    # check nothing will happen
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.is_empty
    assert len(invoice['billing_tech']['transactions']) == 1

    # check stats
    assert mock_trust_clear_basket.times_called == 1
    assert mock_trust_check_basket.times_called == 1
    await stq3_context.metrics.sync()
    stat = await stq3_context.mongo.transactions_stat.find_one()
    actual_metrics = stat['metrics']
    if transaction_status == 'clear_success':
        transaction_status_for_stat = 'success'
    else:
        transaction_status_for_stat = 'hold-fail'
        assert actual_metrics['card_resp-codes_not-enough-funds'] == 1

    # lightweight and full calls twice, thus 4
    assert (
        stat['metrics']['card_methods_check-basket-light_success']
        + stat['metrics']['card_methods_check-basket-light']
        == 2
    )
    assert (
        stat['metrics']['card_methods_check-basket_success']
        + stat['metrics']['card_methods_check-basket']
        == 2
    )

    assert actual_metrics['card_methods_clear-basket_success'] == 1
    assert actual_metrics['card_methods_clear-basket'] == 1
    assert (
        actual_metrics[f'card_transactions_{transaction_status_for_stat}'] == 1
    )


@pytest.mark.parametrize(
    'invoice_id, clear_result, refund_result, payment_resp_code, '
    'transaction_status, expected_uid',
    [
        (
            'clear_pending',
            'autorized',
            'autorized',
            None,
            'autorized',
            'transaction-uid',
        ),
        (
            'refund_pending',
            'autorized',
            'autorized',
            None,
            'autorized',
            'transaction-uid',
        ),
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
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
        refund_result,
        payment_resp_code,
        transaction_status,
        expected_uid,
        caplog,
):
    caplog.set_level(logging.INFO, logger=_WATCHDOG_LOGGER)

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

    @mockserver.json_handler('/trust-payments/v2/refunds/tri234/start/')
    def mock_trust_create_refund(_request):
        assert 'X-Uid' in _request.headers
        assert _request.headers['X-Uid'] == 'transaction-uid'
        return {'status': refund_result, 'trust_refund_id': 'refund1234'}

    # check that pending transactions was planned to run later
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        # check 10s offset from now for task eta for first reschedule
        assert task['eta'] == datetime.datetime(2020, 1, 1, 0, 0, 10)
        assert not stq.is_empty
        assert stq.transactions_watchdog.times_called == 1
        watchdog_task = stq.transactions_watchdog.next_call()
        assert watchdog_task

    with stq.flushing():
        await _run_watchdog_task(
            stq3_context,
            watchdog_task['kwargs']['events'],
            watchdog_task['kwargs']['invoice_id'],
        )

    records = [
        x.getMessage() for x in caplog.records if x.name == _WATCHDOG_LOGGER
    ]
    # we should see some watchdog log
    assert records


@pytest.mark.config(
    TRANSACTIONS_STATUS_CHANGES_ON_ERROR=[],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_clear_payment_not_found(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        now,
        mock_experiments3,
):
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['eta'] == datetime.datetime(1970, 1, 1, 0, 0)

    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice['billing_tech']['transactions'][0]['status'] == 'clear_init'

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/clear/')
    async def mock_trust_clear_basket(_request):
        assert _request.headers['FallBackRefundable'] == 'yes'
        return {'status': 'error', 'status_code': 'payment_not_found'}

    with stq.flushing():
        with pytest.raises(trust.UnexpectedPaymentNotFoundError):
            await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice['billing_tech']['transactions'][0]['status'] == 'clear_init'


@pytest.mark.config(
    TRANSACTIONS_STATUS_CHANGES_ON_ERROR=[],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
    TRANSACTIONS_CLEAR_ATTEMPTS_BACKOFF={
        'min_interval': 2,
        'max_interval': 1800,
        'max_attempts': 2,
    },
)
@pytest.mark.parametrize(
    'invoice_id,is_successful',
    [
        ('hold-success', True),
        ('hold-success', False),
        ('hold-success-automatic-clear-delay', True),
        ('hold-success-automatic-clear-delay', False),
    ],
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_clear_attempts_backoff(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        mock_randomize_delay,
        invoice_id: str,
        is_successful: bool,
):
    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/clear/')
    async def mock_trust_clear_basket_fail(_request):
        return web.json_response(
            {'status': 'error', 'status_code': 'Server error'}, status=500,
        )

    await _to_clear_init(stq3_context, stq, invoice_id, now=now)
    await _try_to_clear_pending(
        stq3_context,
        stq,
        invoice_id,
        clear_attempts=1,
        eta=datetime.datetime(2020, 1, 1, 0, 0, 2),
    )

    if is_successful:

        @mockserver.json_handler('/trust-payments/v2/payments/tr1234/clear/')
        async def mock_trust_clear_basket_success(_request):
            return {'status': 'success'}

        await _to_clear_init(
            stq3_context,
            stq,
            invoice_id,
            now=datetime.datetime(2020, 1, 1, 0, 0, 10),
        )
        await _success_to_clear_pending(stq3_context, stq, invoice_id)
    else:
        await _to_clear_init(
            stq3_context,
            stq,
            invoice_id,
            now=datetime.datetime(2020, 1, 1, 0, 0, 10),
        )
        await _try_to_clear_pending(
            stq3_context,
            stq,
            invoice_id,
            clear_attempts=2,
            eta=datetime.datetime(2020, 1, 1, 0, 0, 4),
        )

        await _to_clear_init(
            stq3_context,
            stq,
            invoice_id,
            now=datetime.datetime(2020, 1, 1, 0, 0, 10),
        )
        await _fail_to_clear_pending(
            stq3_context, stq, invoice_id, clear_attempts=2,
        )

        await _fail_to_clear_pending(
            stq3_context, stq, invoice_id, clear_attempts=2,
        )


async def _to_clear_init(
        stq3_context, stq, invoice_id: str, now: datetime.datetime,
):
    with freezegun.freeze_time(now):
        with stq.flushing():
            await _run_task(stq3_context, invoice_id)
            assert stq.transactions_events.times_called == 1
            task = stq.transactions_events.next_call()
            assert task['eta'] == datetime.datetime(1970, 1, 1)
            assert stq.is_empty
    invoice = await stq3_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'clear_init'


async def _try_to_clear_pending(
        stq3_context,
        stq,
        invoice_id: str,
        clear_attempts: int,
        eta: datetime.datetime,
):
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['eta'] == eta
        assert stq.is_empty
    invoice = await stq3_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_success'
    assert transaction['clear_attempts'] == clear_attempts
    assert 'clear_eta' in transaction


async def _success_to_clear_pending(stq3_context, stq, invoice_id: str):
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['eta'] != datetime.datetime(1970, 1, 1, 0, 0)
        assert stq.is_empty
    invoice = await stq3_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'clear_pending'
    assert 'clear_eta' not in transaction
    assert 'clear_attempts' not in transaction


async def _fail_to_clear_pending(
        stq3_context, stq, invoice_id: str, clear_attempts: int,
):
    with stq.flushing():
        with pytest.raises(RuntimeError):
            await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        assert stq.is_empty
    invoice = await stq3_context.transactions.invoices.find_one(
        {'_id': invoice_id},
    )
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'clear_init'
    assert transaction['clear_attempts'] == clear_attempts


@pytest.mark.now(_NOW)
async def test_resize(
        stq3_context: stq_context.Context, mockserver, stq, mock_experiments3,
):
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': '2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '75'}],
                },
            },
            '$set': {
                'payment_tech.clear_eta': datetime.datetime(
                    2022, 12, 11, 15, 40,
                ),
            },
        },
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_resize'
    assert transaction['sum'] == {'ride': 750000}
    assert transaction['resizes'] == [
        {'created': _NOW_DATETIME, 'request_id': '2'},
    ]

    @mockserver.json_handler(
        '/trust-payments/v2/payments/tr1234/orders/order-ride/resize',
    )
    def mock_trust_resize_basket(request):
        assert request.headers['X-Uid'] == 'transaction-uid'
        assert request.json == {'amount': '75.00', 'qty': '1'}
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_success'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        assert task['args'] == [invoice_id, '2', 'done', 'operation_finish']

        _ensure_transactions_called(stq)

    assert mock_trust_resize_basket.times_called == 1
    await stq3_context.metrics.sync()
    stat = await stq3_context.mongo.transactions_stat.find_one()
    assert stat['metrics'] == {
        'card_methods_resize-basket_success': 1,
        'card_transactions_success': 1,
        'card_methods_resize-basket': 1,
        # payment type namespace
        'card_card_transactions_success': 1,
    }


async def test_operation_will_done_if_update_contains_same_amount(
        stq3_context: stq_context.Context, mockserver, stq, mock_experiments3,
):
    invoice_id = 'clear-success-for-update-contains-same-amount'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': '2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            },
            '$set': {
                'payment_tech.clear_eta': datetime.datetime(
                    2022, 12, 11, 15, 40,
                ),
            },
        },
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    operations = invoice['invoice_request']['operations']
    assert operations[1]['status'] == 'processing'

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        assert stq.order_payment_result.times_called == 1

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    operations = invoice['invoice_request']['operations']
    assert operations[1]['status'] == 'done'


@pytest.mark.parametrize(
    'check_refund_status_desc, expected_refund_status, '
    'expected_transaction_status',
    [
        ('shoop_da_whoop', 'refund_waiting', 'refund_waiting'),
        pytest.param(
            'shoop_da_whoop',
            'refund_fail',
            'clear_success',
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_REFUND_TERMINAL_ERRORS=['shoop_da_whoop'],
                ),
            ],
        ),
    ],
)
async def test_terminal_refund_errors(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        check_refund_status_desc,
        expected_refund_status,
        expected_transaction_status,
        mock_experiments3,
):
    now = datetime.datetime.utcnow()
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': 'op/2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '75'}],
                },
            },
            '$set': {
                'billing_tech.transactions.0.status': 'refund_waiting',
                'billing_tech.transactions.0.clear_notify_ts': now,
                'billing_tech.transactions.0.refunds': [
                    {
                        'created': now,
                        'status': 'refund_waiting',
                        'sum': {'ride': '25'},
                        'trust_refund_id': 'refund1234',
                        'billing_response': {},
                    },
                ],
            },
        },
    )

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/refunds/refund1234/')
    async def mock_trust_check_refund(request):
        return {'status': 'error', 'status_desc': check_refund_status_desc}

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.order_payment_result.times_called == 0

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == expected_transaction_status
    assert len(transaction['refunds']) == 1
    assert transaction['refunds'][0]['status'] == expected_refund_status


@pytest.mark.parametrize(
    'terminated',
    [
        pytest.param(
            False,
            marks=[
                _OPERATION_TERMINATION_ENABLED,
                _LONG_OPERATION_TERMINATION_DELAY,
            ],
        ),
        pytest.param(False, marks=[_SHORT_OPERATION_TERMINATION_DELAY]),
        pytest.param(
            True,
            marks=[
                _OPERATION_TERMINATION_ENABLED,
                _SHORT_OPERATION_TERMINATION_DELAY,
            ],
        ),
    ],
)
@pytest.mark.now(_NOW)
async def test_termination_on_refund_error(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        mock_experiments3,
        terminated,
        mock_uuid4,
):
    run_context = contextlib.nullcontext()
    expected = {'num_task_calls': 1, 'terminated_operations': []}
    if terminated:
        run_context = pytest.raises(operations_handler.ProcessingTerminated)
        expected = {
            'num_task_calls': 0,
            'terminated_operations': [
                {
                    'id': '11111111111111111111111111111111',
                    'operation_id': 'op/2',
                    'terminated_at': _NOW_DATETIME,
                    'termination_context': {
                        'error_kind': 'hanging_transaction',
                        'action_type': 'refund',
                        'gateway_name': 'trust',
                        'gateway_response': {
                            'status': 'error',
                            'status_desc': 'shoop_da_whoop',
                        },
                        'invoice_id': 'hold-success',
                        'refund_id': 'refund1234',
                        'transaction_id': 'tr1234',
                        'transactions_scope': 'taxi',
                    },
                },
            ],
        }
    now = datetime.datetime.utcnow()
    refund_created = now - datetime.timedelta(seconds=600)
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': 'op/2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '75'}],
                },
            },
            '$set': {
                'billing_tech.transactions.0.status': 'refund_waiting',
                'billing_tech.transactions.0.clear_notify_ts': now,
                'billing_tech.transactions.0.refunds': [
                    {
                        'created': refund_created,
                        'status': 'refund_waiting',
                        'sum': {'ride': '25'},
                        'trust_refund_id': 'refund1234',
                        'billing_response': {},
                    },
                ],
            },
        },
    )

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/refunds/refund1234/')
    async def mock_trust_check_refund(request):
        return {'status': 'error', 'status_desc': 'shoop_da_whoop'}

    with stq.flushing():
        with run_context:
            await _run_task(stq3_context, invoice_id)
        assert stq.order_payment_result.times_called == 0
        assert stq.transactions_events.times_called == (
            expected['num_task_calls']
        )

    invoice = await collection.find_one({'_id': invoice_id})
    invoice_request = invoice['invoice_request']
    operations = invoice_request['operations']
    assert operations[-1]['status'] == 'processing'

    terminated_operations = invoice_request.get('terminated_operations', [])
    assert terminated_operations == expected['terminated_operations']
    is_processing_halted = invoice_request.get('is_processing_halted', False)
    assert is_processing_halted == terminated

    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'refund_waiting'
    assert len(transaction['refunds']) == 1
    assert transaction['refunds'][0]['status'] == 'refund_waiting'


@pytest.mark.parametrize(
    'do_refund_status, check_refund_status, check_refund_status_desc,'
    'expectation, expected_refund_status, expected_transaction_status',
    [
        (
            'wait_for_notification',
            'success',
            'some',
            contextlib.nullcontext(),
            'refund_success',
            'clear_success',
        ),
        pytest.param(
            'wait_for_notification',
            'success',
            'some',
            pytest.raises(exceptions.TooSmallRefundError),
            'refund_success',
            'clear_success',
            marks=pytest.mark.config(BILLING_MIN_REFUND={'RUR': '26'}),
        ),
        (
            'success',
            None,
            None,
            contextlib.nullcontext(),
            'refund_success',
            'clear_success',
        ),
        (
            'wait_for_notification',
            'error',
            'Invalid payment state [ChargeBack]',
            contextlib.nullcontext(),
            'refund_success',
            'clear_success',
        ),
        # fixme system will try another refund immediately if previous fails
        # fixme think how it should work in order not to break trust
        # ('wait_for_notification', 'failed', 'refund_failed', 'clear_success')
        # ('failed', None, 'refund_failed', 'clear_success')
    ],
)
@pytest.mark.now(_NOW)
async def test_refund(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        do_refund_status,
        check_refund_status,
        check_refund_status_desc,
        expectation,
        expected_refund_status,
        expected_transaction_status,
        mock_experiments3,
):
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': 'op/2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'trust_afs_params': {'afs': 'params'},
                    'items': [{'item_id': 'ride', 'amount': '75'}],
                },
            },
            '$set': {'billing_tech.transactions.0.status': 'clear_success'},
        },
    )

    @mockserver.json_handler('/trust-payments/v2/refunds/')
    def mock_trust_create_refund(request):
        assert request.headers['X-Uid'] == 'transaction-uid'
        assert request.json == {
            'reason_desc': 'cancel payment',
            'orders': [{'order_id': 'order-ride', 'delta_amount': '25.00'}],
            'purchase_token': 'tr1234',
            'pass_params': {},
            'afs_params': {'afs': 'params'},
        }
        return {'status': 'success', 'trust_refund_id': 'refund1234'}

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    # pylint: disable=unused-variable
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        response = {
            'status': 'success',
            'payment_status': None,
            'data': 'abcd',
            'payment_resp_code': 'done',
            'terminal': {'id': 42},
        }
        return response

    # Initiate refund
    with stq.flushing():
        with expectation:
            await _run_task(stq3_context, invoice_id)
        if not isinstance(expectation, contextlib.nullcontext):  # type: ignore
            return
        _ensure_transactions_called(stq)

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    assert invoice['billing_tech']['refresh_attempts_count'] == 0
    assert invoice['payment_tech']['hold_initiated'] is False
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'refund_pending'
    assert transaction['sum'] == {'ride': '100'}
    assert len(transaction['refunds']) == 1
    assert transaction['refunds'][0]['sum'] == {'ride': 250000}
    assert transaction['refunds'][0]['status'] == 'refund_pending'
    assert transaction['refunds'][0]['refund_made_at'] is None
    assert transaction['refunds'][0]['request_id'] == 'op/2'
    assert 'terminal_id' not in transaction

    @mockserver.json_handler('/trust-payments/v2/refunds/refund1234/start/')
    async def mock_trust_do_refund(request):
        assert 'X-Uid' in request.headers
        assert request.headers['X-Uid'] == 'transaction-uid'
        return {'status': do_refund_status, 'status_desc': 'some'}

    @mockserver.json_handler('/trust-payments/v2/refunds/refund1234/')
    async def mock_trust_check_refund(request):
        return {
            'status': check_refund_status,
            'status_desc': check_refund_status_desc,
        }

    # Start refund and check it if it doesn't succeed right away
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        if check_refund_status is not None:
            _ensure_transactions_called(stq)
            await _run_task(stq3_context, invoice_id)

        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        assert task['id'] == f'{invoice_id}:1:done:transaction_clear'
        assert task['args'] == [invoice_id, '1', 'done', 'transaction_clear']
        assert task['kwargs'] == {
            'created_at': _get_callback_created_at(_NOW_DATETIME),
            'transactions': [
                {
                    'external_payment_id': 'tr1234',
                    'payment_type': 'card',
                    'status': 'clear_success',
                },
            ],
            'payload': {'debt_id': 'some_debt_id', 'service': 'taxi'},
            'log_extra': None,
        }
        _ensure_transactions_called(stq)

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == expected_transaction_status
    assert len(transaction['refunds']) == 1
    assert transaction['refunds'][0]['sum'] == {'ride': 250000}
    assert transaction['refunds'][0]['status'] == expected_refund_status
    assert transaction['terminal_id'] == 42

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.order_payment_result.times_called == 1
        task = stq.order_payment_result.next_call()
        assert task['args'] == [invoice_id, 'op/2', 'done', 'operation_finish']
        assert task['kwargs'] == {
            'created_at': _get_callback_created_at(_NOW_DATETIME),
            'transactions': [],
            'log_extra': None,
        }

    # check stats
    expected_metrics = {}
    assert mock_trust_create_refund.times_called == 1
    assert mock_trust_do_refund.times_called == 1
    if check_refund_status is not None:
        expected_metrics.update({'card_methods_check-refund': 1})
        if check_refund_status == 'success':
            expected_metrics['card_methods_check-refund_success'] = 1
        else:
            assert check_refund_status == 'error'
            expected_metrics['card_methods_check-refund_error'] = 1
        assert mock_trust_check_refund.times_called == 1
    else:
        assert mock_trust_check_refund.times_called == 0
    if do_refund_status == 'success':
        expected_metrics.update(
            {
                'card_methods_check-basket-light': 1,
                'card_methods_check-basket-light_success': 1,
            },
        )
    else:
        expected_metrics.update(
            {
                'card_methods_check-basket-light': 2,
                'card_methods_check-basket-light_success': 2,
            },
        )
    expected_metrics.update(
        {
            'card_methods_create-refund_success': 1,
            'card_methods_create-refund': 1,
            'card_methods_do-refund_success': 1,
            'card_methods_do-refund': 1,
            'card_refunds_success': 1,
        },
    )
    await stq3_context.metrics.sync()
    stat = await stq3_context.mongo.transactions_stat.find_one()
    assert stat['metrics'] == expected_metrics


async def test_remove_item(stq3_context: stq_context.Context, stq):
    invoice_id = 'ride-and-tips'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': '2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            },
            '$set': {'billing_tech.transactions.0.status': 'clear_success'},
        },
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'clear_success'
    assert transaction['sum'] == {'ride': '100'}
    assert invoice['invoice_payment_tech']['sum_to_pay'] == {
        'ride': '100',
        'tips': '0',
    }
    operations = invoice['invoice_request']['operations']
    assert all(operation['status'] == 'done' for operation in operations)


async def test_payment_tech_is_not_reset(
        stq3_context: stq_context.Context, stq, load_json,
):
    invoice_id = 'payment-tech-with-old-fields'
    expected = load_json('test_payment_tech_is_not_reset/expected.json')
    collection = stq3_context.transactions.invoices
    operation = invoices.Operation(
        parent_field='operations',
        index=0,
        values={
            'id': '2',
            'type': 'update',
            'status': 'init',
            'originator': 'processing',
            'items': [{'item_id': 'ride', 'amount': '100'}],
        },
    )
    update: Dict[str, Any] = {}
    invoice_data = await collection.find_one({'_id': invoice_id})
    fields = stq3_context.transactions.fields
    invoice = wrappers.make_invoice(invoice_data, fields)
    await collection.update(
        {'_id': invoice_id}, {'$set': {'invoice_payment_tech.foo': 'bar'}},
    )
    invoices.apply_new_state(
        invoice=invoice, operation=operation, update=update, fields=fields,
    )
    invoice_data = await invoice_operations.commit_processing(
        invoice, update, stq3_context,
    )
    invoice = invoice.updated_data(invoice_data, invoice.fields)
    assert invoice['invoice_payment_tech'] == expected['payment_tech']


@pytest.mark.parametrize(
    'invoice_id, expected_payment_timeout',
    [('need-cvn', 120), ('need-cvn-with-explicit-timeout', 180)],
)
@pytest.mark.now(_NOW)
async def test_hold_need_cvn(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        mock_get_service_order,
        invoice_id,
        expected_payment_timeout,
):
    @mockserver.json_handler('/trust-payments/v2/orders/')
    def _mock_trust_create_order(request):
        return {
            'status': 'success',
            'status_code': 'created',
            'order_id': request.json['order_id'],
        }

    mock_get_service_order('<alias_id>', 'error', 'order_not_found')

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def _mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        data = request.json
        orders = data['orders']
        assert len(orders) == 1
        assert orders[0]['price'] == '100.00'
        assert data['wait_for_cvn'] is True
        assert data['payment_timeout'] == expected_payment_timeout
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
        }

    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    # pylint: disable=unused-variable
    def mock_tins_bulk_retrieve(request):
        return mockserver.make_response(status=200, json={'items': []})

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    # pylint: disable=unused-variable
    def mock_phones_retrieve(request):
        resp_body = {'value': '+79999999999', 'id': 'phone_id'}
        return mockserver.make_response(status=200, json=resp_body)

    collection = stq3_context.transactions.invoices

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task == {
            'eta': datetime.datetime(1970, 1, 1, 0, 0),  # stq agent is weird
            'id': invoice_id,
            'args': [invoice_id],
            'kwargs': {'log_extra': None},
            'queue': 'transactions_events',
        }
    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice is not None
    assert len(invoice['invoice_request']['operations']) == 1
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'processing'

    assert invoice['invoice_payment_tech']['sum_to_pay']['ride'] == '100'
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['sum'] == {'ride': 1000000}
    assert transaction['card_billing_id'] == 'x1234'
    assert transaction['card_owner_uid'] == '123'
    assert transaction['card_payment_id'] == 'card-x1324'
    assert transaction['created'] is not None
    assert transaction['initial_sum'] == {'ride': 1000000}
    assert transaction['payment_method_type'] == 'card'
    assert transaction['refunds'] == []
    assert transaction['status'] == 'hold_init'
    assert transaction['purchase_token'] == 'trust-basket-token'
    assert transaction['trust_payment_id'] == 'trust-payment-id'
    assert transaction['updated'] is not None
    assert transaction['wait_for_cvn'] is True


def _ensure_transactions_called(stq):
    assert stq.transactions_events.times_called == 1
    stq.transactions_events.next_call()
    assert stq.is_empty


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'crutches, call_trust, expected_status',
    [
        (None, True, 'hold_success'),
        ([], True, 'hold_success'),
        (['payment-holdfail-technical'], False, 'hold_fail'),
        (['payment-holdfail'], False, 'hold_fail'),
    ],
)
async def test_crutches_check_basket(
        stq3_context: stq_context.Context,
        mockserver,
        mock_experiments3,
        crutches,
        expected_status,
        call_trust,
        cardstorage_update_card,
        cardstorage_card,
):
    cardstorage_update_card()
    cardstorage_card()
    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {'billing_tech.transactions.0.status': 'hold_pending'}},
    )

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
        }

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
        }

    mock_experiments3.set_crutches(crutches)

    await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == expected_status

    assert mock_check_basket.times_called == 1

    assert mock_experiments3.times_called == 1


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize('initial_status', ['hold_pending', 'hold_fail'])
@pytest.mark.parametrize(
    'comment, expected_status, payment_resp_code',
    [
        ('payment_holdfail', 'hold_fail', 'not_enough_funds'),
        ('payment_holdfail_technical', 'hold_fail', 'tech_error'),
        (
            'speed-300 , payment_holdfail  , payment_holdfail_technical  ,',
            'hold_fail',
            'not_enough_funds',
        ),
        ('comment without debts', 'hold_success', None),
    ],
)
async def test_crutches_by_comment(
        stq3_context: stq_context.Context,
        mockserver,
        mock_experiments3,
        cardstorage_update_card,
        cardstorage_card,
        comment,
        expected_status,
        payment_resp_code,
        initial_status,
):
    cardstorage_update_card()
    cardstorage_card()
    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {'billing_tech.transactions.0.status': initial_status}},
    )

    await collection.update(
        {'_id': invoice_id}, {'$set': {'request.comment': comment}},
    )

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
        }

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
        }

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_phones_retrieve(request):
        resp_body = {'value': '+79999999999', 'id': 'phone_id'}
        return mockserver.make_response(status=200, json=resp_body)

    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    def mock_tins_bulk_retrieve(request):
        return mockserver.make_response(status=200, json={'items': []})

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def _mock_trust_create_basket(request):
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
        }

    await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    if initial_status == 'hold_fail':
        assert len(invoice['billing_tech']['transactions']) == 2
        transaction = invoice['billing_tech']['transactions'][1]
        assert transaction['status'] == 'hold_init'
    else:
        assert len(invoice['billing_tech']['transactions']) == 1
        transaction = invoice['billing_tech']['transactions'][0]
        assert transaction['status'] == expected_status
        assert (
            transaction['billing_response'].get('payment_resp_code')
            == payment_resp_code
        )


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_personal_is_unavailable(
        stq3_context: stq_context.Context,
        mockserver,
        mock_experiments3,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        cardstorage_update_card,
        cardstorage_card,
):
    cardstorage_update_card()
    cardstorage_card()
    personal_phones_store(http_status=500)
    personal_emails_store(http_status=500)
    personal_tins_bulk_store(http_status=500)
    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {'billing_tech.transactions.0.status': 'hold_pending'}},
    )

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
            'user_phone': '+70001234567',
            'user_email': 'vasya@example.com',
            'orders': [],
        }

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        return {
            'status': 'success',
            'payment_status': 'authorized',
            'data': 'abcd',
            'user_phone': '+70001234567',
            'user_email': 'vasya@example.com',
            'orders': [
                {'fiscal_inn': 'none'},
                {},
                {'fiscal_inn': '12345'},
                {'fiscal_inn': '67890'},
            ],
        }

    await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'hold_success'
    assert transaction['billing_response'] == {
        'data': 'abcd',
        'orders': [
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345'},
            {'fiscal_inn': '67890'},
        ],
        'payment_status': 'authorized',
        'status': 'success',
        'user_email': 'vasya@example.com',
        'user_phone': '+70001234567',
    }
    assert mock_check_basket.times_called == 1


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.parametrize(
    'max_attempts, intervals',
    [
        pytest.param(
            5,
            [10, 10, 10, 10, 10, 1800, 1800],
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_CHECK_BASKET_BACKOFF_ALGO={
                        'kind': 'constant_with_increase',
                        'data': {
                            'primary_delay': 10,
                            'num_attempts_with_primary_delay': 5,
                            'increased_delay': 1800,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            5,
            [10, 10, 10, 10, 10, 10, 10],
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_CHECK_BASKET_BACKOFF_ALGO={
                        'kind': 'unknown',
                        'data': {},
                    },
                ),
            ],
        ),
        pytest.param(
            10,
            [8, 9, 40, 80, 160, 320, 640, 1280, 1800, 1800, 1800, 1800],
            marks=[
                pytest.mark.config(
                    TRANSACTIONS_CHECK_BASKET_BACKOFF_ALGO={
                        'kind': 'exponential_backoff',
                        'data': {
                            'min_delay': 10,
                            'max_delay': 1800,
                            'first_delays': [8, 9],
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            10,
            [10, 20, 40, 80, 160, 320, 640, 1280, 1800, 1800, 1800, 1800],
            marks=[_POLLING_BACKOFF_ENABLED, _POLLING_BACKOFF],
            id='take algorithm from by service config',
        ),
        pytest.param(
            10,
            [8, 9, 40, 80, 160, 320, 640, 1280, 1800, 1800, 1800, 1800],
            marks=[
                _POLLING_BACKOFF_ENABLED,
                _POLLING_BACKOFF_WITH_TAXI_OVERRIDE,
            ],
            id='take algorithm from by service config for taxi service',
        ),
    ],
)
async def test_retry_attempts_works(
        stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        patch,
        max_attempts,
        intervals,
):
    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        assert request.method == 'GET'
        return {'status': 'success', 'payment_status': 'started'}

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        return {'status': 'success', 'payment_status': 'started'}

    @patch('random.random')
    def random():
        return 0.5

    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {'billing_tech.transactions.0.status': 'hold_pending'}},
    )

    async def _ensure_next_refresh_time(repeat_interval, iteration):
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['eta'] == now + datetime.timedelta(
            seconds=repeat_interval,
        ), f'Error when processing {iteration}-th iteration'

    intervals_copy = list(intervals)
    with stq.flushing():
        for i in range(max_attempts):
            await _ensure_next_refresh_time(intervals_copy.pop(0), i)
        await _ensure_next_refresh_time(intervals_copy.pop(0), 100)
        await _ensure_next_refresh_time(
            intervals_copy.pop(0), 101,
        )  # and so on
        assert intervals_copy == []
    assert mock_check_basket.times_called == max_attempts + 2


async def test_new_state_applied(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        mock_experiments3,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
):
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    invoice_id = 'hold-success'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': '2',
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '175'}],
                    'yandex_uid': 'new-uid',
                    'pass_params': {'new': 'pass_params'},
                    'trust_afs_params': {'afs': 'params'},
                    'trust_developer_payload': 'some developer payload',
                    'antifraud_payload': {'new': 'antifraud_payload'},
                    'payment_timeout': 180,
                    'mcc': 1234,
                    'login_id': 'some_login_id',
                    'disable_automatic_composite_refund': True,
                    'user_ip': 'new-user-ip',
                    'wallet_payload': {'foo': 'bar'},
                },
            },
        },
    )

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def _mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        data = request.json
        orders = data['orders']
        assert len(orders) == 1
        assert data['pass_params'] == {'new': 'pass_params'}
        assert data['afs_params'] == {'afs': 'params'}
        assert data['developer_payload'] == 'some developer payload'
        assert data['mcc'] == 1234
        assert data['login_id'] == 'some_login_id'
        assert data['payment_timeout'] == 180
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
        }

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    invoice = await collection.find_one({'_id': invoice_id})
    assert invoice['invoice_request']['pass_params'] == {'new': 'pass_params'}
    assert invoice['invoice_request']['trust_afs_params'] == {'afs': 'params'}
    assert (
        invoice['invoice_request']['trust_developer_payload']
        == 'some developer payload'
    )
    assert invoice['invoice_request']['antifraud_payload'] == {
        'new': 'antifraud_payload',
    }
    assert (
        invoice[stq3_context.transactions.fields.PAYMENT_TECH]['last_known_ip']
        == 'new-user-ip'
    )
    assert invoice['invoice_request']['yandex_uid'] == 'new-uid'
    assert invoice['invoice_request']['mcc'] == 1234
    assert invoice['invoice_request']['login_id'] == 'some_login_id'
    assert (
        invoice['invoice_request']['disable_automatic_composite_refund']
        is True
    )
    assert invoice['invoice_request']['wallet_payload'] == {'foo': 'bar'}
    assert invoice['yandex_uid'] == 'new-uid'
    assert _mock_trust_create_basket.times_called == 1


@pytest.mark.parametrize(
    'queue', ['transactions_events', 'transactions_events_hold'],
)
@pytest.mark.nofilldb
@pytest.mark.now(_NOW)
async def test_backoff_on_trust_error(
        stq3_context,
        stq,
        iteration_raises_trust_error,
        stq_reschedule,
        mock_stq_agent_reschedule,
        patch_random,
        queue,
):
    # Assert that task gets rescheduled to the same queue
    mock_stq_agent_reschedule(expected_queue=queue)
    with stq.flushing():
        task_info = helpers.create_task_info(queue)
        await _call_events_handler_task(stq3_context, task_info)
        _assertions.assert_rescheduled_at(
            stq_reschedule,
            datetime.datetime(2019, 6, 3, 12, 0, 7, 500000),
            _NOW_DATETIME,
        )


@pytest.mark.parametrize(
    'queue', ['transactions_events', 'transactions_events_hold'],
)
@pytest.mark.nofilldb
@pytest.mark.now(_NOW)
async def test_backoff_on_rate_limit_exceeded(
        stq3_context,
        stq,
        iteration_raises_rate_limit,
        stq_reschedule,
        mock_stq_agent_reschedule,
        patch_random,
        queue,
):
    # Assert that task gets rescheduled to the same queue
    mock_stq_agent_reschedule(expected_queue='transactions_events')
    with stq.flushing():
        task_info = helpers.create_task_info(queue)
        await _call_events_handler_task(stq3_context, task_info)
        _assertions.assert_rescheduled_at(
            stq_reschedule,
            datetime.datetime(2019, 6, 3, 12, 0, 30),
            _NOW_DATETIME,
        )


@pytest.mark.now(_NOW)
@pytest.mark.parametrize('has_new_fiscal_receipts', [False, True])
async def test_notify_on_fiscal_receipt(
        stq3_context: stq_context.Context,
        stq,
        mockserver,
        mock_experiments3,
        has_new_fiscal_receipts,
):
    invoice_id = 'for_test_notify_on_fiscal_receipt'
    collection = stq3_context.transactions.invoices
    upd_set = {
        'billing_tech.transactions.$[].has_new_fiscal_receipts': (
            has_new_fiscal_receipts
        ),
    }
    await collection.update({'_id': invoice_id}, {'$set': upd_set})

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        invoice = await collection.find_one({'_id': invoice_id})
        assert len(invoice['billing_tech']['transactions']) == 2
        assert not any(
            transaction['has_new_fiscal_receipts']
            for transaction in invoice['billing_tech']['transactions']
        )
        assert all(
            transaction['updated'] != _NOW_DATETIME
            for transaction in invoice['billing_tech']['transactions']
        )
        if has_new_fiscal_receipts:
            assert stq.transactions_notify_on_fiscal_receipt.times_called == 1
            task = stq.transactions_notify_on_fiscal_receipt.next_call()
            assert task['id'] == invoice_id
        else:
            assert stq.transactions_notify_on_fiscal_receipt.times_called == 0


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expected_num_get_order_calls,expected_create_order_calls,expected_orders',
    [
        # Use generated order id
        pytest.param(
            1,
            [
                {
                    'product_id': '123',
                    'order_id': '<alias_id>',
                    'start_ts': 1559563140.0,
                    'start_ts_offset': 0,
                },
            ],
            [{'order_id': '<alias_id>', 'price': '100.00', 'qty': '1'}],
            marks=pytest.mark.config(
                TRANSACTIONS_GENERATE_ORDER_ID={'__default__': True},
                TRANSACTIONS_MAX_GENERATED_ORDER_ID_LENGTH=10,
            ),
        ),
        # Use Trust automatic order id
        pytest.param(
            0,
            [
                {
                    'product_id': '123',
                    'start_ts': 1559563140.0,
                    'start_ts_offset': 0,
                },
            ],
            [
                {
                    'order_id': 'autogenerated_by_trust',
                    'price': '100.00',
                    'qty': '1',
                },
            ],
            marks=pytest.mark.config(
                TRANSACTIONS_GENERATE_ORDER_ID={'__default__': False},
                TRANSACTIONS_MAX_GENERATED_ORDER_ID_LENGTH=10,
            ),
        ),
        # We've gone past the limit - use Trust automatic order id
        pytest.param(
            0,
            [
                {
                    'product_id': '123',
                    'start_ts': 1559563140.0,
                    'start_ts_offset': 0,
                },
            ],
            [
                {
                    'order_id': 'autogenerated_by_trust',
                    'price': '100.00',
                    'qty': '1',
                },
            ],
            marks=pytest.mark.config(
                TRANSACTIONS_GENERATE_ORDER_ID={'__default__': True},
                TRANSACTIONS_MAX_GENERATED_ORDER_ID_LENGTH=9,
            ),
        ),
    ],
)
async def test_generated_order_id(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        mock_get_service_order,
        personal_phones_retrieve,
        personal_emails_retrieve,
        personal_tins_bulk_retrieve,
        expected_num_get_order_calls,
        expected_create_order_calls,
        expected_orders,
):
    invoice_id = 'pending-invoice'
    get_order_mock = mock_get_service_order(
        '<alias_id>', 'error', 'order_not_found',
    )

    @mockserver.json_handler('/trust-payments/v2/orders/')
    def mock_trust_create_order(request):
        assert request.headers['X-Uid'] == '123'
        if 'order_id' not in request.json:
            order_id = 'autogenerated_by_trust'
        else:
            order_id = request.json['order_id']
        return {
            'status': 'success',
            'status_code': 'created',
            'order_id': order_id,
        }

    @mockserver.json_handler('/trust-payments/v2/payments/')
    def mock_trust_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        assert request.json['orders'] == expected_orders
        return {
            'status': 'success',
            'purchase_token': 'trust-basket-token',
            'trust_payment_id': 'trust-payment-id',
        }

    personal_phones_retrieve()
    personal_emails_retrieve()
    personal_tins_bulk_retrieve()

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)

    assert get_order_mock.times_called == expected_num_get_order_calls
    create_order_calls = [
        call['request'].json for call in _get_calls(mock_trust_create_order)
    ]
    assert create_order_calls == expected_create_order_calls


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expected_op_status,expected_num_notifications',
    [
        pytest.param(
            'processing',
            0,
            id=(
                'No match for error in config, expect operation to continue '
                'trying'
            ),
        ),
        pytest.param(
            'failed',
            1,
            marks=[_TERMINAL_CREATE_BASKET_ERROR],
            id='Match for error found in config, expect operation to fail',
        ),
    ],
)
async def test_terminal_create_basket_errors(
        stq3_context: stq_context.Context,
        mockserver,
        stq,
        mock_experiments3,
        personal_phones_retrieve,
        expected_op_status,
        expected_num_notifications,
):
    now = datetime.datetime.utcnow()
    personal_phones_retrieve()
    invoice_id = 'hold-success'
    op_id = 'op/2'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$push': {
                'invoice_request.operations': {
                    'id': op_id,
                    'type': 'update',
                    'status': 'init',
                    'originator': 'processing',
                    'items': [{'item_id': 'ride', 'amount': '150'}],
                },
            },
            '$set': {
                'billing_tech.transactions.0.status': 'clear_success',
                'billing_tech.transactions.0.clear_notify_ts': now,
            },
        },
    )

    @mockserver.json_handler('/trust-payments/v2/payments/')
    # pylint: disable=unused-variable
    def mock_create_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        assert request.method == 'POST'
        response = {
            'status': 'error',
            'status_code': 'shoop_da_whoop',
            'status_desc': 'Firin my laser',
        }
        return response

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        num_notifications = stq.order_payment_result.times_called
        assert num_notifications == expected_num_notifications
        assert mock_create_basket.has_calls

    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    operations = invoice['invoice_request']['operations']
    assert len(operations) == 2
    operation = operations[-1]
    assert operation['id'] == op_id
    assert operation['status'] == expected_op_status


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_held_time_set_on_clear(
        stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        cardstorage_card,
):
    cardstorage_card()

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        assert request.method == 'GET'
        return {'status': 'success', 'payment_status': 'cleared'}

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        assert request.method == 'GET'
        return {'status': 'success', 'payment_status': 'cleared'}

    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {
            '$set': {
                'billing_tech.transactions.0.status': 'hold_pending',
                'invoice_request.originator': 'processing',
            },
        },
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
    invoice = await collection.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    transaction = invoice['billing_tech']['transactions'][0]
    assert transaction['status'] == 'clear_success'
    assert transaction['cleared'] == now
    assert transaction['holded'] == now


@pytest.mark.parametrize(
    'product,invoice_id,expected_queue',
    [
        ('taxi', 'hold-pending', 'transactions_events'),
        pytest.param(
            'taxi',
            'hold-pending',
            'transactions_events_hold',
            marks=[_QUEUE_FOR_HOLD_TAXI],
            id='schedule_hold_in_dedicated_queue_for_taxi',
        ),
        pytest.param(
            'taxi',
            'hold-pending',
            'transactions_events_hold',
            marks=[_QUEUE_FOR_EVERYTHING_TAXI],
            id='schedule_everything_in_dedicated_queue_for_taxi',
        ),
        pytest.param(
            'taxi',
            'hold-pending',
            'transactions_events_hold',
            marks=[_QUEUE_FOR_HOLD_EVERYWHERE],
            id='schedule_hold_in_dedicated_queue_for_all_installations',
        ),
        pytest.param(
            'taxi',
            'hold-pending',
            'transactions_events_hold',
            marks=[_QUEUE_FOR_EVERYTHING_EVERYWHERE],
            id='schedule_everything_in_dedicated_queue_for_all_installations',
        ),
        pytest.param(
            'taxi',
            'clear-pending',
            'transactions_events_clear',
            marks=[_QUEUE_FOR_CLEAR_TAXI],
            id='schedule_clear_in_dedicated_queue_for_taxi',
        ),
        pytest.param(
            'eda',
            'clear-pending',
            'transactions_eda_events_clear',
            marks=[_QUEUE_FOR_CLEAR_EDA],
            id='schedule_clear_in_dedicated_queue_for_eda',
        ),
        pytest.param(
            'eda',
            'hold-pending',
            'transactions_eda_events_hold',
            marks=[_QUEUE_FOR_HOLD_EDA],
            id='schedule_hold_in_dedicated_queue_for_eda',
        ),
    ],
)
async def test_schedule_to_queue_for_stage(
        mockserver,
        stq,
        stq3_context,
        eda_stq3_context,
        product,
        invoice_id,
        expected_queue,
):
    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/start/')
    def mock_pay_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        return {
            'status': 'success',
            'payment_status': 'started',
            'data': 'abc',
        }

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/clear/')
    async def mock_trust_clear_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        return {'status': 'success'}

    with stq.flushing():
        context = eda_stq3_context if product == 'eda' else stq3_context
        await _run_task(context, invoice_id)
        assert getattr(stq, expected_queue).times_called == 1


@_QUEUE_FOR_HOLD_TAXI
@pytest.mark.parametrize(
    'invoice_id,transaction_status,queue,expected_queue',
    [
        (
            'hold-pending',
            'hold_success',
            'transactions_events_hold',
            'transactions_events',
        ),
        (
            'hold-pending',
            'hold_pending',
            'transactions_events',
            'transactions_events_hold',
        ),
    ],
)
async def test_move_to_correct_queue(
        mockserver,
        stq,
        stq3_context,
        invoice_id,
        transaction_status,
        queue,
        expected_queue,
):
    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/start/')
    def mock_pay_basket(request):
        assert request.headers['FallBackRefundable'] == 'yes'
        return {'status': 'success', 'payment_status': 'started'}

    @mockserver.json_handler('/trust-payments/v2/payment_status/tr1234/')
    def mock_check_basket(request):
        return {'status': 'success', 'payment_status': 'started'}

    @mockserver.json_handler('/trust-payments/v2/payments/tr1234/')
    def mock_check_basket_full(request):
        return {'status': 'success', 'payment_status': 'started'}

    status_key = 'billing_tech.transactions.0.status'
    sum_key = 'billing_tech.transactions.0.sum'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {status_key: transaction_status, sum_key: {'ride': '100.0'}}},
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id, queue=queue)
        assert getattr(stq, queue).times_called == 0
        assert getattr(stq, expected_queue).times_called == 1


async def test_task_exits_if_processing_halted(
        stq, stq3_context: stq_context.Context, mock_experiments3,
):
    invoice_id = 'hold-pending'
    collection = stq3_context.transactions.invoices
    await collection.update(
        {'_id': invoice_id},
        {'$set': {'invoice_request.is_processing_halted': True}},
    )
    initial_invoice = await collection.find_one({'_id': invoice_id})
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
    new_invoice = await collection.find_one({'_id': invoice_id})
    assert initial_invoice == new_invoice


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'expected_calls',
    [
        [
            {
                'args': [],
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'id': 'for_test_notify_on_terminated_operations:error-2',
                'kwargs': {
                    'error_data': {
                        'id': 'error-2',
                        'operation_id': 'op-id-2',
                        'terminated_at': {'$date': 1559476800000},
                        'termination_context': {'baz': 'xyzzy'},
                    },
                    'log_extra': None,
                },
                'queue': 'transactions_store_error',
            },
        ],
    ],
)
async def test_notify_on_terminated_operations(
        stq3_context: stq_context.Context,
        stq,
        mockserver,
        mock_experiments3,
        expected_calls,
):
    invoice_id = 'for_test_notify_on_terminated_operations'
    collection = stq3_context.transactions.invoices
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_store_error.times_called == len(expected_calls)
        for expected_call in expected_calls:
            actual_call = stq.transactions_store_error.next_call()
            assert actual_call == expected_call
    invoice = await collection.find_one({'_id': invoice_id})
    invoice_request = invoice['invoice_request']
    errors = invoice_request['terminated_operations']
    assert len(errors) == 2
    assert errors[0]['notify_ts']
    assert errors[1]['notify_ts'] == _NOW_DATETIME


@pytest.mark.now('2020-01-01T00:06:00')
async def test_expired_operations(
        stq3_context: stq_context.Context, stq, mockserver, mock_experiments3,
):
    invoice_id = 'expired-operation'
    collection = stq3_context.transactions.invoices
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 1
        assert stq.order_payment_result.times_called == 0
    invoice = await collection.find_one({'_id': invoice_id})
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'obsolete'
    assert operation['needs_notification'] is True
    assert invoice['billing_tech']['version'] == 2
    assert not invoice['billing_tech']['transactions']

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        assert stq.order_payment_result.times_called == 1
    invoice = await collection.find_one({'_id': invoice_id})
    operation = invoice['invoice_request']['operations'][0]
    assert operation['status'] == 'obsolete'
    assert operation['needs_notification'] is False
    assert invoice['billing_tech']['version'] == 2
    assert not invoice['billing_tech']['transactions']


def _get_calls(mock):
    result = []
    while mock.has_calls:
        result.append(mock.next_call())
    return result


@pytest.fixture
def iteration_raises_trust_error(patch):
    iteration = 'transactions.stq.events_handler.invoice_processing_iteration'

    @patch(iteration)
    async def invoice_processing_iteration(
            context, task_info, invoice_id, log_extra=None,
    ):
        raise rest_client.BaseError


@pytest.fixture
def iteration_raises_rate_limit(patch):
    iteration = 'transactions.stq.events_handler.invoice_processing_iteration'

    @patch(iteration)
    async def invoice_processing_iteration(
            context, task_info, invoice_id, log_extra=None,
    ):
        raise rest_client.RateLimitExceededError


@pytest.fixture
def mock_randomize_delay(monkeypatch):
    monkeypatch.setattr(eta_util, '_randomize_delay', lambda delay: delay)


async def _call_events_handler_task(stq3_context, task_info):
    await events_handler.task(
        context=stq3_context,
        task_info=task_info,
        invoice_id='some_invoice_id',
        log_extra=None,
    )


def _assert_rescheduled_at(mock, expected):
    calls = mock.calls
    assert len(calls) == 1
    eta = calls[0]['eta']
    msg = f'{eta!r} != {expected!r}'
    expected_delta = (expected - _NOW_DATETIME).total_seconds()
    actual_delta = (eta - _NOW_DATETIME).total_seconds()
    assert actual_delta == pytest.approx(expected_delta), msg


def _assert_correct_call_to_uantifraud(call):
    def _iso_str_datetimes_equality(date_a: str, date_b: str) -> bool:
        date_a_obj = datetime.datetime.fromisoformat(date_a)
        date_b_obj = datetime.datetime.fromisoformat(date_b)
        return date_a_obj == date_b_obj

    assert list(call) == ['request']
    content = call['request'].json

    assert content['request_id'] == '11111111111111111111111111111111'
    assert content['service_id'] == 124
    assert content['transaction'] == {
        'amount_by_type': {'ride': '100'},
        'currency': 'RUR',
    }
    assert content['user'] == {'ip': '127.0.0.1', 'passport_uid': '123'}
    assert content['payment'] == {'type': 'card', 'method': 'card-x1324'}
    assert content['order_id'] == 'pending-invoice'
    assert content['billing_service'] == 'card'
    assert content['external_user_info'] == {}
    assert content['payload'] == {}
    assert content['personal_phone_id'] == 'personal-phone-id'
    assert content['products'] == {'ride': '123'}
    assert content['transactions_scope'] == 'taxi'
    assert content['payload'] == {}
    assert _iso_str_datetimes_equality(
        content['created'], '2019-01-01T03:00:00+03:00',
    )


async def _run_task(stq_context, invoice_id, queue='transactions_events'):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue=queue),
        invoice_id,
        log_extra=None,
    )


def _get_callback_created_at(date_time: datetime.datetime) -> dict:
    assert date_time.tzinfo is None
    return {
        '$date': int(
            date_time.replace(tzinfo=datetime.timezone.utc).timestamp() * 1000,
        ),
    }


async def _run_watchdog_task(
        stq_context, events, invoice_id, queue='transactions_watchdog',
):
    await watchdog_events_handler.task(
        stq_context, invoice_id, events, log_extra=None,
    )
