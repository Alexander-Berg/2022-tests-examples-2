import pytest


@pytest.mark.parametrize(
    'stq_params, eaters_response, applications_config',
    [
        pytest.param(
            {
                'user_id': 'eater_id',
                'device_id': 'device_id_value1',
                'subscription': {
                    'endpoint': (
                        'https://fcm.googleapis.com/fcm/subscription-id'
                    ),
                    'keys': {
                        'auth': 'Kdascewc123DSadasd',
                        'p256dh': 'safas12casc-ascasx-123da',
                    },
                },
                'auth_token': 'eats:12345',
                'locale': 'en',
            },
            {
                'eater': {
                    'id': 'eater_id',
                    'uuid': 'eater_uuid',
                    'created_at': '2018-01-01T10:59:59+03:00',
                    'updated_at': '2018-01-01T10:59:59+03:00',
                },
            },
            {
                'eda_web': {
                    'type': 'xiva',
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='webpush',
        ),
    ],
)
async def test_success_save_device_web(
        taxi_config,
        mockserver,
        pgsql,
        stq_runner,
        stq_params,
        eaters_response,
        applications_config,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_find(request):
        assert request.json['id'] == 'eater_id'
        return eaters_response

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        assert request.json == {
            'service': applications_config['eda_web']['settings']['service'],
            'client': {
                'client_id': eaters_response['eater']['uuid'],
                'device_type': 'web',
                'session_id': stq_params['device_id'],
                'app_name': 'eda.web',
            },
            'channel': {'name': 'webpush'},
            'subscription': {
                'endpoint': stq_params['subscription']['endpoint'],
                'keys': {
                    'auth': stq_params['subscription']['keys']['auth'],
                    'p256dh': stq_params['subscription']['keys']['p256dh'],
                },
            },
        }
        return {}

    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    await stq_runner.eats_notifications_save_device_web.call(
        task_id='task_id', expect_fail=False, kwargs=stq_params,
    )

    assert _mock_subscribe.times_called == 1

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT ud.user_id, ud.auth_token, ud.active,'
        'ud.device_id,'
        'ud.push_enabled, eater.eater_uuid, ud.registered, '
        'eater.push_tag_bitset, ud.device_type '
        'FROM eats_notifications.user_devices ud '
        'JOIN eats_notifications.eaters eater ON eater.eater_id = ud.user_id '
        'WHERE ud.device_id = \'{}\''.format(stq_params['device_id']),
    )

    user_devices = list(cursor)
    assert user_devices

    device = user_devices[0]

    assert device[0] == stq_params['user_id']
    assert device[1] == stq_params['auth_token']
    assert device[2] is True  # is active
    assert device[3] == stq_params['device_id']
    assert device[4]  # push_enabled
    assert device[5] == eaters_response['eater']['uuid']
    assert device[6]  # is registered
    assert device[7] == 3  # push_tag_bitset
    assert device[8] == 'eda_web'

    cursor.execute(
        """
        SELECT eater_id, device_id, locale
        FROM eats_notifications.locale
        """,
    )

    locale = list(cursor)[0]
    assert locale[0] == stq_params['user_id']
    assert locale[1] == stq_params['device_id']
    assert locale[2] == stq_params['locale']


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.user_devices '
        '(user_id, auth_token, active, device_id) '
        'VALUES (\'eater_id_2\', \'test\', TRUE, \'device_id_value1\')',
        'INSERT INTO eats_notifications.eaters '
        '(eater_id, eater_uuid) '
        'VALUES (\'eater_id_2\', \'eater_uuid_2\')',
    ],
)
@pytest.mark.parametrize(
    'stq_params, eaters_response, applications_config',
    [
        pytest.param(
            {
                'user_id': 'eater_id_1',
                'device_id': 'device_id_value1',
                'subscription': {
                    'endpoint': (
                        'https://fcm.googleapis.com/fcm/subscription-id'
                    ),
                    'keys': {
                        'auth': 'Kdascewc123DSadasd',
                        'p256dh': 'safas12casc-ascasx-123da',
                    },
                },
                'auth_token': 'eats:12345',
            },
            {
                'eater': {
                    'id': 'eater_id_1',
                    'uuid': 'eater_uuid_1',
                    'created_at': '2018-01-01T10:59:59+03:00',
                    'updated_at': '2018-01-01T10:59:59+03:00',
                },
            },
            {
                'eda_web': {
                    'type': 'xiva',
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='webpush',
        ),
    ],
)
async def test_deactivate_other_web_devices(
        taxi_config,
        mockserver,
        pgsql,
        stq_runner,
        stq_params,
        eaters_response,
        applications_config,
):
    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_find(request):
        assert request.json['id'] == 'eater_id_1'
        return eaters_response

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        return {}

    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        assert request.json == {
            'service': applications_config['eda_web']['settings']['service'],
            'client': {
                'client_id': 'eater_uuid_2',
                'device_id': stq_params['device_id'],
            },
            'channel': {'name': 'webpush'},
        }
        return {}

    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT active, eater_uuid '
        'FROM eats_notifications.user_devices '
        'JOIN eats_notifications.eaters ON eater_id = user_id',
    )
    user_devices = list(cursor)
    assert user_devices
    assert user_devices[0][0] is True  # is active

    await stq_runner.eats_notifications_save_device_web.call(
        task_id='task_id', expect_fail=False, kwargs=stq_params,
    )

    assert _mock_unsubscribe.times_called == 1

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('SELECT active FROM eats_notifications.user_devices')
    user_devices = list(cursor)
    assert user_devices
    assert user_devices[0][0] is False  # is deactivated
