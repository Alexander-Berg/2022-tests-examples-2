import copy
import re

import pytest

from tests_authproxy_manager import utils

# Test only rule-type='passenger-authorizer'. We expect all rule types are
# handled in the same way, no need to duplicate tests.


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_create(authproxy_manager, proxy):
    # No rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == []

    rule = copy.deepcopy(utils.PA_BASE_RULE)
    rule['proxy']['webview_cookie_suffixes'] = ['eats', 'grocery']

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 201
    assert response.text == ''

    # The rule is visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [rule]

    # The rule is visible by name
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='/4.0/',
    )
    assert response.status == 200
    assert response.json() == rule

    # The rule is not visible in other proxy's rules
    response = await authproxy_manager.v1_rules(proxy='grocery-authproxy')
    assert response.status == 200
    assert response.json()['rules'] == []

    # The rule is not visible by name w/ other proxy
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy='grocery-authproxy', name='/4.0/',
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'RULE_NOT_FOUND',
        'message': 'Rule not found',
    }


@pytest.mark.parametrize('proxy', ['passenger-authorizer'])
async def test_rule_create_no_priority(authproxy_manager, proxy):
    # No rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == []

    new_rule = copy.deepcopy(utils.PA_BASE_RULE)
    del new_rule['input']['priority']

    # draft is created w/o priority
    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 200
    assert response.json() == {
        'data': new_rule,
        'diff': {'current': {}, 'new': new_rule},
    }

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 201
    assert response.text == ''
    new_rule1 = copy.deepcopy(new_rule)
    new_rule1['input']['priority'] = 100

    new_rule['input']['prefix'] = '/second'
    new_rule['input']['rule_name'] = 'second'
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='second',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 201
    assert response.text == ''
    new_rule2 = copy.deepcopy(new_rule)
    new_rule2['input']['priority'] = 200

    # an actual rule is created with priority
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [new_rule1, new_rule2]


@pytest.mark.parametrize('proxy', ['passenger-authorizer'])
@pytest.mark.parametrize('invalid_rewrite', ['', '/', '///'])
async def test_rule_rewrite_invalid(authproxy_manager, proxy, invalid_rewrite):
    expected_body = {
        'code': 'INVALID_REWRITE',
        'message': 'rewrite_path_prefix should be either missing or non-empty',
    }

    new_rule = copy.deepcopy(utils.PA_BASE_RULE)
    new_rule['output']['rewrite_path_prefix'] = invalid_rewrite

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 400
    assert response.json() == expected_body

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 400
    assert response.json() == expected_body


@pytest.mark.parametrize('proxy', ['passenger-authorizer'])
@pytest.mark.parametrize('rewrite', ['smth', 'some/thing', '/x', 'x/', '/x/'])
async def test_rule_rewrite_ok(authproxy_manager, proxy, rewrite):
    new_rule = copy.deepcopy(utils.PA_BASE_RULE)
    new_rule['output']['rewrite_path_prefix'] = rewrite

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 200
    assert response.json() == {
        'diff': {'current': {}, 'new': new_rule},
        'data': new_rule,
    }

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 201
    assert response.text == ''

    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [new_rule]


async def test_rule_distinct_proxies_same_name(authproxy_manager):
    rules = [
        (utils.adjust_rule({}), 'passenger-authorizer'),
        (
            utils.adjust_rule({'output': {'upstream': 'http://other.com'}}),
            'ya-authproxy',
        ),
    ]

    for rule, proxy in rules:
        response = await authproxy_manager.v1_rules_by_name_put(
            proxy=proxy,
            name='/4.0/',
            maintained_by='common_components',
            rule=rule,
        )
        assert response.status == 201
        assert response.text == ''

    for rule, proxy in rules:
        response = await authproxy_manager.v1_rules(proxy=proxy)
        assert response.status == 200
        assert response.json()['rules'] == [rule]


RULE_UPDATE_NEW_RULES = [
    pytest.param(utils.adjust_rule({}), id='same'),
    pytest.param(
        utils.adjust_rule({'output': {'upstream': 'http://123'}}), id='output',
    ),
    pytest.param(
        utils.adjust_rule({'input': {'rule_name': 'test'}}), id='name',
    ),
    pytest.param(
        utils.adjust_rule({'input': {'maintained_by': 'someone'}}),
        id='maintained_by',
    ),
]


