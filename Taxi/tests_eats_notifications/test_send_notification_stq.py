import pytest


def _get_app_config(check_active_device=False, duplicate_with_sms=False):
    return {
        'eda_native': {
            'type': 'test',
            'settings': {
                'service': 'test',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': 'ios_system_option',
            'check_active_device': check_active_device,
            'duplicate_with_sms': duplicate_with_sms,
        },
    }


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
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id', 'device_id_test', 1)
        """,
        """
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id_1', 'device_id_test_1', 1)
        """,
        """
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id_2', 'device_id_test_2', 1)
        """,
        """
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id_3', 'device_id_test_3', 1)
        """,
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
        (\'user_id\', \'test\', TRUE, \'device_id_test\',
        TRUE, FALSE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id_1\', \'test\', TRUE, \'device_id_test_1\',
        FALSE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id_2\', \'test\', FALSE, \'device_id_test_2\',
        TRUE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled, device_type)
        VALUES
        (\'user_id_3\', \'test\', TRUE, \'device_id_test_3\',
        TRUE, TRUE, \'eda_web\')
        """,
    ],
)
@pytest.mark.parametrize(
    'device_id',
    [
        pytest.param('device_id_test'),
        pytest.param('device_id_test_1'),
        pytest.param('device_id_test_2'),
        pytest.param('device_id_test_3'),
    ],
)
@pytest.mark.parametrize(
    'check_active_device_on',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_NOTIFICATIONS_APPLICATIONS_V2=_get_app_config(
                    check_active_device=True,
                ),
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_NOTIFICATIONS_APPLICATIONS_V2=_get_app_config(
                    check_active_device=False,
                ),
            ),
        ),
    ],
)
async def test_check_active_device(
        stq_runner,
        taxi_config,
        mockserver,
        pgsql,
        device_id,
        check_active_device_on,
):
    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('TRUNCATE TABLE eats_notifications.notifications;')
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return mockserver.make_response(
            status=200, json={'notification_id': 'notification_id_test'},
        )

    await stq_runner.eats_notifications_messages.call(
        task_id=device_id,
        expect_fail=False,
        kwargs={
            'user_id': device_id,
            'service': 'service_test',
            'route': 'eda',
            'transport_type': 1,
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
            'locale': 'locale_test',
            'user_device_id': device_id,
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )

    if check_active_device_on:
        assert _mock_push.times_called == 0
    else:
        assert _mock_push.times_called == 1


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
        (\'user_id1\', \'test\', TRUE, \'device_id_test\',
        TRUE, FALSE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id2\', \'test\', TRUE, \'device_id_test_1\',
        FALSE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id3\', \'test\', FALSE, \'device_id_test_2\',
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
            'check_active_device': True,
        },
    },
)
@pytest.mark.parametrize(
    'eater_id',
    [
        pytest.param('user_id1'),
        pytest.param('user_id2'),
        pytest.param('user_id3'),
    ],
)
async def test_check_active_device_true_sms(
        stq_runner, taxi_config, mockserver, pgsql, eater_id,
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
        assert False

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        assert True
        return mockserver.make_response(status=500, json={})

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters(request):
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
        expect_fail=True,
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
            'locale': 'locale_test',
            'user_device_id': 'user_device_id',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id', 'user_id', 3)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id\', \'token_test\', TRUE, \'user_device_id\',
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
            'check_active_device': True,
        },
    },
)
@pytest.mark.parametrize('eater_id', [pytest.param('user_id')])
async def test_duplicate(
        stq_runner,
        taxi_config,
        mockserver,
        taxi_eats_notifications_monitor,
        get_single_metric_by_label_values,
        eater_id,
):
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}

    taxi_config.set_values(config_values)

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return mockserver.make_response(status=409, json={})

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        assert False

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters(request):
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
            'locale': 'locale_test',
            'user_device_id': 'user_device_id',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )

    metric = await get_single_metric_by_label_values(
        taxi_eats_notifications_monitor,
        sensor='notification_event_send_count',
        labels={'type': 'client_notify', 'status': 'duplicate'},
    )
    assert metric.value == 1


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id', 'user_id', 3)
        """,
        """
        INSERT INTO eats_notifications.user_devices
        (user_id, auth_token, active, device_id,
        registered, push_enabled)
        VALUES
        (\'user_id\', \'token_test\', TRUE, \'user_device_id\',
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
            'check_active_device': True,
        },
    },
)
@pytest.mark.parametrize(
    'push_response_code, sms_response_code, transport_type, expect_fail',
    [
        pytest.param(500, None, 1, True),  # fails because can't send
        pytest.param(500, 500, 3, True),  # fails because can't send
        pytest.param(500, 200, 3, False),  # not fails because sms is sent
        pytest.param(409, None, 1, False),  # not fails because duplicated push
        pytest.param(
            409, None, 3, False,
        ),  # not fails because duplicated push, no attempt to send sms
        pytest.param(200, None, 3, False),  # not fails because push is sent
    ],
)
async def test_stq_status(
        stq_runner,
        taxi_config,
        mockserver,
        taxi_eats_notifications_monitor,
        get_single_metric_by_label_values,
        push_response_code,
        sms_response_code,
        transport_type,
        expect_fail,
):
    eater_id = 'user_id'
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}

    taxi_config.set_values(config_values)

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return mockserver.make_response(
            status=push_response_code, json={'notification_id': 'id'},
        )

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        assert transport_type == 3
        return mockserver.make_response(
            status=sms_response_code, json={'message': 'msg', 'code': 'code'},
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters(request):
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
        expect_fail=expect_fail,
        kwargs={
            'user_id': eater_id,
            'service': 'service_test',
            'route': 'eda',
            'transport_type': transport_type,
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
            'locale': 'locale_test',
            'user_device_id': 'user_device_id',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
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
        INSERT INTO eats_notifications.eaters(
        eater_id, eater_uuid, push_tag_bitset)
        VALUES('user_id', 'uuid_test', 1)
        """,
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
        (\'user_id\', \'test\', TRUE, \'device_id_test\',
        TRUE, FALSE)
        """,
    ],
)
@pytest.mark.parametrize(
    'duplicate_with_sms',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_NOTIFICATIONS_APPLICATIONS_V2=_get_app_config(
                    duplicate_with_sms=True,
                ),
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                EATS_NOTIFICATIONS_APPLICATIONS_V2=_get_app_config(
                    duplicate_with_sms=False,
                ),
            ),
        ),
    ],
)
async def test_duplicate_with_sms(
        stq_runner, taxi_config, mockserver, pgsql, duplicate_with_sms,
):
    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('TRUNCATE TABLE eats_notifications.notifications;')
    config_values = taxi_config.get_values()
    config_values['EATS_NOTIFICATIONS_NOTIFICATION_RETRY_SETTINGS'][
        'project'
    ] = {'ttl': 10, 'attempts': 3}

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return mockserver.make_response(
            status=200, json={'notification_id': 'notification_id_test'},
        )

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        return mockserver.make_response(
            status=200,
            json={
                'message_id': 'notification_id_test',
                'message': 'OK',
                'content': 'Test message',
                'code': '200',
            },
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters_by_uuid(request):
        return {
            'eater': {
                'id': request.json['uuid'],
                'uuid': 'uuid_test',
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': 'personal_phone_id',
            },
        }

    await stq_runner.eats_notifications_messages.call(
        task_id='idempotency_token',
        expect_fail=False,
        kwargs={
            'user_id': 'user_id',
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
            'locale': 'locale_test',
            'user_device_id': 'device_id_test',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
    )

    assert _mock_push.times_called == 1

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT sent_transport_type from eats_notifications.notifications',
    )
    notification = list(cursor)
    assert len(notification) == 1

    if duplicate_with_sms:
        assert _mock_sms.times_called == 1
        assert notification[0][0] == 'sms'
    else:
        assert _mock_sms.times_called == 0
        assert notification[0][0] == 'push'
