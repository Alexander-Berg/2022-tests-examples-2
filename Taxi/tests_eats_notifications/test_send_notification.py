import json

import pytest

import tests_eats_notifications.utils as utils


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        ' VALUES (1, \'eda_android\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (1, \'eda_native\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
async def test_notification_post(
        taxi_eats_notifications_monitor,
        get_single_metric_by_label_values,
        taxi_eats_notifications,
        load_json,
        taxi_config,
        stq,
):
    taxi_config.set_values(
        {
            'EATS_NOTIFICATIONS_APPLICATIONS_V2': {
                'go': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'android_system_option',
                },
                'eda_native': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'ios_system_option',
                },
            },
        },
    )

    # add notification
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    response = await taxi_eats_notifications.post(
        '/v1/notification', json=load_json('send_notification.json'),
    )
    assert response.status_code == 200
    assert response.json()['token']

    assert stq.eats_notifications_messages.times_called == 1

    stq_call = stq.eats_notifications_messages.next_call()
    assert stq_call['queue'] == 'eats_notifications_messages'
    assert stq_call['kwargs']['user_id'] == '228'
    assert stq_call['kwargs']['options_values'] == {
        'ios_system_option': 'olololololo',
        'option1': 3,
        'option3': 'str',
    }
    assert stq_call['kwargs']['push_deeplink'] == 'yandex//sdfdsfsd-3-str'
    assert stq_call['kwargs']['user_device_id'] == 'device_id_test'

    metric = await get_single_metric_by_label_values(
        taxi_eats_notifications_monitor,
        sensor='notification_event_count',
        labels={'project_key': 'project_key', 'status': 'resolve_event'},
    )
    assert metric.labels == {
        'app_key': 'eda_native',
        'keys': 'key',
        'project_key': 'project_key',
        'status': 'resolve_event',
        'sensor': 'notification_event_count',
    }


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        ' VALUES (1, \'go\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (1, \'eda_native\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
@pytest.mark.parametrize(
    'app, expected_msg_count, expected_code',
    [pytest.param('go', 1, 200), pytest.param('eda_native', 0, 204)],
)
async def test_notification_post_app(
        taxi_eats_notifications,
        load_json,
        taxi_config,
        stq,
        app,
        expected_msg_count,
        expected_code,
):
    taxi_config.set_values(
        {
            'EATS_NOTIFICATIONS_APPLICATIONS_V2': {
                'go': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'android_system_option',
                },
                'eda_native': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'ios_system_option',
                },
            },
        },
    )
    # add notification
    notification = load_json('notification_app.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification = load_json('send_notification.json')
    notification['application'] = app
    notification['notification_key'] = 'key_app'
    response = await taxi_eats_notifications.post(
        '/v1/notification', json=notification,
    )
    assert response.status_code == expected_code
    assert stq.eats_notifications_messages.times_called == expected_msg_count


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        ' VALUES (1, \'go\')',
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (1, \'eda_native\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
@pytest.mark.parametrize(
    'app',
    [
        pytest.param(['go']),
        pytest.param(['eda_native']),
        pytest.param(['go', 'eda_native']),
    ],
)
async def test_notification_post_app_empty(
        taxi_eats_notifications, load_json, taxi_config, stq, app,
):
    taxi_config.set_values(
        {
            'EATS_NOTIFICATIONS_APPLICATIONS_V2': {
                'go': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'android_system_option',
                },
                'eda_native': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': 'ios_system_option',
                },
            },
        },
    )
    # add notification
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    notification = load_json('send_notification.json')
    notification['applications'] = app
    response = await taxi_eats_notifications.post(
        '/v1/notification', json=notification,
    )
    assert response.status_code == 200

    assert stq.eats_notifications_messages.times_called == 1


