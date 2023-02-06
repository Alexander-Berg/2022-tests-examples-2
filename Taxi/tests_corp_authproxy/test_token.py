import pytest

CLIENT_ID_1 = 'client_id_1'
ROLE = 'Client'
DEPARTMENT_ID = 'dep_id_1'

UPSTREAM_HEADERS = {
    'X-Request-Language': 'ru',
    'X-Request-Language-Region': 'RU',
    'X-YaTAxi-Corp-ACL-Client-Id': CLIENT_ID_1,
    'X-YaTAxi-Corp-ACL-Role': ROLE,
    'X-YaTAxi-Corp-ACL-Permissions': 'taxi_client,taxi_department_part',
    'X-YaTAxi-Corp-ACL-Department-Id': DEPARTMENT_ID,
}

REQUEST_HEADERS = {
    'Authorization': 'Bearer oauth_token_1',
    'X-Real-IP': '0.0.0.0',
    'Accept-Language': 'ru-RU',
}


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'body',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            {},
            400,
            {
                'code': 'request_cannot_have_content',
                'message': 'Request cannot have content',
            },
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='not_valid',
        ),
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            None,
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='valid',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {'__default__': {'GET': ['taxi_client']}},
    },
)
async def test_valid(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        body,
        expected_code,
        expected_content,
        mockserver,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    def corp_managers_handler(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=200,
            json={
                'client_id': CLIENT_ID_1,
                'role': ROLE,
                'permissions': ['taxi_client', 'taxi_department_part'],
                'department_id': DEPARTMENT_ID,
            },
        )

    request_body = body
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=200,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.get(
        url_path,
        json=request_body,
        headers=request_headers,
        params={'a': 'b'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_content

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration',
            {},
            {},
            401,
            {'code': 'unauthorized', 'message': 'Not authorized request'},
            id='401, no token',
        ),
        pytest.param(
            '/integration',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='happy path',
        ),
        pytest.param(
            '/notinconfig',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            403,
            {'code': 'no_rule_in_config', 'message': 'No rule in config'},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='not in config',
        ),
        pytest.param(
            '/integration/departments',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='in config default',
        ),
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='in_config_path',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {
            '/2.0/users/search': {'POST': ['taxi_client']},
            '__default__': {'POST': ['taxi_client']},
        },
    },
)
async def test_token_common(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        expected_code,
        expected_content,
        mockserver,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    def corp_managers_handler(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=200,
            json={
                'client_id': CLIENT_ID_1,
                'role': ROLE,
                'permissions': ['taxi_client', 'taxi_department_part'],
                'department_id': DEPARTMENT_ID,
            },
        )

    request_body = {'a': 1, 'b': 'some string', 'x': True}
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=200,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.post(
        url_path,
        json=request_body,
        headers=request_headers,
        params={'a': 'b'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_content

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='in_config_path',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {
            '/2.0/users/search': {'POST': ['taxi_client']},
            '__default__': {},
        },
    },
)
async def test_token_path(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        expected_code,
        expected_content,
        mockserver,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    def corp_managers_handler(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=200,
            json={
                'client_id': CLIENT_ID_1,
                'role': ROLE,
                'permissions': ['taxi_client', 'taxi_department_part'],
                'department_id': DEPARTMENT_ID,
            },
        )

    request_body = {'a': 1, 'b': 'some string', 'x': True}
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=200,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.post(
        url_path,
        json=request_body,
        headers=request_headers,
        params={'a': 'b'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_content

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            403,
            {'code': 'no_method_in_config', 'message': 'No method in config'},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='wrong method in config path',
        ),
        pytest.param(
            '/integration/departments',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            403,
            {'code': 'no_method_in_config', 'message': 'No method in config'},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='wrong method in config default',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {
            '/integration/2.0/users/search': {'GET': ['taxi_client']},
            '__default__': {'GET': ['taxi_client']},
        },
    },
)
async def test_token_wrong_method(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        expected_code,
        expected_content,
        mockserver,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    def corp_managers_handler(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=200,
            json={
                'client_id': CLIENT_ID_1,
                'role': ROLE,
                'permissions': ['taxi_client', 'taxi_department_part'],
                'department_id': DEPARTMENT_ID,
            },
        )

    request_body = {'a': 1, 'b': 'some string', 'x': True}
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=200,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.post(
        url_path,
        json=request_body,
        headers=request_headers,
        params={'a': 'b'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_content

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration/2.0/users/search',
            REQUEST_HEADERS,
            UPSTREAM_HEADERS,
            403,
            {
                'code': 'permission_check_failed',
                'message': 'Permission check failed',
            },
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='wrong permission in config path',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {
            '/integration/2.0/users/search': {'POST': ['taxi_client']},
            '__default__': {'POST': ['taxi_client']},
        },
    },
)
async def test_token_wrong_permission(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        expected_code,
        expected_content,
        mockserver,
):
    @mockserver.json_handler('/corp-managers/v1/managers/access-data')
    def corp_managers_handler(request):  # pylint: disable=W0612
        return mockserver.make_response(
            status=200,
            json={
                'client_id': CLIENT_ID_1,
                'role': ROLE,
                'permissions': ['taxi_department_part'],
                'department_id': DEPARTMENT_ID,
            },
        )

    request_body = {'a': 1, 'b': 'some string', 'x': True}
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=200,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.post(
        url_path,
        json=request_body,
        headers=request_headers,
        params={'a': 'b'},
    )

    assert response.status_code == expected_code
    assert response.json() == expected_content

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls
