import pytest

from . import web_common


PERSONAL_ID_TO_TG_ID = {'pd1': '123'}

ENDPOINT = '/fleet/fleet-notifications-telegram-bot/v1/telegram-user'


@pytest.mark.pgsql(
    'fleet_notifications_telegram_bot',
    files=['pg_fleet_notifications_telegram_bot.sql'],
)
@pytest.mark.parametrize(
    'park_id, user_id, telegram_login, expected_code, expected_json',
    [
        pytest.param(
            'p1',
            '1',
            'login1',
            200,
            {'telegram_login': 'login1'},
            id='link exists',
        ),
        pytest.param(
            'p1',
            '1000',
            None,
            404,
            {'code': '404', 'message': 'User is not registered in Bot'},
            id='no link',
        ),
    ],
)
async def test_no_token(
        taxi_fleet_notifications_telegram_bot_web,
        park_id,
        user_id,
        telegram_login,
        personal,
        telegram,
        expected_code,
        expected_json,
):
    telegram.set_telegram_login(telegram_login)

    personal.set_personal_to_tg_id(PERSONAL_ID_TO_TG_ID)

    headers = {'X-Park-Id': park_id, **web_common.make_headers(user_id)}

    response = await taxi_fleet_notifications_telegram_bot_web.get(
        ENDPOINT, headers=headers,
    )

    assert response.status == expected_code
    assert await response.json() == expected_json
