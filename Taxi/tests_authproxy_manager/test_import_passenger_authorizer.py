import pytest

from tests_authproxy_manager import utils


@pytest.mark.parametrize(
    'proxy', ['passenger-authorizer', 'grocery-authproxy', 'ya-authproxy'],
)
async def test_import_empty(authproxy_manager, proxy, pgsql):
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    response = await authproxy_manager.v1_rules(proxy=proxy)
    assert response.status == 200
    assert response.json() == {'rules': []}

    assert_proxy_rules_count(pgsql, proxy, 0)


def proxy_with_config(rules, *, extra=(), name, exclude=None):
    if exclude is None:
        exclude = ()

    result = []
    if 'passenger-authorizer' not in exclude:
        result.append(
            pytest.param(
                'passenger-authorizer',
                *extra,
                marks=[pytest.mark.config(PASS_AUTH_ROUTER_RULES_2=rules)],
                id='pa/' + name,
            ),
        )

    if 'grocery-authproxy' not in exclude:
        result.append(
            pytest.param(
                'grocery-authproxy',
                *extra,
                marks=[
                    pytest.mark.config(GROCERY_AUTHPROXY_ROUTER_RULES=rules),
                ],
                id='grocery-authproxy/' + name,
            ),
        )

    if 'ya-authproxy' not in exclude:
        result.append(
            pytest.param(
                'ya-authproxy',
                *extra,
                marks=[pytest.mark.config(YA_AUTHPROXY_ROUTER_RULES_2=rules)],
                id='ya-authproxy/' + name,
            ),
        )

    return result


def assert_proxy_rules_count(pgsql, proxy, count):
    cursor = pgsql['authproxy_manager'].cursor()
    cursor.execute(
        f'SELECT count(*) FROM authproxy_manager.rules '
        f'WHERE proxy = \'{proxy}\'',
    )
    assert [(count,)] == list(cursor)


@pytest.mark.parametrize(
    'proxy,',
    proxy_with_config(
        [
            {
                'prefix': '/4.0/',
                'server-hosts': ['*'],
                'to': 'http://example.com',
                'timeout-ms': 1000,
                'attempts': 1,
                'tvm-service': 'mock',
            },
        ],
        name='x',
    ),
)
async def test_simple(authproxy_manager, proxy, pgsql):
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
        rules=[utils.PA_BASE_RULE],
        key='passenger-authorizer-rules',
        proxy=proxy,
    )


@pytest.mark.parametrize(
    'proxy,',
    proxy_with_config(
        [
            {
                'prefix': '/4.0/',
                'server-hosts': ['*'],
                'to': 'http://example.com',
                'attempts': 1,
                'tvm-service': 'mock',
            },
        ],
        name='x',
    ),
)
async def test_no_timeout(authproxy_manager, proxy, pgsql):
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
        rules=[utils.PA_BASE_RULE],
        key='passenger-authorizer-rules',
        proxy=proxy,
    )


