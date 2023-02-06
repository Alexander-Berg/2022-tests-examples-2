import pytest

from tests_authproxy_manager import utils


PROXY = 'driver-authproxy'


async def test_import_empty(authproxy_manager, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=PROXY)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=PROXY)
    assert response.status == 200
    assert response.json() == {'rules': []}

    assert_proxy_rules_count(pgsql, PROXY, 0)


def assert_proxy_rules_count(pgsql, proxy, count):
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert [(count,)] == list(cursor)


@pytest.mark.config(
    DRIVER_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/driver/v1/auth'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {'server-hosts': ['*']},
        },
    ],
)
async def test_simple(authproxy_manager, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=PROXY)
    assert response.status == 200

    # No extra rules in DB
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{PROXY}\'',
    )
    assert [(1,)] == list(cursor)

    await utils.compare_rules(
        authproxy_manager,
        rules=[
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/auth',
                    'priority': 100,
                    'rule_name': '/driver/v1/auth',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': False,
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
        ],
        key='driver-authproxy-rules',
        proxy=PROXY,
    )


@pytest.mark.config(
    DRIVER_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/driver/v1/noauth'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {'proxy-401': True, 'server-hosts': ['*']},
        },
        {
            'input': {'http-path-prefix': '/driver/v1/noauth/cookie'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {
                'cookie-enabled': True,
                'cookies-to-proxy': ['foobarcookie'],
                'proxy-401': True,
                'server-hosts': ['*'],
            },
        },
        {
            'input': {'http-path-prefix': '/driver/v1/auth'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {'server-hosts': ['*']},
        },
        {
            'input': {'http-path-prefix': '/driver/v1/cookie'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {
                'cookie-enabled': True,
                'cookies-to-proxy': ['foobarcookie'],
                'server-hosts': ['*'],
            },
        },
        {
            'input': {'http-path-prefix': '/driver/v1/passport_only'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {
                'auth-type': 'optional-passport-only',
                'cookie-enabled': True,
                'server-hosts': ['*'],
            },
        },
        {
            'input': {
                'http-path-prefix': '/driver/v1/probability_percent/30_70',
            },
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com/30',
            },
            'proxy': {
                'cookie-enabled': True,
                'probability-percent': 30,
                'server-hosts': ['*'],
            },
        },
        {
            'input': {
                'http-path-prefix': '/driver/v1/probability_percent/30_70',
            },
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com/70',
            },
            'proxy': {
                'cookie-enabled': True,
                'probability-percent': 70,
                'server-hosts': ['*'],
            },
        },
    ],
)
async def test_rule_all_options(authproxy_manager, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=PROXY)
    assert response.status == 200

    # No extra rules in DB
    assert_proxy_rules_count(pgsql, PROXY, 7)

    await utils.compare_rules(
        authproxy_manager,
        rules=[
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/noauth',
                    'priority': 100,
                    'rule_name': '/driver/v1/noauth',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': False,
                    'proxy-401': True,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/noauth/cookie',
                    'priority': 200,
                    'rule_name': '/driver/v1/noauth/cookie',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': True,
                    'cookies-to-proxy': ['foobarcookie'],
                    'proxy-401': True,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/auth',
                    'priority': 300,
                    'rule_name': '/driver/v1/auth',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': False,
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/cookie',
                    'priority': 400,
                    'rule_name': '/driver/v1/cookie',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': True,
                    'cookies-to-proxy': ['foobarcookie'],
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/passport_only',
                    'priority': 500,
                    'rule_name': '/driver/v1/passport_only',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth-type': 'optional-passport-only',
                    'cookies-enabled': True,
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/probability_percent/30_70',
                    'priority': 600,
                    'probability': 30,
                    'rule_name': '/driver/v1/probability_percent/30_70',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com/30',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': True,
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'driver_authproxy_rules',
                    'prefix': '/driver/v1/probability_percent/30_70',
                    'priority': 700,
                    'probability': 70,
                    'rule_name': '/driver/v1/probability_percent/30_70 1',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com/70',
                },
                'proxy': {
                    'auth-type': 'driver-session',
                    'cookies-enabled': True,
                    'proxy-401': False,
                },
                'rule_type': 'driver-authproxy',
            },
        ],
        key='driver-authproxy-rules',
        proxy=PROXY,
    )