@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        'eda_native': {
            'type': 'test',
            'settings': {
                'service': 'test',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': 'ios_system_option',
            'check_active_device': True,
        },
    },
)
@pytest.mark.translations(
    notify={
        'test_title': {'locale_test': 'Тестовый заголовок'},
        'push_message_test': {'locale_test': 'Тестовое сообщение'},
    },
)
@pytest.mark.config(
    EATS_NOTIFICATIONS_HISTORY_TAGS={
        'regular': ['city', 'country'],
        'sensitive': ['order_id', 'user_id'],
    },
)
@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.projects (name, key, tanker_project,
        tanker_keyset, intent)
        VALUES ('project_name_test', 'project_key_test', 'tanker_project_test',
        'notify', 'intent_test')
        """,
        """
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 3, 0, 'sent', 0)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled, created_at, updated_at)
        VALUES
        ('user_id', 'test', TRUE, 'user_device_id_test', TRUE, TRUE,
        '2020-01-01 00:00:00+0000', '2021-02-02 00:00:00+0000'),
        ('user_id', 'test', TRUE, 'user_device_id_test_2', TRUE, TRUE,
        '2021-01-01 00:00:00+0000', '2021-01-01 00:00:00+0000')
        """,
        """
        INSERT INTO eats_notifications.eaters
        (eater_id, eater_uuid)
        VALUES
        ('user_id', 'user_id_test')
        """,
    ],
)
@pytest.mark.parametrize(
    'device_id',
    [
        pytest.param(None, id='without_device_id'),
        pytest.param('user_device_id_test', id='with_device_id'),
    ],
)
@pytest.mark.parametrize(
    'client_type, is_fail, client_notify_code, client_notify_response,'
    'ucommunications_code, ucommunications_response, transport_type,'
    'expected_status, expected_title, expected_body, expected_transport_type,'
    'expected_phone_id',
    [
        pytest.param(
            'client-notify',
            False,
            200,
            {'notification_id': 'notification_id_test'},
            500,
            {},
            1,
            'sent',
            'Тестовый заголовок',
            'Тестовое сообщение',
            'push',
            None,
            id='test_send_push',
        ),
        pytest.param(
            'ucommunications',
            False,
            400,
            {},
            200,
            {
                'message_id': 'notification_id_test',
                'message': 'OK',
                'content': 'Test message',
                'code': '200',
            },
            2,
            'sent',
            '',
            'Test message',
            'sms',
            'test_personal_phone_id',
            id='test_send_sms',
        ),
        pytest.param(
            'ucommunications',
            True,
            400,
            {},
            500,
            {'message_id': '', 'message': 'Error', 'code': '500'},
            2,
            'failed',
            '',
            '',
            None,
            None,
            id='test_fail',
        ),
    ],
)
async def test_stq_worker(
        stq_runner,
        pgsql,
        mockserver,
        client_type,
        is_fail,
        client_notify_code,
        client_notify_response,
        ucommunications_code,
        ucommunications_response,
        transport_type,
        expected_status,
        expected_title,
        expected_body,
        expected_transport_type,
        expected_phone_id,
        device_id,
):
    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        assert request.json == {
            'client_id': 'user_id_test',
            'device_id': 'user_device_id_test',
            'intent': 'intent_test',
            'locale': 'locale_test',
            'ttl': 60,
            'notification': {
                'link': 'push_deeplink_test',
                'text': 'Тестовое сообщение',
                'title': 'Тестовый заголовок',
            },
            'data': {
                'client_id': 'user_id_test',
                'timestamp_sent': '2527875900',
                'user_notification_id': 'test',
                'deeplink': 'push_deeplink_test',
                'options_values': {'option_bool': True, 'option_int': 3},
                'push_tags': ['common'],
            },
            'service': 'service_test',
        }
        return mockserver.make_response(
            status=client_notify_code, json=client_notify_response,
        )

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        return mockserver.make_response(
            status=ucommunications_code, json=ucommunications_response,
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters(request):
        return {
            'eater': {
                'id': 'test_id',
                'uuid': 'test_uuid',
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': expected_phone_id,
            },
        }

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters_by_id(request):
        assert expected_phone_id is None
        return {
            'eater': {
                'id': 'test_id',
                'uuid': 'test_uuid',
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': expected_phone_id,
            },
        }

    notifications_kwargs = {
        'token': 'test',
        'user_id': 'user_id_test',
        'service': 'service_test',
        'route': 'eda',
        'transport_type': transport_type,
        'tanker_keyset': 'notify',
        'options_values': {'option_bool': True, 'option_int': 3},
        'intent': 'intent_test',
        'project_key': 'project_key_test',
        'key': 'key_test',
        'sent_at': '2050-02-07T19:45:00.922+0000',
        'project_id': 1,
        'application_key': 'eda_native',
        'template_id': 1,
        'request': 'request_test',
        'sender': 'sender_test',
        'locale': 'locale_test',
        'sms_message': 'sms_message_test',
        'push_title': 'test_title',
        'push_message': 'push_message_test',
        'push_deeplink': 'push_deeplink_test',
        'waiting_condition': 'sent',
        'ttl': 0,
        'tags': [],
    }
    if device_id:
        notifications_kwargs['user_device_id'] = device_id
    await stq_runner.eats_notifications_messages.call(
        task_id='test', kwargs=notifications_kwargs, expect_fail=is_fail,
    )

    expected_response = None
    if not is_fail and transport_type == 1:
        expected_response = client_notify_response
    if not is_fail and transport_type == 2:
        expected_response = ucommunications_response

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT token, status, project_id, template_id, user_id, application,'
        'user_device_id, notification_params, message_title, message_body,'
        'deeplink, api_response, request, message_id, client_type, sent_at,'
        'sent_transport_type, personal_phone_id '
        'FROM eats_notifications.notifications',
    )
    notifications = list(cursor)
    assert len(notifications) == 1
    assert notifications[0][utils.NotificationsFields.token] == 'test'
    assert (
        notifications[0][utils.NotificationsFields.status] == expected_status
    )
    assert notifications[0][utils.NotificationsFields.project_id] == 1
    assert notifications[0][utils.NotificationsFields.template_id] == 1
    assert (
        notifications[0][utils.NotificationsFields.user_id] == 'user_id_test'
    )
    assert (
        notifications[0][utils.NotificationsFields.application] == 'eda_native'
    )
    assert (
        notifications[0][utils.NotificationsFields.user_device_id] == device_id
    )
    assert (
        notifications[0][utils.NotificationsFields.notification_params]
        == notifications_kwargs
    )
    assert (
        notifications[0][utils.NotificationsFields.message_title]
        == expected_title
    )
    assert (
        notifications[0][utils.NotificationsFields.message_body]
        == expected_body
    )
    assert (
        notifications[0][utils.NotificationsFields.deeplink]
        == 'push_deeplink_test'
    )
    response_raw = notifications[0][utils.NotificationsFields.api_response]
    response = json.loads(response_raw) if response_raw else None
    assert response == expected_response
    assert (
        notifications[0][utils.NotificationsFields.request] == 'request_test'
    )
    assert notifications[0][utils.NotificationsFields.message_id] == (
        'notification_id_test' if expected_status == 'sent' else None
    )
    assert (
        notifications[0][utils.NotificationsFields.client_type] == client_type
    )
    assert notifications[0][utils.NotificationsFields.sent_at] is not None
    assert (
        notifications[0][utils.NotificationsFields.sent_transport_type]
        == expected_transport_type
    )
    assert (
        notifications[0][utils.NotificationsFields.personal_phone_id]
        == expected_phone_id
    )


@pytest.mark.translations(
    notify={
        'test_title': {'locale_test': 'Тестовый заголовок'},
        'push_message_test': {'locale_test': 'Тестовое сообщение'},
        'sms_message_test': {'locale_test': 'Тестовое сообщение'},
    },
)
@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.projects (name, key, tanker_project,
        tanker_keyset, intent)
        VALUES ('project_name_test', 'project_key_test', 'tanker_project_test',
        'notify', 'intent_test')
        """,
        """
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 0, 'sent', 0)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id\', \'test\', TRUE, \'user_device_id_test\',
        TRUE, TRUE)
        """,
    ],
)
@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        'eda_native': {
            'type': 'test',
            'settings': {
                'service': 'test',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': 'ios_system_option',
            'check_active_device': False,
        },
    },
)
@pytest.mark.parametrize(
    'time, expected_status',
    [
        pytest.param('2050-02-07T19:45:00.922+0000', 'sent'),
        pytest.param('2016-02-07T19:45:00.922+0000', 'skipped'),
    ],
)
async def test_stq_worker_ttl_message(
        stq_runner, taxi_config, pgsql, mockserver, time, expected_status,
):
    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('TRUNCATE TABLE eats_notifications.notifications;')
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}
    taxi_config.set_values(config_values)

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        assert request.json == {
            'client_id': 'user_id_test',
            'device_id': 'user_device_id_test',
            'intent': 'intent_test',
            'locale': 'locale_test',
            'ttl': 60,
            'notification': {
                'link': 'push_deeplink_test',
                'text': 'Тестовое сообщение',
                'title': 'Тестовый заголовок',
            },
            'data': {
                'client_id': 'user_id_test',
                'timestamp_sent': '2527875900',
                'user_notification_id': 'token_test',
                'deeplink': 'push_deeplink_test',
                'options_values': {},
                'push_tags': ['common'],
            },
            'service': 'service_test',
        }
        return {'notification_id': 'notification_id_test'}

    await stq_runner.eats_notifications_messages.call(
        task_id='test',
        kwargs={
            'user_id': 'user_id_test',
            'service': 'service_test',
            'route': 'eda',
            'transport_type': 1,
            'tanker_keyset': 'notify',
            'options_values': {},
            'intent': 'intent_test',
            'project_key': 'project_key_test',
            'key': 'key_test',
            'sent_at': time,
            'project_id': 1,
            'application_key': 'eda_native',
            'template_id': 1,
            'request': 'request_test',
            'token': 'token_test',
            'sender': 'sender_test',
            'locale': 'locale_test',
            'user_device_id': 'user_device_id_test',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT token, status, project_id, template_id, user_id, application, '
        'user_device_id, notification_params, message_title, message_body, '
        'deeplink, api_response, request, message_id, client_type, sent_at '
        'FROM eats_notifications.notifications',
    )
    notifications = list(cursor)
    assert notifications[0][1] == expected_status


@pytest.mark.translations(
    notify={
        'test_title': {'ru': 'Тестовый заголовок'},
        'push_message_test': {'ru': 'Тестовое сообщение'},
        'sms_message_test': {'ru': 'Тестовое сообщение'},
    },
)
@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.projects (name, key, tanker_project,
        tanker_keyset, intent)
        VALUES ('project_name_test', 'project_key_test', 'tanker_project_test',
        'notify', 'intent_test')
        """,
        """
        INSERT INTO eats_notifications.project2app (project_id, app_key)
        VALUES (1, 'eda_native')
        """,
        """
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 3, 'sent', 0)
        """,
    ],
)
@pytest.mark.parametrize(
    'applications_config, send_request',
    [
        pytest.param(
            {
                'eda_native': {
                    'type': 'type_test',
                    'settings': {'service': 'service_test', 'route': 'go'},
                    'user_identity_name': 'ios_system_option',
                },
            },
            {
                'application': 'eda_native',
                'device_id': 'test_device_id',
                'locale': 'ru',
                'notification_key': 'key',
                'options_values': {
                    'ios_system_option': 'identity_test',
                    'option1': 3,
                },
                'project': 'project_key_test',
                'user_id': 'user_id_test',
            },
            id='stq fail',
        ),
    ],
)
async def test_db_record_after_stq_fail(
        taxi_config,
        taxi_eats_notifications,
        mockserver,
        pgsql,
        load_json,
        applications_config,
        send_request,
):
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_APPLICATIONS_V2'] = applications_config
    taxi_config.set_values(config_values)

    # add notifications
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _mock_fail_stq(request, queue_name):
        return mockserver.make_response(json={}, status=500)

    response = await taxi_eats_notifications.post(
        '/v1/notification', json=send_request,
    )
    assert response.status_code == 200
    assert response.json()['token']

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        """
        SELECT token, status, project_id, template_id, user_id, application,
        user_device_id, notification_params, message_title, message_body,
        deeplink, api_response, request, message_id, client_type, sent_at
        FROM eats_notifications.notifications
        """,
    )

    notifications = cursor.fetchall()
    assert len(notifications) == 1
    notification = notifications[0]
    assert notification[utils.NotificationsFields.status] == 'waiting'
    assert (
        notification[utils.NotificationsFields.token]
        == response.json()['token']
    )
    assert (
        notification[utils.NotificationsFields.notification_params] is not None
    )


@pytest.mark.translations(
    notify={
        'test_title': {'ru': 'Тестовый заголовок'},
        'push_message_test': {'ru': 'Тестовое сообщение'},
        'sms_message_test': {'ru': 'Тестовое сообщение'},
    },
)
@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.projects (name, key, tanker_project,
        tanker_keyset, intent)
        VALUES ('project_name_test', 'project_key_test', 'tanker_project_test',
        'notify', 'intent_test')
        """,
        """
        INSERT INTO eats_notifications.project2app (project_id, app_key)
        VALUES (1, 'eda_native')
        """,
        """
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 3, 'sent', 0)
        """,
    ],
)
@pytest.mark.parametrize(
    'applications_config, send_request',
    [
        pytest.param(
            {
                'eda_native': {
                    'type': 'type_test',
                    'settings': {'service': 'service_test', 'route': 'go'},
                    'user_identity_name': 'ios_system_option',
                },
            },
            {
                'application': 'eda_native',
                'device_id': 'test_device_id',
                'locale': 'ru',
                'notification_key': 'key',
                'options_values': {
                    'ios_system_option': 'identity_test',
                    'option1': 3,
                },
                'project': 'project_key_test',
                'user_id': 'user_id_test',
            },
            id='stq disable',
        ),
    ],
)
async def test_db_record_after_stq_disable(
        taxi_config,
        taxi_eats_notifications,
        mockserver,
        pgsql,
        load_json,
        applications_config,
        send_request,
):
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_APPLICATIONS_V2'] = applications_config
    config_values['EATS_NOTIFICATIONS_DISABLE_STQ'] = True
    taxi_config.set_values(config_values)

    # add notifications
    notification = load_json('notification1.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _mock_stq(request, queue_name):
        assert False  # task should not be sent to stq

    response = await taxi_eats_notifications.post(
        '/v1/notification', json=send_request,
    )
    assert response.status_code == 200
    assert response.json()['token']

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        """
        SELECT token, status, project_id, template_id, user_id, application,
        user_device_id, notification_params, message_title, message_body,
        deeplink, api_response, request, message_id, client_type, sent_at
        FROM eats_notifications.notifications
        """,
    )

    notifications = cursor.fetchall()
    assert len(notifications) == 1
    notification = notifications[0]
    assert notification[utils.NotificationsFields.status] == 'waiting'
    assert (
        notification[utils.NotificationsFields.token]
        == response.json()['token']
    )
    assert (
        notification[utils.NotificationsFields.notification_params] is not None
    )


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.project2app (project_id, app_key)'
        'VALUES (1, \'eda_native\')',
        'INSERT INTO eats_notifications.projects (name, key, tanker_project, '
        'tanker_keyset, intent)'
        'VALUES (\'project\', \'project_key\', \'tanker_project\', '
        '\'tanker_keyset\', \'intent\')',
    ],
)
@pytest.mark.parametrize(
    'options',
    [
        pytest.param({'option_bool': True}, id='bool'),
        pytest.param(
            {'option_bool': False, 'option_str': 'option_string'}, id='string',
        ),
    ],
)
async def test_condition(
        taxi_eats_notifications, load_json, taxi_config, stq, options,
):
    taxi_config.set_values(
        {
            'EATS_NOTIFICATIONS_APPLICATIONS_V2': {
                'eda_native': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': '',
                },
            },
        },
    )

    # add notification
    notification = load_json('notification_with_bool_and_str.json')
    response = await taxi_eats_notifications.post(
        '/v1/admin/notification', json=notification,
    )
    assert response.status_code == 204

    response = await taxi_eats_notifications.post(
        '/v1/notification',
        json={
            'application': 'eda_native',
            'device_id': 'device_id_test',
            'locale': 'ru',
            'notification_key': 'key',
            'options_values': options,
            'project': 'project_key',
            'user_id': 'user_id_test',
        },
    )
    assert response.status_code == 200
    assert response.json()['token']

    assert stq.eats_notifications_messages.times_called == 1

    stq_call = stq.eats_notifications_messages.next_call()
    assert stq_call['queue'] == 'eats_notifications_messages'
    assert stq_call['kwargs']['options_values'] == options
    assert stq_call['kwargs']['push_message'] == 'message'
