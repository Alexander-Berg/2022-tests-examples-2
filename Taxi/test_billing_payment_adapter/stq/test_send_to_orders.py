from __future__ import annotations

import contextlib
import dataclasses
import datetime as dt
from typing import List
from typing import Optional

from aiohttp import web
import bson
import pytest

from taxi.billing.util import dates
from taxi.stq import async_worker_ng
from taxi.util import payment_helpers

from billing_payment_adapter.stq import send_to_orders
from billing_payment_adapter.stq import taxi_send_to_orders_callback

_DEFAULT_CONFIG_VALUES = dict(
    BILLING_PAYMENT_ADAPTER_PAYMENT_TYPES=['applepay', 'card', 'compensation'],
    BILLING_PAYMENT_ADAPTER_PAYMENTS={
        'tips': {
            'billing_orders_payment_kind': 'trip_tips',
            'is_ignored': False,
        },
        'ride': {
            'billing_orders_payment_kind': 'trip_payment',
            'is_ignored': False,
        },
        'rebate': {
            'billing_orders_payment_kind': 'unknown',
            'is_ignored': True,
        },
        'ride_compensation': {
            'billing_orders_payment_kind': 'trip_compensation',
            'is_ignored': False,
        },
    },
    BILLING_PAYMENT_ADAPTER_BILLING_TYPES=['card'],
    BILLING_TLOG_SERVICE_IDS={'card': 124},
    ARCHIVE_API_CLIENT_QOS={'__default__': {'timeout-ms': 300, 'attempts': 1}},
    BILLING_DOCS_REPLICATION_SETTINGS={'billing_docs_doc': {'TTL_DAYS': 6}},
    BILLING_PAYMENT_ADAPTER_ORDERS_SENDING_SETTINGS={
        'bulk_limit': 4,
        'delay_ms': 1,
    },
)

_CONFIG_MARK = pytest.mark.config(**_DEFAULT_CONFIG_VALUES)

_COMMON_TEST_CASES = [
    'transaction_with_id_not_found.json',
    'transaction_not_cleared.json',
    'transaction_with_not_allowed_payment_type.json',
    'transaction_old_personal_wallet.json',
]


@dataclasses.dataclass(frozen=True)
class Mocks:
    docs_select: object
    orders_process_async: object
    stq_agent_reschedule: object


@dataclasses.dataclass(frozen=True)
class _TestData:
    order_id: str
    version: int
    created_at: dt.datetime
    transaction_id: str
    notification_type: Optional[str]
    billing_client_id: dict
    order_doc: dict
    contract: dict
    docs_select_response: Optional[dict]
    expected_num_reschedules: int
    expected_fail: bool
    expected_orders: List[dict]
    expected_docs_select_request: Optional[dict]


@pytest.mark.now('2019-10-23 00:00:00')
@_CONFIG_MARK
@pytest.mark.parametrize(
    'test_data_json',
    [
        'reschedule_if_incorrect_invoice_version.json',
        'new_transaction.json',
        'new_yandex_card_transaction.json',
        'new_sbp_transaction.json',
        'old_transaction_not_created_yet.json',
        'old_transaction_already_created.json',
        'old_transaction_and_old_task.json',
        'old_transaction_and_too_old_task.json',
        'transaction_zero_payment.json',
        *_COMMON_TEST_CASES,
    ],
)
@pytest.mark.nofilldb()
async def test_send_to_orders_task(
        mock_common_deps, test_data_json, load_json, run_task,
):
    data = _load_test_data(load_json, test_data_json)

    mocks = mock_common_deps(
        billing_client_id=data.billing_client_id,
        order_doc=data.order_doc,
        contract=data.contract,
        docs_select_response=data.docs_select_response,
    )

    with _expectation(data.expected_fail):
        await run_task(
            order_id=data.order_id,
            version=data.version,
            created_at=data.created_at,
            transaction_id=data.transaction_id,
        )
    _check_reschedule(
        mocks.stq_agent_reschedule,
        data,
        'billing_payment_adapter_send_to_orders',
    )

    _check_orders_process_async(
        mocks.orders_process_async, data.expected_orders,
    )
    _check_docs_select(mocks.docs_select, data.expected_docs_select_request)


def _check_reschedule(stq_agent_reschedule, data, expected_queue):
    assert stq_agent_reschedule.times_called == data.expected_num_reschedules
    assert data.expected_num_reschedules in [0, 1]
    if data.expected_num_reschedules:
        assert (
            stq_agent_reschedule.next_call()['request'].json['queue_name']
            == expected_queue
        )


