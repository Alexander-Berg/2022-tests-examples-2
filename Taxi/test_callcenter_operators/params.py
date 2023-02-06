PASSPORT_MAPPING = {
    'admin@unit.test': 'admin_uid',
    'supervisor@unit.test': 'supervisor_uid',
    'login1@unit.test': 'uid1',
    'login2@unit.test': 'uid2',
    'login3@unit.test': 'uid3',
    'login6@unit.test': 'uid6',
    'login7@unit.test': 'uid7',
}

NEOPHONISH_UIDS = {'uid1', 'uid2', 'uid3', 'uid6', 'uid7'}

BASE_TEL_RESPONSE = {
    'PARAM': {},
    'TYPE': 'REPLY',
    'STATUSCODE': 200,
    'STATUSDESC': None,
    'STATUS': 'TRUE',
}

CALLCENTER_INFO_MAP = {
    'cc1': {
        'name': 'cc_name_1',
        'domain': 'unit.test',
        'staff_login_required': False,
        'telegram_login_required': False,
        'timezone': 'Europe/Moscow',
        'connect_department_id': 1,
    },
    'cc2': {
        'name': 'cc_name_2',
        'domain': 'unit.test',
        'staff_login_required': True,
        'telegram_login_required': False,
        'timezone': 'Europe/Volgograd',
        'connect_department_id': 2,
    },
    'cc3': {
        'name': 'cc_name_3',
        'domain': 'unit.test',
        'staff_login_required': False,
        'telegram_login_required': True,
        'timezone': 'Europe/Moscow',
        'connect_department_id': 3,
    },
}

ORGANIZATIONS_TOKENS = [
    {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
]

ACCESS_CONTROL_ROLES = {
    'ru_disp_operator': {'project': 'disp', 'group': 'operators'},
    'ru_disp_call_center_head': {
        'project': 'disp',
        'group': 'call_center_heads',
    },
    'ru_disp_team_leader': {'project': 'disp', 'group': 'team_leaders'},
    'ru_disp_account_manager': {
        'project': 'disp',
        'group': 'account_managers',
    },
    'ru_support_operator': {
        'project': 'support',
        'group': 'support_operators',
    },
    'operator': {
        'project': 'disp',
        'group': 'operators',
        'local_name': 'оператор',
    },
}

ACCESS_CONTROL_ROLES_FOR_STQ_TASK = {
    'operator': {
        'project': 'disp',
        'group': 'operators',
        'tags': ['operator', 'cc-reg'],
    },
    'center_head': {'project': 'disp', 'group': 'call_center_heads'},
    'team_leader': {'project': 'disp', 'group': 'team_leaders'},
    'account_manager': {'project': 'disp', 'group': 'account_managers'},
    'support_operator': {'project': 'support', 'group': 'support_operators'},
    'role_to_delete': {'project': 'support', 'group': 'group_to_delete'},
}

CALLCENTER_STATS_OPERATORS_STATUS_BY_AGENT_ID = {
    '1777777777': {
        'agent_id': '1000000001',
        'status': 'disconnected',
        'status_updated_at': '2016-06-22T20:00:00+00:00',
        'substatus_updated_at': '2016-06-22T20:00:00+00:00',
    },
    '1888888888': {
        'agent_id': '1000000001',
        'status': 'disconnected',
        'status_updated_at': '2016-06-22T20:00:00+00:00',
        'substatus_updated_at': '2016-06-22T20:00:00+00:00',
    },
    '1000000000': {
        'agent_id': '1000000000',
        'status': 'paused',
        'status_updated_at': '2018-06-23T07:03:15+00:00',
        'substatus': 'break',
        'substatus_updated_at': '2018-06-23T07:03:15+00:00',
    },
    '1000000001': {
        'agent_id': '1000000001',
        'status': 'disconnected',
        'status_updated_at': '2016-06-22T20:00:00+00:00',
        'substatus_updated_at': '2016-06-22T20:00:00+00:00',
    },
    '1000000002': {
        'agent_id': '1000000002',
        'status': 'connected',
        'status_updated_at': '2019-05-20T07:03:15+00:00',
        'substatus': 'talking',
        'substatus_updated_at': '2019-05-20T12:15:30+00:00',
    },
}

OPERATOR_1 = {
    'login': 'login1',
    'first_name': 'name1',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'aaaaaaaaaa',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+111',
    'timezone': 'Europe/Moscow',
    'staff_login': 'login1_staff',
}

NEOPHONISH_OPERATOR_1 = {
    'uid': 'uid1',
    'first_name': 'name1',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'aaaaaaaaaa',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+111',
    'timezone': 'Europe/Moscow',
    'staff_login': 'login1_staff',
}

OPERATOR_2 = {
    'login': 'login2',
    'first_name': 'name2',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'bbbbbbbbbb',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+222',
}
OPERATOR_3 = {
    'login': 'login3',
    'first_name': 'name3',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'aaaaaaaaaa',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+333',
    'staff_login': 'login3_staff',
}
NEOPHONISH_OPERATOR_3 = {
    'uid': 'uid3',
    'first_name': 'name3',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'aaaaaaaaaa',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+333',
    'staff_login': 'login3_staff',
}
OPERATOR_4 = {
    'login': 'login4',
    'first_name': 'name4',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'dddddddddd',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+444',
    'staff_login': 'login4_staff',
}
NEOPHONISH_OPERATOR_4 = {
    'uid': 'uid4',
    'first_name': 'name4',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'dddddddddd',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+444',
    'staff_login': 'login4_staff',
}
OPERATOR_5 = {
    'login': 'login5',
    'first_name': 'name5',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'eeeeeeeeee',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+555',
}
OPERATOR_6 = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'supervisor@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
    'timezone': 'europe/samara',
}
OPERATOR_WO_PASSWORD = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_LOGIN = {
    'login': 'login6@unit.test',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'supervisor@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_SUPERVISOR_LOGIN_1 = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'super_admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_SUPERVISOR_LOGIN_2 = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'admin',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_MENTOR_LOGIN_1 = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'mentor_login': 'super_admin@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_MENTOR_LOGIN_2 = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'mentor_login': 'admin',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_ROLE = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'admin@unit.test',
    'roles': ['operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_CALLCENTER_ID = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc6',
    'password': 'ffffffffff',
    'supervisor_login': 'supervisor@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
}
OPERATOR_WITH_BAD_TIMEZONE = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'ffffffffff',
    'supervisor_login': 'supervisor@unit.test',
    'roles': ['ru_disp_operator'],
    'phone_number': '+666',
    'timezone': 'Vologda/Vologda',
}
OPERATOR_WITH_MISSING_STAFF_LOGIN = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'ffffffffff',
    'roles': ['ru_disp_operator'],
    'supervisor_login': 'admin@unit.test',
    'phone_number': '+666',
}
OPERATOR_WITH_UNKNOWN_STAFF_LOGIN = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'ffffffffff',
    'roles': ['ru_disp_operator'],
    'supervisor_login': 'admin@unit.test',
    'phone_number': '+666',
    'staff_login': 'login6',
}
MULTI_OPERATOR = {
    'login': 'login6',
    'first_name': 'name6',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'ffffffffff',
    'supervisor_login': 'admin@unit.test',
    'roles': ['ru_support_operator', 'ru_disp_operator'],
    'phone_number': '+666',
    'staff_login': 'login6_staff',
}
OPERATOR_WO_ROLE = {
    'login': 'login2',
    'first_name': 'name2',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'password': 'bbbbbbbbbb',
    'supervisor_login': 'admin@unit.test',
    'roles': [],
    'phone_number': '+222',
}
CALL_CENTER_HEAD = {
    'login': 'login7',
    'first_name': 'name7',
    'middle_name': 'middlename extra big',
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'password': 'ffffffffff',
    'roles': ['ru_disp_call_center_head'],
    'phone_number': '+777',
    'staff_login': 'login7_staff',
}

