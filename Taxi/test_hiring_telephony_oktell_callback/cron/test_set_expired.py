import pytest

QUERY = """SELECT "task_id", "task_state", "is_expired"
FROM "hiring_telephony_oktell_callback"."tasks"
ORDER BY "task_id"
"""


@pytest.mark.now('3000-01-01T12:00:00+0000')
async def test_set_expired_(load_json, cron_context, cron_runner):
    expected_tasks = load_json('expected_result.json')['tasks']

    await cron_runner.set_expired()
    async with cron_context.pg.fast_pool.acquire() as conn:
        tasks = await conn.fetch(QUERY)
        assert [dict(task) for task in tasks] == expected_tasks
