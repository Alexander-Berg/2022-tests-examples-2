import pytest


AM_ROUTE_RULES = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/proxy_no_cookie',
            'priority': 100,
            'rule_name': '/proxy_no_cookie',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/proxy_no_cookie',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': [],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'eats_common_components',
            'prefix': '/proxy_some_cookie',
            'priority': 100,
            'rule_name': '/proxy_some_cookie',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/proxy_some_cookie',
            'timeout_ms': 100,
            'tvm_service': 'mock',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {
            'auth_type': 'session',
            'cookie_webview_enabled': False,
            'passport_scopes': [],
            'proxy_cookie': ['some_cookie_1', 'some_cookie_2'],
            'personal': {
                'eater_id': True,
                'eater_uuid': True,
                'email_id': True,
                'phone_id': True,
            },
            'proxy_401': False,
        },
        'rule_type': 'eats-authproxy',
    },
]


@pytest.mark.parametrize(
    'path,cookies',
    [
        pytest.param('/proxy_no_cookie', [], id='no_cookies'),
        pytest.param(
            '/proxy_some_cookie',
            ['some_cookie_1', 'some_cookie_2'],
            id='has_cookies',
        ),
    ],
)
@pytest.mark.eater_session(outer={'inner': 'in', 'eater_id': '100'})
@pytest.mark.eater(i100={'id': '100'})
@pytest.mark.routing_rules(AM_ROUTE_RULES)
async def test_rewrite(
        mock_core_eater,
        mock_eater_authorizer,
        mockserver,
        request_proxy,
        path,
        cookies,
):
    @mockserver.json_handler(path)
    def test_handle(request):
        assert len(request.cookies) == len(cookies) + 1
        assert 'PHPSESSID' in request.cookies
        for cookie in cookies:
            assert cookie in request.cookies
            assert request.cookies[cookie] == ('val' + cookie)

    request_cookie = {}
    for cookie in cookies:
        request_cookie[cookie] = 'val' + cookie

    response = await request_proxy(
        auth_method=None, url=path, cookies=request_cookie,
    )
    assert response.status_code == 200
    assert test_handle.times_called == 1
