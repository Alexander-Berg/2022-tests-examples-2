import json

import pytest


async def test_complete_no_goal(taxi_personal_goals_web):
    data = {'yandex_uid': 'random_uid'}
    response = await taxi_personal_goals_web.post(
        '/internal/v2/goal/complete', data=json.dumps(data),
    )
    assert response.status == 200


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_not_rewarded_goal(taxi_personal_goals_web):
    data = {'yandex_uid': '666666'}
    response = await taxi_personal_goals_web.post(
        '/internal/v2/goal/complete', data=json.dumps(data),
    )
    assert response.status == 200

    result = await response.json()

    assert result == {
        'goals': [
            {
                'goal_id': 'c69e65c601c04ffdaa6277c80cafe7f8',
                'status': 'finished',
            },
        ],
    }


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_complete_many(taxi_personal_goals_web):
    data = {'yandex_uid': '999999'}
    response = await taxi_personal_goals_web.post(
        '/internal/v2/goal/complete', data=json.dumps(data),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'goals': [
            {
                'goal_id': '9921d89db101479ab1e476d8910d72fb',
                'status': 'finished',
            },
            {'goal_id': 'user_goal_id_4', 'status': 'not_finished'},
        ],
    }


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_goal_with_fixed_cashback_bonus(
        taxi_personal_goals_web, pg_goals,
):
    data = {'yandex_uid': 'yandex_uid_3'}
    response = await taxi_personal_goals_web.post(
        '/internal/v2/goal/complete', data=json.dumps(data),
    )
    assert response.status == 200

    result = await response.json()
    assert result == {
        'goals': [{'goal_id': 'user_goal_id_3', 'status': 'finished'}],
    }

    # expect a new notification for finished user goal to be added
    notifications = await pg_goals.notifications.by_user_goal('user_goal_id_3')
    assert len(notifications) == 1
    assert notifications[0]['event'] == 'goal_finish'
    assert notifications[0]['status'] == 'new'
