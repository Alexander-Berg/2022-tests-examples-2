import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


@pytest.mark.config(
    AGENT_GAP_DISABLE_ACCESS_CHATTERBOX_REASON={
        'enable': True,
        'exclude_logins': ['webalex'],
        'workflow': ['vacation', 'illness', 'maternity'],
    },
)
async def test_import_absent_users(
        cron_context: context.Context, mock_staff_gap_api,
):
    await run_cron.main(['agent.crontasks.import_absent_users', '-t', '0'])

    query = 'SELECT * FROM agent.absent_users'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert len(rows) == 1
        assert dict(rows[0]) == {'login': 'absent_login'}
