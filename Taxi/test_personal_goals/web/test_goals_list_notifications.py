import json

import pytest

from . import common


def _prepare_headers(
        yandex_uid=None, user_id=None, x_request_application=None,
):
    default_application = (
        'app_name=android,app_build=release,'
        'platform_ver2=1,app_ver2=116,app_ver1=3,'
        'platform_ver1=8,app_ver3=0,platform_ver3=0'
    )
    return {
        'X-YaTaxi-UserId': user_id or 'random_user_id',
        'X-Yandex-UID': yandex_uid or 'yandex_uid_1',
        'X-Request-Application': x_request_application or default_application,
    }


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.translations(
    client_messages=common.CLIENT_MESSAGES, tariff=common.TARIFF,
)
@pytest.mark.pgsql('personal_goals', files=['goal_list_goals.sql'])
async def test_goal_list_notifications(web_app_client, taxi_tariffs):
    data = {}
    response = await web_app_client.get(
        '/4.0/goals/v1/list?zone_name=moscow',
        data=json.dumps(data),
        headers=_prepare_headers(yandex_uid='yandex_uid_2'),
    )
    assert response.status == 200


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.translations(
    client_messages=common.CLIENT_MESSAGES, tariff=common.TARIFF,
)
@pytest.mark.pgsql('personal_goals', files=['goal_list_goals.sql'])
async def test_goal_list_notifications_seen(web_app_client, taxi_tariffs):
    headers = _prepare_headers(yandex_uid='yandex_uid_2')

    data = {
        'notification_ids': [
            'new_notification_2',
            'goal_progress_2',
            'finish_notification_1',
        ],
    }
    response = await web_app_client.post(
        '/4.0/goals/v1/notifications/seen',
        data=json.dumps(data),
        headers=headers,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/4.0/goals/v1/list?zone_name=moscow',
        data=json.dumps({}),
        headers=_prepare_headers(yandex_uid='yandex_uid_2'),
    )
    assert response.status == 200
    content = await response.json()

    notifications = [
        {'title': n['title'], 'bonus_type': n['bonus_type']}
        for n in content['notifications']
    ]

    assert notifications == [
        {
            'title': '5 ride unt. 30 августа - get 10%',
            'bonus_type': 'promocode',
        },
        {'title': 'Cashback 4% in 2 rides', 'bonus_type': 'cashback-boost'},
    ]
