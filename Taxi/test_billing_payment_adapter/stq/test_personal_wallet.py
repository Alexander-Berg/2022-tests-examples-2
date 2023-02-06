import datetime

from aiohttp import web
import bson
import pytest

from taxi.billing.util import dates as billing_dates
from taxi.util import dates

from billing_payment_adapter.stq import adapter
from billing_payment_adapter.stq import helpers


@pytest.mark.now('2019-10-23 00:00:00')
@pytest.mark.config(
    BILLING_PAYMENT_ADAPTER_PAYMENT_TYPES=['card', 'personal_wallet'],
    BILLING_PAYMENT_ADAPTER_PAYMENTS={
        'tips': {
            'billing_orders_payment_kind': 'trip_tips',
            'is_ignored': False,
        },
        'ride': {
            'billing_orders_payment_kind': 'trip_payment',
            'is_ignored': False,
        },
    },
    BILLING_PAYMENT_ADAPTER_BILLING_TYPES=['card'],
    BILLING_TLOG_SERVICE_IDS={
        'card': 124,
        'coupon/netted': 111,
        'coupon/paid': 137,
        'cargo_card': 1162,
        'cargo_coupon/netted': 1161,
        'cargo_coupon/paid': 1164,
    },
    BILLING_DRIVER_MODES_ENABLED=True,
    BILLING_DRIVER_MODES_SCOPE={},
    ARCHIVE_API_CLIENT_QOS={'__default__': {'timeout-ms': 300, 'attempts': 1}},
    BILLING_DOCS_REPLICATION_SETTINGS={'__default__': {'TTL_DAYS': 6}},
    BILLING_PAYMENT_ADAPTER_ORDERS_SENDING_SETTINGS={
        'bulk_limit': 4,
        'delay_ms': 1,
    },
    BILLING_PAYMENT_ADAPTER_PLUS_PAYOUT_SETTINGS_BY_COUNTRY={
        'blr': {'is_payable': True, 'product': 'coupon_plus_expense'},
        'rus': {'is_payable': False, 'product': 'coupon_plus'},
    },
    BILLING_SUBVENTIONS_CONTRACT_DELAY_ENABLED=True,
)
@pytest.mark.parametrize(
    'test_data_json, expected_exception',
    [
        ('card_and_wallet.json', None),
        ('card_and_wallet_transaction_payload.json', None),
        ('card_and_wallet_without_performer.json', None),
        ('card_and_cargo_wallet.json', None),
        ('card_and_wallet_blr.json', None),
        ('card_and_wallet_driver_fix.json', None),
        ('skip_not_from_transactions.json', None),
        ('unknown_country.json', ValueError),
        ('no_contract.json', helpers.contracts.ContractNotFoundError),
        ('no_marketing_contract.json', None),
        ('wait_for_marketing_contract.json', None),
    ],
)
@pytest.mark.filldb(cities='for_test_wallet', currency_rates='for_test_wallet')
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
    billing_client_id_by_clid = test_data['billing_client_id_by_clid']
    expected_orders = test_data['expected_orders']
    order_doc = test_data['order_doc']
    contract = test_data.get('contract')
    subscription_doc = test_data.get('subscription_doc')

    @mockserver.json_handler('/archive-api/archive/order')
    def _get_order_by_id(request):
        return web.Response(
            body=bson.BSON.encode({'doc': order_doc}),
            headers={'Content-Type': 'application/bson'},
        )

    @mock_parks_replica('/v1/parks/billing_client_id/retrieve')
    def _get_v1_parks_billing_client_id(request):
        return web.json_response(
            billing_client_id_by_clid[request.args['park_id']],
        )

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
            tzinfo=datetime.timezone.utc,
        )
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

    assert orders == expected_orders


@pytest.mark.parametrize(
    'contracts, expected_currency, exception',
    [
        (
            [{'CURRENCY': 'RUR', 'ID': 1, 'DT': '2018-08-01 00:00:00'}],
            'RUB',
            None,
        ),
        (
            [{'CURRENCY': 'USD', 'ID': 1, 'DT': '2018-08-01 00:00:00'}],
            'USD',
            None,
        ),
        (
            [{'CURRENCY': None, 'ID': 1, 'DT': '2018-08-01 00:00:00'}],
            'USD',
            helpers.contracts.ContractNotFoundError,
        ),
        ([], None, helpers.contracts.ContractNotFoundError),
        (
            [
                {'CURRENCY': 'USD', 'ID': 1, 'DT': '2018-08-01 00:00:00'},
                {'CURRENCY': 'RUB', 'ID': 2, 'DT': '2018-08-01 00:00:00'},
            ],
            None,
            helpers.contracts.ContractNotFoundError,
        ),
        (
            [
                {'CURRENCY': 'RUR', 'ID': 1, 'DT': '2018-08-01 00:00:00'},
                {'CURRENCY': 'USD', 'ID': 2, 'DT': '2020-01-01 00:00:00'},
            ],
            'USD',
            None,
        ),
    ],
)
@pytest.mark.nofilldb
async def test_fetch_contract_currency(
        contracts,
        expected_currency,
        exception,
        mock_billing_replication,
        stq3_context,
):
    @mock_billing_replication('/v1/active-contracts/')
    def _get_active_contracts(request):
        del request  # unused
        return web.json_response(contracts)

    as_of = datetime.datetime.now(tz=datetime.timezone.utc)
    billing_client_id = '1'
    service_id = '137'
    if exception:
        with pytest.raises(exception):
            await helpers.contracts.fetch_active_contract(
                stq3_context, billing_client_id, as_of, service_id,
            )
    else:
        active_contract = await helpers.contracts.fetch_active_contract(
            stq3_context, billing_client_id, as_of, service_id,
        )
        actual_currency = helpers.contracts.get_contract_currency(
            active_contract,
        )
        assert expected_currency == actual_currency
