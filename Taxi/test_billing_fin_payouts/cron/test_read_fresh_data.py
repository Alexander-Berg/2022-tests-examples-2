# pylint: disable=redefined-outer-name
import json

import pytest

from billing_fin_payouts.generated.cron import cron_context
from billing_fin_payouts.generated.cron import run_cron
from . import configs


def _cmp_data(actual, expected, key_fields=None):
    if key_fields is None:
        key_fields = ['id', 'client_id', 'contract_id']

    def _key(doc):
        return tuple(doc[key] for key in key_fields)

    def _sorted(docs):
        return sorted(docs, key=_key)

    assert _sorted(actual) == _sorted(expected)


async def _read_data_from_pg(table, columns):
    # pylint: disable=unused-variable
    context = cron_context.Context()
    await context.on_startup()

    query = f"""
    select {','.join(columns)}
      from {table}
     where 1=1
    """

    pool = context.pg.master_pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    await context.on_shutdown()

    data = [dict(row) for row in rows]

    data_created = json.loads(
        json.dumps(data, ensure_ascii=False, default=str),
    )

    for doc in data_created:
        if 'payload' in doc:
            doc['payload'] = json.loads(doc['payload'])

    return data_created


async def _check_expected_results(interface_table, data_expected):

    columns = [
        'id',
        'status_code',
        'accounting_date',
        'client_id',
        'contract_id',
        'currency',
        'amount_tlog',
        'amount',
        'table_name',
        'row_index',
        'payload',
        'dry_run',
        'external_ref',
    ]

    data_created = await _read_data_from_pg(
        table=interface_table, columns=columns,
    )
    _cmp_data(data_created, data_expected, key_fields=columns)


async def _check_table_info(interface_table, yt_table_data):
    context = cron_context.Context()
    await context.on_startup()
    prefix = 'interface.'
    branch_type = interface_table[len(prefix) :]
    query = f"""
        select max_row_index
        from interface.info
        where branch_type = '{branch_type}'
    """

    pool = context.pg.master_pool
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    await context.on_shutdown()

    assert len(rows) == 1
    assert rows[0]['max_row_index'] == len(yt_table_data) - 1


async def _check_expected_parsing_errors_results(data_expected):
    columns = [
        'id',
        'branch_type',
        'table_name',
        'row_index',
        'status_code',
        'status_msg',
        'payload',
    ]

    data_created = await _read_data_from_pg(
        table='interface.parsing_errors', columns=columns,
    )

    _cmp_data(data_created, data_expected, key_fields=columns)


