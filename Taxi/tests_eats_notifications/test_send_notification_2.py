import pytest


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
    'applications_config, response_code',
    [
        pytest.param(
            {
                'eda_native': {
                    'type': 'test',
                    'settings': {
                        'service': 'test',
                        'route': 'eda',
                        'app_host': 'yandex',
                    },
                    'user_identity_name': '',
                    'aliases': ['eda_android', 'eda_android228'],
                },
            },
            200,
        ),
        pytest.param(
            {
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
            400,
        ),
    ],
)
async def test_application_aliases(
        taxi_eats_notifications,
        load_json,
        taxi_config,
        applications_config,
        response_code,
):
    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
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
            'application': 'eda_android',
            'device_id': 'device_id_test',
            'locale': 'ru',
            'notification_key': 'key',
            'options_values': {'option_bool': True},
            'project': 'project_key',
            'user_id': 'user_id_test',
        },
    )
    assert response.status_code == response_code


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
@pytest.mark.config(
    EATS_NOTIFICATIONS_HISTORY_TAGS={
        'regular': ['city', 'country', 'group_id'],
        'sensitive': ['order_id', 'user_id'],
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
    'tags, expected_tags',
    [
        pytest.param(
            [
                {'key': 'order_id', 'value': 'order_id_1'},
                {'key': 'user_id', 'value': 'user_id_1'},
                {'key': 'country', 'value': 'ru'},
                {'key': 'orderNr', 'value': 'orderNr_not_allowed'},
            ],
            [
                ('order_id', 'order_id_1', 'token_test'),
                ('user_id', 'user_id_1', 'token_test'),
                ('country', 'ru', 'token_test'),
            ],
            id='filter_tags',
        ),
        pytest.param([], [], id='empty_tags'),
        pytest.param(
            [
                {'key': 'group_id', 'value': 'group_id_1'},
                {'key': 'group_id', 'value': 'group_id_2'},
            ],
            [
                ('group_id', 'group_id_1', 'token_test'),
                ('group_id', 'group_id_2', 'token_test'),
            ],
            id='double_key',
        ),
        pytest.param(
            [
                {'key': 'not_allowed_key_1', 'value': 'any'},
                {'key': 'not_allowed_key_2', 'value': 'any'},
            ],
            [],
            id='not_allowed_keys',
        ),
    ],
)
async def test_history_tags(
        stq_runner, pgsql, mockserver, tags, expected_tags,
):
    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        return mockserver.make_response(
            status=200, json={'notification_id': 'notification_id_test'},
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
            'user_device_id': 'device_id_test',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
            'tags': tags,
        },
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT key, value, notification_token '
        'FROM eats_notifications.notifications_tags',
    )
    tags = list(cursor)
    assert sorted(tags) == sorted(expected_tags)


TEST_LOCALE_TRANSLATIONS = {
    'test_title': {'ru': 'Тестовый заголовок', 'en': 'Test title'},
    'push_message_test': {'ru': 'Тестовое сообщение', 'en': 'Test message'},
    'sms_message_test': {'ru': 'Тестовое сообщение', 'en': 'Test message'},
}


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
@pytest.mark.translations(notify=TEST_LOCALE_TRANSLATIONS)
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
        TRUE, TRUE)
        """,
    ],
)
@pytest.mark.parametrize(
    'locale',
    [
        pytest.param(
            'ru',
            marks=pytest.mark.pgsql(
                'eats_notifications',
                queries=[
                    """
                    INSERT INTO eats_notifications.locale
                    (eater_id, device_id, locale, updated_at)
                    VALUES
                    ('user_id', 'device_id_test',
                    'ru', '2021-08-28T18:00:00+00:00')
                    """,
                ],
            ),
        ),
        pytest.param(
            'en',
            marks=pytest.mark.pgsql(
                'eats_notifications',
                queries=[
                    """
                    INSERT INTO eats_notifications.locale
                    (eater_id, device_id, locale, updated_at)
                    VALUES
                    ('user_id', 'device_id_test',
                    'en', '2021-08-28T18:00:00+00:00')
                    """,
                ],
            ),
        ),
    ],
)
async def test_locale(stq_runner, pgsql, mockserver, locale):
    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        assert (
            request.json['notification']['title']
            == TEST_LOCALE_TRANSLATIONS['test_title'][locale]
        )
        assert (
            request.json['notification']['text']
            == TEST_LOCALE_TRANSLATIONS['push_message_test'][locale]
        )

        return mockserver.make_response(
            status=200, json={'notification_id': 'notification_id_test'},
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters_by_uuid(request):
        return {
            'eater': {
                'id': request.json['id'],
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
            'user_type': 'eater_id',
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
        """
        SELECT message_title, message_body
        FROM eats_notifications.notifications
        """,
    )
    notifications = list(cursor)
    assert len(notifications) == 1
    row = notifications[0]

    assert row[0] == TEST_LOCALE_TRANSLATIONS['test_title'][locale]
    assert row[1] == TEST_LOCALE_TRANSLATIONS['push_message_test'][locale]
