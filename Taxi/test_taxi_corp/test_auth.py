# pylint: disable=redefined-outer-name
import datetime

import freezegun
import pytest


@pytest.fixture
async def taxi_corp_csrf_auth_client(
        aiohttp_client, passport_mock, taxi_corp_auth_app,
):
    return await aiohttp_client(taxi_corp_auth_app)


@pytest.mark.parametrize(
    'passport_mock', ['client1'], indirect=['passport_mock'],
)
@pytest.mark.config(CORP_CSRF_VALIDATION_ENABLED=True)
async def test_get_csrf_valid(taxi_corp_csrf_auth_client, passport_mock):
    response = await taxi_corp_csrf_auth_client.get(
        '/me', headers={'Cookie': 'yandexuid=yandexuid'},
    )
    assert response.status == 200
    csrf_token = (await response.json())['csrf_token']

    response = await taxi_corp_csrf_auth_client.get(
        '/1.0/class',
        headers={'Cookie': 'yandexuid=yandexuid', 'X-Csrf-Token': csrf_token},
        params={'service': 'taxi'},
    )
    assert response.status == 200, await response.json()

    response = await taxi_corp_csrf_auth_client.get(
        '/1.0/class?csrf_token={}'.format(csrf_token),
        headers={'Cookie': 'yandexuid=yandexuid'},
        params={'service': 'taxi'},
    )
    assert response.status == 200, await response.json()


@pytest.mark.parametrize(
    'url, headers, expected_status',
    [
        ('/me', {}, 401),
        ('/1.0/class', {}, 403),
        ('/1.0/class', {'Cookie': 'yandexuid=yandexuid'}, 403),
        (
            '/1.0/class',
            {'Cookie': 'yandexuid=yandexuid', 'X-Csrf-Token': 'bad token'},
            403,
        ),
    ],
)
@pytest.mark.config(CORP_CSRF_VALIDATION_ENABLED=True)
async def test_get_csrf_invalid(
        taxi_corp_csrf_auth_client, url, headers, expected_status,
):
    response = await taxi_corp_csrf_auth_client.get(url, headers=headers)
    assert response.status == expected_status


@pytest.mark.parametrize(
    'url, expected_error, expected_status',
    [('/auth', ['Session id has expired'], 401)],
)
async def test_session_expired_errors(
        taxi_corp_real_auth_client,
        patch,
        url,
        expected_error,
        expected_status,
):
    @patch('taxi.clients.passport.PassportClient._request_bb_method')
    async def _request_bb_method(*args, **kwargs):
        return {'status': {'value': 'EXPIRED', 'id': 2}, 'error': 'OK'}

    response = await taxi_corp_real_auth_client.get(
        url, headers={'Cookie': 'Session_id=1'},
    )
    response_json = await response.json()

    errors = [error['text'] for error in response_json['errors']]
    message = response_json['message']

    assert errors == expected_error
    assert [message] == expected_error
    assert response.status == expected_status


@pytest.mark.parametrize(
    'url, client, expected_error',
    [
        (
            '/auth',
            {'uid': 'client1_uid', 'login': None, 'is_staff': False},
            ['Empty login for session'],
        ),
    ],
)
async def test_empty_session(
        taxi_corp_real_auth_client, patch, url, client, expected_error,
):
    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args, **kwargs):
        return client

    response = await taxi_corp_real_auth_client.get(url)
    response_json = await response.json()

    errors = [error['text'] for error in response_json['errors']]
    message = response_json['message']

    assert errors == expected_error
    assert [message] == expected_error


@pytest.mark.parametrize(
    'url, expected_status, expected_error',
    [('/auth', 401, ['Session id is not specified'])],
)
async def test_session_not_valid_error(
        taxi_corp_real_auth_client, url, expected_status, expected_error,
):
    response = await taxi_corp_real_auth_client.get(url)
    response_json = await response.json()
    errors = [error['text'] for error in response_json['errors']]
    message = response_json['message']

    assert errors == expected_error
    assert [message] == expected_error
    assert response.status == expected_status, response_json


@pytest.mark.parametrize(
    'url, passport_mock, expected_status, expected_error',
    [('/1.0/client/client404', 'unknown', 401, ['Yandex UID not found'])],
    indirect=['passport_mock'],
)
async def test_uid_not_found_error(
        taxi_corp_real_auth_client,
        url,
        passport_mock,
        expected_status,
        expected_error,
):
    response = await taxi_corp_real_auth_client.get(url)
    response_json = await response.json()

    errors = [error['text'] for error in response_json['errors']]
    message = response_json['message']

    assert [message] == expected_error
    assert errors == expected_error
    assert response.status == expected_status, response_json