@pytest.mark.now('2019-10-23 00:00:00')
@_CONFIG_MARK
@pytest.mark.parametrize(
    'test_data_json',
    [
        *_COMMON_TEST_CASES,
        'reschedule_if_not_terminal.json',
        'callback_new_transaction.json',
        pytest.param(
            'callback_new_transaction_trust_payment_id.json',
            id='it should use transaction.trust_payment_id for new invoices',
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADAPTER_WRITE_TRUST_PAYMENT_ID_SINCE=(
                        '2000-01-01T00:00:00+00:00'
                    ),
                    **_DEFAULT_CONFIG_VALUES,
                ),
            ],
        ),
        pytest.param(
            'compensation_trust_payment_id.json',
            id='it should use compensation.trust_payment_id for new invoices',
            marks=[
                pytest.mark.config(
                    BILLING_PAYMENT_ADAPTER_WRITE_TRUST_PAYMENT_ID_SINCE=(
                        '2000-01-01T00:00:00+00:00'
                    ),
                    **_DEFAULT_CONFIG_VALUES,
                ),
            ],
        ),
        'callback_new_yandex_card_transaction.json',
        'callback_new_sbp_transaction.json',
        'callback_new_transaction_doc_exists.json',
        'callback_transaction_zero_payment.json',
        'transaction_held.json',
        'transaction_hold_fail.json',
        'transaction_clear_fail.json',
        'compensation.json',
        'transaction_refund.json',
        'transaction_refund_transaction_payload.json',
        'transaction_resize.json',
        'compensation_refund.json',
    ],
)
@pytest.mark.nofilldb()
async def test_taxi_send_to_orders_callback_task(
        mock_common_deps, test_data_json, load_json, run_callback_task,
):
    data = _load_test_data(load_json, test_data_json)

    mocks = mock_common_deps(
        billing_client_id=data.billing_client_id,
        order_doc=data.order_doc,
        contract=data.contract,
        docs_select_response=data.docs_select_response,
        transaction_id=data.transaction_id,
    )

    with _expectation(data.expected_fail):
        await run_callback_task(
            order_id=data.order_id,
            version=data.version,
            created_at=data.created_at,
            transaction_id=data.transaction_id,
            order_doc=data.order_doc,
            notification_type=data.notification_type,
        )
    _check_reschedule(
        mocks.stq_agent_reschedule, data, 'taxi_send_to_orders_callback',
    )

    _check_orders_process_async(
        mocks.orders_process_async, data.expected_orders,
    )
    _check_docs_select(mocks.docs_select, data.expected_docs_select_request)


def _expectation(expected_fail):
    if expected_fail:
        return pytest.raises(RuntimeError)
    return contextlib.nullcontext()


def _load_test_data(load_json, test_data_json) -> _TestData:
    raw = load_json(test_data_json)
    return _TestData(
        order_id=raw['order_id'],
        version=raw['version'],
        created_at=raw['task_created_at'],
        transaction_id=raw['transaction_id'],
        notification_type=raw.get('notification_type'),
        billing_client_id=raw['billing_client_id'],
        order_doc=load_json(raw['order_doc_json_path']),
        contract=raw.get('contract'),
        docs_select_response=raw.get('docs_select_response'),
        expected_num_reschedules=raw.get('expected_num_reschedules', False),
        expected_fail=raw.get('expected_fail', False),
        expected_orders=raw['expected_orders'],
        expected_docs_select_request=raw.get('expected_docs_select_request'),
    )


