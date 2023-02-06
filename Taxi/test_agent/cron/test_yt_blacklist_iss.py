import pytest

from agent.generated.cron import run_cron


@pytest.mark.config(
    AGENT_MOE_COURSES=[
        {
            'deadline': '2022-01-01',
            'enable': True,
            'id': 1,
            'required': True,
            'success_score': 80,
            'departments': ['yandex_taxi'],
            'join_timeout_days': 14,
        },
    ],
)
async def test_blacklist_init(cron_context, taxi_config, yt_apply, yt_client):
    await run_cron.main(['agent.crontasks.yt_blacklist_iss', '-t', '0'])

    path = '//home/taxi-fraud/export/production/agent/blacklist_unittests'

    rows = list(yt_client.select_rows(f'* FROM [{path}]'))

    assert rows == [
        {
            'created_at': rows[0]['created_at'],
            'login': 'liambaev',
            'reason': ['Did not complete the course moe 1'],
        },
        {
            'created_at': rows[1]['created_at'],
            'login': 'orangevl',
            'reason': ['Did not complete the course moe 1'],
        },
    ]

    rows = list(
        yt_client.read_table(
            '//home/taxi-fraud/export/production/agent/history_unittests',
        ),
    )

    assert rows == [
        {
            'created_at': rows[0]['created_at'],
            'login': 'liambaev',
            'reason': ['Did not complete the course moe 1'],
            'action': 'add',
        },
        {
            'created_at': rows[1]['created_at'],
            'login': 'orangevl',
            'reason': ['Did not complete the course moe 1'],
            'action': 'add',
        },
    ]


@pytest.mark.config(
    AGENT_MOE_COURSES=[
        {
            'deadline': '2022-01-01',
            'enable': True,
            'id': 1,
            'required': True,
            'success_score': 80,
            'departments': ['yandex_taxi'],
            'join_timeout_days': 14,
        },
    ],
)
@pytest.mark.yt(
    dyn_table_data=['yt_data_first_blacklist.yaml'],
    static_table_data=['yt_data_first_history.yaml'],
    schemas=['yt_schema_first_blacklist.yaml', 'yt_schema_first_history.yaml'],
)
async def test_passed_one_people(
        cron_context, taxi_config, yt_apply, yt_client,
):
    query = """INSERT INTO agent.courses_results VALUES
     (1,\'orangevl\',NOW(),NOW(),\'moe\',100)"""
    async with cron_context.pg.master_pool.acquire() as conn:
        await conn.execute(query)

    await run_cron.main(['agent.crontasks.yt_blacklist_iss', '-t', '0'])
    path = '//home/taxi-fraud/export/production/agent/blacklist_unittests'
    rows = list(yt_client.select_rows(f'* FROM [{path}]'))

    assert rows == [
        {
            'created_at': rows[0]['created_at'],
            'login': 'liambaev',
            'reason': ['Did not complete the course moe 1'],
        },
    ]

    rows = list(
        yt_client.read_table(
            '//home/taxi-fraud/export/production/agent/history_unittests',
        ),
    )

    assert rows == [
        {
            'created_at': rows[0]['created_at'],
            'login': 'liambaev',
            'reason': ['Did not complete the course moe 1'],
            'action': 'add',
        },
        {
            'created_at': rows[1]['created_at'],
            'login': 'orangevl',
            'reason': ['Did not complete the course moe 1'],
            'action': 'add',
        },
        {
            'created_at': rows[2]['created_at'],
            'login': 'orangevl',
            'reason': ['Did not complete the course moe 1'],
            'action': 'delete',
        },
    ]
