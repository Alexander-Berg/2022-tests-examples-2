# pylint: disable=redefined-outer-name
import pytest


from agent.generated.cron import run_cron


@pytest.mark.config(AGENT_SYNC_STAFF_DEPS_ROW_LIMIT=1)
async def test_import_deps(cron_context, mock_staff_groups_api, taxi_config):

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.departments'
        deps = await conn.fetch(query)
        assert len(deps) == 3
        keys = [dep['key'] for dep in deps]
        keys.sort()
        expected_sorted = [
            'yandex',
            'taxi_dep72956_dep20857',
            'taxi_dep11496_dep38268_dep08025',
        ]
        expected_sorted.sort()
        assert keys == expected_sorted
    await run_cron.main(['agent.crontasks.import_staff_deps', '-t', '0'])

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.departments'
        insert_deps_results = await conn.fetch(query)
        assert len(insert_deps_results) == 2
        keys = [dep['key'] for dep in insert_deps_results]
        assert keys.sort() == ['taxi_dep72956_dep20857', 'ext'].sort()


@pytest.mark.config(AGENT_SYNC_STAFF_DEPS_ROW_LIMIT=1)
async def test_import_deps_heads(
        cron_context, mock_staff_groups_api, taxi_config,
):

    async with cron_context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.departments_heads'
        res = await conn.fetch(query)

        assert len(res) == 3
        for row in res:
            if row['key'] == 'taxi_dep72956_dep20857':
                assert row['login'] == 'login1'
            if row['key'] == 'taxi_dep11496_dep38268_dep08025':
                assert row['login'] == 'login2'
            if row['key'] == 'yandex':
                assert row['login'] == 'mikh-vasily'

    await run_cron.main(['agent.crontasks.import_staff_deps', '-t', '0'])

    async with cron_context.pg.slave_pool.acquire() as conn:

        query = 'SELECT * FROM agent.departments_heads'
        res = await conn.fetch(query)
        assert len(res) == 1
        assert res[0]['login'] == 'webalex'
