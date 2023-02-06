import json

import pytest


DEFAULT_GOAL_BODY = {
    'selection_id': 'selection_1',
    'goal_id': 'goal_1',
    'yandex_uid': 'yandex_uid_1',
    'application': 'yandex',
    'conditions': {
        'type': 'ride',
        'count': 5,
        'classes': ['econom'],
        'date_start': '2019-07-29T16:12:48.372+03:00',
        'date_finish': '2019-09-01T16:12:48.372+03:00',
    },
    'bonus': {
        'type': 'promocode',
        'value': '500',
        'series': 'bonus',
        'currency': 'RUB',
    },
}


async def test_add_bulk(web_app_client, pg_goals):
    data = [DEFAULT_GOAL_BODY]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )
    assert response.status == 200

    selections = await pg_goals.selections.all()
    assert len(selections) == 1
    assert selections[0]['selection_id'] == 'selection_1'
    assert selections[0]['status'] == 'hidden'

    goals = await pg_goals.goals.all()
    assert len(goals) == 1
    assert goals[0]['id'] == 'goal_1'

    user_goals = await pg_goals.user_goals.all()
    assert len(user_goals) == 1
    assert user_goals[0]['yandex_uid'] == 'yandex_uid_1'
    assert user_goals[0]['status'] == 'active'

    notifications = await pg_goals.notifications.all()
    assert len(notifications) == 1
    assert notifications[0]['user_goal'] == user_goals[0]['id']
    assert notifications[0]['event'] == 'goal_start'


async def test_many_selections(web_app_client, pg_goals):
    data = [
        {
            **DEFAULT_GOAL_BODY,
            'yandex_uid': '123456',
            'selection_id': 'selection_1',
        },
        {
            **DEFAULT_GOAL_BODY,
            'yandex_uid': 'different',
            'selection_id': 'selection_2',
        },
    ]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )
    assert response.status == 200

    selections = await pg_goals.selections.all()
    assert len(selections) == 2


async def test_consistency(web_app_client, pg_goals):
    data = [DEFAULT_GOAL_BODY]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )
    assert response.status == 200
    assert len(await pg_goals.selections.all()) == 1
    assert len(await pg_goals.goals.all()) == 1
    assert len(await pg_goals.user_goals.all()) == 1
    assert len(await pg_goals.notifications.all()) == 1


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_two_active_goals(web_app_client):
    data = [
        {
            **DEFAULT_GOAL_BODY,
            'yandex_uid': '999999',
            'goal_id': 'goal_for_exclude',
        },
    ]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'excluded_goals': [{'goal_id': 'goal_for_exclude'}],
    }


async def test_two_goals_in_same_bulk(web_app_client):
    data = [
        {
            **DEFAULT_GOAL_BODY,
            'yandex_uid': '999999',
            'goal_id': 'correct_goal',
        },
        {
            **DEFAULT_GOAL_BODY,
            'yandex_uid': '999999',
            'goal_id': 'goal_for_exclude',
        },
    ]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )

    assert response.status == 200
    response_json = await response.json()
    assert response_json == {
        'excluded_goals': [{'goal_id': 'goal_for_exclude'}],
    }


async def test_broken_payload(web_app_client):
    data = [
        {
            **DEFAULT_GOAL_BODY,
            'conditions': {'type': 'ride', 'count': 5},
            'yandex_uid': '999998',
            'goal_id': 'broken_goal',
        },
    ]

    response = await web_app_client.post(
        '/internal/admin/add_bulk', data=json.dumps(data),
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {'reason': 'date_finish is required property'},
        'message': 'Some parameters are invalid',
    }
