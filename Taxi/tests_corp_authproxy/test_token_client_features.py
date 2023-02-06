import pytest

CLIENT_ID_1 = 'client_id_1'
ROLE = 'Client'
DEPARTMENT_ID = 'dep_id_1'


@pytest.mark.parametrize(
    [
        'url_path',
        'request_headers',
        'upstream_headers',
        'client_features',
        'expected_code',
        'expected_content',
    ],
    [
        pytest.param(
            '/integration/2.0/users/search',
            {
                'Authorization': 'Bearer oauth_token_1',
                'X-Real-IP': '0.0.0.0',
                'Accept-Language': 'ru-RU',
            },
            {
                'X-Request-Language': 'ru',
                'X-Request-Language-Region': 'RU',
                'X-YaTAxi-Corp-ACL-Client-Id': CLIENT_ID_1,
                'X-YaTAxi-Corp-ACL-Role': ROLE,
                'X-YaTAxi-Corp-ACL-Permissions': (
                    'taxi_client,taxi_department_part'
                ),
                'X-YaTAxi-Corp-ACL-Department-Id': DEPARTMENT_ID,
            },
            ['api_allowed', 'new_limits', 'zzz'],
            200,
            {},
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='client_feature_happy',
        ),
        pytest.param(
            '/integration/2.0/users/search',
            {
                'Authorization': 'Bearer oauth_token_1',
                'X-Real-IP': '0.0.0.0',
                'Accept-Language': 'ru-RU',
            },
            {
                'X-Request-Language': 'ru',
                'X-Request-Language-Region': 'RU',
                'X-YaTAxi-Corp-ACL-Client-Id': CLIENT_ID_1,
                'X-YaTAxi-Corp-ACL-Role': ROLE,
                'X-YaTAxi-Corp-ACL-Permissions': (
                    'taxi_client,taxi_department_part'
                ),
                'X-YaTAxi-Corp-ACL-Department-Id': DEPARTMENT_ID,
            },
            ['api_allowed'],
            403,
            {
                'code': 'features_check_failed',
                'message': 'Features check failed',
            },
            marks=[
                pytest.mark.passport_token(
                    oauth_token_1={'uid': '100', 'login_id': 'test_login_id'},
                ),
            ],
            id='client_feature_403',
        ),
    ],
)
@pytest.mark.config(
    CORP_AUTHPROXY_CLIENT_FEATURES={
        '/integration': {
            '/2.0/users/search': {'POST': ['api_allowed', 'new_limits']},
            '__default__': {'POST': ['api_allowed']},
        },
    },
    CORP_AUTHPROXY_PERMISSION_RULES={
        '/integration': {'__default__': {'POST': ['taxi_client']}},
    },
)
async def test_features(
        taxi_corp_authproxy,
        mock_remote,
        blackbox_service,
        url_path,
        request_headers,
        upstream_headers,
        client_features,
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

    @mockserver.json_handler('/corp-clients-uservices/v1/clients')
    def _mock_corp_clients(request):
        return {'id': CLIENT_ID_1, 'features': client_features}

    request_body = {'a': 1, 'b': 'some string', 'x': True}
    await taxi_corp_authproxy.invalidate_caches()
    mocked_handler = mock_remote(
        url_path,
        request_body=request_body,
        response_code=expected_code,
        request_headers=upstream_headers,
    )
    response = await taxi_corp_authproxy.post(
        url_path, json=request_body, headers=request_headers,
    )

    assert response.json() == expected_content
    assert response.status_code == expected_code

    if expected_code == 200:
        assert mocked_handler.has_calls
    else:
        assert not mocked_handler.has_calls
