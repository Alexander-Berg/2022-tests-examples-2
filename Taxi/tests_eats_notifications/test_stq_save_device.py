import pytest


@pytest.mark.parametrize(
    'stq_params, eaters_response, applications_config',
    [
        pytest.param(
            {
                'device_id': 'device_id_value1',
                'user_id': 'eater_id',
                'push_notifications_enabled': True,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'HTC',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_firebase': 'test',
                'app_metrica_device_id': 'app_metrica_device_id_value1',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='fcm',
        ),
        pytest.param(
            {
                'device_id': 'device_id_value2',
                'user_id': 'eater_id',
                'push_notifications_enabled': True,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'Apple',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_origin': 'test',
                'app_metrica_device_id': '',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='ios',
        ),
        pytest.param(
            {
                'device_id': 'device_id_value3',
                'user_id': 'eater_id',
                'push_notifications_enabled': False,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'Samsung',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_hms': 'test',
                'app_metrica_device_id': 'app_metrica_device_id_value1',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='hms',
        ),
    ],
)
async def test_success(
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

    token_type = (
        'apns'
        if 'push_token_origin' in stq_params
        else ('hms' if 'push_token_hms' in stq_params else 'fcm')
    )
    token = (
        stq_params['push_token_origin']
        if 'push_token_origin' in stq_params
        else (
            stq_params['push_token_firebase']
            if 'push_token_firebase' in stq_params
            else stq_params['push_token_hms']
        )
    )

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        operation_system = (
            'ios' if 'push_token_origin' in stq_params else 'android'
        )
        assert request.json == {
            'service': applications_config['eda_native']['xiva_settings'][
                operation_system
            ]['service'],
            'client': {
                'client_id': eaters_response['eater']['uuid'],
                'device_type': operation_system,
                'device_id': stq_params['device_id'],
                'app_install_id': stq_params['appmetrica_uuid'],
                'app_name': applications_config['eda_native']['xiva_settings'][
                    operation_system
                ]['app_name'],
            },
            'channel': {'name': token_type, 'token': token},
        }
        return {}

    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id', expect_fail=False, kwargs=stq_params,
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT ud.user_id, ud.auth_token, ud.active, ud.os_version, '
        'ud.app_version, ud.model, ud.device_id, ud.brand, '
        'ud.code_version, ud.push_enabled, eater.eater_uuid, ud.registered, '
        'udt.type, udt.token, eater.push_tag_bitset, ud.app_metrica_device_id '
        'FROM eats_notifications.user_devices ud '
        'JOIN eats_notifications.user_device_tokens '
        'udt ON ud.id = udt.user_device_id '
        'JOIN eats_notifications.eaters eater ON eater.eater_id = ud.user_id '
        'WHERE ud.device_id = \'{}\''.format(stq_params['device_id']),
    )
    user_devices = list(cursor)
    device_index = 0
    assert user_devices
    assert user_devices[device_index][0] == 'eater_id'
    assert user_devices[device_index][1] == stq_params['taxi_session']
    assert user_devices[device_index][2] is True  # is active
    assert user_devices[device_index][3] == stq_params['os_version']
    assert user_devices[device_index][4] == stq_params['app_version']
    assert user_devices[device_index][5] == stq_params['device_model']
    assert user_devices[device_index][6] == stq_params['device_id']
    assert user_devices[device_index][7] == stq_params['device_brand']
    assert user_devices[device_index][8] == stq_params['code_version']
    assert (
        user_devices[device_index][9]
        == stq_params['push_notifications_enabled']
    )
    assert user_devices[device_index][10] == eaters_response['eater']['uuid']
    assert user_devices[device_index][11] == (
        True if stq_params['push_notifications_enabled'] else None
    )  # is registered
    assert user_devices[device_index][12] == token_type
    assert user_devices[device_index][13] == token
    assert user_devices[device_index][14] == 3
    assert (
        user_devices[device_index][15] == stq_params['app_metrica_device_id']
    )

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
        'VALUES (\'user_id\', \'test\', TRUE, \'test\')',
        'INSERT INTO eats_notifications.eaters '
        '(eater_id, eater_uuid) '
        'VALUES (\'user_id\', \'test\')',
    ],
)
@pytest.mark.parametrize(
    'stq_params, eaters_response, applications_config',
    [
        pytest.param(
            {
                'device_id': 'test',
                'user_id': 'eater_id',
                'push_notifications_enabled': False,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'Apple',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_hms': 'test',
                'app_metrica_device_id': 'app_metrica_device_id_value1',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='deactivate',
        ),
    ],
)
async def test_deactivate(
        taxi_eats_notifications,
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
        return eaters_response

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        return {}

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT active, eater_uuid '
        'FROM eats_notifications.user_devices '
        'JOIN eats_notifications.eaters ON eater_id = user_id',
    )
    user_devices = list(cursor)
    assert user_devices
    assert user_devices[0][0] is True  # is active

    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        operation_system = (
            'ios' if 'push_token_origin' in stq_params else 'android'
        )
        assert request.json == {
            'service': applications_config['eda_native']['xiva_settings'][
                operation_system
            ]['service'],
            'client': {
                'client_id': user_devices[0][1],
                'device_id': stq_params['device_id'],
            },
        }
        return {}

    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'device_id': stq_params['device_id'],
            'user_id': stq_params['user_id'],
            'push_notifications_enabled': stq_params[
                'push_notifications_enabled'
            ],
            'taxi_session': stq_params['taxi_session'],
            'app_version': stq_params['app_version'],
            'device_brand': stq_params['device_brand'],
            'code_version': stq_params['code_version'],
            'device_model': stq_params['device_model'],
            'os_version': stq_params['os_version'],
            'appmetrica_uuid': stq_params['appmetrica_uuid'],
            'push_token_firebase': stq_params.get('push_token_firebase'),
            'push_token_hms': stq_params.get('push_token_hms'),
            'push_token_origin': stq_params.get('push_token_origin'),
            'app_metrica_device_id': stq_params.get('app_metrica_device_id'),
        },
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('SELECT active FROM eats_notifications.user_devices')
    user_devices = list(cursor)
    assert user_devices
    assert user_devices[0][0] is False  # is deactivated


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        'INSERT INTO eats_notifications.user_devices '
        '(user_id, auth_token, active, device_id) '
        'VALUES (\'eater_id\', \'taxi_session_value\', TRUE, '
        '\'device_id_test\')',
        'INSERT INTO eats_notifications.eaters '
        '(eater_id, eater_uuid) '
        'VALUES (\'eater_id\', \'aaaa\')',
    ],
)
@pytest.mark.parametrize(
    'stq_params, eaters_response, applications_config',
    [
        pytest.param(
            {
                'device_id': 'device_id_test',
                'user_id': 'eater_id',
                'push_notifications_enabled': False,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'Apple',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_hms': 'test',
                'app_metrica_device_id': 'app_metrica_device_id_value1',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            id='deactivate',
        ),
    ],
)
async def test_find_uuid(
        taxi_eats_notifications,
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
        return eaters_response

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        return {}

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute('SELECT active FROM eats_notifications.user_devices')
    user_devices = list(cursor)

    assert len(user_devices) == 1
    assert user_devices
    assert user_devices[0][0] is True  # is active

    @mockserver.json_handler('client-notify/v1/unsubscribe')
    def _mock_unsubscribe(request):
        return {}

    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': applications_config},
    )

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'device_id': stq_params['device_id'],
            'user_id': stq_params['user_id'],
            'push_notifications_enabled': stq_params[
                'push_notifications_enabled'
            ],
            'taxi_session': stq_params['taxi_session'],
            'app_version': stq_params['app_version'],
            'device_brand': stq_params['device_brand'],
            'code_version': stq_params['code_version'],
            'device_model': stq_params['device_model'],
            'os_version': stq_params['os_version'],
            'appmetrica_uuid': stq_params['appmetrica_uuid'],
            'push_token_firebase': stq_params.get('push_token_firebase'),
            'push_token_hms': stq_params.get('push_token_hms'),
            'push_token_origin': stq_params.get('push_token_origin'),
            'app_metrica_device_id': stq_params.get('app_metrica_device_id'),
        },
    )

    cursor = pgsql['eats_notifications'].cursor()
    cursor.execute(
        'SELECT active FROM eats_notifications.user_devices '
        'WHERE device_id = \'%s\'' % stq_params['device_id'],
    )
    user_devices = list(cursor)
    assert len(user_devices) == 1
    assert user_devices

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id',
        expect_fail=False,
        kwargs={
            'device_id': stq_params['device_id'],
            'user_id': stq_params['user_id'],
            'push_notifications_enabled': stq_params[
                'push_notifications_enabled'
            ],
            'taxi_session': stq_params['taxi_session'],
            'app_version': stq_params['app_version'],
            'device_brand': stq_params['device_brand'],
            'code_version': stq_params['code_version'],
            'device_model': stq_params['device_model'],
            'os_version': stq_params['os_version'],
            'appmetrica_uuid': stq_params['appmetrica_uuid'],
            'push_token_firebase': stq_params.get('push_token_firebase'),
            'push_token_hms': stq_params.get('push_token_hms'),
            'push_token_origin': stq_params.get('push_token_origin'),
            'app_metrica_device_id': stq_params.get('app_metrica_device_id'),
        },
    )

    cursor.execute(
        'SELECT eater_uuid FROM eats_notifications.user_devices '
        'JOIN eats_notifications.eaters ON eater_id = user_id '
        'WHERE device_id = \'%s\'' % stq_params['device_id'],
    )
    user_devices = list(cursor)
    assert len(user_devices) == 1
    assert user_devices[0][0] == 'aaaa'

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id',
        expect_fail=True,
        kwargs={
            'device_id': stq_params['device_id'],
            'user_id': stq_params['user_id'],
            'push_notifications_enabled': False,
            'taxi_session': stq_params['taxi_session'],
            'app_version': stq_params['app_version'],
            'device_brand': stq_params['device_brand'],
            'code_version': stq_params['code_version'],
            'device_model': stq_params['device_model'],
            'os_version': stq_params['os_version'],
            'appmetrica_uuid': stq_params['appmetrica_uuid'],
            'app_metrica_device_id': stq_params.get('app_metrica_device_id'),
        },
    )


