import pytest

SERVICE = 'service-name'
IOS_APP_NAME = 'ios-app'
ANDROID_APP_NAME = 'android-app'

CONFIG = {
    'eda_native': {
        'type': 'xiva',
        'xiva_settings': {
            'ios': {'app_name': IOS_APP_NAME, 'service': 'eda-client'},
            'android': {'app_name': ANDROID_APP_NAME, 'service': 'eda-client'},
        },
        'settings': {'service': SERVICE, 'route': 'eda'},
        'user_identity_name': 'eater_id',
    },
}


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices(
            user_id, auth_token, active, device_id, registered,
            push_enabled)
        VALUES('228', 'auth_token', TRUE, 'device_id', TRUE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens(
            user_device_id, type, token, is_registered)
        VALUES(1, 'apns', 'token_ios', true)
        """,
        """
        INSERT INTO eats_notifications.user_devices(
            user_id, auth_token, active, device_id, registered,
            push_enabled)
        VALUES('228', 'auth_token', TRUE, 'device_id2', TRUE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens(
            user_device_id, type, token, is_registered)
        VALUES(2, 'fcm', 'token_android', true)
        """,
        """
        INSERT INTO eats_notifications.eaters(
            eater_id, eater_uuid, push_tag_bitset)
        VALUES(228, 'uuid', 3)
        """,
    ],
)
@pytest.mark.parametrize(
    'os_name, app_name, device_id, token_type, token',
    [
        pytest.param('ios', IOS_APP_NAME, 'device_id', 'apns', 'token_ios'),
        pytest.param(
            'android', ANDROID_APP_NAME, 'device_id2', 'fcm', 'token_android',
        ),
    ],
)
async def test_success_with_eater_in_local_db(
        mockserver,
        taxi_config,
        stq_runner,
        os_name,
        app_name,
        device_id,
        token_type,
        token,
):

    taxi_config.set_values({'EATS_NOTIFICATIONS_APPLICATIONS_V2': CONFIG})

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        assert request.json['service'] == SERVICE
        assert request.json['client'] == {
            'device_type': os_name,
            'app_name': app_name,
            'device_id': device_id,
            'client_id': 'uuid',
        }
        assert request.json['channel'] == {'name': token_type, 'token': token}
        assert request.json['push_settings'] == {
            'enabled_by_system': True,
            'included_tags': [],
            'excluded_tags': ['marketing'],
        }
        return {}

    await stq_runner.eats_notifications_subscriptions.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'eater_id': '228',
            'device_id': device_id,
            'push_tag_bitset': 1,
        },
    )


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices(
            user_id, auth_token, active, device_id, registered,
            push_enabled)
        VALUES('1488', 'auth_token', TRUE, 'device_id', TRUE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens(
            user_device_id, type, token, is_registered)
        VALUES(1, 'apns', 'token_ios', true)
        """,
    ],
)
async def test_success_with_eats_eaters_fallback(
        mockserver, taxi_config, stq_runner,
):

    taxi_config.set_values({'EATS_NOTIFICATIONS_APPLICATIONS_V2': CONFIG})

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        assert request.json['client']['client_id'] == '1488_uuid'
        return {}

    @mockserver.json_handler('eats-eaters/v1/eaters/find-by-id')
    def _mock_eaters(request):
        assert request.json['id'] == '1488'
        return {
            'eater': {
                'id': '1488',
                'uuid': '1488_uuid',
                'created_at': '2019-12-31T10:59:59+03:00',
                'updated_at': '2019-12-31T10:59:59+03:00',
            },
        }

    await stq_runner.eats_notifications_subscriptions.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'eater_id': '1488',
            'device_id': 'device_id',
            'push_tag_bitset': 1,
        },
    )


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices(
            user_id, auth_token, active, device_id, registered,
            push_enabled)
        VALUES('228', 'auth_token', TRUE, 'device_id', FALSE, TRUE)
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens(
            user_device_id, type, token, is_registered, updated_at)
        VALUES
        (1, 'apns', 'token_ios_old', true, '2019-01-01 00:00:00+0000'),
        (1, 'apns', 'token_ios', true, '2021-01-01 00:00:00+0000')
        """,
        """
        INSERT INTO eats_notifications.eaters(
            eater_id, eater_uuid, push_tag_bitset)
        VALUES(228, 'uuid', 3)
        """,
    ],
)
@pytest.mark.parametrize(
    'os_name, app_name, device_id, token_type, token',
    [pytest.param('ios', IOS_APP_NAME, 'device_id', 'apns', 'token_ios')],
)
async def test_tokens_order_by_updated_at(
        mockserver,
        taxi_config,
        stq_runner,
        os_name,
        app_name,
        device_id,
        token_type,
        token,
):

    taxi_config.set_values({'EATS_NOTIFICATIONS_APPLICATIONS_V2': CONFIG})

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        assert request.json['channel'] == {'name': token_type, 'token': token}
        return {}

    await stq_runner.eats_notifications_subscriptions.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'eater_id': '228',
            'device_id': device_id,
            'push_tag_bitset': 1,
        },
    )
    assert _mock_subscribe.times_called == 1
