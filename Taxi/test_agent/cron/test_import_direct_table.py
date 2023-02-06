import datetime

import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


NOW = datetime.datetime(2021, 11, 5)

EXPECTED_DATA = {
    'login': 'unholy',
    'dt': datetime.date(2021, 11, 1),
    'wfm_perc': 1.123,
    'skip_perc': 2.234,
    'goal_1': 3.345,
    'avg_dur_fcalls': 4.456,
    'avg_dur_no_fcalls': 5.567,
    'goal_2': 6.678,
    'pos_oscore': 7.789,
    'iscore': 8.890,
    'upsale_exec': 9.901,
}


@pytest.mark.now(NOW.isoformat())
@pytest.mark.yt(
    static_table_data=['yt_data_direct.yaml'],
    schemas=['yt_schema_direct.yaml'],
)
async def test_fetch_data_direct_from_yt(
        cron_context: context.Context, yt_apply,
):
    await run_cron.main(['agent.crontasks.import_direct_table', '-t', '0'])

    query = 'SELECT * FROM agent.direct'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert len(rows) == 1
        assert dict(rows[0]) == EXPECTED_DATA
