import pytest

from billing_fin_payouts.stq import process_tlog_transactions
from test_billing_fin_payouts import common_utils
from . import configs


@pytest.mark.now('2022-05-30T00:00:00.000000+00:00')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_STQ_PROCESS_TLOG_TRANSACTIONS_ENABLED=True,
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_PAYMENT_PROCESSOR_YA_BANK_CLIENTS=(
        configs.BILLING_FIN_PAYOUTS_PAYMENT_PROCESSOR_YA_BANK_CLIENTS,
    ),
)
@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_EXPENSES_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_PAYMENTS_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_REVENUES_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_DATA_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_ENRICH_DATA_ENABLED=True)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_SKIP_NETTING_SERVICES=(
        configs.BILLING_FIN_PAYOUTS_SKIP_NETTING_SERVICES
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_PRODUCT_WITH_VAT=(
        configs.BILLING_FIN_PAYOUTS_PRODUCT_WITH_VAT
    ),
)
@pytest.mark.config(
    BILLING_ORDERS_DISABLE_CONTRACT_CHECK=(
        configs.BILLING_ORDERS_DISABLE_CONTRACT_CHECK
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_VAT_RATE=configs.BILLING_FIN_PAYOUTS_VAT_RATE,
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_NETTING_SETTINGS=(
        configs.BILLING_FIN_PAYOUTS_NETTING_SETTINGS
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_AGENT_REWARD_SETTINGS=(
        configs.BILLING_FIN_PAYOUTS_AGENT_REWARD_SETTINGS
    ),
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_EXPENSE_IN_REVENUE_PRODUCTS={
        'enabled': True,
        'products': ['coupon', 'coupon_plus', 'subvention'],
    },
)
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_ACCRUALS_PAYSYSTYPE_MAPPING={
        'by_product': {'trip_compensation': 'yandex'},
        'by_agent_id': {'agent_psb': 'psb_logist', 'agent_altocar': 'altocar'},
    },
)
@pytest.mark.config(BILLING_FIN_PAYOUTS_SCHEDULE_PAYOUTS_FROM_STQ_ENABLED=True)
@pytest.mark.parametrize(
    'table_name, input_data, expected_data',
    [
        (
            'interface.revenues',
            'revenues_static_data_stq.json',
            'revenues_static_data_expected.json',
        ),
    ],
)
async def test_process_tlog_transactions(
        mockserver,
        stq3_context,
        stq,
        process_tlog_transactions_info,
        load_json,
        table_name,
        input_data,
        expected_data,
):
    entries = load_json(input_data)

    mock_responses(mockserver, load_json)

    await process_tlog_transactions.task(
        stq3_context, process_tlog_transactions_info, entries,
    )
    query = f"""
        SELECT
        id,
        status_code,
        status_msg,
        transaction_id,
        accounting_date,
        client_id,
        contract_id,
        currency,
        amount_tlog,
        amount,
        table_name,
        row_index,
        payload,
        dry_run,
        external_ref,
        payment_processor
        FROM {table_name}
    """
    pool = await stq3_context.pg.master_pool
    expected_data = load_json(expected_data)
    await common_utils.check_pg_expected_results(pool, query, expected_data)


def mock_responses(mockserver, load_json):
    balance_replica_response = load_json('balance_replica_response.json')
    billing_replication_resp = load_json('billing_replication_response.json')

    @mockserver.json_handler('/billing-replication/v2/contract/by_id/')
    async def _contract_by_id(request):
        resp = billing_replication_resp['/v2/contract/by_id/'][0]
        resp['json']['ID'] = request.json['ID']
        return mockserver.make_response(**resp)

    @mockserver.json_handler(
        '/balance-replica/v1/personal_accounts/by_contract_id',
    )
    async def _personal_accounts_by_contract_id(request):
        resp = balance_replica_response[
            '/v1/personal_accounts/by_contract_id/'
        ][0]
        return mockserver.make_response(**resp)
