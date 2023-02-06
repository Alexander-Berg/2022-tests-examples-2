# pylint: disable=redefined-outer-name
import json

import pytest

from billing_fin_payouts.generated.cron import cron_context
from billing_fin_payouts.generated.cron import run_cron


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


async def _upload_data_to_pg(pool, interface_list: list):
    for item in interface_list:
        for table, data in item.items():
            query = f"""
                    INSERT INTO {table}
                    SELECT *
                        FROM json_populate_recordset (
                        NULL::{table},
                        '{json.dumps(data)}'
                        )
                    """
            async with pool.acquire() as conn:
                await conn.execute(query)


async def _check_expected_results(pool, query, data_expected):
    data_created = await _read_data_from_pg(pool=pool, query=query)
    # print('**** data_created')
    # print(data_created)
    # print('**** data_expected')
    # print(data_expected)
    _cmp_data(data_created, data_expected)


async def _patches(yt_periods, patch):
    # pylint: disable=unused-variable
    # pylint: disable=redefined-builtin
    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'read_table',
    )
    async def read_table(table_path):
        return yt_periods

    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'row_count',
    )
    async def row_count(*args, **kwargs):
        return len(yt_periods)

    @patch(
        'billing_fin_payouts.generated.cron.yt_wrapper.plugin.AsyncYTClient.'
        'exists',
    )
    async def exists(node_path):
        return True


@pytest.mark.config(BILLING_FIN_PAYOUTS_READ_PERIOD_ENABLED=True)
@pytest.mark.parametrize(
    'interface_table, yt_periods, db_periods, expected_periods',
    [
        (
            'interface.accounting_periods',
            'accounting_periods_yt.json',
            'accounting_periods_db.json',
            'accounting_periods_expected.json',
        ),
    ],
    ids=['read_periods_01'],
)
async def test_read_accounting_periods(
        load_json,
        interface_table,
        yt_periods,
        db_periods,
        expected_periods,
        patch,
):
    context = cron_context.Context()
    await context.on_startup()
    pool = context.pg.master_pool

    yt_periods = load_json(yt_periods)
    db_periods = load_json(db_periods)
    data_expected = load_json(expected_periods)

    await _upload_data_to_pg(
        pool=pool, interface_list=[{interface_table: db_periods}],
    )

    await _patches(yt_periods=yt_periods, patch=patch)

    cron_name = 'billing_fin_payouts.crontasks.read_accounting_periods'
    await run_cron.main([cron_name, '-t', '0'])

    await _check_expected_results(
        pool=pool,
        query=f"""
                select period_type,
                    period_name,
                    period_status
                from {interface_table}
               """,
        data_expected=data_expected,
    )

    await context.on_shutdown()
