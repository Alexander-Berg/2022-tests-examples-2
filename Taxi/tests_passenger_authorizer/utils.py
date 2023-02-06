import copy


BASE_RULE = {
    'input': {
        'description': '(imported from taxi config)',
        'maintained_by': 'common_components',
        'prefix': '/4.0/',
        'priority': 100,
        'rule_name': '/4.0/',
    },
    'output': {
        'attempts': 1,
        'timeout_ms': 1000,
        'tvm_service': 'mock',
        'upstream': {'$mockserver': ''},
    },
    'proxy': {
        'auth_type': 'oauth-or-session',
        'dbusers_authorization_allowed': False,
        'late_login_allowed': False,
        'parse_user_id_from_json_body': False,
        'personal': {
            'bounded_uids': False,
            'eater_id': False,
            'eater_uuid': False,
            'staff_login': False,
            'eats_email_id': False,
            'eats_phone_id': False,
            'email_id': False,
            'phone_id': False,
        },
        'phone_validation': 'disabled',
        'proxy_cookie': ['x', 'y'],
        'proxy_401': False,
    },
    'rule_type': 'passenger-authorizer',
}


def merge(lhs, rhs):
    if isinstance(lhs, dict):
        for k in rhs:
            if k not in lhs:
                lhs[k] = rhs[k]
            else:
                lhs[k] = merge(lhs[k], rhs[k])
        return lhs

    return rhs


def make_rule(overwrite: dict) -> dict:
    rule = copy.deepcopy(BASE_RULE)
    return merge(rule, overwrite)
