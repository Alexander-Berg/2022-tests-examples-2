import pytest

QUERY = """SELECT "task_id", "task_state"
FROM "hiring_telephony_oktell_callback"."tasks"
ORDER BY "task_id"
"""


@pytest.mark.now('2021-10-10T12:00:00+0000')
async def test_acquire_ttl(load_json, cron_runner, pgsql, cron_context):
    expected = load_json('expected_results.json')['tasks']

    await cron_runner.acquire_ttl()

    cursor = pgsql['hiring_telephony_oktell_callback'].cursor()
    cursor.execute(QUERY)
    result = list(list(row) for row in cursor)
    assert result == expected
