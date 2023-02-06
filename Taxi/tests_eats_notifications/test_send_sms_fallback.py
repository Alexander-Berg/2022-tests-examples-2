import pytest


# Логика теста:
# Проверяем, что нельзя послать пуш, потому что
# у пользователя нет активных девайсов
# и пытаемся отправить смс.
# Проверяем, что метрики правильные, то есть кол-во
# скипнутых пушей = кол-во отправленных смс = 1.
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
        VALUES ('project_name_test', 'project_key_test',
        'tanker_project_test', 'notify', 'intent_test')
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
        (\'user_id1\', \'test\', FALSE, \'device_id_test\',
        FALSE, FALSE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id2\', \'test\', FALSE, \'device_id_test_1\',
        FALSE, FALSE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id3\', \'test\', FALSE, \'device_id_test_2\',
        FALSE, FALSE)
        """,
    ],
)
@pytest.mark.parametrize(
    'eater_id, phone, is_fallback',
    [
        pytest.param('user_id1', 'phone1', False),
        pytest.param('user_id2', 'phone1', False),
        pytest.param('user_id3', None, False),
    ],
)
async def test_fallback_sms(
        taxi_eats_notifications_monitor,
        taxi_eats_notifications,
        stq_runner,
        taxi_config,
        mockserver,
        pgsql,
        eater_id,
        phone,
        is_fallback,
):
    await taxi_eats_notifications.tests_control(reset_metrics=True)

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('TRUNCATE TABLE eats_notifications.notifications;')
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}

    taxi_config.set_values(config_values)

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return {}

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        return mockserver.make_response(
            status=200, json={'message': 'message', 'code': 'code'},
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters_uuid(request):
        if is_fallback:
            return mockserver.make_response(status=500, json={})

        return {
            'eater': {
                'id': 'test_id',
                'uuid': 'test_uuid',
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': phone,
            },
        }

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters(request):
        assert is_fallback
        return {
            'eater': {
                'id': 'test_id',
                'uuid': 'test_uuid',
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': 'dd',
            },
        }

    await stq_runner.eats_notifications_messages.call(
        task_id=eater_id,
        expect_fail=False,
        kwargs={
            'user_id': eater_id,
            'service': 'service_test',
            'route': 'eda',
            'transport_type': 3,
            'tanker_keyset': 'notify',
            'options_values': {},
            'intent': 'intent_test',
            'project_key': 'project_key_test',
            'key': 'key_test',
            'sent_at': '2050-02-07T19:45:00.922+0000',
            'project_id': 1,
            'application_key': 'eda_native',
            'template_id': 1,
            'request': 'request_test',
            'token': 'token_test',
            'sender': 'sender_test',
            'locale': 'ru',
            'user_device_id': 'user_device_id',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )

    assert _mock_sms.times_called == 1
    assert _mock_push.times_called == 0

    metrics = await taxi_eats_notifications_monitor.get_metric(
        'notification_event_send_count',
    )

    transport_metrics = metrics['project_key_test']['eda_native']['key_test']
    assert (
        transport_metrics['client_notify']['skipped']
        == transport_metrics['ucommunications']['success']
        == 1
    )
