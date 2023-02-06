import pytest

REMOTE_IP = '127.0.0.1'


@pytest.fixture(name='mock_ucommunications')
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def sendsms(request):
        assert request.headers['X-Remote-IP'] == REMOTE_IP
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    return sendsms


def find_user(pgsql, user_id):
    cursor = pgsql['user-authconfirm-pg'].cursor()
    cursor.execute(
        f'SELECT id, code, authorized FROM auth_data WHERE id = \'{user_id}\'',
    )
    result = list(cursor)
    cursor.close()
    return result


def find_phone_at_phone_data(pgsql, personal_phone_id):
    cursor = pgsql['user-authconfirm-pg'].cursor()
    cursor.execute(
        f'SELECT personal_phone_id, last_sms_sent FROM phone_data '
        f'WHERE personal_phone_id = \'{personal_phone_id}\'',
    )
    result = list(cursor)
    cursor.close()
    return result


async def test_auth(taxi_user_authconfirm, pgsql, mock_ucommunications):
    user_id = '1'
    personal_phone_id = 'new_phone'
    phone_data_list = find_phone_at_phone_data(pgsql, personal_phone_id)
    assert phone_data_list == []
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': user_id,
            'personal_phone_id': personal_phone_id,
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'X-Remote-IP': REMOTE_IP},
    )
    assert response.status_code == 200
    assert mock_ucommunications.times_called == 1
    user_and_code_list = find_user(pgsql, user_id)
    assert user_and_code_list[0][0] == user_id
    assert user_and_code_list[0][1] != ''
    assert user_and_code_list[0][2] is False
    result = await mock_ucommunications.wait_call()
    assert result['request'].json == {
        'intent': 'protocol_auth',
        'locale': 'ru',
        'phone_id': 'new_phone',
        'text': {
            'key': 'sms.auth',
            'keyset': 'notify',
            'params': {'code': user_and_code_list[0][1]},
        },
    }
    phone_data_list = find_phone_at_phone_data(pgsql, personal_phone_id)
    assert phone_data_list[0][0] == personal_phone_id
    assert phone_data_list[0][1] != ''


@pytest.mark.config(
    APPLICATION_MAP_TRANSLATIONS={'android:4': {'notify': 'notify_go'}},
)
@pytest.mark.parametrize(
    ['config_enabled', 'user_agent', 'expected_keyset'],
    [
        (
            False,
            'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            'notify',
        ),
        (
            False,
            'yandex-taxi/4.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            'notify',
        ),
        (
            True,
            'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            'notify',
        ),
        (
            True,
            'yandex-taxi/4.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            'notify_go',
        ),
    ],
)
async def test_auth_keyset_override(
        taxi_user_authconfirm,
        pgsql,
        mock_ucommunications,
        config_enabled,
        user_agent,
        expected_keyset,
        taxi_config,
):
    taxi_config.set(YANDEX_GO_USE_MAJOR_VERSION_AT_SMS_SEND=config_enabled)
    await taxi_user_authconfirm.invalidate_caches()

    user_id = '1'
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': '1',
            'personal_phone_id': 'new_phone',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'User-Agent': user_agent, 'X-Remote-IP': REMOTE_IP},
    )
    assert response.status_code == 200
    assert mock_ucommunications.times_called == 1
    user_and_code_list = find_user(pgsql, user_id)
    result = await mock_ucommunications.wait_call()
    assert result['request'].json == {
        'intent': 'protocol_auth',
        'locale': 'ru',
        'phone_id': 'new_phone',
        'text': {
            'key': 'sms.auth',
            'keyset': expected_keyset,
            'params': {'code': user_and_code_list[0][1]},
        },
    }


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.parametrize(
    ['app', 'version', 'enabled', 'authorized'],
    [
        # config is enabled and client is below minimum
        ('android', [99, 99, 99], True, False),
        # config is disabled and client is below minimum
        ('android', [99, 99, 99], False, True),
        # config is enabled and client is above minimum
        ('android', [3, 1, 99], True, True),
        # config is enabled and client is absent in config
        ('iphone', [99, 99, 99], False, True),
        # config is disabled and client is absent in config
        ('iphone', [99, 99, 99], True, True),
    ],
)
async def test_authconfirm_legacy_client(
        taxi_user_authconfirm, app, version, enabled, authorized, taxi_config,
):
    taxi_config.set_values(
        {
            'AUTHCONFIRM_LEGACY_CHECK_CLIENT_VERSION_ENABLED': enabled,
            'AUTHCONFIRM_LEGACY_CLIENT_MIN_VERSION': {
                app: {'version': version},
            },
        },
    )
    await taxi_user_authconfirm.invalidate_caches()

    response = await taxi_user_authconfirm.post(
        'v0/authconfirm',
        {'id': '42', 'confirmation_code': '123'},
        headers={
            'User-Agent': (
                'yandex-taxi/3.42.0.85658 Android/9 (OnePlus; ONEPLUS A5010)'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json()['authorized'] is authorized


@pytest.mark.now('2019-02-01T14:10:00Z')
async def test_auth_existed_user(
        taxi_user_authconfirm, pgsql, mock_ucommunications,
):
    user_id = '8'
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': user_id,
            'personal_phone_id': '777',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'X-Remote-IP': REMOTE_IP},
    )
    assert response.status_code == 200
    assert mock_ucommunications.times_called == 1
    user_and_code_list = find_user(pgsql, user_id)
    assert user_and_code_list[0][0] == user_id
    assert user_and_code_list[0][1] != ''
    assert user_and_code_list[0][2] is False


@pytest.mark.now('2019-02-01T14:10:00Z')
async def test_auth_existed_user_but_no_last_sms_sent(
        taxi_user_authconfirm, pgsql, mock_ucommunications,
):
    user_id = '3'
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': user_id,
            'personal_phone_id': '111',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'X-Remote-IP': REMOTE_IP},
    )
    assert response.status_code == 200
    assert mock_ucommunications.times_called == 1