@pytest.mark.parametrize('new_rule', RULE_UPDATE_NEW_RULES)
@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_update(authproxy_manager, proxy, new_rule):
    # create
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    # update
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by=new_rule['input']['maintained_by'],
        rule=new_rule,
    )
    assert response.status == 200

    # The rule is visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [new_rule]

    new_name = new_rule['input']['rule_name']
    # The rule is visible by name
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name=new_name,
    )
    assert response.status == 200
    assert response.json() == new_rule

    # The rule is not visible in other proxy's rules
    response = await authproxy_manager.v1_rules(proxy='grocery-authproxy')
    assert response.status == 200
    assert response.json()['rules'] == []

    # The rule is not visible by name w/ other proxy
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy='grocery-authproxy', name=new_name,
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'RULE_NOT_FOUND',
        'message': 'Rule not found',
    }


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_create_existing(authproxy_manager, proxy):
    new_rule = RULE_UPDATE_NEW_RULES[0].values[0]
    # assert new_rule == {}

    # create
    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
        create=True,
    )
    assert response.status == 200
    assert response.json()['data'] == new_rule

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
        create=True,
    )
    assert response.status == 201

    # try to re-create
    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by=new_rule['input']['maintained_by'],
        rule=new_rule,
        create=True,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'RENAMING_TO_EXISTING_NAME',
        'message': (
            'Trying to use new rule name that already belongs to another rule'
        ),
    }

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by=new_rule['input']['maintained_by'],
        rule=new_rule,
        create=True,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'RENAMING_TO_EXISTING_NAME',
        'message': (
            'Trying to use new rule name that already belongs to another rule'
        ),
    }


@pytest.mark.parametrize(
    'new_rule',
    RULE_UPDATE_NEW_RULES
    + [
        pytest.param(
            utils.adjust_rule({'input': {'rule_name': 'test'}}), id='rename',
        ),
    ],
)
@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_update_draft(authproxy_manager, proxy, new_rule):
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by=new_rule['input']['maintained_by'],
        rule=new_rule,
    )
    assert response.status == 200
    assert response.json() == {
        'data': new_rule,
        'diff': {'current': utils.PA_BASE_RULE, 'new': new_rule},
    }

    # The old rule is visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [utils.PA_BASE_RULE]


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_rename_duplicate_priority(authproxy_manager, proxy):
    rule1 = utils.adjust_rule({})
    rule2 = utils.adjust_rule(
        {'input': {'rule_name': 'other'}, 'output': {'attempts': 2}},
    )

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name=rule1['input']['rule_name'],
        maintained_by='common_components',
        rule=rule1,
    )
    assert response.status == 201
    assert response.text == ''

    args = {
        'proxy': proxy,
        'name': rule2['input']['rule_name'],
        'maintained_by': 'common_components',
        'rule': rule2,
    }
    expected_body = {
        'code': 'TWO_RULES_SAME_PRIORITY',
        'message': (
            'Trying to use new rule priority that already belongs to another '
            'rule'
        ),
    }

    response = await authproxy_manager.v1_rules_by_name_put(**args)
    assert response.status == 400
    assert response.json() == expected_body

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(**args)
    assert response.status == 400
    assert response.json() == expected_body


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_rename_duplicate_name(authproxy_manager, proxy):
    rule1 = utils.adjust_rule({})
    rule2 = utils.adjust_rule(
        {
            'input': {'rule_name': 'other', 'priority': 200},
            'output': {'attempts': 2},
        },
    )

    for rule in (rule1, rule2):
        response = await authproxy_manager.v1_rules_by_name_put(
            proxy=proxy,
            name=rule['input']['rule_name'],
            maintained_by='common_components',
            rule=rule,
        )
        assert response.status == 201
        assert response.text == ''

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name=rule2['input']['rule_name'],
        maintained_by='common_components',
        rule=rule1,
    )
    assert response.status == 400
    assert response.json() == {
        'code': 'RENAMING_TO_EXISTING_NAME',
        'message': (
            'Trying to use new rule name that already belongs to another rule'
        ),
    }


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_rename(authproxy_manager, proxy):
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    new_rule = utils.adjust_rule({'input': {'rule_name': 'test'}})
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=new_rule,
    )
    assert response.status == 200

    # The rule is visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [new_rule]

    # The rule is not visible by the old name
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='/4.0/',
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'RULE_NOT_FOUND',
        'message': 'Rule not found',
    }

    # The rule is visible by the new name
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='test',
    )
    assert response.status == 200
    assert response.json() == new_rule


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_delete_draft(authproxy_manager, proxy):
    response = await authproxy_manager.v1_rules_by_name_check_draft_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 200
    assert response.json() == {'data': {}, 'diff': {'current': {}, 'new': {}}}

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_by_name_check_draft_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 200
    assert response.json() == {
        'data': {},
        'diff': {'current': utils.PA_BASE_RULE, 'new': {}},
    }

    # The old rule is visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [utils.PA_BASE_RULE]


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_delete(authproxy_manager, proxy):
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_by_name_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 204

    for proxy2 in {
            'passenger-authorizer',
            'ya-authproxy',
            'grocery-authproxy',
    }:
        # The rule is not visible in rules
        response = await authproxy_manager.v1_rules(proxy=proxy2)
        assert response.status == 200
        assert response.json()['rules'] == []

        # The rule is not visible by name
        response = await authproxy_manager.v1_rules_by_name_get(
            proxy=proxy2, name='/4.0/',
        )
        assert response.status == 404
        assert response.json() == {
            'code': 'RULE_NOT_FOUND',
            'message': 'Rule not found',
        }


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_delete_nonexisting(authproxy_manager, proxy):
    response = await authproxy_manager.v1_rules_by_name_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 204


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_delete_twice(authproxy_manager, proxy):
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_by_name_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 204

    response = await authproxy_manager.v1_rules_by_name_delete(
        proxy=proxy, name='/4.0/', maintained_by='common_components',
    )
    assert response.status == 204


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_create_maintained_mismatch(authproxy_manager, proxy):
    expected_body = {
        'code': 'MAINTAINED_BY_MISMATCH',
        'message': '\'maintained-by\' in query and in body mismatch',
    }

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='someone else',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 400
    assert response.json() == expected_body

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='someone else',
        rule=utils.PA_BASE_RULE,
    )
    assert response.status == 400
    assert response.json() == expected_body


