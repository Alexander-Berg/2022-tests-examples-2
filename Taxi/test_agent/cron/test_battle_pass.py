# pylint: disable=redefined-outer-name
import operator

import pytest

from agent.generated.cron import cron_context
from agent.generated.cron import run_cron
from agent.internal import billing
from agent.stq import billing as stq_billing

COINS_BALANCE = {
    'mikh-vasily': 120,
    'webalex': 220,
    'slon': 0,
    'korol': 0,
    'meetka': 0,
}

START_RESULT_TEST = [
    {'login': 'mikh-vasily', 'bo': 1500, 'attempts': 5, 'current_score': 100},
    {'login': 'slon', 'bo': 0, 'attempts': 0, 'current_score': 0},
    {'login': 'korol', 'bo': 0, 'attempts': 0, 'current_score': 0},
    {'login': 'meetka', 'bo': 0, 'attempts': 0, 'current_score': 0},
]

FINISH_RESULT_TEST = [
    {
        'login': 'mikh-vasily',
        'bo': 10000.0,
        'attempts': 33,
        'current_score': 184,
    },
    {'login': 'slon', 'bo': 100.0, 'attempts': 0, 'current_score': 0},
    {'login': 'korol', 'bo': 1000.0, 'attempts': 3, 'current_score': 3},
    {'login': 'meetka', 'bo': 5000.0, 'attempts': 16, 'current_score': 16},
]


PIECEWORK_RESPONSE_FIRST = {
    'calculation': {'commited': True},
    'logins': [
        {
            'login': 'mikh-vasily',
            'date': '2021-01-01',
            'bo': {
                'daytime_cost': 10000,
                'night_cost': 0,
                'holidays_daytime_cost': 0,
                'holidays_night_cost': 0,
            },
        },
    ],
}

PIECEWORK_RESPONSE_SECOND = {
    'calculation': {'commited': True},
    'logins': [
        {
            'login': 'mikh-vasily',
            'date': '2021-01-01',
            'bo': {
                'daytime_cost': 12000,
                'night_cost': 0,
                'holidays_daytime_cost': 0,
                'holidays_night_cost': 0,
            },
        },
    ],
}


async def get_rating(context: cron_context.Context):
    async with context.pg.slave_pool.acquire() as conn:
        query = 'SELECT * FROM agent.battle_pass_rating'
        return await conn.fetch(query)


async def test_battle_pass_disable(cron_context):

    rating = await get_rating(context=cron_context)
    data = [
        {
            'login': user['login'],
            'bo': user['bo'],
            'attempts': user['attempts'],
            'current_score': user['current_score'],
        }
        for user in rating
    ]

    data.sort(key=operator.itemgetter('login'))
    START_RESULT_TEST.sort(key=operator.itemgetter('login'))
    assert data == START_RESULT_TEST

    await run_cron.main(['agent.crontasks.battle_pass_add_score', '-t', '0'])

    rating = await get_rating(context=cron_context)

    data = [
        {
            'login': user['login'],
            'bo': user['bo'],
            'attempts': user['attempts'],
            'current_score': user['current_score'],
        }
        for user in rating
    ]

    data.sort(key=operator.itemgetter('login'))
    START_RESULT_TEST.sort(key=operator.itemgetter('login'))
    assert data == START_RESULT_TEST


@pytest.mark.config(
    AGENT_BATTLE_PASS_PERCENT_DROP_SCORE={
        'default': {
            'snowflakes': [{'percent': 100, 'value': 1}],
            'coins': [{'percent': 100, 'value': 2}],
        },
        'team_1': {
            'snowflakes': [{'percent': 100, 'value': 3}],
            'coins': [{'percent': 100, 'value': 2}],
        },
    },
)
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': False,
            'main_permission': 'user_calltaxi',
            'wallet': 'calltaxi',
            'piecework_tariff': 'call-taxi-unified',
        },
    },
)
@pytest.mark.config(AGENT_BATTLE_PASS_AUTO_ADD_SCORE_ENABLE=True)
async def test_battle_pass(
        stq,
        cron_context,
        stq3_context,
        web_app_client,
        mock_piecework_daily_load,
        mock_billing_balance,
        mock_billing_orders,
):
    mock_piecework_daily_load(response=PIECEWORK_RESPONSE_FIRST)

    rating = await get_rating(context=cron_context)

    for user in rating:
        balance_coins = await billing.balance(
            context=cron_context,
            login=user['login'],
            project='calltaxi'
            if user['login'] in ['webalex', 'mikh-vasily']
            else 'taxisupport',
        )

        assert balance_coins == COINS_BALANCE.get(user['login'])

    data = [
        {
            'login': user['login'],
            'bo': user['bo'],
            'attempts': user['attempts'],
            'current_score': user['current_score'],
        }
        for user in rating
    ]

    data.sort(key=operator.itemgetter('login'))
    START_RESULT_TEST.sort(key=operator.itemgetter('login'))
    assert data == START_RESULT_TEST

    await run_cron.main(['agent.crontasks.battle_pass_add_score', '-t', '0'])

    rating = await get_rating(context=cron_context)

    data = [
        {
            'login': user['login'],
            'bo': user['bo'],
            'attempts': user['attempts'],
            'current_score': user['current_score'],
        }
        for user in rating
    ]
    assert data.sort(
        key=operator.itemgetter('login'),
    ) == FINISH_RESULT_TEST.sort(key=operator.itemgetter('login'))

    data.sort(key=operator.itemgetter('login'))
    FINISH_RESULT_TEST.sort(key=operator.itemgetter('login'))
    assert data == FINISH_RESULT_TEST

    count_stq_tasks = 3
    assert stq.agent_billing_queue.times_called == count_stq_tasks

    for _i in range(count_stq_tasks):
        task = stq.agent_billing_queue.next_call()
        assert task == {
            'args': [],
            'eta': task['eta'],
            'id': task['id'],
            'kwargs': {
                'amount': task['kwargs']['amount'],
                'login': task['kwargs']['login'],
                'method': 'deposit',
                'operation_type': 'payment',
                'project': task['kwargs']['project'],
                'section_type': 'auto coins',
                'payment_uid': task['kwargs']['payment_uid'],
                'description': 'Battle Pass',
            },
            'queue': 'agent_billing_queue',
        }
        await stq_billing.task(stq3_context, **task['kwargs'])
    assert stq.is_empty
