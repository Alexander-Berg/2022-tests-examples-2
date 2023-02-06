import pytest

from tests_authproxy_manager import utils


async def test_import_empty(authproxy_manager, pgsql):
    proxy = 'eats-authproxy'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json() == {'rules': []}

    assert_proxy_rules_count(pgsql, proxy, 0)


def assert_proxy_rules_count(pgsql, proxy, count):
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert (count,) == cursor.fetchone()


SIMPLE_ROUTES = [
    {
        'input': {'http-path-prefix': '/test'},
        'output': {'tvm-service': 'test', 'upstream': 'http://example.com'},
        'proxy': {},
    },
]


@pytest.mark.config(EATS_AUTHPROXY_ROUTE_RULES=SIMPLE_ROUTES)
async def test_simple(authproxy_manager, pgsql):
    proxy = 'eats-authproxy'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    # No extra rules in DB
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert [(1,)] == list(cursor)

    await utils.compare_rules(
        authproxy_manager,
        rules=[
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'eats_common_components',
                    'prefix': '/test',
                    'priority': 100,
                    'rule_name': '/test',
                },
                'output': {
                    'attempts': 1,
                    'timeout_ms': 100,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'auth_type': 'session',
                    'cookie_webview_enabled': False,
                    'proxy_401': False,
                    'personal': {
                        'eater_id': True,
                        'phone_id': True,
                        'email_id': True,
                        'eater_uuid': False,
                    },
                },
                'rule_type': 'eats-authproxy',
            },
        ],
        key='eats-authproxy-rules',
        proxy=proxy,
    )


FULL_ROUTES = [
    {
        'input': {
            'http-path-prefix': '/test',
            'passport-scopes': ['some_scope'],
            'probability': 30,
        },
        'output': {
            'tvm-service': 'test',
            'upstream': 'http://example.com',
            'timeout-ms': 999,
            'attempts': 10,
        },
        'proxy': {
            'server-hosts': ['"*"'],
            'proxy-401': True,
            'auth-type': 'session-eater-id-generator',
            'cookie-webview-enabled': True,
        },
    },
]


@pytest.mark.config(EATS_AUTHPROXY_ROUTE_RULES=FULL_ROUTES)
async def test_rule_all_options(authproxy_manager, pgsql):
    proxy = 'eats-authproxy'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    # No extra rules in DB
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert [(1,)] == list(cursor)

    await utils.compare_rules(
        authproxy_manager,
        rules=[
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'eats_common_components',
                    'prefix': '/test',
                    'priority': 100,
                    'rule_name': '/test',
                    'probability': 30,
                },
                'output': {
                    'attempts': 10,
                    'timeout_ms': 999,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                },
                'proxy': {
                    'passport_scopes': ['some_scope'],
                    'auth_type': 'session-eater-id-generator',
                    'cookie_webview_enabled': True,
                    'proxy_401': True,
                    'personal': {
                        'eater_id': True,
                        'phone_id': True,
                        'email_id': True,
                        'eater_uuid': False,
                    },
                },
                'rule_type': 'eats-authproxy',
            },
        ],
        key='eats-authproxy-rules',
        proxy=proxy,
    )