@pytest.fixture(name='mock_common_deps')
def _mock_common_deps(
        mock_billing_orders,
        mock_billing_replication,
        mock_billing_reports,
        mock_transactions_ng,
        mock_parks_replica,
        mock_taxi_agglomerations,
        mockserver,
):
    def _mock(
            order_doc,
            billing_client_id,
            contract,
            docs_select_response,
            transaction_id=None,
    ) -> Mocks:
        @mock_transactions_ng('/v2/invoice/retrieve')
        def _invoice_retrieve(request):
            return _convert_order_doc_to_invoice(order_doc, transaction_id)

        @mockserver.json_handler('/archive-api/archive/order')
        def _get_order_by_id(request):
            return web.Response(
                body=bson.BSON.encode({'doc': order_doc}),
                headers={'Content-Type': 'application/bson'},
            )

        @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
        def _get_v1_parks_billing_client_id(request):
            return web.json_response(billing_client_id)

        @mock_billing_orders('/v2/process/async')
        def _process_async(request):
            return web.json_response(
                {'orders': [{'doc_id': 0, 'external_ref': '', 'topic': ''}]},
            )

        @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
        def _get_mvp_oebs_id(request):
            del request  # unused
            return web.json_response({'oebs_mvp_id': 'Moscow_OEBS_ID'})

        @mock_billing_replication('/v1/active-contracts/')
        def _get_active_contracts(request):
            del request  # unused
            return web.json_response([contract] if contract else [])

        @mockserver.json_handler('/stq-agent/queues/api/reschedule')
        def _patch_stq_agent_reschedule(request):
            return {}

        @mock_billing_reports('/v1/docs/select')
        def _patch_docs_select(request):
            resp = docs_select_response or {'docs': [], 'cursor': {}}
            return web.json_response(resp)

        return Mocks(
            docs_select=_patch_docs_select,
            orders_process_async=_process_async,
            stq_agent_reschedule=_patch_stq_agent_reschedule,
        )

    return _mock


def _check_docs_select(patch_docs_select, expected_docs_select_request):
    if expected_docs_select_request is None:
        assert patch_docs_select.times_called == 0
    else:
        assert patch_docs_select.times_called == 1
        docs_select_request = patch_docs_select.next_call()['request'].json
        assert docs_select_request == expected_docs_select_request


def _check_orders_process_async(orders_process_async, expected_orders):
    assert orders_process_async.times_called == len(expected_orders)
    for order in expected_orders:
        call = orders_process_async.next_call()
        assert call['request'].json == order


def _convert_order_doc_to_invoice(order_doc, transaction_id):
    result = {
        'id': order_doc['_id'],
        'invoice_due': dates.format_time(order_doc['request']['due']),
        'currency': order_doc['performer']['tariff']['currency'],
        'created': dates.format_time(order_doc['created']),
        'status': 'cleared',
        'operation_info': {},
        'sum_to_pay': [],
        'held': [],
        'cleared': [],
        'debt': [],
        'commit_version': order_doc['billing_tech']['version'],
        'transactions': _convert_to_invoice_transactions(
            order_doc, transaction_id,
        ),
        'compensation': {
            'version': 1,
            'compensations': _convert_to_invoice_compensations(
                order_doc, transaction_id,
            ),
            'operations': [],
        },
        'yandex_uid': 'some_yandex_uid',
        'payment_types': [],
    }
    return result


def _convert_to_invoice_transactions(order_doc, transaction_id):
    now = dt.datetime.now(tz=dt.timezone.utc)
    result = []
    for tx in order_doc['billing_tech']['transactions']:
        refunds = []
        for refund in tx.get('refunds', []):
            refund_id = refund['trust_refund_id']
            refunds.append(
                {
                    'created': _maybe_format_time(refund.get('created', now)),
                    'updated': _maybe_format_time(refund.get('updated', now)),
                    'refunded': _maybe_format_time(
                        refund.get('refund_made_at'),
                    ),
                    'sum': _convert_to_sum(refund['sum']),
                    'status': refund['status'],
                    'external_payment_id': refund_id,
                    'operation_id': _get_operation_id(
                        refund_id, transaction_id,
                    ),
                },
            )
        resizes = []
        for resize in tx.get('resizes', []):
            resizes.append(
                {
                    'operation_id': _get_operation_id(
                        resize['id'], transaction_id,
                    ),
                    'created': _maybe_format_time(now),
                },
            )
        tx_id = tx.get('purchase_token', tx['trust_payment_id'])
        transaction = {
            'created': _maybe_format_time(tx.get('created', now)),
            'updated': _maybe_format_time(tx.get('updated', now)),
            'held': _maybe_format_time(tx.get('holded')),
            'cleared': _maybe_format_time(tx.get('cleared')),
            'sum': _convert_to_sum(tx['sum']),
            'initial_sum': _convert_to_sum(tx.get('initial_sum', tx['sum'])),
            'terminal_id': _get_terminal_id(tx),
            'status': tx['status'],
            'refunds': refunds,
            'resizes': resizes,
            'trust_payment_id': tx['trust_payment_id'],
            'external_payment_id': tx_id,
            'operation_id': _get_operation_id(tx_id, transaction_id),
            'payment_type': tx['payment_method_type'],
        }
        if 'transaction_payload' in tx:
            transaction['transaction_payload'] = tx['transaction_payload']
        result.append(transaction)
    return result


