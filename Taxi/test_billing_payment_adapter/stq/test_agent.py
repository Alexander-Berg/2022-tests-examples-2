import contextlib
import datetime as dt

from aiohttp import web
import bson
import pytest

from taxi.billing.util import dates as billing_dates
from taxi.stq import async_worker_ng
from taxi.util import dates

from billing_payment_adapter.stq import adapter
from billing_payment_adapter.stq import helpers
from billing_payment_adapter.stq import send_to_orders


@pytest.mark.now('2019-10-23 00:00:00')
@pytest.mark.config(
    BILLING_PAYMENT_ADAPTER_PAYMENT_TYPES=['agent', 'compensation'],
    BILLING_PAYMENT_ADAPTER_PAYMENTS={
        'tips': {
            'billing_orders_payment_kind': 'trip_tips',
            'is_ignored': False,
        },
        'ride': {
            'billing_orders_payment_kind': 'trip_payment',
            'is_ignored': False,
        },
        'toll_road': {
            'billing_orders_payment_kind': 'trip_toll_road',
            'is_ignored': False,
        },
        'ride_compensation': {
            'billing_orders_payment_kind': 'trip_compensation',
            'is_ignored': False,
        },
    },
    BILLING_PAYMENT_ADAPTER_BILLING_TYPES=['card'],
    BILLING_TLOG_SERVICE_IDS={'agent': 124},
    BILLING_DRIVER_MODES_ENABLED=True,
    BILLING_DRIVER_MODES_SCOPE={},
    ARCHIVE_API_CLIENT_QOS={'__default__': {'timeout-ms': 300, 'attempts': 1}},
    BILLING_DOCS_REPLICATION_SETTINGS={'__default__': {'TTL_DAYS': 6}},
    BILLING_PAYMENT_ADAPTER_ORDERS_SENDING_SETTINGS={
        'bulk_limit': 4,
        'delay_ms': 1,
    },
)
@pytest.mark.parametrize(
    'test_data_json, expected_exception',
    [
        ('orders.json', None),
        ('orders_with_transaction_payload.json', None),
        ('orders_send_driver_details.json', None),
        ('driver_fix.json', None),
        ('tips.json', NotImplementedError),
        ('no_contract.json', helpers.contracts.ContractNotFoundError),
        ('order_toll_road.json', None),
        ('order_toll_road_driver_fix.json', None),
        # per transaction tests
        ('agent_payment.json', None),
        ('agent_refund.json', None),
        ('agent_payment_driver_fix.json', None),
        ('agent_refund_driver_fix.json', None),
        ('agent_compensation.json', None),
        ('agent_compensation_refund.json', None),
        ('agent_compensation_driver_fix.json', None),
        ('agent_compensation_refund_driver_fix.json', None),
        ('per_transaction_tips.json', NotImplementedError),
        (
            'per_transaction_no_contract.json',
            helpers.contracts.ContractNotFoundError,
        ),
    ],
)
async def test_task(
        patch,
        monkeypatch,
        stq3_context,
        mock_billing_orders,
        mock_parks_replica,
        mock_taxi_agglomerations,
        mock_billing_replication,
        mock_billing_reports,
        mockserver,
        test_data_json,
        expected_exception,
        load_json,
        run_per_order_task,
        run_per_transaction_task,
):
    test_data = load_json(test_data_json)

    order_id = test_data['order_id']
    billing_client_id = test_data['billing_client_id']
    expected_orders = test_data['expected_orders']
    order_doc = load_json(test_data['order_doc_path'])
    contract = test_data.get('contract')
    subscription_doc = test_data.get('subscription_doc')
    transaction_id = test_data.get('transaction_id')

    monkeypatch.setattr(
        stq3_context.config,
        'BILLING_INVOICE_TRANSACTION_SEND_DRIVER_DETAILS',
        test_data.get(
            'BILLING_INVOICE_TRANSACTION_SEND_DRIVER_DETAILS', False,
        ),
    )

    @mockserver.json_handler('/archive-api/archive/order')
    def _get_order_by_id(request):
        return web.Response(
            body=bson.BSON.encode({'doc': order_doc}),
            headers={'Content-Type': 'application/bson'},
        )

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    def _get_v1_parks_billing_client_id(request):
        return web.json_response(billing_client_id)

    orders = []

    @mock_billing_orders('/v2/process/async')
    def _process_async(request):
        orders.append(request.json)
        return web.json_response(
            {'orders': [{'doc_id': 0, 'external_ref': '', 'topic': ''}]},
        )

    @mock_taxi_agglomerations('/v1/geo_nodes/get_mvp_oebs_id')
    def _get_mvp_oebs_id(request):
        del request  # unused
        return web.json_response({'oebs_mvp_id': 'Moscow_OEBS_ID'})

    @mock_billing_replication('/v1/active-contracts/')
    def _get_active_contracts(request):
        # check request contract on order due only
        active_ts = dates.parse_timestring(request.args['active_ts'])
        assert active_ts == order_doc['request']['due']
        return web.json_response([contract] if contract else [])

    @mock_billing_reports('/v1/docs/select')
    def _get_subscription_doc(request):
        end_time = billing_dates.parse_datetime(request.json['end_time'])
        assert end_time == order_doc['request']['due'].replace(
            tzinfo=dt.timezone.utc,
        )
        resp = {
            'docs': [subscription_doc] if subscription_doc else [],
            'cursor': {},
        }
        return web.json_response(resp)

    run_context = contextlib.nullcontext()
    if expected_exception:
        run_context = pytest.raises(expected_exception)

    with run_context:
        if transaction_id is None:
            await run_per_order_task(order_id=order_id)
        else:
            await run_per_transaction_task(
                order_id=order_id,
                version=1,
                created_at=dates.utcnow(),
                transaction_id=transaction_id,
            )

    assert orders == expected_orders


@pytest.fixture(name='run_per_order_task')
def _run_per_order_task(stq3_context):
    async def do_run(order_id: str):
        await adapter.task(stq3_context, order_id, 1, dates.utcnow())

    return do_run


@pytest.fixture(name='run_per_transaction_task')
def _run_per_transaction_task(stq3_context):
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
