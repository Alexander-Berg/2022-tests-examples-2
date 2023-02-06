import pytest

from tests_authproxy_manager import utils


PROXY = 'int-authproxy'


async def test_import_empty(authproxy_manager, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=PROXY)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=PROXY)
    assert response.status == 200
    assert response.json() == {'rules': []}

    assert_proxy_rules_count(pgsql, PROXY, 0)


def proxy_with_config(rules, *, extra=(), name):
    return [
        pytest.param(
            *extra,
            marks=[pytest.mark.config(INT_AUTHPROXY_ROUTE_RULES=rules)],
            id=name,
        ),
    ]


def assert_proxy_rules_count(pgsql, proxy, count):
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert (count,) == cursor.fetchone()


@pytest.mark.config(
    INT_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/test'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
            },
            'proxy': {},
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
                    'maintained_by': 'common_components',
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
                'proxy': {},
                'rule_type': 'int-authproxy',
            },
        ],
        key='int-authproxy-rules',
        proxy=PROXY,
    )


@pytest.mark.config(
    INT_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/test'},
            'output': {
                'tvm-service': 'test',
                'upstream': 'http://example.com',
                'timeout-ms': 999,
                'attempts': 10,
            },
            'proxy': {'path-rewrite-strict': '/rewrite'},
        },
    ],
)
async def test_rule_all_options(authproxy_manager, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=PROXY)
    assert response.status == 200

    # No extra rules in DB
    assert_proxy_rules_count(pgsql, PROXY, 1)

    await utils.compare_rules(
        authproxy_manager,
        rules=[
            {
                'input': {
                    'description': '(imported from taxi config)',
                    'maintained_by': 'common_components',
                    'prefix': '/test',
                    'priority': 100,
                    'rule_name': '/test',
                },
                'output': {
                    'attempts': 10,
                    'timeout_ms': 999,
                    'tvm_service': 'test',
                    'upstream': 'http://example.com',
                    'rewrite_path_prefix': '/rewrite',
                },
                'proxy': {},
                'rule_type': 'int-authproxy',
            },
        ],
        key='int-authproxy-rules',
        proxy=PROXY,
    )
