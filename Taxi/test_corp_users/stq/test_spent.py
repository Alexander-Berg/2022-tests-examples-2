import uuid

import pytest

from taxi.util import dates
from taxi.util import payment_helpers

from corp_users.stq import inc_spent


def _get_spent_from_user(user, now, timezone):
    month = dates.this_month_start(now, timezone).strftime('%Y-%m')
    if month in user['stat']:
        return int(
            payment_helpers.inner2cost(
                user['stat'][month].get('spent_with_vat', 0),
            ),
        )
    return 0


async def _test_inc_spent(
        db, stq3_context, user_id, start_cost, costs, timezone, stamp,
):
    corp_user = await db.corp_users.find_one({'_id': user_id})
    assert _get_spent_from_user(corp_user, stamp, timezone) == start_cost
    order_ids = [uuid.uuid4().hex for _ in costs]

    expected_cost = start_cost
    for order_id, cost in zip(order_ids, costs):
        expected_cost += cost
        await inc_spent.task(
            stq3_context, user_id, order_id, cost * 10000, stamp,
        )

        corp_user = await db.corp_users.find_one({'_id': user_id})
        assert (
            _get_spent_from_user(corp_user, stamp, timezone) == expected_cost
        )

    # check that duplicate request for same order_id doesn't affect spent
    for order_id, cost in zip(order_ids, costs):
        await inc_spent.task(
            stq3_context, user_id, order_id, cost * 10000, stamp,
        )

        corp_user = await db.corp_users.find_one({'_id': user_id})
        assert (
            _get_spent_from_user(corp_user, stamp, timezone) == expected_cost
        )


@pytest.mark.parametrize(
    ['stamp', 'start_cost', 'timezone'],
    [
        pytest.param(
            dates.parse_timestring('2016-03-31 22:00:00+03'),
            2000,
            'Europe/Moscow',
            id='default',
        ),
        pytest.param(
            dates.parse_timestring('2016-03-31 22:00:00+03'),
            1000,
            'Asia/Yekaterinburg',
            id='ekb',
        ),
        pytest.param(
            dates.parse_timestring('2016-05-02 01:02:03+03'),
            0,
            'Europe/Moscow',
            id='future',
        ),
        pytest.param(
            dates.parse_timestring('2016-02-02 01:02:03+03'),
            0,
            'Europe/Moscow',
            id='past',
        ),
    ],
)
async def test_inc_spent_now(
        mockserver, db, stq3_context, stamp, timezone, start_cost,
):
    @mockserver.json_handler('/corp-clients/v1/clients')
    async def _get_clients(request):
        return {'id': 'id1', 'tz': timezone}

    await _test_inc_spent(
        db,
        stq3_context,
        'test_user_1',
        start_cost,
        [100, 200],
        timezone,
        stamp,
    )