@pytest.mark.parametrize(
    'url, passport_mock, expected_status',
    [
        # MANAGER role
        ('/1.0/class', 'client1', 200),
        ('/1.0/class', 'manager1', 200),
        # MANAGER role AND client owners
        ('/1.0/client/client1', 'client1', 200),
        ('/1.0/client/client1', 'client2', 403),
        ('/1.0/client/client1', 'manager1', 200),
        ('/1.0/client/client1', 'manager2', 403),
        ('/1.0/client/client1', 'unknown', 401),
        ('/1.0/client/client2', 'manager1', 403),
        ('/1.0/client/client2', 'manager2', 200),
        # client 404
        ('/1.0/client/client404', 'client1', 404),
        ('/1.0/client/client404', 'manager1', 404),
        ('/1.0/client/client404', 'unknown', 401),
    ],
    indirect=['passport_mock'],
)
async def test_access(
        patch, taxi_corp_real_auth_client, url, passport_mock, expected_status,
):
    @patch('taxi_corp.util.corp_billing_helper.fill_corp_billing_data')
    async def _get_client(*args, **kwargs):
        return {}

    response = await taxi_corp_real_auth_client.get(
        url, params={'service': 'taxi'},
    )
    assert response.status == expected_status, await response.json()


@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'default_language': 'ru', 'web_ui_languages': ['ru', 'en']},
        'kaz': {'default_language': 'kk', 'web_ui_languages': ['kk', 'en']},
    },
)
@pytest.mark.parametrize(
    'passport_mock, status, role,  perms, yandex_login, client_state',
    [
        pytest.param(
            ['client1', {'attributes': {'200': '1'}}],
            200,
            'client',
            [
                'logistics',
                'taxi',
                'taxi_client',
                'taxi_department_full',
                'taxi_department_part',
                'taxi_other',
            ],
            'client1_login',
            {
                'client_id': 'client1',
                'ui': {
                    'default_language': 'ru',
                    'web_ui_languages': ['ru', 'en'],
                },
                'country': 'rus',
                'has_2fa': True,
            },
            id='client1',
        ),
        pytest.param(
            ['client2', {'attributes': {'1003': '1'}}],
            200,
            'client',
            [
                'logistics',
                'taxi',
                'taxi_client',
                'taxi_department_full',
                'taxi_department_part',
                'taxi_other',
            ],
            'client2_login',
            {
                'client_id': 'client2',
                'ui': {
                    'default_language': 'kk',
                    'web_ui_languages': ['kk', 'en'],
                },
                'country': 'kaz',
                'has_2fa': True,
            },
            id='client2',
        ),
        pytest.param(
            ['manager1', {'attributes': {'200': '1', '1003': '1'}}],
            200,
            'manager',
            [
                'logistics',
                'taxi',
                'taxi_client',
                'taxi_department_full',
                'taxi_department_part',
                'taxi_other',
            ],
            'manager1_login',
            {
                'client_id': 'client1',
                'ui': {
                    'default_language': 'ru',
                    'web_ui_languages': ['ru', 'en'],
                },
                'country': 'rus',
                'has_2fa': True,
            },
            id='manager1',
        ),
        pytest.param(
            'manager2',
            200,
            'manager',
            [
                'logistics',
                'taxi',
                'taxi_client',
                'taxi_department_full',
                'taxi_department_part',
                'taxi_other',
            ],
            'manager2_login',
            {
                'client_id': 'client2',
                'ui': {
                    'default_language': 'kk',
                    'web_ui_languages': ['kk', 'en'],
                },
                'country': 'kaz',
                'has_2fa': False,
            },
            id='manager2',
        ),
        pytest.param(
            'department_manager1',
            200,
            'department_manager',
            ['taxi', 'taxi_other'],
            'department_manager1_login',
            {
                'client_id': 'client1',
                'ui': {
                    'default_language': 'ru',
                    'web_ui_languages': ['ru', 'en'],
                },
                'country': 'rus',
                'has_2fa': False,
            },
            id='department_manager1',
        ),
        pytest.param(
            'department_secretary1',
            200,
            'department_secretary',
            ['taxi', 'taxi_other'],
            'department_secretary1_login',
            {
                'client_id': 'client1',
                'ui': {
                    'default_language': 'ru',
                    'web_ui_languages': ['ru', 'en'],
                },
                'country': 'rus',
                'has_2fa': False,
            },
            id='department_secretary',
        ),
        pytest.param('401', 401, None, None, None, None, id='401'),
    ],
    indirect=['passport_mock'],
)
async def test_get_auth(
        taxi_corp_real_auth_client,
        passport_mock,
        status,
        role,
        perms,
        yandex_login,
        client_state,
):
    response = await taxi_corp_real_auth_client.get('/auth')
    assert response.status == status
    if role or yandex_login:
        expected_result = {'role': role, 'yandex_login': yandex_login}

        if client_state is not None:
            expected_result.update(client_state)
        response_json = await response.json()
        if role in ['department_manager', 'department_secretary']:
            expected_result['department_ids'] = ['d1']

        assert set(response_json.pop('permissions')) == set(perms)
        assert response_json == expected_result


