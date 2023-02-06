import copy


PGW_BASE_RULE = {
    'input': {
        'prefix': '/test/',
        'rule_name': '/test/',
        'description': 'description',
        'priority': 100,
        'maintained_by': 'partner_product_backend_1',
    },
    'proxy': {},
    'output': {
        'upstream': 'http://example.com',
        'tvm_service': 'mock',
        'timeout_ms': 1000,
        'attempts': 1,
    },
    'rule_type': 'pro-gateway',
}


async def test_rule_crud(authproxy_manager):
    proxy = 'pro-gateway'

    # No rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == []

    rule = copy.deepcopy(PGW_BASE_RULE)

    # create
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/test/',
        maintained_by='partner_product_backend_1',
        rule=rule,
    )
    assert response.status == 201
    assert response.text == ''

    # The rule is visible in proxy's rules (read)
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == [rule]

    # The rule is visible by name (read)
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='/test/',
    )
    assert response.status == 200
    assert response.json() == rule

    # update
    rule['input']['maintained_by'] = 'someone'
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name='/test/',
        maintained_by=rule['input']['maintained_by'],
        rule=rule,
    )
    assert response.status == 200

    # The rule is still visible
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='/test/',
    )
    assert response.status == 200
    assert response.json() == rule

    # delete
    response = await authproxy_manager.v1_rules_by_name_delete(
        proxy=proxy,
        name='/test/',
        maintained_by=rule['input']['maintained_by'],
    )
    assert response.status == 204

    # The rule is not visible in proxy's rules
    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json()['rules'] == []

    # The rule is not visible by name
    response = await authproxy_manager.v1_rules_by_name_get(
        proxy=proxy, name='/test/',
    )
    assert response.status == 404
    assert response.json() == {
        'code': 'RULE_NOT_FOUND',
        'message': 'Rule not found',
    }
