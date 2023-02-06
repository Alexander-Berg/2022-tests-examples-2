import pytest

from tests_authproxy_manager import utils


RULES = [
    {
        'prefix': 'auth',
        'server-hosts': ['*'],
        'to': 'http://1',
        'tvm-service': 'mock',
    },
    {
        'prefix': 'authorization',
        'server-hosts': ['*'],
        'to': 'http://2',
        'tvm-service': 'mock',
    },
    {
        'prefix': 'incorrekt/autorization',
        'server-hosts': ['*'],
        'to': 'http://3',
        'tvm-service': 'mock',
    },
    {
        'prefix': 'someauth',
        'server-hosts': ['*'],
        'to': 'http://4',
        'tvm-service': 'mock',
    },
]


@pytest.mark.parametrize(
    'filters,result',
    [
        ({}, ['1', '2', '3', '4']),
        ({'prefix_substring': 'auth'}, ['1', '2', '4']),
        ({'prefix_substring': 'a'}, ['1', '2', '3', '4']),
        ({'prefix_substring': 'missing'}, []),
        ({'name_substring': 'auth'}, ['1', '2', '4']),
        ({'name_substring': 'missing'}, []),
        ({'prefix_substring': 'auth', 'name_substring': 'ion'}, ['2']),
        ({'maintained_by': 'missing'}, []),
        ({'maintained_by': 'common_components'}, ['1', '2', '3', '4']),
    ],
)
@pytest.mark.config(PASS_AUTH_ROUTER_RULES_2=RULES)
async def test_filter(authproxy_manager, filters, result):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=proxy, filters=filters)
    assert response.status == 200
    rules = response.json()['rules']
    upstreams = [r['output']['upstream'][7:] for r in rules]
    assert upstreams == result


@pytest.mark.config(
    PASS_AUTH_ROUTER_RULES_2=RULES, AUTHPROXY_MANAGER_RULES_PAGE_SIZE=1,
)
async def test_filter_in_cursor(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    filters = {'name_substring': 'auth'}
    # => 1 2 4

    response = await authproxy_manager.v1_rules(proxy=proxy, filters=filters)
    assert response.status == 200
    res = response.json()
    rules = res['rules']
    cursor = res['cursor']

    for _ in [1, 2]:
        response = await authproxy_manager.v1_rules(proxy=proxy, cursor=cursor)
        assert response.status == 200
        res = response.json()
        rules += res['rules']
        cursor = res['cursor']

    response = await authproxy_manager.v1_rules(proxy=proxy, cursor=cursor)
    assert response.status == 200
    assert response.json() == {'rules': []}

    upstreams = [r['output']['upstream'][7:] for r in rules]
    assert upstreams == ['1', '2', '4']


async def test_filter_conflict(authproxy_manager):
    response = await authproxy_manager.v1_rules(
        proxy='passenger-authorizer', cursor='123', filters={},
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'CURSOR_AND_FILTER_CONFLICT',
        'message': '\'cursor\' and \'filter\' are mutually exclusive',
    }


@pytest.mark.parametrize(
    'name,num', [('auth', 1), ('someauth', 4), ('missing', None)],
)
@pytest.mark.config(PASS_AUTH_ROUTER_RULES_2=RULES)
async def test_rules_by_name(authproxy_manager, name, num):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules_by_name_get(
        proxy='passenger-authorizer', name=name,
    )
    if num is not None:
        assert response.status == 200

        expected_rule = utils.adjust_rule(
            {
                'input': {
                    'prefix': name,
                    'rule_name': name,
                    'priority': num * 100,
                },
                'output': {'upstream': f'http://{num}'},
            },
        )
        assert response.json() == expected_rule
    else:
        assert response.status == 404
        assert response.json() == {
            'code': 'RULE_NOT_FOUND',
            'message': 'Rule not found',
        }
