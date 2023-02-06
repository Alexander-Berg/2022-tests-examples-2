import datetime

import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron
from agent.internal import taxi_delivery

NOW = datetime.datetime(2021, 12, 1)

EXPECTED_DATA = [
    {
        'date': datetime.date(2021, 12, 1),
        'cnt_corp_contract_id': 6,
        'cnt_corp_contract_id_this_month': 1,
        'sum_deliveries_sccs': 1440,
        'active_days_percent': 0.34,
        'avg_quality_rate': 4.0,
        'avg_tov_rate': 4.4,
        'avg_hygiene_rate': 3,
        'avg_algorithm_rate': 9,
        'sum_calls_sccs_60': 29,
        'overall_done_tasks': 55,
        'login': 'justmark0',
    },
    {
        'date': datetime.date(2021, 12, 1),
        'cnt_corp_contract_id': 1,
        'cnt_corp_contract_id_this_month': 0,
        'sum_deliveries_sccs': 257,
        'active_days_percent': 0.03,
        'avg_quality_rate': 3.0,
        'avg_tov_rate': 4.38,
        'avg_hygiene_rate': 4.38,
        'avg_algorithm_rate': 4.5,
        'sum_calls_sccs_60': 15,
        'overall_done_tasks': 9,
        'login': 'random',
    },
]

CBM_DATA = [
    {
        'login': 'justmark0',
        'cnt_corp_contract_id': 1,
        'sum_deliveries_sccs': 1002,
        'active_days': 2,
        'start_dt': '2021-11-20',
        'month': '2021-11',
    },
    {
        'login': 'justmark0',
        'cnt_corp_contract_id': 2,
        'sum_deliveries_sccs': 269,
        'active_days': 3,
        'start_dt': '2021-12-01',
        'month': '2021-12',
    },
    {
        'login': 'justmark0',
        'cnt_corp_contract_id': 3,
        'sum_deliveries_sccs': 169,
        'active_days': 5,
        'start_dt': '2021-11-20',
        'month': '2021-11',
    },
    {
        'login': 'random',
        'cnt_corp_contract_id': 1,
        'sum_deliveries_sccs': 257,
        'active_days': 1,
        'start_dt': '2021-09-24',
        'month': '2021-11',
    },
]

QUALITY_CONTROL_DATA = [
    {
        'login': 'justmark0',
        'avg_quality_rate': 4.0,
        'avg_tov_rate': 4.4,
        'avg_hygiene_rate': 3,
        'avg_algorithm_rate': 9,
    },
    {
        'login': 'random',
        'avg_quality_rate': 3.0,
        'avg_tov_rate': 4.375,
        'avg_hygiene_rate': 4.375,
        'avg_algorithm_rate': 4.5,
    },
]

TASKS_DATA = [
    {'login': 'justmark0', 'overall_done_tasks': 55},
    {'login': 'random', 'overall_done_tasks': 9},
]

CALLS_DATA = [
    {'login': 'justmark0', 'sum_calls_sccs_60': 29},
    {'login': 'random', 'sum_calls_sccs_60': 15},
    {'login': None, 'sum_calls_sccs_60': 65},
]


@pytest.mark.now('2021-12-07T00:00:01')
async def test_fetch_data_taxi_delivery_from_yt(
        patch, cron_context: context.Context, yt_apply,
):
    @patch('agent.internal.taxi_delivery.get_table_data')
    def _(*args, **kwargs):
        if args[1] == taxi_delivery.CONTRACTS_BY_MANAGER_QUERY_NAME:
            return CBM_DATA
        if args[1] == taxi_delivery.QUALITY_CONTROL_QUERY_NAME:
            return QUALITY_CONTROL_DATA
        if args[1] == taxi_delivery.TASKS_QUERY_NAME:
            return TASKS_DATA
        if args[1] == taxi_delivery.CALLS_QUERY_NAME:
            return CALLS_DATA
        return None

    await run_cron.main(['agent.crontasks.import_taxi_delivery', '-t', '0'])

    query = 'SELECT * FROM agent.taxi_delivery'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert len(rows) == len(EXPECTED_DATA)
        for i, row in enumerate(EXPECTED_DATA):
            assert dict(rows[i]) == row