async def _patches(yt_table_data, yt_tables_list, patch):
    # pylint: disable=unused-variable
    # pylint: disable=redefined-builtin
    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'read_table',
    )
    async def read_table(table_path, control_attributes: dict, format: {}):
        start = table_path.ranges[0]['lower_limit']['row_index']
        end = table_path.ranges[0]['upper_limit']['row_index']
        return yt_table_data[start:end]

    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'row_count',
    )
    async def row_count(*args, **kwargs):
        return len(yt_table_data)

    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'list',
    )
    async def yt_list(*args, **kwargs):
        if yt_tables_list is not None:
            return yt_tables_list
        return ['2021-11-18', '2021-11-19']

    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'exists',
    )
    async def exists(node_path):
        return True


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
@pytest.mark.now('2021-11-18T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'cron_name, interface_table, yt_table_data, billing_replication_response, '
    'balance_replica_response_json, data_expected, yt_tables_list',
    [
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected.json',
            ['2021-11-18'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_payments',
            'interface.payments',
            'payments_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'payments_static_data_expected.json',
            ['2021-11-18'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_revenues',
            'interface.revenues',
            'revenues_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'revenues_static_data_expected.json',
            ['2021-11-18'],
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_no_enrich.json',
            ['2021-11-18'],
            marks=pytest.mark.config(
                BILLING_FIN_PAYOUTS_ENRICH_DATA_ENABLED=False,
            ),
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_filter_client_by_mod.json',
            ['2021-11-18'],
            marks=pytest.mark.config(
                BILLING_FIN_PAYOUTS_READ_FRESH_DATA_SETTINGS={
                    'bulk_fresh_insert_chunk_size': 10000,
                    'tlog_path': 'export/tlog/',
                    'yt_clusters': ['hahn', 'arnold'],
                    'billing_client_ids': {'mod': 10, 'suffixes': [0, 5]},
                },
            ),
        ),
        pytest.param(
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_filter_client_by_id.json',
            ['2021-11-18'],
            marks=pytest.mark.config(
                BILLING_FIN_PAYOUTS_READ_FRESH_DATA_SETTINGS={
                    'bulk_fresh_insert_chunk_size': 10000,
                    'tlog_path': 'export/tlog/',
                    'yt_clusters': ['hahn', 'arnold'],
                    'billing_client_ids': {'suffixes': [25147782, 69896727]},
                },
            ),
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_migrate_client.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_migrate_client.json',
            ['2021-11-18'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_demigrate_client.json',
            'billing_replication_response.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_demigrate_client.json',
            ['2021-11-19'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_migrate_client.json',
            'billing_replication_response_firm_id_12.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_migrate_firm.json',
            ['2021-11-18'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_demigrate_client.json',
            'billing_replication_response_firm_id_12.json',
            'balance_replica_response.json',
            'expenses_static_data_expected_demigrate_firm.json',
            ['2021-11-19'],
        ),
    ],
    ids=[
        'read-fresh-expenses_01',
        'read-fresh-payments_01',
        'read-fresh-revenues_01',
        'read-fresh-expenses_no_enrich',
        'read-fresh-expenses_filter_client_by_mod',
        'read-fresh-expenses_filter_client_by_id',
        'read-fresh-expenses_migrate_client',
        'read-fresh-expenses_demigrate_client',
        'read-fresh-expenses_migrate_firm',
        'read-fresh-expenses_demigrate_firm',
    ],
)
@pytest.mark.pgsql(
    dbname='billing_fin_payouts', files=('fill_migrations.psql',),
)
async def test_read(
        mockserver,
        load_json,
        cron_name,
        interface_table,
        yt_table_data,
        billing_replication_response,
        balance_replica_response_json,
        data_expected,
        yt_tables_list,
        patch,
):

    yt_table_data = load_json(yt_table_data)
    data_expected = load_json(data_expected)

    billing_replication_resp = load_json(billing_replication_response)
    balance_replica_response = load_json(balance_replica_response_json)

    await _patches(
        yt_table_data=yt_table_data,
        yt_tables_list=yt_tables_list,
        patch=patch,
    )

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

    await run_cron.main([cron_name, '-t', '0'])

    await _check_expected_parsing_errors_results({})

    await _check_expected_results(
        interface_table=interface_table, data_expected=data_expected,
    )

    await _check_table_info(interface_table, yt_table_data)


@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_EXPENSES_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_FRESH_DATA_ENABLED=True)
@pytest.mark.config(BILLING_FIN_PAYOUTS_ENRICH_DATA_ENABLED=True)
@pytest.mark.now('2021-11-18T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'cron_name, interface_table, yt_table_data, parsing_errors_data_expected,'
    'billing_replication_resp_json, yt_tables_list',
    [
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_test_br_errors.json',
            'expenses_parsing_errors_br_404_expected.json',
            'billing_replication_response_404.json',
            ['2021-11-18'],
        ),
        (
            'billing_fin_payouts.crontasks.read_fresh_expenses',
            'interface.expenses',
            'expenses_static_data_yt_test_br_errors.json',
            'expenses_parsing_errors_br_429_expected.json',
            'billing_replication_response_429.json',
            ['2021-11-18'],
        ),
    ],
    ids=[
        'read-fresh-expenses_contract_not_found',
        'read-fresh-expenses_br_429_retry',
    ],
)
async def test_parsing_errors(
        mockserver,
        load_json,
        cron_name,
        interface_table,
        yt_table_data,
        parsing_errors_data_expected,
        billing_replication_resp_json,
        yt_tables_list,
        patch,
):

    yt_table_data = load_json(yt_table_data)
    data_expected = load_json(parsing_errors_data_expected)
    billing_replication_resp = load_json(billing_replication_resp_json)

    await _patches(
        yt_table_data=yt_table_data,
        yt_tables_list=yt_tables_list,
        patch=patch,
    )

    @mockserver.json_handler('/billing-replication/v2/contract/by_id/')
    async def _contract_by_id(request):
        resp = billing_replication_resp['/v2/contract/by_id/'][0]
        return mockserver.make_response(**resp)

    await run_cron.main([cron_name, '-t', '0'])

    await _check_expected_parsing_errors_results(data_expected)

    await _check_table_info(interface_table, yt_table_data)
