import json

import pytest

from personal_goals import models
from personal_goals.api.modules import goals_list as module
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
async def test_goal_list(web_app_client, web_context, taxi_tariffs):
    data = {}
    response = await web_app_client.get(
        '/4.0/goals/v1/list?zone_name=moscow',
        data=json.dumps(data),
        headers=_prepare_headers(),
    )
    assert response.status == 200

    response_json = await response.json()
    user_goals = response_json['goals']
    assert len(user_goals) == 1
    assert not response_json['notifications']

    user_goal = user_goals[0]
    assert user_goal['goal'] == 'user_goal_id_1'
    assert user_goal['status'] == 'active'
    assert user_goal['bonus_type'] == 'promocode'
    assert user_goal['title']
    assert user_goal['progress']
    assert user_goal['currency_rules']


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.parametrize(
    'goal_ids, dates_finish, remaining_goals',
    [
        (
            ['goal_1', 'goal_2'],
            ['2019-07-28T00:00:00+0', '2019-07-25T00:00:00+0'],
            ['goal_1'],
        ),
        (
            ['goal_1', 'goal_2'],
            ['2019-07-20T00:00:00+0', '2019-07-25T00:00:00+0'],
            [],
        ),
        (
            ['goal_1', 'goal_2'],
            ['2021-07-20T00:00:00+0', '2021-07-25T00:00:00+0'],
            ['goal_1', 'goal_2'],
        ),
    ],
)
async def test_valid_goals(
        goal_ids,
        dates_finish,
        remaining_goals,
        make_default_goal,
        web_context,
):
    goal_list = []
    for goal_id, date_finish in zip(goal_ids, dates_finish):
        goal_doc = make_default_goal(
            {
                'goal_id': goal_id,
                'conditions': {
                    'type': 'ride',
                    'count': 5,
                    'date_finish': date_finish,
                },
            },
        )
        # pylint: disable=W0212
        goal = models.parse.parse_personal_goal(goal_doc)
        goal_list.append(goal)

    # pylint: disable=W0212
    filtered_goals = module.goals._get_valid_goals(web_context, goal_list)
    assert [goal.user_goal_id for goal in filtered_goals] == remaining_goals


@pytest.mark.parametrize(
    'notification_ids, filtered_notifications',
    [
        (['new_notification_1'], ['new_notification_1']),
        (['new_notification_1', 'goal_progress_1'], ['goal_progress_1']),
        (
            ['goal_progress_1', 'finish_notification_1'],
            ['finish_notification_1'],
        ),
        (['finish_notification_2', []]),
    ],
)
@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['goal_list_goals.sql'])
async def test_valid_notifications(
        notification_ids, filtered_notifications, web_context,
):
    # pylint: disable=W0212
    notifications = await module.notifications._fetch_notifications(
        yandex_uid='yandex_uid_2',
        user_application='yandex',
        context=web_context,
    )
    selected_notitifcations = list(
        filter(lambda x: x.notification_id in notification_ids, notifications),
    )
    # pylint: disable=W0212
    filtered = module.notifications._filter_notifications(
        web_context, selected_notitifcations,
    )
    filtered_ids = [elem.notification_id for elem in filtered]
    assert filtered_ids == filtered_notifications


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.translations(
    client_messages=common.CLIENT_MESSAGES, tariff=common.TARIFF,
)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_hidden_goals(web_app_client, web_context, taxi_tariffs):
    data = {}
    response = await web_app_client.get(
        '/4.0/goals/v1/list?zone_name=moscow',
        data=json.dumps(data),
        headers=_prepare_headers(yandex_uid='hidden_uid'),
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['goals']
    assert not response_json['notifications']


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_different_app(web_app_client, web_context, taxi_tariffs):
    data = {}
    x_request_application = (
        'app_name=uber_android,app_build=release,'
        'platform_ver2=1,app_ver2=116,app_ver1=3,'
        'platform_ver1=8,app_ver3=0,platform_ver3=0'
    )
    response = await web_app_client.get(
        '/4.0/goals/v1/list?zone_name=moscow',
        data=json.dumps(data),
        headers=_prepare_headers(x_request_application=x_request_application),
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['goals']
    assert not response_json['notifications']
