from aiohttp import web
import bson
import pytest

from taxi.util import dates

from billing_payment_adapter.stq import adapter

_CONVERT_CURRENCY_SINCE = '2015-10-01T00:00:00+00:00'


@pytest.mark.now('2019-10-23 00:00:00')
@pytest.mark.config(
    BILLING_PAYMENT_ADAPTER_PAYMENT_TYPES=['card'],
    BILLING_PAYMENT_ADAPTER_PAYMENTS={
        'ride': {
            'billing_orders_payment_kind': 'trip_payment',
            'is_ignored': False,
        },
        'cashback': {
            'billing_orders_payment_kind': 'plus_payment',
            'is_ignored': False,
        },
    },
    BILLING_PAYMENT_ADAPTER_BILLING_TYPES=['card'],
    BILLING_TLOG_SERVICE_IDS={'card': 124},
    BILLING_DRIVER_MODES_ENABLED=True,
    BILLING_DRIVER_MODES_SCOPE={},
    ARCHIVE_API_CLIENT_QOS={'__default__': {'timeout-ms': 300, 'attempts': 1}},
    BILLING_DOCS_REPLICATION_SETTINGS={'__default__': {'TTL_DAYS': 6}},
    BILLING_PAYMENT_ADAPTER_ORDERS_SENDING_SETTINGS={
        'bulk_limit': 4,
        'delay_ms': 1,
    },
    BILLING_PAYMENT_ADAPTER_PLUS_PAYMENTS=['plus_payment'],
    BILLING_PAYMENT_ADAPTER_PLUS_OPERATOR_SETTINGS_BY_COUNTRY={
        'rus': [
            {'start': '2015-10-01T00:00:00+00:00', 'billing_client_id': '100'},
        ],
        'kaz': [
            {'start': '2015-10-01T00:00:00+00:00', 'billing_client_id': '200'},
        ],
    },
    BILLING_PAYMENT_ADAPTER_WRITE_RATED_AMOUNT_SINCE=_CONVERT_CURRENCY_SINCE,
    BILLING_PAYMENT_ADAPTER_WRITE_AGENT_PERCENT_SINCE=_CONVERT_CURRENCY_SINCE,
    BILLING_PAYMENT_ADAPTER_STRICT_AGENT_REWARD_CHECK=False,
)
@pytest.mark.parametrize(
    'test_data_json, expected_exception',
    [('orders.json', None), ('kaz_orders.json', None)],
)
@pytest.mark.filldb(currency_rates='for_test_task', cities='for_test_task')
async def test_task(
        patch,
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
):
    test_data = load_json(test_data_json)

    order_id = test_data['order_id']
    billing_client_id = test_data['billing_client_id']
    expected_orders = test_data['expected_orders']
    order_doc = test_data['order_doc']
    contracts = test_data.get('contracts')
    subscription_doc = test_data.get('subscription_doc')

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
        client_id = request.args['client_id']
        result = [
            contract
            for contract in contracts or []
            if contract['CLIENT_ID'] == client_id
        ]
        return web.json_response(result)

    @mock_billing_reports('/v1/docs/select')
    def _get_subscription_doc(request):
        del request  # unused
        resp = {
            'docs': [subscription_doc] if subscription_doc else [],
            'cursor': {},
        }
        return web.json_response(resp)

    if expected_exception:
        with pytest.raises(expected_exception):
            await adapter.task(stq3_context, order_id, 1, dates.utcnow())
    else:
        await adapter.task(stq3_context, order_id, 1, dates.utcnow())

    for payout in orders:
        for order in payout['orders']:
            order['data']['payments'].sort(key=lambda x: x['payment_kind'])
    assert orders == expected_orders
