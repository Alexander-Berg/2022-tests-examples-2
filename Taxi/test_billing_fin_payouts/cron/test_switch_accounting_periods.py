# pylint: disable=redefined-outer-name
import json

import pytest

from billing_fin_payouts.generated.cron import cron_context
from billing_fin_payouts.generated.cron import run_cron
from . import configs


def _cmp_data(actual, expected):
    keys_actual = actual[0].keys() if actual else []
    keys_expected = expected[0].keys() if expected else []
    keys = keys_actual if keys_actual else keys_expected

    def _key(doc):
        return tuple(doc[key] for key in keys)

    def _sorted(docs):
        return sorted(docs, key=_key)

    assert _sorted(actual) == _sorted(expected)


async def _read_data_from_pg(pool, query):
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)

    data = [dict(row) for row in rows]
    data_created = json.loads(
        json.dumps(data, ensure_ascii=False, default=str),
    )
    for doc in data_created:
        if 'payload' in doc:
            doc['payload'] = json.loads(doc['payload'])

    return data_created


async def _check_expected_results(pool, query, data_expected):
    data_created = await _read_data_from_pg(pool=pool, query=query)
    # print('**** data_created')
    # print(data_created)
    # print('**** data_expected')
    # print(data_expected)
    _cmp_data(data_created, data_expected)


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
@pytest.mark.now('2021-11-18T00:00:00.000000+00:00')
@pytest.mark.parametrize(
    'cron_name, interface_table, yt_table_data,'
    'data_expected, accounting_periods,'
    'accounting_periods_expected, yt_tables_list',
    [
        (
            'billing_fin_payouts.crontasks.read_fresh_revenues',
            'interface.revenues',
            'revenues_static_data_yt.json',
            'revenues_static_data_expected.json',
            'accounting_periods.json',
            'accounting_periods_expected.json',
            ['2021-11-18'],
        ),
    ],
    ids=['read-fresh-revenues_01'],
)
async def test_read(
        mockserver,
        load_json,
        cron_name,
        interface_table,
        yt_table_data,
        data_expected,
        accounting_periods,
        accounting_periods_expected,
        yt_tables_list,
        patch,
):

    context = cron_context.Context()

    yt_table_data = load_json(yt_table_data)
    data_expected = load_json(data_expected)
    accounting_periods = load_json(accounting_periods)
    accounting_periods_expected = load_json(accounting_periods_expected)

    billing_replication_resp = load_json('billing_replication_response.json')
    balance_replica_response = load_json('balance_replica_response.json')

    # insert data to accounting_periods
    query = f"""
            INSERT INTO interface.accounting_periods
            SELECT *
                FROM json_populate_recordset (
                NULL::interface.accounting_periods,
                '{json.dumps(accounting_periods)}'
                )
            """
    pool = await context.pg.master_pool
    async with pool.acquire() as conn:
        await conn.execute(query)

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

    # check payout_batches
    pool = await context.pg.master_pool
    await _check_expected_results(
        pool=pool,
        data_expected=data_expected,
        query="""
                select id,
                    status_code,
                    accounting_date,
                    accounting_period,
                    client_id,
                    contract_id,
                    currency,
                    amount_tlog,
                    amount,
                    table_name,
                    row_index,
                    payload,
                    external_ref
                  from interface.revenues
            """,
    )

    # interface.accounting_periods
    pool = await context.pg.master_pool
    await _check_expected_results(
        pool=pool,
        data_expected=accounting_periods_expected,
        query="""
                select  id,
                        period_type,
                        period_name,
                        period_status,
                        date_start::text as date_start,
                        date_end::text as date_end,
                        period_year,
                        period_num
                  from interface.accounting_periods
            """,
    )
