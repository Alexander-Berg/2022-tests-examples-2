import copy

import pytest


PA_BASE_RULE = {
    'input': {
        'prefix': '/4.0/',
        'rule_name': '/4.0/',
        'description': '(imported from taxi config)',
        'priority': 100,
        'maintained_by': 'common_components',
    },
    'proxy': {
        'auth_type': 'oauth-or-session',
        'late_login_allowed': False,
        'dbusers_authorization_allowed': False,
        'parse_user_id_from_json_body': False,
        'phone_validation': 'disabled',
        'personal': {
            'email_id': False,
            'phone_id': False,
            'bounded_uids': False,
            'eater_id': False,
            'eats_phone_id': False,
            'eats_email_id': False,
            'eater_uuid': False,
            'staff_login': False,
        },
        'proxy_401': False,
    },
    'output': {
        'upstream': 'http://example.com',
        'tvm_service': 'mock',
        'timeout_ms': 1000,
        'attempts': 1,
    },
    'rule_type': 'passenger-authorizer',
}


def merge_data(base, extra) -> dict:
    if base is None:
        return extra

    if not isinstance(extra, dict):
        return extra

    for key in extra:
        base[key] = merge_data(base.get(key), extra[key])
    return base


def adjust_rule(extra: dict) -> dict:
    return merge_data(copy.deepcopy(PA_BASE_RULE), extra)


async def compare_rules(authproxy_manager, rules, key, **kwargs):
    response = await authproxy_manager.v1_rules(**kwargs)
    assert response.status == 200
    assert response.json() == {'rules': rules}


def default_dev_team_by_proxy(proxy_name, dev_team):
    default = {
        'passenger-authorizer': 'common_components',
        'grocery-authproxy': 'common_components',
        'ya-authproxy': 'common_components',
        'int-authproxy': 'common_components',
        'eats-authproxy-common': 'eats_common_components',
    }

    assert proxy_name in default.keys()

    default[proxy_name] = dev_team

    return pytest.mark.config(
        AUTHPROXY_MANAGER_DEFAULT_DEV_TEAM_BY_PROXY=default,
    )
