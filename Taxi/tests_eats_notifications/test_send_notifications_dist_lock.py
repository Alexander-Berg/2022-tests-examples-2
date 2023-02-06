import json

import pytest

import tests_eats_notifications.utils as utils


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
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 3, 'sent', 0)
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
async def test_post_with_stq_fail(
        taxi_eats_notifications_monitor,
        taxi_eats_notifications,
        taxi_config,
        mockserver,
        pgsql,
):

    notification_rec = json.dumps(
        {
            'token': 'token_test',
            'user_id': 'user_id_test',
            'service': 'service_test',
            'route': 'eda',
            'transport_type': 3,
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
            'locale': 'ru',
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
        """
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, notification_params, message_title,
        message_body, sent_at)
        VALUES ('token_test', 'waiting', 1, 1, (%s), '', '',
        '2050-02-07T19:45:00.922+0000')
        """,
        (notification_rec,),
    )

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        assert request.json == {
            'client_id': 'user_id_test',
            'device_id': 'user_device_id_test',
            'intent': 'intent_test',
            'locale': 'ru',
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
                'options_values': {'option_bool': True, 'option_int': 3},
                'push_tags': ['common'],
            },
            'service': 'service_test',
        }
        return {'notification_id': 'notification_id'}

    @mockserver.json_handler('ucommunications/user/sms/send')
    def _mock_user_sms_send(request):
        assert request.json == {}
        return {'message': '', 'code': '200'}

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_general_sms_send(request):
        assert request.json == {}
        return {'message': '', 'code': '200'}

    await taxi_eats_notifications.run_task('send-notifications-dist-lock')

    metric = await taxi_eats_notifications_monitor.get_metric(
        'eats-notifications-have-unsent-notification',
    )
    assert metric == 1

    cursor.execute(
        """
        SELECT token, status, project_id, template_id, user_id, application,
        user_device_id, notification_params, message_title, message_body,
        deeplink, api_response, request, message_id, client_type, sent_at,
        sent_transport_type
        FROM eats_notifications.notifications
        """,
    )

    notifications = list(cursor)

    for notification in notifications:
        assert notification[utils.NotificationsFields.status] == 'sent'
        assert (
            notification[utils.NotificationsFields.sent_transport_type]
            == 'push'
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
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 3, 'sent', 0)
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
async def test_dont_send_in_processing(
        taxi_eats_notifications_monitor,
        taxi_eats_notifications,
        taxi_config,
        mockserver,
        pgsql,
):

    notification_rec = json.dumps(
        {
            'token': 'token_test',
            'user_id': 'user_id_test',
            'service': 'service_test',
            'route': 'eda',
            'transport_type': 3,
            'tanker_keyset': 'notify',
            'options_values': {'option_bool': True, 'option_int': 3},
            'intent': 'intent_test',
            'project_key': 'project_key_test',
            'key': 'key_test',
            'sent_at': '2050-02-07T19:45:00.922+0000',
            'project_id': 1,
            'application_key': 'application_key_test',
            'template_id': 1,
            'request': 'request_test',
            'sender': 'sender_test',
            'locale': 'ru',
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
        """
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, notification_params, message_title,
        message_body, sent_at)
        VALUES ('token_test', 'processing', 1, 1, (%s), '', '',
        '2050-02-07T19:45:00.922+0000')
        """,
        (notification_rec,),
    )
    cursor.execute(
        """
        INSERT INTO eats_notifications.notifications (token, status,
        project_id, template_id, notification_params, message_title,
        message_body, sent_at)
        VALUES ('token_test_2', 'processing', 1, 1, (%s), '', '',
        '2050-02-07T19:45:00.922+0000')
        """,
        (notification_rec,),
    )

    await taxi_eats_notifications.run_task('send-notifications-dist-lock')

    metric = await taxi_eats_notifications_monitor.get_metric(
        'eats-notifications-have-unsent-notification',
    )
    assert metric == 1

    cursor.execute(
        """
        SELECT token, status, project_id, template_id, user_id, application,
        user_device_id, notification_params, message_title, message_body,
        deeplink, api_response, request, message_id, client_type, sent_at,
        sent_transport_type
        FROM eats_notifications.notifications
        """,
    )

    notifications = list(cursor)

    assert notifications[0][utils.NotificationsFields.status] == 'processing'
