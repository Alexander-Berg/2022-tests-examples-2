import json

import pytest


@pytest.mark.parametrize(
    'goal_id, expected_code',
    [
        ('random_goal_id', 409),
        ('user_goal_id_1', 409),
        ('user_goal_id_2', 200),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_reward_complete(web_app_client, goal_id, expected_code):
    data = {'user_goal_id': goal_id}
    response = await web_app_client.post(
        '/internal/reward/complete', data=json.dumps(data),
    )
    assert response.status == expected_code


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_reward_complete_conflict(web_app_client, pg_goals):
    goal_id = 'user_goal_id_2'
    data = {'user_goal_id': goal_id}
    response = await web_app_client.post(
        '/internal/reward/complete', data=json.dumps(data),
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/internal/reward/complete', data=json.dumps(data),
    )
    assert response.status == 200

    events = await pg_goals.notifications.by_user_goal(goal_id)
    assert len(events) == 1
    assert events[0]['event'] == 'goal_finish'


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_reward_fixed_cashback_bonus(web_app_client, pg_goals):
    data = {'user_goal_id': 'user_goal_id_3'}
    response = await web_app_client.post(
        '/internal/reward/complete', data=json.dumps(data),
    )
    assert response.status == 200

    events = await pg_goals.notifications.by_user_goal('user_goal_id_3')
    assert not events
