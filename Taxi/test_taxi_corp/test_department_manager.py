import typing

import pytest

LONG_FULLNAME = 'a' * 257
PD_ID = 'pd_id'

CORP_USER_PHONES_SUPPORTED = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+7'],
        'matches': ['^7'],
    },
]


BASE_CLIENT = 'client1'

BASE_REQUEST: typing.Dict[str, typing.Any] = {
    'department_id': 'd1',
    'email': 'mr_anderson@matrix.corp',
    'phone': '+79161237700',
    'fullname': 'Mr. Anderson',
    'role': 'department_manager',
    'yandex_login': 'mr_anderson',
}


@pytest.fixture(name='managers_info_mock')
def _managers_info_mock(mockserver, load_json):
    @mockserver.json_handler('/corp-managers/v1/managers/info')
    def _mock(request):
        mock_managers_info = load_json('mock_managers_info.json')
        for manager_info in mock_managers_info:
            if manager_info['id'] == request.query['manager_id']:
                return mockserver.make_response(json=manager_info, status=200)
        return mockserver.make_response(
            json={'code': 'NotFound', 'message': 'Manager not found'},
            status=404,
        )


@pytest.mark.parametrize(
    [
        'passport_mock',
        'request_body',
        'corp_managers_response_body',
        'expected_response_body',
        'expected_status',
        'validation_errors',
    ],
    [
        pytest.param(
            BASE_CLIENT,
            BASE_REQUEST,
            {'id': 'created_manager_id'},
            {'_id': 'created_manager_id'},
            200,
            None,
        ),
        pytest.param(
            BASE_CLIENT,
            {
                **BASE_REQUEST,
                **{'email': 'invalid_email', 'phone': 'invalid_phone'},
            },
            {},
            {},
            400,
            [
                '\'invalid_email\' does not match',
                '\'invalid_phone\' does not match',
            ],
        ),
        pytest.param(
            BASE_CLIENT,
            {
                'fullname': '',
                'department_id': '',
                'role': '',
                'yandex_login': '',
                'email': '',
                'phone': '',
            },
            {},
            {},
            404,
            ['Department not found'],
        ),
        pytest.param(
            BASE_CLIENT,
            {**BASE_REQUEST, **{'fullname': LONG_FULLNAME}},
            {},
            {},
            400,
            ['\'' + LONG_FULLNAME + '\' is too long'],
        ),
        pytest.param(
            BASE_CLIENT,
            {**BASE_REQUEST, **{'department_id': None}},
            {},
            {},
            400,
            ['None is not of type \'string\''],
        ),
        pytest.param(
            BASE_CLIENT,
            BASE_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'A user with this login already exists',
            },
            {},
            400,
            None,
        ),
        pytest.param(
            BASE_CLIENT,
            BASE_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'Unknown username (yandex_login)',
            },
            {},
            400,
            None,
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_create_manager(
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        request_body,
        corp_managers_response_body,
        expected_response_body,
        expected_status,
        validation_errors,
):
    @mockserver.json_handler('/corp-managers/v1/managers/create')
    async def _mock_create_manager(request):
        return mockserver.make_response(
            json=corp_managers_response_body, status=expected_status,
        )

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/department_manager'.format(passport_mock),
        json=request_body,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json

    if expected_status == 200:
        assert response_json == expected_response_body
        mock_call = _mock_create_manager.next_call()

        assert 'X-Remote-Ip' in mock_call['request'].headers

        corp_managers_request_body = dict(
            **request_body, client_id=passport_mock,
        )
        assert mock_call['request'].json == corp_managers_request_body

    if validation_errors is not None:
        response_errors = [error['text'] for error in response_json['errors']]
        assert len(response_errors) == len(validation_errors)
        for response_error, expected_error in zip(
                response_errors, validation_errors,
        ):
            assert expected_error in response_error

    if expected_status != 200 and validation_errors is None:
        assert response_json == corp_managers_response_body


@pytest.mark.parametrize(
    'client_id, department_id, passport_mock, status',
    [
        # client access to own department
        ('client1', 'd1', 'client1', 200),
        # manager access to own department
        ('client1', 'd1', 'manager1', 403),
        # manager access to child department
        ('client1', 'd1_1', 'manager1', 200),
        ('client1', 'd1_1_1', 'manager1', 200),
        # manager access to parent department
        ('client1', 'd1', 'manager1_1', 403),
        # client access to foreign department
        ('client1', 'd2', 'client1', 403),
        # manager access to foreign department
        ('client1', 'd2', 'manager1', 403),
    ],
    indirect=['passport_mock'],
)
async def test_create_manager_access(
        taxi_corp_real_auth_client,
        mockserver,
        client_id,
        department_id,
        passport_mock,
        status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/create')
    async def _mock_create_manager(request):
        return mockserver.make_response(json={'id': ''}, status=200)

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/{}/department_manager'.format(client_id),
        json={**BASE_REQUEST, **{'department_id': department_id}},
    )

    response_json = await response.json()
    assert response.status == status, response_json


@pytest.mark.parametrize(
    'passport_mock, manager_id',
    [('client1', 'manager1'), ('manager1', 'manager1_1')],
    indirect=['passport_mock'],
)
async def test_delete_manager(
        taxi_corp_real_auth_client,
        mockserver,
        managers_info_mock,
        passport_mock,
        manager_id,
):
    @mockserver.json_handler('/corp-managers/v1/managers/delete')
    async def _mock_delete_manager(request):
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/client1/department_manager/{}'.format(manager_id),
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    mock_call = _mock_delete_manager.next_call()
    assert mock_call['request'].query['manager_id'] == manager_id


@pytest.mark.parametrize(
    'passport_mock, manager_id, client_id, expected_status',
    [
        # client1 (enable departments)
        ('manager1', 'manager1', 'client1', 403),
        ('manager1', 'manager2', 'client1', 403),
        ('manager1', 'secretary1', 'client1', 403),
        ('secretary1', 'manager1', 'client1', 403),
        ('secretary1', 'manager1_1', 'client1', 403),
        ('client1', 'client2_secretary1', 'client1', 403),
        ('manager1', 'client2_secretary1', 'client1', 403),
        ('manager1', 'client2_manager1_1', 'client1', 403),
        # client2 (disable departments)
        ('client2_manager1', 'client2_manager1_1', 'client2', 403),
        ('client2_manager1', 'client2_secretary1', 'client2', 403),
    ],
    indirect=['passport_mock'],
)
async def test_delete_manager_access(
        taxi_corp_real_auth_client,
        mockserver,
        managers_info_mock,
        passport_mock,
        manager_id,
        client_id,
        expected_status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/delete')
    async def _mock_delete_manager(request):
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.delete(
        '/1.0/client/{}/department_manager/{}'.format(client_id, manager_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json


@pytest.mark.parametrize(
    [
        'passport_mock',
        'manager_id',
        'expected_response_body',
        'expected_status',
    ],
    [
        pytest.param(
            'client1',
            'manager1',
            {
                '_id': 'manager1',
                'department_id': 'd1',
                'email': 'manager1@client1',
                'fullname': 'manager1',
                'phone': '+79161237701',
                'role': 'department_manager',
                'yandex_login': 'manager1',
            },
            200,
        ),
        pytest.param(
            'manager1',
            'secretary1',
            {
                '_id': 'secretary1',
                'department_id': 'd1',
                'email': 'secretary1@client1',
                'fullname': 'secretary1',
                'phone': '+79161237705',
                'role': 'department_secretary',
                'yandex_login': 'secretary1',
            },
            200,
        ),
        pytest.param('client1', 'not_existed_manager_id', None, 404),
    ],
    indirect=['passport_mock'],
)
async def test_get_one_manager(
        taxi_corp_real_auth_client,
        mockserver,
        managers_info_mock,
        passport_mock,
        manager_id,
        expected_response_body,
        expected_status,
):
    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/department_manager/{}'.format(manager_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json

    if response.status == 200:
        assert response_json == expected_response_body


@pytest.mark.parametrize(
    'passport_mock, manager_id, expected_status',
    [
        ('client1', 'client2_secretary1', 403),
        ('client1', 'client2_manager1_1', 403),
        ('manager1', 'client2_secretary1', 403),
        ('secretary1', 'client2_secretary1', 403),
        ('manager1_1', 'manager1', 403),
        ('manager3', 'manager1', 403),
        ('manager3', 'manager1_1', 403),
    ],
    indirect=['passport_mock'],
)
async def test_get_one_manager_access(
        taxi_corp_real_auth_client,
        managers_info_mock,
        passport_mock,
        manager_id,
        expected_status,
):

    response = await taxi_corp_real_auth_client.get(
        '/1.0/client/client1/department_manager/{}'.format(manager_id),
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json


@pytest.mark.parametrize(
    [
        'passport_mock',
        'manager_id',
        'request_body',
        'corp_managers_response_body',
        'expected_status',
    ],
    [
        pytest.param(
            BASE_CLIENT, 'manager1', BASE_REQUEST, {}, 200, id='max fill',
        ),
        pytest.param(
            BASE_CLIENT,
            'manager1',
            BASE_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'A user with this login already exists',
            },
            400,
            id='change role from manager to secretary',
        ),
        pytest.param(
            BASE_CLIENT,
            'manager1',
            BASE_REQUEST,
            {
                'code': 'BadRequest',
                'message': 'Unknown username (yandex_login)',
            },
            400,
        ),
        pytest.param(
            BASE_CLIENT,
            'not_existed_manager_id',
            BASE_REQUEST,
            {'code': 'NotFound', 'message': 'Manager not found'},
            404,
            id='min fill',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED)
async def test_update_manager(
        taxi_corp_real_auth_client,
        mockserver,
        managers_info_mock,
        passport_mock,
        manager_id,
        request_body,
        corp_managers_response_body,
        expected_status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    async def _mock_update_manager(request):
        return mockserver.make_response(
            json=corp_managers_response_body, status=expected_status,
        )

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/client1/department_manager/{}'.format(manager_id),
        json=request_body,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json

    assert response_json == corp_managers_response_body

    if expected_status == 200:
        mock_call = _mock_update_manager.next_call()

        assert mock_call['request'].query['manager_id'] == manager_id
        assert 'X-Remote-Ip' in mock_call['request'].headers

        assert mock_call['request'].json == request_body


@pytest.mark.parametrize(
    'client_id, department_id, passport_mock, department_manager_id, status',
    [
        ('client1', 'd1', 'manager1', 'secretary1', 403),
        ('client1', 'd1_1', 'manager1', 'manager1_1', 200),
        ('client1', 'd1', 'manager1', 'manager1', 403),
        ('client1', 'd1', 'manager1', 'manager2', 403),
        ('client1', 'd1', 'secretary1', 'manager1', 403),
        ('client1', 'd1_1', 'secretary1', 'manager1_1', 403),
        ('client1', 'd1', 'client1', 'client2_secretary1', 403),
        ('client1', 'd1', 'manager1', 'client2_secretary1', 403),
        ('client1', 'd1', 'manager1', 'client2_manager1_1', 403),
        ('client2', 'd2', 'client2_manager1', 'client2_manager1_1', 403),
        ('client2', 'd2', 'client2_manager1', 'client2_secretary1', 403),
    ],
    indirect=['passport_mock'],
)
async def test_update_manager_access(
        taxi_corp_real_auth_client,
        mockserver,
        managers_info_mock,
        client_id,
        department_id,
        passport_mock,
        department_manager_id,
        status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/update')
    async def _mock_update_manager(request):
        return mockserver.make_response(json={}, status=200)

    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/department_manager/{}'.format(
            client_id, department_manager_id,
        ),
        json={**BASE_REQUEST, **{'department_id': department_id}},
    )

    response_json = await response.json()
    assert response.status == status, response_json


@pytest.mark.parametrize(
    [
        'passport_mock',
        'request_body',
        'corp_managers_request_body',
        'corp_managers_response',
        'expected_response',
    ],
    [
        (
            'client1',
            {},
            {
                'client_id': 'client1',
                'roles': ['department_manager', 'department_secretary'],
                'limit': 10,
                'offset': 0,
            },
            {
                'managers': [
                    {
                        'id': 'manager1',
                        'department_id': 'd1',
                        'email': 'manager1@client1',
                        'fullname': 'manager1',
                        'phone': '+79161237701',
                        'role': 'department_manager',
                        'yandex_login': 'manager1',
                    },
                    {
                        'id': 'manager1_1',
                        'department_id': 'd1_1',
                        'email': 'manager1_1@client1',
                        'fullname': 'manager1_1',
                        'phone': '+79161237702',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1',
                    },
                ],
                'total': 2,
            },
            {
                'department_managers': [
                    {
                        '_id': 'manager1',
                        'department_id': 'd1',
                        'email': 'manager1@client1',
                        'fullname': 'manager1',
                        'phone': '+79161237701',
                        'role': 'department_manager',
                        'yandex_login': 'manager1',
                    },
                    {
                        '_id': 'manager1_1',
                        'department_id': 'd1_1',
                        'email': 'manager1_1@client1',
                        'fullname': 'manager1_1',
                        'phone': '+79161237702',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1',
                    },
                ],
                'total': 2,
            },
        ),
        (
            'client1',
            {
                'department_id': 'd1_1',
                'limit': 1,
                'offset': 3,
                'sort': [{'field': 'fullname', 'direction': 'desc'}],
                'search': 'manager1',
            },
            {
                'client_id': 'client1',
                'roles': ['department_manager', 'department_secretary'],
                'department_ids': ['d1_1', 'd1_1_1', 'd1_1_1_1'],
                'sort': [{'field': 'fullname', 'direction': 'desc'}],
                'search': 'manager1',
                'limit': 1,
                'offset': 3,
            },
            {
                'managers': [
                    {
                        'id': 'manager1_1',
                        'department_id': 'd1_1',
                        'email': 'manager1_1@client1',
                        'fullname': 'manager1_1',
                        'phone': '+79161237702',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1',
                    },
                ],
                'total': 1,
            },
            {
                'department_managers': [
                    {
                        '_id': 'manager1_1',
                        'department_id': 'd1_1',
                        'email': 'manager1_1@client1',
                        'fullname': 'manager1_1',
                        'phone': '+79161237702',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1',
                    },
                ],
                'total': 1,
            },
        ),
        (
            'manager1_1',
            {},
            {
                'client_id': 'client1',
                'roles': ['department_manager', 'department_secretary'],
                'department_ids': ['d1_1_1', 'd1_1_1_1'],
                'limit': 10,
                'offset': 0,
            },
            {
                'managers': [
                    {
                        'id': 'manager1_1_1',
                        'department_id': 'd1_1_1',
                        'email': 'manager1_1_1@client1',
                        'fullname': 'manager1_1_1',
                        'phone': '+79161237703',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1_1',
                    },
                ],
                'total': 1,
            },
            {
                'department_managers': [
                    {
                        '_id': 'manager1_1_1',
                        'department_id': 'd1_1_1',
                        'email': 'manager1_1_1@client1',
                        'fullname': 'manager1_1_1',
                        'phone': '+79161237703',
                        'role': 'department_manager',
                        'yandex_login': 'manager1_1_1',
                    },
                ],
                'total': 1,
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_search_handler(
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        request_body,
        corp_managers_request_body,
        corp_managers_response,
        expected_response,
):
    @mockserver.json_handler('/corp-managers/v1/managers/search')
    async def _mock_search_managers(request):
        assert request.json == corp_managers_request_body
        return mockserver.make_response(
            json=corp_managers_response, status=200,
        )

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/department_manager/search', json=request_body,
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_response


@pytest.mark.parametrize(
    'passport_mock, post_content, expected_status',
    [('client2', {}, 403)],
    indirect=['passport_mock'],
)
async def test_search_handler_access(
        taxi_corp_real_auth_client,
        mockserver,
        passport_mock,
        post_content,
        expected_status,
):
    @mockserver.json_handler('/corp-managers/v1/managers/search')
    async def _mock_search_managers(request):
        return mockserver.make_response(json={}, status=200)

    response = await taxi_corp_real_auth_client.post(
        '/1.0/client/client1/department_manager/search', json=post_content,
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