async def test_config_has_no_eda_native_key(
        taxi_eats_notifications, stq_runner,
):
    stq_params = {
        'device_id': 'device_id_test',
        'user_id': 'eater_id',
        'push_notifications_enabled': False,
        'taxi_session': 'taxi_session_value',
        'app_version': 'test',
        'device_brand': 'Apple',
        'code_version': 'test',
        'device_model': 'test',
        'os_version': 'test',
        'appmetrica_uuid': 'test',
        'app_metrica_device_id': 'app_metrica_device_id_value1',
    }

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id',
        expect_fail=True,
        kwargs={
            'device_id': stq_params['device_id'],
            'user_id': stq_params['user_id'],
            'push_notifications_enabled': False,
            'taxi_session': stq_params['taxi_session'],
            'app_version': stq_params['app_version'],
            'device_brand': stq_params['device_brand'],
            'code_version': stq_params['code_version'],
            'device_model': stq_params['device_model'],
            'os_version': stq_params['os_version'],
            'appmetrica_uuid': stq_params['appmetrica_uuid'],
            'app_metrica_device_id': stq_params['app_metrica_device_id'],
        },
    )


@pytest.mark.pgsql(
    'eats_notifications',
    queries=[
        """
        INSERT INTO eats_notifications.user_devices
            (id, user_id, auth_token, active, device_id, registered)
        VALUES (
            111,
            'eater_id',
            'taxi_session_value',
            true,
            'device_id_value1',
            true
        )
        """,
        """
        INSERT INTO eats_notifications.user_device_tokens
            (user_device_id, type, token, is_registered)
        VALUES (
            111,
            'fcm',
            'token_1',
            true
        )
        """,
    ],
)
@pytest.mark.parametrize(
    """
        p_stq_params,
        p_eaters_response,
        p_applications_config,
        p_subscribe_request,
        p_user_device,
        p_user_device_token
    """,
    [
        pytest.param(
            {
                'device_id': 'device_id_value1',
                'user_id': 'eater_id',
                'push_notifications_enabled': True,
                'taxi_session': 'taxi_session_value',
                'app_version': 'test',
                'device_brand': 'HTC',
                'code_version': 'test',
                'device_model': 'test',
                'os_version': 'test',
                'appmetrica_uuid': 'test',
                'push_token_firebase': 'token_2',
                'app_metrica_device_id': 'app_metrica_device_id_value1',
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
                'eda_native': {
                    'type': 'xiva',
                    'xiva_settings': {
                        'ios': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                        'android': {
                            'app_name': 'com.appkode.foodfox',
                            'service': 'eda-client',
                        },
                    },
                    'settings': {'service': 'eda-client', 'route': 'eda'},
                    'user_identity_name': 'eater_id',
                },
            },
            {
                'service': 'eda-client',
                'client': {
                    'client_id': 'eater_uuid',
                    'device_type': 'android',
                    'device_id': 'device_id_value1',
                    'app_install_id': 'test',
                    'app_name': 'com.appkode.foodfox',
                },
                'channel': {'name': 'fcm', 'token': 'token_2'},
            },
            {
                'user_id': 'eater_id',
                'device_id': 'device_id_value1',
                'registered': True,
            },
            {
                'user_device_id': 111,
                'type': 'fcm',
                'token': 'token_2',
                'is_registered': True,
            },
            id='fcm',
        ),
    ],
)
async def test_register_new_token_when_device_exist(
        taxi_config,
        mockserver,
        pgsql,
        stq_runner,
        p_stq_params,
        p_eaters_response,
        p_applications_config,
        p_subscribe_request,
        p_user_device,
        p_user_device_token,
):
    taxi_config.set_values(
        {'EATS_NOTIFICATIONS_APPLICATIONS_V2': p_applications_config},
    )

    @mockserver.json_handler('/eats-eaters/v1/eaters/find-by-id')
    def _mock_find(request):
        assert request.json['id'] == p_stq_params['user_id']
        return p_eaters_response

    @mockserver.json_handler('client-notify/v1/subscribe')
    def _mock_subscribe(request):
        assert request.json == p_subscribe_request
        return {}

    await stq_runner.eats_notifications_save_device.call(
        task_id='task_id', expect_fail=False, kwargs=p_stq_params,
    )

    cursor = pgsql['eats_notifications'].cursor()

    cursor.execute(
        """
            SELECT user_id, device_id, registered
            FROM eats_notifications.user_devices
            WHERE user_id = %s AND device_id = %s
        """,
        (p_user_device['user_id'], p_user_device['device_id']),
    )
    user_devices = list(cursor)
    assert len(user_devices) == 1
    assert user_devices[0] == tuple(p_user_device.values())

    cursor.execute(
        """
            SELECT user_device_id, type, token, is_registered
            FROM eats_notifications.user_device_tokens
            WHERE user_device_id = %s AND type = %s AND token = %s
        """,
        (
            p_user_device_token['user_device_id'],
            p_user_device_token['type'],
            p_user_device_token['token'],
        ),
    )
    user_device_tokens = list(cursor)
    assert len(user_device_tokens) == 1
    assert user_device_tokens[0] == tuple(p_user_device_token.values())
