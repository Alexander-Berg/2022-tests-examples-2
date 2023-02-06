# pylint: disable=redefined-outer-name
import datetime

from aiohttp import web
import pytest

from agent.generated.cron import run_cron

OEBS_RESPONSE = {
    'data': [
        {'login': 'webalex', 'term_date': '03.01.2019'},
        {'login': 'nouser', 'term_date': '04.01.2019'},
        {'login': 'dublicate_login', 'term_date': '05.01.2019'},
        {'login': 'evrum', 'term_date': '15.01.2019'},
    ],
}

EXPECTED_DATA_1 = [
    {
        'login': 'dublicate_login',
        'term_date': datetime.datetime(2019, 1, 5).date(),
        'chief_login': 'webalex',
        'team': 'taxi',
        'organization': 'taxi',
        'projects': ['user_call_taxi'],
        'status': 'new',
        'completed_at': None,
    },
    {
        'login': 'evrum',
        'term_date': datetime.datetime(2019, 1, 10).date(),
        'chief_login': 'webalex',
        'team': 'taxi',
        'organization': 'taxi',
        'projects': ['user_call_taxi'],
        'status': 'new',
        'completed_at': None,
    },
]

EXPECTED_DATA_2 = [
    {
        'login': 'dublicate_login',
        'term_date': datetime.datetime(2019, 1, 5).date(),
        'chief_login': 'webalex',
        'team': 'taxi',
        'organization': 'taxi',
        'projects': ['user_call_taxi'],
        'status': 'new',
        'completed_at': None,
    },
    {
        'login': 'evrum',
        'term_date': datetime.datetime(2019, 1, 15).date(),
        'chief_login': None,
        'team': None,
        'organization': None,
        'projects': None,
        'status': 'new',
        'completed_at': None,
    },
    {
        'login': 'webalex',
        'term_date': datetime.datetime(2019, 1, 3).date(),
        'chief_login': None,
        'team': None,
        'organization': None,
        'projects': None,
        'status': 'new',
        'completed_at': None,
    },
]


async def get_users(context):
    query = (
        'SELECT '
        'login,'
        'term_date,'
        'chief_login,'
        'team,'
        'organization,'
        'projects,'
        'status,'
        'completed_at  '
        'FROM agent.dismissed_users ORDER BY login'
    )
    async with context.pg.slave_pool.acquire() as conn:
        return await conn.fetch(query)


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_oebs_term(cron_context, mock_oebs, taxi_config):
    @mock_oebs('/rest/getSdelTerm', prefix=True)
    def handler(request):  # pylint: disable=unused-variable
        assert request.method == 'POST'
        assert request.json == {
            'Date_from': '2018-12-31',
            'Date_to': '2019-01-31',
        }
        return web.json_response(OEBS_RESPONSE)

    users = await get_users(context=cron_context)
    assert len(users) == 2
    assert dict(users[0]) == EXPECTED_DATA_1[0]
    assert dict(users[1]) == EXPECTED_DATA_1[1]

    await run_cron.main(['agent.crontasks.sdel_import_dismissed', '-t', '0'])

    users = await get_users(context=cron_context)

    users = list(map(dict, users))
    assert len(users) == 3
    assert dict(users[0]) == EXPECTED_DATA_2[0]
    assert dict(users[1]) == EXPECTED_DATA_2[1]
    assert dict(users[2]) == EXPECTED_DATA_2[2]

    await run_cron.main(['agent.crontasks.sdel_import_dismissed', '-t', '0'])

    users = await get_users(context=cron_context)
    assert len(users) == 3