# Compare that rule['config'] in taxi config is converted to rule['service']
# in DB.
#
# Note: rule['service'] are almost the same except 1-2 fields, so it is
# compiled from PA_BASE_RULE + explicit patch to avoid JSON copy-paste.
RULES_LIST = [
    {
        'name': 'base',
        'config': {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({}),
    },
    {
        'name': 'proxy-cookie',
        'config': {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
            'cookies-to-proxy': ['x', 'y'],
        },
        'service': utils.adjust_rule({'proxy': {'proxy_cookie': ['x', 'y']}}),
    },
    {
        'name': 'proxy401',
        'config': {
            'prefix': '/4.0/',
            'proxy-401': True,
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'proxy': {'proxy_401': True}}),
    },
    {
        'name': 'cookie-suffix-root',
        'config': {
            'cookie-enabled': True,
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({}),
    },
    {
        'name': 'cookie-suffix',
        'config': {
            'cookie-enabled': True,
            'cookie-suffix': 'eats',
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'webview_cookie_suffix': 'eats'}},
        ),
        # PA/YA
        'exclude': ['ya-authproxy'],
    },
    {
        'name': 'eats-phpsessid',
        'config': {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
            'check-eats-php-session-id': True,
        },
        'service': utils.adjust_rule(
            {'proxy': {'auth_type': 'eats-php-session-id'}},
        ),
        # PA / ya-authproxy
        'exclude': ['grocery-authproxy'],
    },
    {
        'name': 'csrf-token-generator',
        'config': {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
            'csrf-token-generator': True,
        },
        'service': utils.adjust_rule(
            {'proxy': {'auth_type': 'csrf-token-generator'}},
        ),
        # No CSRF in PA
        'exclude': ['passenger-authorizer'],
    },
    {
        'name': 'passport-scopes',
        'config': {
            'passport-scopes': ['scope'],
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'passport_scopes': ['scope']}},
        ),
    },
    {
        'name': 'phone-validation-rule=proxy',
        'config': {
            'passport-scopes': [],
            'phone-validation-rule': 'proxy',
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'phone_validation': 'proxy', 'passport_scopes': []}},
        ),
    },
    {
        'name': 'phone-validation-rule=strict',
        'config': {
            'phone-validation-rule': 'strict',
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'phone_validation': 'strict'}},
        ),
    },
    {
        'name': 'parse-user-id-from-body=True',
        'config': {
            'parse-user-id-from-body': True,
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'parse_user_id_from_json_body': True}},
        ),
    },
    {
        'name': 'phone_id=True',
        'config': {
            'personal': {'phone_id': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'personal': {'phone_id': True}}},
        ),
    },
    {
        'name': 'email_id=True',
        'config': {
            'personal': {'email_id': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'personal': {'email_id': True}}},
        ),
    },
    {
        'name': 'email_id=True,phone_id=True',
        'config': {
            'personal': {'email_id': True, 'phone_id': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'personal': {'phone_id': True, 'email_id': True}}},
        ),
    },
    {
        'name': 'eats_email_id=True,eats_phone_id=True',
        'config': {
            'personal': {
                'need_eats_email_id': True,
                'need_eats_phone_id': True,
            },
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {
                'proxy': {
                    'personal': {'eats_phone_id': True, 'eats_email_id': True},
                },
            },
        ),
    },
    {
        'name': 'bounded_uids=True',
        'config': {
            'personal': {'bounded_uids': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'personal': {'bounded_uids': True}}},
        ),
    },
    {
        'name': 'eater_id',
        'config': {
            'personal': {'need_eats_user_info': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'personal': {'eater_id': True}}},
        ),
    },
    {
        'name': 'eater_id',
        'config': {
            'personal': {
                'need_eats_user_info': True,
                'need_eats_phone_id': True,
                'need_eats_email_id': True,
            },
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {
                'proxy': {
                    'personal': {
                        'eater_id': True,
                        'eats_phone_id': True,
                        'eats_email_id': True,
                        'eater_uuid': (
                            False  # new field - false after conversion
                        ),
                        'staff_login': False,
                    },
                },
            },
        ),
    },
    {
        'name': 'courier-jwt',
        'config': {
            'check-user-id-in-db': False,
            'parse-user-id-from-jwt': True,
            'personal': {},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'proxy': {'auth_type': 'courier-jwt'}}),
        # was not implemented in GAP
        'exclude': ['grocery-authproxy'],
    },
    {
        'name': 'probability',
        'config': {
            'prefix': '/4.0/',
            'probability-percent': 30,
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'input': {'probability': 30}}),
    },
    {
        'name': 'probability-0',
        'config': {
            'prefix': '/4.0/',
            'probability-percent': 0,
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'input': {'probability': 0}}),
    },
    {
        'name': 'probability-100',
        'config': {
            'prefix': '/4.0/',
            'probability-percent': 100,
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'input': {'probability': 100}}),
    },
    {
        'name': 'only-token',
        'config': {
            'check-session-id-cookie': False,
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'proxy': {'auth_type': 'oauth'}}),
    },
    {
        'name': 'late-login',
        'config': {
            'allow-late-login': True,
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule({'proxy': {'late_login_allowed': True}}),
    },
    {
        'name': 'user-id-generator',
        'config': {
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
            'user-id-generator': True,
        },
        'service': utils.adjust_rule(
            {'proxy': {'auth_type': 'user-id-generator'}},
        ),
    },
    {
        'name': 'user-id-generator-with-late-login',
        'config': {
            'allow-late-login': True,
            'personal': {'email_id': True, 'phone_id': True},
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
            'user-id-generator': True,
        },
        'service': utils.adjust_rule(
            {
                'proxy': {
                    'auth_type': 'user-id-generator',
                    'late_login_allowed': True,
                    'personal': {'phone_id': True, 'email_id': True},
                },
            },
        ),
    },
    {
        'name': 'dbusers-authorized',
        'config': {
            'allow-dbusers-authorized': True,
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'service': utils.adjust_rule(
            {'proxy': {'dbusers_authorization_allowed': True}},
        ),
        # not implemented for GAP
        'exclude': ['grocery-authproxy'],
    },
]


def flatten(data):
    return [item for sublist in data for item in sublist]


@pytest.mark.config(PASS_AUTH_COOKIE_PATHS={'eats': '123', 'root': ''})
@pytest.mark.parametrize(
    'proxy,result',
    flatten(
        [
            proxy_with_config(
                [rule['config']],
                extra=(rule['service'],),
                name=rule['name'],
                exclude=rule.get('exclude'),
            )
            for rule in RULES_LIST
        ],
    ),
)
async def test_rule_ok(authproxy_manager, proxy, pgsql, result):
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 200

    # No extra rules in DB
    assert_proxy_rules_count(pgsql, proxy, 1)

    await utils.compare_rules(
        authproxy_manager,
        rules=[result],
        key='passenger-authorizer-rules',
        proxy=proxy,
    )


INVALID_RULES = [
    {
        'name': 'cookie-suffix',
        'config': {
            'cookie-enabled': True,
            # suffix not in PASS_AUTH_COOKIE_PATHS
            'cookie-suffix': 'eats',
            'prefix': '/4.0/',
            'server-hosts': ['*'],
            'to': 'http://example.com',
            'tvm-service': 'mock',
        },
        'message': (
            'Validation failed (prefix=/4.0/): cookie_suffix=eats is missing '
            'in PASS_AUTH_COOKIE_PATHS'
        ),
        # PA-specific
        'exclude': ['ya-authproxy', 'grocery-authproxy'],
    },
]


@pytest.mark.parametrize(
    'proxy,message',
    flatten(
        [
            proxy_with_config(
                [rule['config']],
                extra=(rule['message'],),
                name=rule['name'],
                exclude=rule.get('exclude'),
            )
            for rule in INVALID_RULES
        ],
    ),
)
@pytest.mark.config(PASS_AUTH_COOKIE_PATHS={})
async def test_rule_invalid(authproxy_manager, proxy, pgsql, message):
    response = await authproxy_manager.v1_rules_import(proxy=proxy)
    assert response.status == 400
    assert response.json() == {'code': 'VALIDATION_FAILED', 'message': message}

    # No rule is imported
    assert_proxy_rules_count(pgsql, proxy, 0)
