import json

import pytest


DEFAULT_HEADERS = {
    'X-YaTaxi-UserId': 'random_user_id',
    'X-Yandex-UID': '666666',
    'X-Request-Application': (
        'app_name=android,app_build=release,'
        'platform_ver2=1,app_ver2=116,app_ver1=3,'
        'platform_ver1=8,app_ver3=0,platform_ver3=0'
    ),
}


async def test_notification_seen_disabled(web_app_client):
    data = {'notification_ids': []}
    response = await web_app_client.post(
        '/4.0/goals/v1/notifications/seen',
        data=json.dumps(data),
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 429


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.parametrize(
    'notifications,new_count',
    [
        (['b7fc20328ae043fb830d4c3453331906'], 3),
        (
            [
                'b7fc20328ae043fb830d4c3453331906',
                'b7fc20328ae043fb830d4c3453331906',
            ],
            3,
        ),
        (
            [
                'b7fc20328ae043fb830d4c3453331906',
                '8072aa213e914b00b066b5f9f83f663d',
            ],
            2,
        ),
        (['random'], 4),
    ],
)
async def test_notification_seen(
        web_app_client, pg_goals, notifications, new_count,
):
    data = {'notification_ids': notifications}
    response = await web_app_client.post(
        '/4.0/goals/v1/notifications/seen',
        data=json.dumps(data),
        headers=DEFAULT_HEADERS,
    )
    assert response.status == 200

    notifs = await pg_goals.notifications.by_status('new')
    assert len(notifs) == new_count


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
async def test_notification_seen_wronguid(web_app_client, pg_goals):
    notification_id = 'b7fc20328ae043fb830d4c3453331906'
    data = {'notification_ids': [notification_id]}
    headers = {
        **DEFAULT_HEADERS,
        'X-YaTaxi-UserId': 'random_user_id',
        'X-Yandex-UID': 'no_uid',
    }
    response = await web_app_client.post(
        '/4.0/goals/v1/notifications/seen',
        data=json.dumps(data),
        headers=headers,
    )
    assert response.status == 200

    notification = (await pg_goals.notifications.by_ids([notification_id]))[0]
    assert notification['status'] == 'new'