def _convert_to_invoice_compensations(order_doc, transaction_id):
    result = []
    for tx in order_doc['billing_tech'].get('compensations', []):
        refunds = []
        for refund in tx.get('refunds', []):
            refund_id = refund['trust_refund_id']
            refunds.append(
                {
                    'refunded': _maybe_format_time(
                        refund.get('refund_made_at'),
                    ),
                    'sum': _convert_to_sum(refund['sum']),
                    'status': refund['status'],
                    'external_payment_id': refund_id,
                    'operation_id': _get_operation_id(
                        refund_id, transaction_id,
                    ),
                },
            )
        tx_id = tx.get('purchase_token', tx['trust_payment_id'])
        result.append(
            {
                'compensated': _maybe_format_time(
                    tx.get('compensation_made_at'),
                ),
                'sum': _convert_to_sum(tx['sum']),
                'terminal_id': _get_terminal_id(tx),
                'status': tx['status'],
                'refunds': refunds,
                'trust_payment_id': tx['trust_payment_id'],
                'external_payment_id': tx_id,
                'operation_id': _get_operation_id(tx_id, transaction_id),
            },
        )
    return result


def _get_terminal_id(tx):
    if tx.get('terminal_id') is not None:
        return str(tx.get('terminal_id'))
    return None


def _get_operation_id(cur_id, id_):
    if cur_id == id_:
        return 'some_operation_id'
    return 'another_operation_id'


def _maybe_format_time(value: Optional[dt.datetime]) -> Optional[str]:
    if value is None:
        return None
    return dates.format_time(value)


def _convert_to_sum(inner_sum):
    result = []
    for key, value in inner_sum.items():
        result.append(
            {
                'item_id': key,
                'amount': str(payment_helpers.inner_to_decimal(value)),
            },
        )
    return result


def _convert_order_doc_to_payload(order_doc):
    completed_at = order_doc.get('statistics', {}).get('complete_time')
    return {
        'payment_type': order_doc['payment_tech']['type'],
        'source': order_doc['request'].get('source', 'yandex'),
        'is_roaming_user': order_doc['request'].get('is_roaming_user', False),
        'order_id': order_doc['_id'],
        'alias_id': order_doc['performer']['taxi_alias']['id'],
        'due': dates.format_time(order_doc['request']['due']),
        'completed_at': (
            dates.format_time(completed_at) if completed_at else None
        ),
        'driver': {
            'clid': order_doc['performer']['clid'],
            'park_id': order_doc['performer'].get('db_id'),
            'driver_profile_id': order_doc['performer']['uuid'],
        },
        'tariff_class': order_doc['performer']['tariff']['class'],
        'nearest_zone': order_doc['nz'],
        'city': order_doc['city'],
    }


@pytest.fixture(name='run_task')
def _run_task(stq3_context):
    async def do_run(
            order_id: str,
            version: int,
            created_at: dt.datetime,
            transaction_id: str,
    ):
        task_info = async_worker_ng.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='billing_payment_adapter_send_to_orders',
        )
        await send_to_orders.task(
            context=stq3_context,
            task_info=task_info,
            order_id=order_id,
            version=version,
            created_at=created_at,
            transaction_id=transaction_id,
            log_extra=None,
        )

    return do_run


@pytest.fixture(name='run_callback_task')
def _run_callback_task(stq3_context):
    async def do_run(
            order_id: str,
            version: int,
            created_at: dt.datetime,
            transaction_id: str,
            order_doc: dict,
            notification_type: Optional[str] = None,
    ):
        if notification_type is None:
            notification_type = 'transaction_clear'
        task_info = async_worker_ng.TaskInfo(
            id='task_id',
            exec_tries=0,
            reschedule_counter=0,
            queue='taxi_send_to_orders_callback',
        )
        await taxi_send_to_orders_callback.task(
            context=stq3_context,
            task_info=task_info,
            invoice_id=order_id,
            operation_id='some_operation_id',
            operation_status='done',
            notification_type=notification_type,
            id_namespace='some_id_namespace',
            payload=_convert_order_doc_to_payload(order_doc),
            version=version,
            created_at=created_at,
            transactions=[],
        )

    return do_run