@pytest.mark.now('2019-02-01T14:10:00Z')
async def test_auth_already_sent_last_minute(
        taxi_user_authconfirm, pgsql, mock_ucommunications,
):
    user_id = '4'
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': user_id,
            'personal_phone_id': '123',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'X-Remote-IP': '127.0.0.1'},
    )
    assert response.status_code == 429
    assert mock_ucommunications.times_called == 0


async def test_auth_already_authorized(
        taxi_user_authconfirm, pgsql, mock_ucommunications,
):
    user_id = '9'
    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': user_id,
            'personal_phone_id': '666',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={'X-Remote-IP': REMOTE_IP},
    )
    assert response.status_code == 200
    assert mock_ucommunications.times_called == 0
    user_and_code_list = find_user(pgsql, user_id)
    assert user_and_code_list[0][0] == user_id
    assert user_and_code_list[0][2] is True


async def test_authconfirm_failure(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authconfirm',
        json={'id': '5', 'confirmation_code': '666666' + '1'},
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': False, 'attempts': 1}


async def test_authconfirm_failure_too_much_attempts(
        taxi_user_authconfirm, pgsql,
):
    response = await taxi_user_authconfirm.post(
        'v0/authconfirm',
        json={'id': '7', 'confirmation_code': '666666' + '1'},
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': False, 'attempts': 5}


async def test_authconfirm_success(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authconfirm', json={'id': '5', 'confirmation_code': '666666'},
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': True, 'attempts': 1}


async def test_authconfirm_success_boundary_case(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authconfirm', json={'id': '6', 'confirmation_code': '666666'},
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': True, 'attempts': 4}


async def test_authconfirm_user_not_found(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authconfirm',
        json={'id': 'not_found_id', 'confirmation_code': '666666' + '1'},
    )
    assert response.status_code == 404


async def test_authstatus_true(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authstatus', json={'id': '9'},
    )
    assert response.status_code == 200
    assert response.json() == {'authorized': True, 'personal_phone_id': '666'}


async def test_authstatus_false(taxi_user_authconfirm, pgsql):
    response = await taxi_user_authconfirm.post(
        'v0/authstatus', json={'id': 'not_found_id'},
    )
    assert response.status_code == 404


async def test_pass_ua(taxi_user_authconfirm, mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def sendsms(request):
        assert (
            request.headers['X-Real-User-Agent']
            == 'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)'
        )
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    response = await taxi_user_authconfirm.post(
        'v0/auth',
        json={
            'id': '1',
            'personal_phone_id': 'new_phone',
            'code_length': 6,
            'locale': 'ru',
            'idempotency_token': 'idemp_token',
        },
        headers={
            'User-Agent': (
                'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)'
            ),
            'X-Remote-IP': REMOTE_IP,
        },
    )
    assert response.status_code == 200
    assert sendsms.times_called == 1
