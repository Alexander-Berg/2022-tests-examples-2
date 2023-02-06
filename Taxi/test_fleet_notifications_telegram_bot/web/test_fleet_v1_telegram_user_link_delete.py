import pytest

from . import web_common

ENDPOINT = '/fleet/fleet-notifications-telegram-bot/v1/telegram-user/link'


def _check_deleted(pgsql, park_id, user_id):
    db = pgsql['fleet_notifications_telegram_bot'].cursor()
    db.execute(
        'SELECT TRUE '
        'FROM fleet_notifications_telegram_bot.tg_users_info '
        f'WHERE receiver = {(park_id, user_id)}::PARK_USER_PAIR',
    )
    return list(db) == []


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'park_id, user_id,',
    [
        pytest.param('p1', '1', id='exists'),
        pytest.param('p1', '6', id='doesn\'t exist'),
    ],
)
async def test_token(
        taxi_fleet_notifications_telegram_bot_web, pgsql, park_id, user_id,
):
    headers = {'X-Park-Id': park_id, **web_common.make_headers(user_id)}

    response = await taxi_fleet_notifications_telegram_bot_web.delete(
        ENDPOINT, headers=headers,
    )

    assert response.status == 200
    assert _check_deleted(pgsql, park_id, user_id)
