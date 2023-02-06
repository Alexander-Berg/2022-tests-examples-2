# pylint: disable=import-error
import aiohttp
import pytest

from client_blackbox import mock_blackbox  # noqa: F403 F401, I100, I202

ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/cc/token'},
        'proxy': {'auth': 'token', 'server-hosts': ['*']},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
    {
        'input': {'http-path-prefix': '/cc/session'},
        'proxy': {'auth': 'session', 'server-hosts': ['*']},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]
UID = '1234567890123456'
TOKEN = {
    'uid': UID,
    'scope': 'taxi-cc:all',
    'emails': [mock_blackbox.make_email('smth@drvrc.com')],
}
SESSION = TOKEN
AC_RULES = [
    {
        'prefix': '/cc/token',
        'access_rules': [
            {
                'path': '/cc/token/test',
                'method': 'POST',
                'check_restrictions': True,
                'access_conditions': {
                    'any_of': [
                        {'all_of': [{'type': 'permission', 'name': 'edit'}]},
                    ],
                },
            },
        ],
    },
    {
        'prefix': '/cc/session',
        'access_rules': [
            {
                'path': '/cc/session/test',
                'method': 'POST',
                'check_restrictions': True,
                'access_conditions': {
                    'any_of': [
                        {'all_of': [{'type': 'permission', 'name': 'edit'}]},
                    ],
                },
            },
        ],
    },
]


