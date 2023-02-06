import json

import pytest

from testsuite.utils import json_util

from personal_goals.modules.goalcheck import exceptions


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=False)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_register_order_disabled(web_app_client, make_default_order):
    order = make_default_order({'_id': 'order_id-77'})
    data = {
        'order_id': 'order_id-77',
        'yandex_uid': 'yandex_uid_1',
        'created': '2019-05-24T10:00:00.0',
        'order_info': json_util.dumps(order),
    }

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200

    json_response = await response.json()
    assert json_response == {'goals': []}


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_register_order_base(web_app_client, make_default_order):
    data = {
        'order_id': 'order_id',
        'yandex_uid': 'user_uid',
        'created': '2019-05-24T10:00:00.0',
    }
    order = make_default_order({'_id': data['order_id']})
    data['order_info'] = json_util.dumps(order)

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200
    json_response = await response.json()
    assert json_response == {'goals': []}


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_register_order_with_data(
        web_app_client, make_default_order, pg_goals, json_loads,
):
    user_goal_id = 'user_goal_id_1'
    order = make_default_order(
        {'_id': 'order_id-77', 'statistics': {'application': 'android'}},
    )
    data = {
        'order_id': 'order_id-77',
        'yandex_uid': 'yandex_uid_1',
        'created': '2019-05-24T10:00:00.0',
        'order_info': json_util.dumps(order),
    }

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200

    json_response = await response.json()
    assert json_response == {
        'goals': [{'goal_id': user_goal_id, 'status': 'registered'}],
    }

    event = (await pg_goals.goal_events.by_user_goal(user_goal_id))[0]
    notif = (await pg_goals.notifications.by_user_goal(user_goal_id))[0]

    event_data = json_loads(event['event_data'])
    assert event['event_id'] == data['order_id']
    assert event['event_type'] == 'taxi_order'
    assert event_data == order

    assert notif['status'] == 'new'
    assert notif['event'] == 'goal_progress'
    assert notif['id'] == '2169ed4c68a89fd293cd147db15f1b77'


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_register_order_conflict(
        web_app_client, make_default_order, pg_goals,
):
    user_goal_id = 'user_goal_id_1'
    data = {
        'order_id': 'order_id-77',
        'yandex_uid': 'yandex_uid_1',
        'created': '2019-05-24T10:00:00.0',
    }
    order = make_default_order({'_id': data['order_id']})
    data['order_info'] = json_util.dumps(order)

    events = await pg_goals.goal_events.by_user_goal(user_goal_id)
    assert not events

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200

    events = await pg_goals.goal_events.by_user_goal(user_goal_id)
    assert len(events) == 1

    notifications = await pg_goals.notifications.by_user_goal(user_goal_id)
    assert len(notifications) == 1


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_fail_register_order(
        web_app_client, make_default_order, pg_goals,
):
    user_goal_id = 'user_goal_id_1'
    data = {
        'order_id': 'order_id-77',
        'yandex_uid': 'yandex_uid_1',
        'created': '2019-05-24T10:00:00.0',
    }
    order = make_default_order(
        {
            '_id': data['order_id'],
            'performer': {'tariff': {'class': 'business'}},
        },
    )
    data['order_info'] = json_util.dumps(order)

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200
    json_response = await response.json()
    assert json_response == {
        'goals': [{'goal_id': user_goal_id, 'status': 'not_registered'}],
    }

    events = await pg_goals.goal_events.by_user_goal(user_goal_id)
    assert len(events) == 1

    event = events[0]
    assert event['suitable'] is False
    assert event['reason'] == exceptions.ERROR_INVALID_CLASS

    notifications = await pg_goals.notifications.by_user_goal(user_goal_id)
    assert not notifications


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_register_order_hidden_goals(web_app_client, make_default_order):
    data = {
        'order_id': 'order_id',
        'yandex_uid': 'hidden_uid',
        'created': '2019-05-24T10:00:00.0',
    }
    order = make_default_order({'_id': data['order_id']})
    data['order_info'] = json_util.dumps(order)

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200
    json_response = await response.json()
    assert json_response == {'goals': []}


@pytest.mark.config(PERSONAL_GOALS_SERVICE_ENABLED=True)
@pytest.mark.now('2019-07-26T00:00:00+0')
async def test_diffetent_application(web_app_client, make_default_order):
    order = make_default_order(
        {'_id': 'order_id-77', 'statistics': {'application': 'uber_android'}},
    )
    data = {
        'order_id': 'order_id-77',
        'yandex_uid': 'yandex_uid_1',
        'created': '2019-05-24T10:00:00.0',
        'order_info': json_util.dumps(order),
    }

    response = await web_app_client.post(
        '/internal/register/order', data=json.dumps(data),
    )
    assert response.status == 200

    json_response = await response.json()
    assert json_response == {'goals': []}
