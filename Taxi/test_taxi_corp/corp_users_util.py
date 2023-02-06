from taxi.util import dictionary

BASE_USER_REQUEST = {
    'fullname': 'base_name',
    'phone': '+79997778877',
    'is_active': True,
}
EXTENDED_USER_REQUEST = {
    **BASE_USER_REQUEST,
    'email': 'example@yandex.ru',
    'department_id': 'dep1',
    'limits': [
        {'limit_id': 'limit3_2', 'service': 'taxi'},
        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
        {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
    ],
    'cost_centers_id': 'cost_center_1',
    'cost_center': 'default',
    'nickname': 'custom ID',
}
TWO_LIMITS_USER_REQUEST = {
    **BASE_USER_REQUEST,
    'department_id': 'dep1',
    'limits': [
        {'limit_id': 'limit3_2', 'service': 'taxi'},
        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
        {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
    ],
    'cost_centers_id': 'cost_center_1',
}
ANOTHER_SERVICE_USER_REQUEST = {
    **BASE_USER_REQUEST,
    'department_id': 'dep1',
    'limits': [{'limit_id': 'limit3_2', 'service': 'eats2'}],
    'cost_centers_id': 'cost_center_1',
}
DELETED_LIMIT_USER_REQUEST = {
    **BASE_USER_REQUEST,
    'department_id': 'dep1',
    'limits': [{'limit_id': 'deleted_limit', 'service': 'taxi'}],
    'cost_centers_id': 'cost_center_1',
}

CORP_USERS_RESPONSE = {
    'phone': '+79654646546',
    'client_id': 'client3',
    'cost_centers_id': 'cost_center_0',
    'department_id': 'dep1',
    'is_deleted': False,
    'email': 'svyat@yandex-team.ru',
    'limits': [
        {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
        {'limit_id': 'drive_limit', 'service': 'drive'},
        {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
    ],
    'is_active': True,
    'id': 'test_user_1',
    'fullname': 'good user',
}
CORP_USERS_NEXT_CURSOR = 'djEgTm9uZSB0ZXN0X3VzZXJfMQ=='

BASE_USER_RESPONSE = {
    'phone': '+79654646546',
    'client_id': 'client3',
    'cost_centers_id': 'cost_center_0',
    'department_id': 'dep1',
    'is_deleted': False,
    'email': 'svyat@yandex-team.ru',
    'limits': [
        {
            'limit_id': 'limit3_2_with_users',
            'name': 'limit3.2_with_users',
            'title': 'limit3.2_with_users',
            'service': 'taxi',
            'limits': {'orders_cost': {'value': '2000', 'period': 'month'}},
        },
        {
            'limit_id': 'limit3_2_eats2',
            'name': 'limit3.2_eats2',
            'title': 'limit3.2_eats2',
            'service': 'eats2',
        },
        {
            'limit_id': 'drive_limit',
            'limits': {'orders_cost': {'period': 'month', 'value': '1000'}},
            'name': 'drive limit',
            'title': 'drive limit',
            'service': 'drive',
        },
        {
            'limit_id': 'limit3_2_tanker',
            'name': 'limit3.2_tanker',
            'title': 'limit3.2_tanker',
            'service': 'tanker',
        },
    ],
    'services': {
        'drive': {
            'promocode': {
                'status': 'linked',
                'updated': '2021-03-28T09:30:00',
            },
        },
    },
    'is_active': True,
    'id': 'test_user_1',
    'fullname': 'good user',
}

UNLINKED_USER_RESPONSE = {
    'client_id': 'client3',
    'cost_centers_id': 'cost_center_1',
    'department_id': 'dep1_1',
    'email': 'svyat@yandex-team.ru',
    'fullname': 'fullname',
    'id': 'test_user_3',
    'is_active': True,
    'is_deleted': False,
    'limits': [
        {
            'limit_id': 'limit3_2_with_users',
            'limits': {'orders_cost': {'period': 'month', 'value': '2000'}},
            'name': 'limit3.2_with_users',
            'title': 'limit3.2_with_users',
            'service': 'taxi',
        },
    ],
    'services': {
        'drive': {
            'promocode': {'status': 'add', 'updated': '2021-03-28T09:30:00'},
        },
    },
    'phone': '+79654646543',
}

CORP_USERS_RESPONSE_ERROR = {
    'message': 'Not found',
    'code': 'NOT_FOUND',
    'reason': 'User test_user_1 not found',
}

CORP_USER_PHONES_SUPPORTED = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]


def api_user_doc(user):
    result = {}
    for key, value in user.items():
        if key == 'limits':
            if not value:
                result['limits'] = []
            else:
                result['limits'] = [
                    dictionary.partial_dict(limit, ('limit_id', 'service'))
                    for limit in value
                ]
        elif key == 'services':
            continue
        else:
            result[key] = value
    return result


def v2_user_doc(user_dict):
    return dict(user_dict, is_deleted=user_dict.get('is_deleted', False))