@pytest.mark.parametrize('csrf_enabled', [True, False])
@pytest.mark.parametrize('url', ['/auth', '/ping', '/1.0/class'])
async def test_oauth(patch, taxi_corp_csrf_auth_client, csrf_enabled, url):
    app = taxi_corp_csrf_auth_client.server.app
    app.config.CORP_CSRF_VALIDATION_ENABLED = csrf_enabled

    @patch('taxi.clients.passport.PassportClient.get_token_info')
    async def _get_token_info(*args, **kwargs):
        from taxi.clients.passport import Token
        return Token(
            'uid', 'login', 'is_staff', 'scopes', 'token_expires', 'uber_id',
        )

    response = await taxi_corp_csrf_auth_client.get(
        url, headers={'Authorization': 'xxx'}, params={'service': 'taxi'},
    )
    assert response.status == 200, await response.json()


@pytest.mark.parametrize(
    'request_token, passport_request_token',
    [
        pytest.param('xxx', 'xxx', id='no-bearer'),
        pytest.param('Bearer xxx', 'xxx', id='with-bearer'),
    ],
)
async def test_oauth_bearer(
        patch,
        taxi_corp_csrf_auth_client,
        request_token,
        passport_request_token,
):
    @patch('taxi.clients.passport.PassportClient.get_token_info')
    async def _get_token_info(token, *args, **kwargs):
        from taxi.clients.passport import Token
        assert token == passport_request_token
        return Token(
            'uid', 'login', 'is_staff', 'scopes', 'token_expires', 'uber_id',
        )

    response = await taxi_corp_csrf_auth_client.get(
        '/auth',
        headers={'Authorization': request_token},
        params={'service': 'taxi'},
    )
    assert response.status == 200, await response.json()


@pytest.mark.config(
    CORP_COUNTRIES_SUPPORTED={
        'rus': {'default_language': 'ru', 'web_ui_languages': ['ru', 'en']},
        'kaz': {'default_language': 'kk', 'web_ui_languages': ['kk', 'en']},
    },
)
@pytest.mark.parametrize('csrf_enabled', [True, False])
@pytest.mark.parametrize(
    ['url', 'expected_status', 'passport_mock', 'is_allowed_by_config'],
    [
        pytest.param('/1.0/class', 403, 'client2', False),
        pytest.param('/auth', 200, 'client2', False),
        pytest.param('/1.0/class', 200, 'client2', True),
        pytest.param('/auth', 200, 'client2', True),
    ],
    indirect=['passport_mock'],
)
async def test_oauth_api_not_allowed(
        patch,
        taxi_corp_real_auth_client,
        csrf_enabled,
        url,
        expected_status,
        passport_mock,
        is_allowed_by_config,
):
    app = taxi_corp_real_auth_client.server.app
    app.config.CORP_CSRF_VALIDATION_ENABLED = csrf_enabled
    app.config.CORP_ALLOWED_OAUTH_API = is_allowed_by_config

    @patch('taxi.clients.passport.PassportClient.get_token_info')
    async def _get_token_info(*args, **kwargs):
        from taxi.clients.passport import Token
        return Token(
            'client2_uid',
            'client2_login',
            'is_staff',
            'scopes',
            'token_expires',
            'uber_id',
        )

    response = await taxi_corp_real_auth_client.get(
        url, headers={'Authorization': 'xxx'}, params={'service': 'taxi'},
    )
    assert response.status == expected_status


@pytest.mark.parametrize(
    ['passport_mock', 'status', 'role', 'uid', 'client'],
    [
        pytest.param(
            'client1', 200, 'client', 'client1_uid', 'client1', id='client1',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_track_attendance(
        patch,
        taxi_corp_real_auth_client,
        passport_mock,
        status,
        role,
        uid,
        client,
        db,
):
    mock_id = 'uuid'

    @patch('taxi_corp.api.handlers.auth._create_client_attendance_id')
    def _get_mock_id(*args, **kwargs):
        return mock_id

    now = datetime.datetime(2019, 3, 19, 12, 40)
    later = datetime.datetime(2019, 3, 22, 11, 40)

    db_item = await db.corp_client_attendance.find_one({'yandex_uid': uid})
    assert not db_item

    with freezegun.freeze_time(now):
        response = await taxi_corp_real_auth_client.get('/auth')
        assert response.status == status
        db_item = await db.corp_client_attendance.find_one({'yandex_uid': uid})
        assert db_item['_id'] == mock_id
        assert db_item['yandex_uid'] == uid
        assert db_item['client_id'] == passport_mock
        assert db_item['role'] == role
        assert db_item['first_seen'] == now
        assert db_item['last_seen'] == now

    with freezegun.freeze_time(later):
        response = await taxi_corp_real_auth_client.get('/auth')
        assert response.status == status
        db_item = await db.corp_client_attendance.find_one({'yandex_uid': uid})
        assert db_item['_id'] == mock_id
        assert db_item['yandex_uid'] == uid
        assert db_item['client_id'] == passport_mock
        assert db_item['role'] == role
        assert db_item['first_seen'] == now
        assert db_item['last_seen'] == later
