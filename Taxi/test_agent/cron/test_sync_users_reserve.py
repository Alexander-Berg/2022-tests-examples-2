from agent.generated.cron import run_cron


async def test_import_leave_balance(
        cron_context, mock_piecework_reserve_users,
):

    await run_cron.main(['agent.crontasks.sync_piecework_reserve', '-t', '0'])

    query = 'SELECT login,value FROM agent.piecework_reserve'
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = {
            row['login']: row['value'] for row in await conn.fetch(query)
        }

        assert result == {
            'webalex': 1000,
            'mikh-vasily': 2000,
            'akozhevina': 3000,
        }