@pytest.mark.parametrize(
    'permissions,ok_',
    [(['edit'], True), (['read'], False), ([], False), (None, False)],
)
@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    CC_AUTHPROXY_PREFIX_ACCESS_RULES=AC_RULES,
)
async def test_permissions_rule(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        mockserver,
        default_response,
        blackbox_service,
        permissions,
        ok_,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote(url_path='/cc/token/test')

    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _get_user_access_info(request):
        assert request.json == {'provider': 'yandex', 'provider_user_id': UID}
        if permissions is None:
            return aiohttp.web.json_response(status=500, data='')
        return {
            'permissions': permissions,
            'evaluated_permissions': [],
            'restrictions': [],
            'roles': [
                {
                    'role': 'role',
                    'permissions': permissions,
                    'evaluated_permissions': [],
                    'restrictions': [],
                },
            ],
        }

    response = await cc_request(url_path='/cc/token/test', token='token1')

    assert handler.has_calls == ok_
    assert _get_user_access_info.has_calls
    if ok_:
        assert response.status_code == 200
    else:
        assert response.status_code == 401


@pytest.mark.parametrize('auth', ['session', 'token'])
@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.passport_session(session1=SESSION)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    CC_AUTHPROXY_PREFIX_ACCESS_RULES=AC_RULES,
    CC_AUTHPROXY_CSRF_TOKEN_SETTINGS={
        'validation-enabled': False,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
async def test_missing_rule(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        mockserver,
        default_response,
        blackbox_service,
        auth,
):
    await taxi_cc_authproxy.invalidate_caches()
    if auth == 'token':
        url_path = '/cc/token/test2'
    else:
        url_path = '/cc/session/test2'
    handler = mock_remote(url_path=url_path)

    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _get_user_access_info(request):
        assert False

    if auth == 'token':
        response = await cc_request(url_path=url_path, token='token1')
    else:
        response = await cc_request(
            url_path=url_path, headers={'Cookie': 'Session_id=session'},
        )

    assert not handler.has_calls
    assert not _get_user_access_info.has_calls
    assert response.status_code == 401


@pytest.mark.parametrize(
    'access_denied',
    [
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    CC_AUTHPROXY_DENY_ACCESS_IF_NO_PREFIX_ACCESS_RULE_FOUND=True,  # noqa: E501 pylint: disable=line-too-long
                ),
            ],
        ),
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    CC_AUTHPROXY_DENY_ACCESS_IF_NO_PREFIX_ACCESS_RULE_FOUND=False,  # noqa: E501 pylint: disable=line-too-long
                ),
            ],
        ),
    ],
)
@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.passport_session(session1=SESSION)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    CC_AUTHPROXY_PREFIX_ACCESS_RULES=[],
    CC_AUTHPROXY_CSRF_TOKEN_SETTINGS={
        'validation-enabled': False,
        'max-age-seconds': 600,
        'delta-seconds': 10,
    },
)
async def test_missing_appropriate_prefix(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        mockserver,
        default_response,
        blackbox_service,
        access_denied,
):
    await taxi_cc_authproxy.invalidate_caches()
    url_path = '/cc/token/test2'
    mock_remote(url_path=url_path)

    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _get_user_access_info(request):
        assert request.json == {'provider': 'yandex', 'provider_user_id': UID}
        return {
            'permissions': ['edit'],
            'evaluated_permissions': [],
            'restrictions': [],
            'roles': [
                {
                    'role': 'role',
                    'permissions': ['edit'],
                    'evaluated_permissions': [],
                    'restrictions': [],
                },
            ],
        }

    response = await cc_request(url_path=url_path, token='token1')

    if access_denied:
        assert response.status_code == 401
    else:
        assert response.status_code == 200


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    CC_AUTHPROXY_PREFIX_ACCESS_RULES=[
        {
            'prefix': '/cc/token',
            'access_rules': [
                {
                    'path': '/cc/token/test',
                    'method': 'POST',
                    'check_restrictions': True,
                    'access_conditions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission_rule',
                                        'name': 'project_rule',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        },
        {
            'prefix': '/cc/session',
            'access_rules': [
                {
                    'path': '/cc/session/test',
                    'method': 'POST',
                    'check_restrictions': True,
                    'access_conditions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission_rule',
                                        'name': 'project_rule',
                                    },
                                ],
                            },
                        ],
                    },
                },
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'permissions,request_body,response_code',
    [
        pytest.param(
            [
                {
                    'rule_name': 'project_rule',
                    'rule_storage': 'body',
                    'rule_path': 'project',
                    'rule_value': 'disp',
                },
            ],
            {'project': 'disp'},
            200,
            id='successful',
        ),
        pytest.param(
            [
                {
                    'rule_name': 'project_rule',
                    'rule_storage': 'body',
                    'rule_path': 'project',
                    'rule_value': 'disp',
                },
            ],
            {'project': 'help'},
            401,
            id='wrong value',
        ),
        pytest.param(
            [
                {
                    'rule_name': 'project_rule',
                    'rule_storage': 'body',
                    'rule_path': 'project',
                    'rule_value': 'disp',
                },
            ],
            {},
            401,
            id='no field',
        ),
        pytest.param(
            [
                {
                    'rule_name': 'project_rule',
                    'rule_storage': 'body',
                    'rule_path': 'project',
                    'rule_value': 'disp',
                },
            ],
            {'project': 123},
            401,
            id='wrong value type',
        ),
        pytest.param(
            [
                {
                    'rule_name': 'project2_rule',
                    'rule_storage': 'body',
                    'rule_path': 'project',
                    'rule_value': 'disp',
                },
            ],
            {'project': 'disp'},
            401,
            id='wrong rule name',
        ),
    ],
)
async def test_eval_permissions(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        mockserver,
        default_response,
        blackbox_service,
        permissions,
        request_body,
        response_code,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote(url_path='/cc/token/test')

    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _get_user_access_info(request):
        assert request.json == {'provider': 'yandex', 'provider_user_id': UID}
        if permissions is None:
            return aiohttp.web.json_response(status=500, data='')
        return {
            'permissions': [],
            'evaluated_permissions': permissions,
            'restrictions': [],
            'roles': [
                {
                    'role': 'role',
                    'permissions': [],
                    'evaluated_permissions': permissions,
                    'restrictions': [],
                },
            ],
        }

    response = await cc_request(
        url_path='/cc/token/test', token='token1', request_body=request_body,
    )

    assert handler.has_calls == (response_code == 200)
    assert _get_user_access_info.has_calls
    assert response.status_code == response_code


@pytest.mark.passport_token(token1=TOKEN)
@pytest.mark.config(
    CC_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    CC_AUTHPROXY_PREFIX_ACCESS_RULES=[
        {
            'prefix': '/cc/token',
            'access_rules': [
                {
                    'access_conditions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'name': 'permission_test',
                                        'type': 'permission',
                                    },
                                ],
                            },
                        ],
                    },
                    'path': '/cc/token/test',
                    'method': 'POST',
                    'check_restrictions': True,
                },
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'restrictions,request_body,response_code',
    [
        pytest.param(
            [
                {
                    'handler_path': '/cc/token/test',
                    'handler_method': 'POST',
                    'restriction': {
                        'init': {
                            'arg_name': 'body:project',
                            'set': ['disp', 'vezet'],
                            'set_elem_type': 'string',
                        },
                        'type': 'in_set',
                    },
                },
            ],
            {'project': 'disp'},
            200,
        ),
        pytest.param(
            [
                {
                    'handler_path': '/cc/token/test',
                    'handler_method': 'POST',
                    'restriction': {
                        'init': {
                            'arg_name': 'body:project',
                            'set': ['disp', 'vezet'],
                            'set_elem_type': 'string',
                        },
                        'type': 'in_set',
                    },
                },
            ],
            {'project': 'eda'},
            401,
        ),
        pytest.param([], {'project': 'eda'}, 200),
    ],
)
async def test_restrictions(
        taxi_cc_authproxy,
        cc_request,
        mock_remote,
        mockserver,
        default_response,
        blackbox_service,
        restrictions,
        request_body,
        response_code,
):
    await taxi_cc_authproxy.invalidate_caches()
    handler = mock_remote(url_path='/cc/token/test')

    @mockserver.json_handler('/access-control/v1/get-user-access-info/')
    def _get_user_access_info(request):
        assert request.json == {'provider': 'yandex', 'provider_user_id': UID}

        return {
            'permissions': ['permission_test'],
            'evaluated_permissions': [],
            'restrictions': restrictions,
            'roles': [
                {
                    'role': 'role',
                    'permissions': ['permission_test'],
                    'evaluated_permissions': [],
                    'restrictions': restrictions,
                },
            ],
        }

    response = await cc_request(
        url_path='/cc/token/test', token='token1', request_body=request_body,
    )

    assert handler.has_calls == (response_code == 200)
    assert _get_user_access_info.has_calls
    assert response.status_code == response_code
