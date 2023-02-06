import base64
import json

import pytest

from tests_authproxy_manager import utils


TWO_RULES = [
    {
        'prefix': '/4.0/',
        'server-hosts': ['*'],
        'to': 'http://example.com',
        'attempts': 1,
        'tvm-service': 'mock',
        'probability-percent': 30,
    },
    {
        'prefix': '/4.0/',
        'server-hosts': ['*'],
        'to': 'http://sample.com',
        'attempts': 1,
        'tvm-service': 'mock',
        'probability-percent': 70,
    },
]


@pytest.mark.config(
    PASS_AUTH_ROUTER_RULES_2=TWO_RULES, AUTHPROXY_MANAGER_RULES_PAGE_SIZE=1,
)
async def test_cursor(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    # rule 1
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [
        utils.adjust_rule({'input': {'probability': 30}}),
    ]

    cursor = response.json()['cursor']
    assert json.loads(base64.b64decode(cursor)) == {
        'Priority': 100,
        'Filter': {},
    }

    # rule 2
    response = await authproxy_manager.v1_rules(proxy=proxy, cursor=cursor)
    assert response.status == 200
    assert response.json()['rules'] == [
        utils.adjust_rule(
            {
                'input': {
                    'priority': 200,
                    'probability': 70,
                    'rule_name': '/4.0/ 1',
                },
                'output': {'upstream': 'http://sample.com'},
            },
        ),
    ]

    # no more rules
    cursor = response.json()['cursor']
    assert json.loads(base64.b64decode(cursor)) == {
        'Priority': 200,
        'Filter': {},
    }

    response = await authproxy_manager.v1_rules(proxy=proxy, cursor=cursor)
    assert response.status == 200
    assert response.json() == {'rules': []}


@pytest.mark.config(
    PASS_AUTH_ROUTER_RULES_2=TWO_RULES, AUTHPROXY_MANAGER_RULES_PAGE_SIZE=1,
)
async def test_limit(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=proxy, limit=2)
    assert response.status == 200
    assert response.json()['rules'] == [
        utils.adjust_rule({'input': {'probability': 30}}),
        utils.adjust_rule(
            {
                'input': {
                    'priority': 200,
                    'probability': 70,
                    'rule_name': '/4.0/ 1',
                },
                'output': {'upstream': 'http://sample.com'},
            },
        ),
    ]


@pytest.mark.config(AUTHPROXY_MANAGER_IMPORT_PROXY_LIST=[])
async def test_import_is_forbidden(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 400
    assert response.json()['code'] == 'IMPORT_IS_FORBIDDEN'

    response = await authproxy_manager.v1_rules_import_draft(proxy=proxy)
    assert response.status == 400
    assert response.json()['code'] == 'IMPORT_IS_FORBIDDEN'


@pytest.mark.config(
    PASS_AUTH_ROUTER_RULES_2=[
        {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
    ],
)
@utils.default_dev_team_by_proxy('passenger-authorizer', 'other_group')
async def test_default_maintainer(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [
        utils.adjust_rule({'input': {'maintained_by': 'other_group'}}),
    ]


@pytest.mark.config(
    PASS_AUTH_ROUTER_RULES_2=[
        {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
    ],
)
@utils.default_dev_team_by_proxy('passenger-authorizer', 'other_group')
async def test_draft(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import_draft(proxy=proxy)
    assert response.status == 200
    assert response.json() == {'data': {}}

    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == []


@pytest.mark.config(AUTHPROXY_MANAGER_DEFAULT_DEV_TEAM_BY_PROXY={})
async def test_no_default_dev_team(authproxy_manager):
    proxy = 'passenger-authorizer'
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 400
    assert response.json()['code'] == 'NO_DEFAULT_DEV_TEAM'

    response = await authproxy_manager.v1_rules_import_draft(proxy=proxy)
    assert response.status == 400
    assert response.json()['code'] == 'NO_DEFAULT_DEV_TEAM'
