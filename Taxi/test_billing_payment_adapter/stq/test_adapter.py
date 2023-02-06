from __future__ import annotations

from aiohttp import web
import bson
import pytest

from taxi.util import dates

from billing_payment_adapter.stq import adapter
from billing_payment_adapter.stq import helpers


@pytest.mark.now('2019-10-23 00:00:00')
@pytest.mark.config(
    BILLING_PAYMENT_ADAPTER_PAYMENT_TYPES=['card', 'compensation'],
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
            'billing_orders_payment_kind': 'trip_payment_compensation',
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
    BILLING_PAYMENT_ADAPTER_WRITE_RATED_AMOUNT_SINCE=(
        '2020-10-23T00:00:00+03:00'
    ),
    BILLING_PAYMENT_ADAPTER_WRITE_AGENT_PERCENT_SINCE=(
        '2020-10-23T00:00:00+03:00'
    ),
    BILLING_PAYMENT_ADAPTER_STRICT_AGENT_REWARD_CHECK=False,
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'many_payments_many_transactions.json',
        'many_transactions_no_contract.json',
        'old_transactions_are_ignored.json',
        'not_cleared_are_ignored.json',
        'unknown_payments_ignored.json',
        'payment_type_is_checked.json',
        'billing_type_is_checked.json',
        'reschedule_if_incorrect_invoice_version.json',
        'compensations.json',
        'invoice_transaction_with_driver_details.json',
        'invoice_transaction_no_db_id_no_driver_details.json',
        'zero_amount_is_ignored.json',
        'no_payments_no_payouts.json',
        'old_transactions_are_not_ignored_due_task_birth_time.json',
        'fail_because_too_old_task.json',
        'many_payments_many_transactions_with_conversion.json',
    ],
)
@pytest.mark.filldb(currency_rates='for_test_task', cities='for_test_task')
async def test_task(
        patch,
        monkeypatch,
        stq3_context,
        mock_billing_orders,
        mock_parks_replica,
        mock_taxi_agglomerations,
        mock_billing_replication,
        mockserver,
        test_data_json,
        load_json,
):
    test_data = load_json(test_data_json)

    order_id = test_data['order_id']
    billing_client_id = test_data['billing_client_id']
    expected_orders = test_data['expected_orders']
    order_doc = test_data['order_doc']
    created_at = test_data.get('task_created_at') or dates.utcnow()
    contract = test_data.get('contract')
    expected_rescheduled = test_data.get('expected_rescheduled', False)
    expected_fail = test_data.get('expected_fail', False)
    expected_contract_not_found_exc = test_data.get(
        'expected_contract_not_found_exc', False,
    )

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

    is_rescheduled = False

    @patch(
        'billing_payment_adapter.generated.service.stq_client.plugin.'
        'QueueClient.call_later',
    )
    async def _call_later(*args, **kwargs):
        assert kwargs['kwargs']['fail_count'] == 2
        nonlocal is_rescheduled
        is_rescheduled = True

    if expected_fail:
        with pytest.raises(RuntimeError):
            await adapter.task(
                stq3_context, order_id, 1, created_at, fail_count=1,
            )
    elif expected_contract_not_found_exc:
        with pytest.raises(helpers.contracts.ContractNotFoundError):
            await adapter.task(
                stq3_context, order_id, 1, created_at, fail_count=1,
            )
    else:
        await adapter.task(stq3_context, order_id, 1, created_at, fail_count=1)
        assert is_rescheduled == expected_rescheduled
        assert orders == expected_orders
