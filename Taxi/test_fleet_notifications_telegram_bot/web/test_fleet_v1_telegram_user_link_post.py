import pytest

from . import web_common

ENDPOINT = '/fleet/fleet-notifications-telegram-bot/v1/telegram-user/link'


def _check_token_in_db(pgsql, park_id, user_id):
    db = pgsql['fleet_notifications_telegram_bot'].cursor()
    db.execute(
        'SELECT identification_token '
        'FROM fleet_notifications_telegram_bot.identification_tokens_info '
        f'WHERE receiver = {(park_id, user_id)}::PARK_USER_PAIR',
    )
    return list(db)


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'park_id, user_id, old_token',
    [
        pytest.param('p1', '6', None, id='new token'),
        pytest.param('p1', '4', 't1', id='renew token'),
    ],
)
async def test_token(
        taxi_fleet_notifications_telegram_bot_web,
        pgsql,
        park_id,
        user_id,
        old_token,
):
    headers = {'X-Park-Id': park_id, **web_common.make_headers(user_id)}

    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers,
    )

    assert response.status == 200
    respone_json = await response.json()

    assert 'telegram_link' in respone_json
    token = _check_token_in_db(pgsql, park_id, user_id)
    assert token
    token = token[0][0]
    assert token in respone_json['telegram_link']
    if old_token:
        assert token != old_token


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'park_id, user_id,', [pytest.param('p1', '1', id='no need token')],
)
async def test_no_token(
        taxi_fleet_notifications_telegram_bot_web, pgsql, park_id, user_id,
):
    headers = {'X-Park-Id': park_id, **web_common.make_headers(user_id)}

    response = await taxi_fleet_notifications_telegram_bot_web.post(
        ENDPOINT, headers=headers,
    )

    assert response.status == 400
