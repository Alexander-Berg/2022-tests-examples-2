import pytest

DEVICE_ID = 'device_id_1'
EATER_ID = 'eater_id_1'
EATER_UUID = 'eater_uuid_1'
APPLICATION_KEY = 'eda_native'


@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        APPLICATION_KEY: {
            'type': 'xiva',
            'settings': {
                'service': 'eda-client',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': EATER_ID,
            'check_active_device': True,
            'user_type': 'eater_uuid',
        },
    },
)
async def test_view(
        taxi_eats_notifications, stq, pgsql, mockserver, taxi_config,
):
    headers = {
        'x-device-id': DEVICE_ID,
        'X-Eats-User': f'user_id={EATER_ID},eater_uuid={EATER_UUID}',
    }
    body = {'application': APPLICATION_KEY}
    response = await taxi_eats_notifications.post(
        '/v1/unsubscribe', json=body, headers=headers,
    )

    assert response.status_code == 204
    assert stq.eats_notifications_unsubscribe.times_called == 1

    stq_args_expected = {
        'eater_uuid': EATER_UUID,
        'eater_id': EATER_ID,
        'device_id': DEVICE_ID,
        'application_key': APPLICATION_KEY,
    }
    stq_args = stq.eats_notifications_unsubscribe.next_call()['kwargs']
    for key, val in stq_args_expected.items():
        assert stq_args[key] == val


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        f"""
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, registered,
         os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (1, '{EATER_ID}', 'x_taxi_session_value', TRUE, TRUE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        '{DEVICE_ID}', 'brand_test', 'code_version_test', TRUE,
        'appmetrica_uuid_test')
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens
        (user_device_id, type, token, is_registered)
        VALUES(1, 'apns', 'token_ios', true)
        """,
    ],
)
@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        APPLICATION_KEY: {
            'type': 'xiva',
            'settings': {
                'service': 'eda-client',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': EATER_ID,
            'check_active_device': True,
            'user_type': 'eater_uuid',
        },
    },
)
async def test_stq(
        taxi_eats_notifications,
        stq,
        stq_runner,
        pgsql,
        mockserver,
        taxi_config,
):
    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        config_values = taxi_config.get_values()
        applications_config = config_values[
            'EATS_NOTIFICATIONS_APPLICATIONS_V2'
        ]
        assert request.json == {
            'service': applications_config[APPLICATION_KEY]['settings'][
                'service'
            ],
            'client': {'client_id': EATER_UUID, 'device_id': DEVICE_ID},
            'channel': {'name': 'apns'},
        }
        return {}

    stq_args = {
        'eater_uuid': EATER_UUID,
        'eater_id': EATER_ID,
        'device_id': DEVICE_ID,
        'application_key': APPLICATION_KEY,
    }

    await stq_runner.eats_notifications_unsubscribe.call(
        task_id='task_id', expect_fail=False, kwargs=stq_args,
    )

    assert _mock_unsubscribe.times_called == 1

    cursor = pgsql['eats_notifications'].cursor()

    cursor.execute(
        'SELECT active, registered ' 'FROM eats_notifications.user_devices',
    )
    devices = list(cursor)
    assert not devices[0][0]  # not active
    assert not devices[0][1]  # not registered

    cursor.execute(
        'SELECT is_registered FROM eats_notifications.user_device_tokens',
    )
    tokens = list(cursor)
    assert not tokens[0][0]  # not registered


@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        APPLICATION_KEY: {
            'type': 'xiva',
            'settings': {
                'service': 'eda-client',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': EATER_ID,
            'check_active_device': True,
            'user_type': 'eater_uuid',
        },
    },
)
async def test_stq_not_found_device(
        taxi_eats_notifications, stq_runner, mockserver,
):
    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        return {}

    stq_args = {
        'eater_uuid': EATER_UUID,
        'eater_id': EATER_ID,
        'device_id': DEVICE_ID,
        'application_key': APPLICATION_KEY,
    }

    await stq_runner.eats_notifications_unsubscribe.call(
        task_id='task_id', expect_fail=False, kwargs=stq_args,
    )

    assert _mock_unsubscribe.times_called == 0


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        f"""
        INSERT INTO eats_notifications.user_devices
        (id, user_id, auth_token, active, registered,
         os, os_version, app_version, model,
        device_id, brand, code_version, push_enabled, appmetrica_uuid)
        VALUES (1, '{EATER_ID}', 'x_taxi_session_value', TRUE, TRUE, 'os_test',
        'os_version_test', 'app_version_test', 'model_test',
        '{DEVICE_ID}', 'brand_test', 'code_version_test', TRUE,
        'appmetrica_uuid_test')
        """,
    ],
)
@pytest.mark.config(
    EATS_NOTIFICATIONS_APPLICATIONS_V2={
        APPLICATION_KEY: {
            'type': 'xiva',
            'settings': {
                'service': 'eda-client',
                'route': 'eda',
                'app_host': 'yandex',
            },
            'user_identity_name': EATER_ID,
            'check_active_device': True,
            'user_type': 'eater_uuid',
        },
    },
)
async def test_stq_not_found_token(
        taxi_eats_notifications, stq_runner, mockserver,
):
    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        return {}

    stq_args = {
        'eater_uuid': EATER_UUID,
        'eater_id': EATER_ID,
        'device_id': DEVICE_ID,
        'application_key': APPLICATION_KEY,
    }

    await stq_runner.eats_notifications_unsubscribe.call(
        task_id='task_id', expect_fail=False, kwargs=stq_args,
    )

    assert _mock_unsubscribe.times_called == 1
