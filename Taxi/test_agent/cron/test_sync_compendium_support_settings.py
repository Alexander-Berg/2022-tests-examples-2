from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


EXPECTED_ANSWER = [
    {
        'assigned_lines': ['line_1'],
        'can_choose_except_assigned_lines': False,
        'can_choose_from_assigned_lines': False,
        'languages': ['ru'],
        'login': 'login_not_for_sync',
        'max_chats': 12,
        'needs_compendium_sync': False,
        'work_off_shift': True,
    },
    {
        'assigned_lines': [],
        'can_choose_except_assigned_lines': True,
        'can_choose_from_assigned_lines': True,
        'languages': None,
        'login': 'login_for_sync',
        'max_chats': 3,
        'needs_compendium_sync': True,
        'work_off_shift': False,
    },
    {
        'assigned_lines': [],
        'can_choose_except_assigned_lines': True,
        'can_choose_from_assigned_lines': True,
        'languages': ['ru', 'en'],
        'login': 'regular_login',
        'max_chats': 3,
        'needs_compendium_sync': True,
        'work_off_shift': True,
    },
]


async def test_sync_compendium_support_settings(cron_context: context.Context):
    await run_cron.main(
        ['agent.crontasks.sync_compendium_support_settings', '-t', '0'],
    )

    query = 'SELECT * FROM agent.chatterbox_support_settings'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert [dict(row) for row in rows] == EXPECTED_ANSWER
