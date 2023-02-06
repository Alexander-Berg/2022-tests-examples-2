# pylint: disable=redefined-outer-name
import datetime

import pytest

from agent.generated.cron import run_cron


EXPECTED_DATA = {
    'piskarev': {
        'username': 'piskarev',
        'uid': None,
        'guid': None,
        'first_name': 'piskarev',
        'en_first_name': 'piskarev',
        'en_last_name': 'piskarev',
        'last_name': 'piskarev',
        'join_at': '2000-01-01',
        'quit_at': None,
        'birthday': None,
        'organization': None,
        'is_robot': False,
        'telegram': [],
        'department': None,
        'team': None,
        'phones': [],
        'source': 'yateam_staff',
        'email': 'piskarev@yandex-team.ru',
        'external_login': None,
        'external': False,
    },
    'webalex': {
        'username': 'webalex',
        'uid': '12345',
        'guid': '12345',
        'first_name': 'Александр',
        'en_first_name': 'Alexandr',
        'last_name': 'Иванов',
        'en_last_name': 'Ivanov',
        'join_at': '2016-06-02',
        'quit_at': None,
        'birthday': '1980-11-21',
        'organization': 'Яндекс',
        'is_robot': False,
        'telegram': [],
        'department': 'something_dep',
        'team': 'standart',
        'phones': ['26fe660e100e45c897225fc8637edfff'],
        'source': 'yateam_staff',
        'email': 'webalex@yandex-team.ru',
        'external_login': 'ssaneka',
        'external': False,
    },
    'liambaev': {
        'username': 'liambaev',
        'uid': '12347',
        'guid': '12347',
        'first_name': 'Лиам',
        'en_first_name': 'Liam',
        'last_name': 'Баев',
        'en_last_name': 'Baev',
        'join_at': '2016-06-02',
        'quit_at': None,
        'birthday': '1981-11-21',
        'organization': 'Яндекс',
        'is_robot': False,
        'telegram': [],
        'department': 'something_dep',
        'team': 'standart',
        'phones': ['26fe660e100e45c897225fc8637edfff'],
        'source': 'yateam_staff',
        'email': 'liambaev@yandex-team.ru',
        'external_login': 'liambaev',
        'external': False,
    },
    'orangevl': {
        'username': 'orangevl',
        'uid': '141111',
        'guid': '141111',
        'first_name': 'Семён',
        'en_first_name': 'Simon',
        'last_name': 'Решетняк',
        'en_last_name': 'Reshetnyak',
        'join_at': '2010-01-01',
        'quit_at': None,
        'birthday': '1982-11-21',
        'organization': 'Яндекс Деньги',
        'is_robot': False,
        'telegram': [],
        'department': 'something_dep',
        'team': 'standart',
        'phones': ['26fe660e100e45c897225fc8637edfff'],
        'source': 'yateam_staff',
        'email': 'orangevl@yandex-team.ru',
        'external_login': None,
        'external': True,
    },
    'robot-support-taxi': {
        'username': 'robot-support-taxi',
        'uid': '15',
        'guid': '15',
        'first_name': 'Robot',
        'en_first_name': 'Robot',
        'last_name': 'Robot',
        'en_last_name': 'Robot',
        'join_at': '2000-01-01',
        'quit_at': None,
        'birthday': '1983-11-21',
        'organization': 'Яндекс Драйв',
        'is_robot': True,
        'telegram': ['ab7326daa774233d779c2e015d2c9e0c'],
        'department': 'yandex',
        'team': None,
        'phones': ['26fe660e100e45c897225fc8637edfff'],
        'source': 'yateam_staff',
        'email': 'robot-support-taxi@yandex-team.ru',
        'external_login': None,
        'external': True,
    },
    'dismissed_user': {
        'username': 'dismissed_user',
        'uid': '15',
        'guid': '15',
        'first_name': 'Dismissed_User',
        'en_first_name': 'Dismissed_User',
        'last_name': 'Dismissed_User',
        'en_last_name': 'Dismissed_User',
        'join_at': '2000-01-01',
        'quit_at': '2021-01-01',
        'birthday': None,
        'organization': 'Яндекс Драйв',
        'is_robot': False,
        'telegram': ['ab7326daa774233d779c2e015d2c9e0c'],
        'department': 'yandex',
        'team': None,
        'phones': ['26fe660e100e45c897225fc8637edfff'],
        'source': 'yateam_staff',
        'email': 'dismissed_user@yandex-team.ru',
        'external_login': None,
        'external': False,
    },
}


async def count_users(cron_context):
    query = 'SELECT count(*) as cnt FROM agent.users'
    async with cron_context.pg.slave_pool.acquire() as conn:
        return await conn.fetchrow(query)


async def get_users(cron_context):
    query = 'SELECT * FROM agent.users'
    async with cron_context.pg.slave_pool.acquire() as conn:
        return await conn.fetch(query)


async def get_user_history_team(cron_context):
    query = 'SELECT * FROM agent.user_history_team'
    async with cron_context.pg.slave_pool.acquire() as conn:
        return await conn.fetch(query)


@pytest.mark.config(
    AGENT_SYNC_STAFF_PERSONS_ROW_LIMIT=1,
    AGENT_ENABLE_AUTOMATIC_TEAM_ASSIGNMENT=True,
    AGENT_AUTOMATIC_TEAM_ASSIGNMENT_SETTINGS=[
        {
            'department': 'something_dep',
            'permission': 'user_calltaxi',
            'team': 'standart',
        },
    ],
)
async def test_import_users_from_staff(
        cron_context,
        mock_staff_persons_api,
        taxi_config,
        bulk_personal_store_phone,
        bulk_personal_store_telegram,
):

    count_user = await count_users(cron_context=cron_context)
    assert count_user['cnt'] == 4
    await run_cron.main(['agent.crontasks.import_staff_persons', '-t', '0'])
    count_user = await count_users(cron_context=cron_context)
    assert count_user['cnt'] == len(EXPECTED_DATA)

    users = await get_users(cron_context)
    user_history_team = await get_user_history_team(cron_context)

    for user in users:
        login = user['login']
        user_data = EXPECTED_DATA.get(login)
        assert user['login'] == user_data['username']
        assert user['uid'] == user_data['uid']
        assert user['first_name'] == user_data['first_name']
        assert user['en_first_name'] == user_data['en_first_name']

        assert user['last_name'] == user_data['last_name']
        assert user['en_last_name'] == user_data['en_last_name']

        if user['join_at'] is not None:
            assert user['join_at'].strftime('%Y-%m-%d') == user_data['join_at']
        if user['quit_at'] is not None:
            assert user['quit_at'].strftime('%Y-%m-%d') == user_data['quit_at']

        assert user['organization'] == user_data['organization']
        assert user['is_robot'] == user_data['is_robot']
        assert user['telegram'] == user_data['telegram']
        assert user['department'] == user_data['department']
        assert user['guid'] == user_data['guid']
        if user['birthday'] is not None:
            assert user.get('birthday').strftime('%Y-%m-%d') == user_data.get(
                'birthday',
            )

        assert user['phones'] == user_data['phones']
        assert user['email'] == user_data['email']
        assert user['source'] == user_data['source']
        assert user['external'] == user_data['external']

        assert user['external_login'] == user_data['external_login']

        assert user['team'] == user_data['team']
        for history in user_history_team:
            if history['login'] == login:
                assert history['dt'] == datetime.date.today()
                assert history['team'] == user_data['team']
