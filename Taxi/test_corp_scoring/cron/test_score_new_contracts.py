# pylint: disable=redefined-outer-name
import datetime

import pytest

from corp_scoring.generated.cron import run_cron


async def _get_last_sync_time(context):
    key = 'contracts'

    async with context.pg.master_pool.acquire(log_extra=None) as conn:
        query = context.postgres_queries['local_pg/get_last_sync_time.sqlt']
        last_sync = await conn.fetchval(query, key)

    return last_sync


async def _update_last_sync_time(
        context, collection_name: str, last_sync_time: datetime.datetime,
):
    async with context.pg.master_pool.acquire(log_extra=None) as conn:
        query = context.postgres_queries['local_pg/update_last_sync_time.sqlt']
        await conn.execute(query, last_sync_time, collection_name)


async def _fill_tins_table(context, lines):
    async with context.pg.master_pool.acquire(log_extra=None) as conn:
        await conn.copy_records_to_table(
            table_name='tins_to_thresholds',
            schema_name='corp_scoring',
            records=lines,
            columns=['tin', 'threshold_val'],
        )


@pytest.fixture
def get_person_mock(patch, load_json):
    @patch('taxi.clients.billing_v2.BalanceClient.get_person')
    async def _get_person(person_id):
        return [{'INN': 'inn-' + person_id}]


@pytest.mark.parametrize(
    ['start_time', 'end_time'],
    [
        pytest.param(
            datetime.datetime(2020, 11, 1, 16, 0, 0),
            datetime.datetime(2020, 11, 1, 19, 0, 0),
        ),
    ],
)
async def test_score_new_clients(
        cron_context,
        mock_corp_clients,
        mock_exp3_get_values,
        get_person_mock,
        start_time,
        end_time,
        load_json,
):
    await _update_last_sync_time(cron_context, 'contracts', start_time)
    await _fill_tins_table(
        cron_context,
        [
            ['inn-10001', -1111.12],
            ['inn-10002', -2222.12],
            ['inn-10003', -3333.12],
            ['inn-10004', -4444.12],
            ['inn-10005', -5555.12],
        ],
    )

    await run_cron.main(
        ['corp_scoring.crontasks.score_new_contracts', '-t', '0'],
    )

    last_sync_time = await _get_last_sync_time(cron_context)

    assert last_sync_time == end_time

    call = mock_corp_clients.update_thresholds.next_call()['request'].json
    assert (
        call['contract_id'] == 2
        and call['prepaid_deactivate_threshold_type'] == 'welcome_overdraft'
    )

    call = mock_corp_clients.update_thresholds.next_call()['request'].json
    assert (
        call['contract_id'] == 3
        and call['prepaid_deactivate_threshold_type'] == 'score_by_manager'
    )

    call = mock_corp_clients.update_thresholds.next_call()['request'].json
    assert (
        call['contract_id'] == 4
        and call['prepaid_deactivate_threshold_type'] == 'welcome_overdraft'
    )

    await run_cron.main(
        ['corp_scoring.crontasks.score_new_contracts', '-t', '0'],
    )

    assert mock_corp_clients.update_thresholds.times_called == 0