NORMAL_REQUEST = {'operators': [OPERATOR_1, OPERATOR_2]}

NEOPHONISH_REQUEST = {'operators': [NEOPHONISH_OPERATOR_1]}

SINGLE_REQUEST = {'operators': [OPERATOR_1]}

DIFFERENT_SUPERVISORS_REQUEST = {'operators': [OPERATOR_1, OPERATOR_6]}

BIG_NORMAL_REQUEST = {
    'operators': [
        OPERATOR_1,
        OPERATOR_2,
        OPERATOR_3,
        OPERATOR_4,
        OPERATOR_5,
        OPERATOR_6,
    ],
}
REQUEST_WITH_NOT_PASSPORT_OPERATOR = {'operators': [OPERATOR_3, OPERATOR_4]}
NEOPHONISH_REQUEST_WITH_NOT_PASSPORT_OPERATOR = {
    'operators': [NEOPHONISH_OPERATOR_3, NEOPHONISH_OPERATOR_4],
}
ALL_OPERATORS_NOT_FOUND_REQUEST = {'operators': [OPERATOR_5, OPERATOR_4]}

INVALID_REQUEST = [{'some_field': 'some_value'}]

REQUEST_OPERATOR_WO_PASSWORD = {'operators': [OPERATOR_WO_PASSWORD]}

REQUEST_WITH_BAD_ROLE_OPERATOR = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_ROLE],
}
REQUEST_ONLY_BAD_ROLE_OPERATOR = {'operators': [OPERATOR_WITH_BAD_ROLE]}
REQUEST_BAD_LOGIN = {'operators': [OPERATOR_WITH_BAD_LOGIN]}
REQUEST_WITH_BAD_SUPERVISOR_LOGIN_1 = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_SUPERVISOR_LOGIN_1],
}
REQUEST_WITH_BAD_SUPERVISOR_LOGIN_2 = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_SUPERVISOR_LOGIN_2],
}
REQUEST_WITH_BAD_MENTOR_LOGIN_1 = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_MENTOR_LOGIN_1],
}
REQUEST_WITH_BAD_MENTOR_LOGIN_2 = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_MENTOR_LOGIN_2],
}
REQUEST_WITH_BAD_CALLCENTER_ID = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_CALLCENTER_ID],
}
REQUEST_WITH_BAD_TIMEZONE = {
    'operators': [OPERATOR_1, OPERATOR_WITH_BAD_TIMEZONE],
}
REQUEST_WITH_MISSING_STAFF_LOGIN = {
    'operators': [OPERATOR_1, OPERATOR_WITH_MISSING_STAFF_LOGIN],
}
REQUEST_WITH_UNKNOWN_STAFF_LOGIN = {
    'operators': [OPERATOR_1, OPERATOR_WITH_UNKNOWN_STAFF_LOGIN],
}
REQUEST_DIFFERENT_ROLES = {
    'operators': [
        OPERATOR_1,
        MULTI_OPERATOR,
        CALL_CENTER_HEAD,
        OPERATOR_WO_ROLE,
        OPERATOR_3,
    ],
}
