import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_notification_200(taxi_eats_notifications, load_json):
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification_id = 1
    response = await taxi_eats_notifications.get(
        '/v1/admin/notification', params={'id': notification_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['id'] == notification_id
    assert response_json['data'] == notification

    # try insert the same notification
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 409


async def test_v1_admin_notification_get_not_found(
        taxi_eats_notifications, taxi_config,
):
    response = await taxi_eats_notifications.get(
        '/v1/admin/notification', params={'id': 1},
    )
    assert response.status_code == 404


async def test_v1_admin_notification_project_not_found(
        taxi_eats_notifications, load_json,
):
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        'v1/admin/notification', json=notification,
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'228\', \'tanker_project\', \'tanker_keyset\','
        '\'intent\')',
    ],
)
async def test_v1_admin_notifications_search_200(
        taxi_eats_notifications, load_json,
):
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification = load_json('notification2.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification = load_json('notification3.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    # empty search
    search_result = load_json('all_notifications_truncated.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications/search',
        json={'project_id': 1, 'pagination': {'number': 1, 'size': 20}},
    )
    assert response.status_code == 200
    assert response.json() == search_result

    # search by name
    search_result = load_json('notification_truncated.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications/search',
        json={'name': 'notification', 'project_id': 1},
    )
    assert response.status_code == 200
    assert response.json() == search_result

    # search by key
    search_result = load_json('notification_truncated.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications/search', json={'key': 'key', 'project_id': 1},
    )
    assert response.status_code == 200
    assert response.json() == search_result

    # search by type and multiple parameters
    search_result = load_json('all_notifications_truncated.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications/search',
        json={
            'project_id': 1,
            'type': {'push': True, 'sms': False, 'call': False},
        },
    )
    assert response.status_code == 200
    assert response.json() == search_result


async def test_v1_admin_notifications_search_invalid_pagination(
        taxi_eats_notifications,
):
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications/search',
        json={'project_id': 1, 'pagination': {'number': 0, 'size': 20}},
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key_2\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_notification_edit_200(
        taxi_eats_notifications, load_json,
):
    notification_id = 1

    # add notification
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=load_json('notification1.json'),
    )
    assert response.status_code == 204

    # update notification
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification',
        json=load_json('notification_update_request.json'),
    )
    assert response.status_code == 204

    # check notification is updated
    response = await taxi_eats_notifications.get(
        '/v1/admin/notification', params={'id': notification_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['id'] == notification_id
    assert response_json['data'] == load_json('notification_updated.json')


async def test_v1_admin_notification_put_invalid_request(
        taxi_eats_notifications, load_json,
):
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification',
        json=load_json('notification_update_request.json'),
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_check_validate_create_notification(
        taxi_eats_notifications, load_json,
):
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-create', json=notification,
    )
    assert response.status_code == 200
    assert response.json()['data'] == load_json('notification1.json')

    notification['key'] = 228
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-create', json=notification,
    )
    assert response.status_code == 400

    notification['key'] = 'KEY'
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-create', json=notification,
    )
    assert response.status_code == 200
    assert response.json()['data']['key'] == 'key'


async def test_v1_admin_check_validate_create_notification_wrong_project_id(
        taxi_eats_notifications, load_json,
):
    # try create notification
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-create',
        json=load_json('notification1.json'),
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_check_validate_update_notification(
        taxi_eats_notifications, load_json,
):
    notification = load_json('notification1.json')
    update_request_json = {'id': 1, 'data': notification}
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-update', json=update_request_json,
    )
    assert response.status_code == 400

    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification['key'] = 228
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-update', json=update_request_json,
    )
    assert response.status_code == 400

    notification['key'] = 'KEY'
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-update', json=update_request_json,
    )
    assert response.status_code == 200
    assert response.json()['data']['data']['key'] == 'key'

    notification['project_id'] = 2
    response = await taxi_eats_notifications.put(
        '/v1/admin/notification/check-update', json=update_request_json,
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_empty_sms_and_push(taxi_eats_notifications, load_json):
    notification = load_json('notification_empty_sms_and_push.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\'), '
        '(\'project2\', \'project_key2\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_v1_admin_notifications_200(taxi_eats_notifications, load_json):
    notification1 = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification1,
    )
    assert response.status_code == 204

    notification2 = load_json('notification2.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification2,
    )
    assert response.status_code == 204

    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications', json={'ids': [1, 2]},
    )
    assert response.status_code == 200
    assert response.json() == {
        'notifications': [
            {
                'id': 1,
                'notification_key': notification1['key'],
                'project_key': 'project_key',
            },
            {
                'id': 2,
                'notification_key': notification2['key'],
                'project_key': 'project_key2',
            },
        ],
    }


async def test_v1_admin_notifications_get_not_found(taxi_eats_notifications):
    response = await taxi_eats_notifications.post(
        '/v1/admin/notifications', json={'ids': [1]},
    )
    assert response.json() == {'notifications': []}
