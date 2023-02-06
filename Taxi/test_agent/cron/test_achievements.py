import pytest

from agent.generated.cron import run_cron


@pytest.mark.now('2022-06-01T12:00:00+0000')
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'achievements_collection': 'collection_1',
        },
        'ms': {
            'enable_chatterbox': False,
            'main_permission': 'user_ms',
            'achievements_collection': 'collection_2',
        },
    },
    AGENT_ACHIEVEMENTS_LOGICS={
        'experience_1month': {'type': 'joined', 'rules': {'months': -1}},
        'experience_1year': {'type': 'joined', 'rules': {'years': -1}},
    },
)
async def test_achievements(cron_context):
    await run_cron.main(['agent.crontasks.achievements', '-t', '0'])

    query = 'SELECT * FROM agent.users_achievements'
    async with cron_context.pg.slave_pool.acquire() as conn:
        res = [
            {'key': ach['key'], 'login': ach['login']}
            for ach in await conn.fetch(query)
        ]
        expected = [
            {'login': 'mikh-vasily', 'key': 'experience_1month'},
            {'login': 'webalex', 'key': 'experience_1month'},
            {'login': 'akozhevina', 'key': 'experience_1month'},
            {'login': 'akozhevina', 'key': 'experience_1year'},
            {'login': 'korol', 'key': 'experience_1month'},
            {'login': 'korol', 'key': 'experience_1year'},
            {'login': 'meetka', 'key': 'experience_1month'},
            {'login': 'meetka', 'key': 'experience_1year'},
        ]

        res_sort = sorted(res, key=lambda d: d['login'])
        expected_sort = sorted(expected, key=lambda d: d['login'])
        assert res_sort == expected_sort

    await run_cron.main(['agent.crontasks.achievements', '-t', '0'])

    async with cron_context.pg.slave_pool.acquire() as conn:
        res_second = [
            {'key': ach['key'], 'login': ach['login']}
            for ach in await conn.fetch(query)
        ]
        res_sort = sorted(res_second, key=lambda d: d['login'])
        expected_sort = sorted(expected, key=lambda d: d['login'])
        assert res_sort == expected_sort

    query = 'SELECT * FROM agent.lootboxes'
    async with cron_context.pg.slave_pool.acquire() as conn:
        res_lootbox = [
            {'login': ach['login'], 'coins': ach['coins'], 'skin': ach['skin']}
            for ach in await conn.fetch(query)
        ]
        expected_lootbox = [
            {'login': 'mikh-vasily', 'coins': 10, 'skin': 'common_card'},
            {'login': 'webalex', 'coins': 10, 'skin': 'common_card'},
            {'login': 'akozhevina', 'coins': 10, 'skin': 'common_card'},
            {'login': 'korol', 'coins': 0, 'skin': 'legendary_card'},
            {'login': 'meetka', 'coins': 0, 'skin': 'legendary_card'},
            {'login': 'akozhevina', 'coins': 20, 'skin': 'rare_card'},
            {'login': 'korol', 'coins': 50, 'skin': 'immortal_card'},
            {'login': 'meetka', 'coins': 50, 'skin': 'immortal_card'},
        ]

        res_lootbox_sort = sorted(res_lootbox, key=lambda d: d['login'])
        expected_lootbox_sort = sorted(
            expected_lootbox, key=lambda d: d['login'],
        )
        assert res_lootbox_sort == expected_lootbox_sort