@pytest.mark.parametrize('proxy', ['passenger-authorizer', 'ya-authproxy'])
async def test_rule_create_invalid_rule_name(authproxy_manager, proxy):
    rule = utils.adjust_rule({'rule_type': 'int-authproxy'})
    rule['proxy'] = {}

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 400
    assert response.json()['code'] == 'INVALID_RULE_TYPE'


async def test_abrupted_probability(authproxy_manager):
    proxy = 'passenger-authorizer'
    rule = copy.deepcopy(utils.PA_BASE_RULE)
    rule['input']['probability'] = 50

    expected_body = {
        'code': 'HIGHEST_PRIORITY_RULE_PROBABILITY_IS_SET',
        'message': (
            'The highest priority rule (\'/4.0/\' with priority 100) with '
            'the prefix \'/4.0/\' has the probability set after the change. '
            'It means that the request that goes to \'/4.0/\' prefix '
            'might get no routing rule. '
            'Please change the rules, so that the last rule '
            'has no probability set.'
        ),
    }

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 400
    assert response.json() == expected_body

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 400
    assert response.json() == expected_body


PARSE_ERROR_REGEX = re.compile(
    'Parse error at pos [0-9]*, path \'[a-z_./]*\': '
    'Unknown key \'(.*)\' at path \'[a-z_./]*\' for type \'[a-z:A-Z]*\'',
)


@pytest.mark.parametrize(
    'rule',
    [
        pytest.param(utils.adjust_rule({'input': {'extra': '1'}}), id='input'),
        pytest.param(utils.adjust_rule({'proxy': {'extra': '1'}}), id='proxy'),
        pytest.param(
            utils.adjust_rule({'proxy': {'personal': {'extra': 1}}}),
            id='personal',
        ),
        pytest.param(utils.adjust_rule({'extra': 1}), id='root'),
        pytest.param(
            utils.adjust_rule({'output': {'extra': '1'}}), id='output',
        ),
    ],
)
async def test_unknown_field_pa(authproxy_manager, rule):
    proxy = 'passenger-authorizer'

    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 400

    msg = response.json()['message']
    match = PARSE_ERROR_REGEX.match(msg)
    assert match, f'Message was: {msg}'
    assert match.group(1) == 'extra'

    assert response.json() == {'code': '400', 'message': msg}

    response = await authproxy_manager.v1_rules_by_name_check_draft_put(
        proxy=proxy,
        name='/4.0/',
        maintained_by='common_components',
        rule=rule,
    )
    assert response.status == 400
    # The same error message
    assert response.json() == {'code': '400', 'message': msg}
