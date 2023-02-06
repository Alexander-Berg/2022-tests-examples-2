import pytest


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.projects
        (id, name, key, tanker_project, tanker_keyset)
        VALUES (1, 'name', 'key', 'tanker_project', 'tanker_keyset')
        """,
        """
        INSERT INTO eats_notifications.templates (name, key, project_id,
        transport_type, waiting_condition, ttl)
        VALUES ('template_name_test', 'template_key_test', 1, 3, 'sent', 0)
        """,
    ],
)
@pytest.mark.parametrize(
    'user_type, user_id, expected_user_type, expected_user_id, '
    'transport_type, is_fail, is_push, check_active_device',
    [
        pytest.param(
            'eater_id',
            'test_eater_id',
            'eater_uuid',
            'eater_uuid_test',
            1,
            False,
            True,
            False,
            id='push exchange eater_id to eater_uuid',
        ),
        pytest.param(
            'eater_uuid',
            'test_eater_uuid',
            'eater_id',
            'eater_id_test',
            1,
            False,
            True,
            False,
            id='push exchange eater_uuid to eater_id',
        ),
        pytest.param(
            'magnit_id',
            'test_magnit_id',
            'eater_uuid',
            'test_eater_uuid',
            1,
            True,
            True,
            False,
            id='push fail with magnit_id',
        ),
        pytest.param(
            'eater_id',
            'test_eater_id',
            'eater_uuid',
            'eater_uuid_test',
            2,
            False,
            False,
            False,
            id='sms get phone_id by eater_id',
        ),
        pytest.param(
            'magnit_id',
            'test_magnit_id',
            'eater_uuid',
            'test_eater_uuid',
            2,
            True,
            False,
            False,
            id='sms fail with magnit_id',
        ),
        pytest.param(
            'eater_id',
            'test_eater_id',
            'eater_uuid',
            'eater_uuid_test',
            1,
            False,
            True,
            True,
            marks=(
                pytest.mark.pgsql(
                    'eats_notifications',
                    queries=[
                        """
                        INSERT INTO eats_notifications.user_devices
                        (id, user_id, auth_token, active, os, os_version,
                        app_version, model, device_id, brand, code_version,
                        push_enabled, appmetrica_uuid, registered)
                        VALUES (1, 'test_eater_id', 'x_taxi_session_value',
                        TRUE, 'os_test', 'os_version_test',
                        'app_version_test', 'model_test',
                        'user_device_id_test', 'brand_test',
                        'code_version_test', TRUE, 'appmetrica_uuid_test',
                        TRUE)
                        """,
                        """
                        INSERT INTO eats_notifications.user_device_tokens
                        (user_device_id, type, token, is_registered)
                        VALUES(1, 'apns', 'token_ios', true)
                        """,
                        """
                        INSERT INTO eats_notifications.eaters(
                        eater_id, eater_uuid, push_tag_bitset)
                        VALUES('test_eater_id', 'eater_uuid_test', 3)
                        """,
                    ],
                ),
            ),
            id='push eater_id check active device',
        ),
    ],
)
async def test_user_id_exchange(
        taxi_config,
        stq_runner,
        mockserver,
        user_type,
        user_id,
        expected_user_type,
        expected_user_id,
        transport_type,
        is_fail,
        is_push,
        check_active_device,
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
                    'user_type': expected_user_type,
                    'check_active_device': check_active_device,
                },
            },
        },
    )

    @mockserver.json_handler('client-notify/v2/push')
    def _mock_push(request):
        assert request.json['client_id'] == expected_user_id
        assert not is_fail
        return mockserver.make_response(
            status=200, json={'notification_id': 'notification_id_test'},
        )

    @mockserver.json_handler('/ucommunications/general/sms/send')
    def _mock_sms(request):
        if is_fail:
            return mockserver.make_response(
                status=500,
                json={'message_id': '', 'message': 'Error', 'code': '500'},
            )
        assert request.json['phone_id'] == 'personal_phone_id'
        return mockserver.make_response(
            status=200,
            json={
                'message_id': 'notification_id_test',
                'message': 'OK',
                'content': 'Test message',
                'code': '200',
            },
        )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters_by_id(request):
        assert user_type == 'eater_id'
        assert not is_fail
        return {
            'eater': {
                'id': request.json['id'],
                'uuid': expected_user_id,
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': 'personal_phone_id',
            },
        }

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-uuid')
    def _mock_eaters(request):
        return {
            'eater': {
                'id': expected_user_id,
                'uuid': request.json['uuid'],
                'created_at': '2050-02-07T19:45:00.922+0000',
                'updated_at': '2050-02-07T19:45:00.922+0000',
                'personal_phone_id': 'personal_phone_id',
            },
        }

    await stq_runner.eats_notifications_messages.call(
        task_id='test',
        kwargs={
            'token': 'test',
            'user_id': user_id,
            'user_type': user_type,
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
            'user_device_id': 'user_device_id_test',
            'sms_message': 'sms_message_test',
            'push_title': 'test_title',
            'push_message': 'push_message_test',
            'push_deeplink': 'push_deeplink_test',
            'waiting_condition': 'sent',
            'ttl': 0,
        },
        expect_fail=is_fail,
    )

    if not is_fail:
        if is_push:
            assert _mock_push.times_called == 1
        else:
            assert _mock_sms.times_called == 1
