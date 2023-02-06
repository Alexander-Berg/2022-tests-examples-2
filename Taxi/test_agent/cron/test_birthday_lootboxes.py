import pytest

from agent import const
from agent.generated.cron import cron_context as cron_ctx
from agent.generated.cron import run_cron
from agent.stq import billing as stq_billing

EXPECTED_BIRTHDAY_LOOTBOXES = [
    {'login': 'webalex', 'coins': 7, 'skin': 'birthday'},
    {'login': 'justmark0', 'coins': 7, 'skin': 'birthday'},
]


async def get_birthday_lootboxes(context: cron_ctx.Context):
    async with context.pg.slave_pool.acquire() as conn:
        query = 'SELECT login, coins, skin FROM agent.created_lootboxes'
        return await conn.fetch(query)


@pytest.mark.now('2021-03-01T22:01:00+0000')
@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'calltaxi': {
            'main_permission': 'user_calltaxi',
            'enable_birthday_lootbox': True,
            'coins_birthday_lootbox': 7,
        },
    },
)
async def test_birthday_lootboxes(
        stq,
        cron_context,
        stq3_context,
        mock_billing_balance,
        mock_billing_orders,
):
    lootboxes = await get_birthday_lootboxes(cron_context)

    assert len(lootboxes) == 1
    expected = {'login': 'akozhevina', 'coins': 7, 'skin': 'rare_card'}
    for field in expected:
        assert lootboxes[0][field] == expected[field]

    await run_cron.main(['agent.crontasks.send_birthday_lootbox', '-t', '0'])

    lootboxes = await get_birthday_lootboxes(cron_context)
    assert len(lootboxes) == 3
    for lootbox in lootboxes:
        assert lootbox['login'] in ['justmark0', 'webalex', 'akozhevina']
        assert lootbox['coins'] == 7
        assert lootbox['skin'] == const.BIRTHDAY_LOOTBOX_SKIN

    count_stq_tasks = 2
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
                'section_type': const.BILLING_LOOTBOX_SECTION_TYPE,
                'payment_uid': task['kwargs']['payment_uid'],
                'description': (const.BILLING_BIRTHDAY_LOOTBOX_DESCRIPTION),
            },
            'queue': 'agent_billing_queue',
        }
        await stq_billing.task(stq3_context, **task['kwargs'])
    assert stq.is_empty
