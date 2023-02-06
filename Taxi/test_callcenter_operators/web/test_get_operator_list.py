import pytest

OP_1 = {
    'id': 1,
    'login': 'admin@unit.test',
    'yandex_uid': 'admin_uid',
    'agent_id': '1777777777',
    'state': 'ready',
    'first_name': 'admin',
    'middle_name': 'adminovich',
    'last_name': 'adminov',
    'callcenter_id': 'cc1',
    'roles': ['admin'],
    'roles_info': [{'role': 'admin', 'source': 'admin'}],
    'name_in_telephony': 'admin_unit.test',
    'phone_number': '+112',
    # 'supervisor_login': None,
    'staff_login': 'ultra_staff',
    'timezone': 'Europe/Moscow',
    'created_at': '2016-06-01T22:10:25+03:00',
    'updated_at': '2016-06-22T22:10:25+03:00',
    'telegram_login': 'telegram_login_admin',
    'employment_date': '2016-06-01',
    'mentor_login': 'admin@unit.test',
    # 'deleted_at': None,
}

OP_2 = {
    'id': 2,
    'login': 'supervisor@unit.test',
    'yandex_uid': 'supervisor_uid',
    'agent_id': '1888888888',
    'state': 'ready',
    'first_name': 'supervisor',
    # 'middle_name': None,
    'last_name': 'supervisorov',
    'callcenter_id': 'cc1',
    'roles': ['supervisor'],
    'roles_info': [{'role': 'supervisor', 'source': 'admin'}],
    'name_in_telephony': 'supervisor_unit.test',
    'phone_number': '+221',
    'supervisor_login': 'admin@unit.test',
    # 'staff_login': None,
    # 'timezone': None,
    'created_at': '2016-06-01T22:10:25+03:00',
    'updated_at': '2016-06-22T22:10:25+03:00',
    'telegram_login': 'telegram_login_supervisor',
    'employment_date': '2016-06-01',
    'mentor_login': 'admin@unit.test',
    # 'deleted_at': None,
}

OP_3 = {
    'id': 3,
    'login': 'login1@unit.test',
    'yandex_uid': 'uid1',
    'agent_id': '1000000000',
    'state': 'ready',
    'first_name': 'name1',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'roles': ['operator'],
    'roles_info': [{'role': 'operator', 'source': 'admin'}],
    'name_in_telephony': 'login1_unit.test',
    'phone_number': '+111',
    'supervisor_login': 'admin@unit.test',
    'staff_login': 'login1_staff',
    'timezone': 'Europe/Moscow',
    'created_at': '2016-06-01T22:10:25+03:00',
    'updated_at': '2016-06-22T22:10:26+03:00',
    'telegram_login': 'telegram_login_1',
    'employment_date': '2016-06-01',
    'mentor_login': 'supervisor@unit.test',
    # 'deleted_at': None,
}

OP_4 = {
    'id': 4,
    'login': 'login2@unit.test',
    'yandex_uid': 'uid2',
    'agent_id': '1000000001',
    'state': 'deleted',
    'first_name': 'name2',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'callcenter_id': 'cc1',
    'roles': ['operator'],
    'roles_info': [{'role': 'operator', 'source': 'admin'}],
    'name_in_telephony': 'login2_unit.test',
    'phone_number': '+222',
    'supervisor_login': 'admin@unit.test',
    # 'staff_login': None,
    # 'timezone': None,
    'created_at': '2016-06-01T22:10:25+03:00',
    'updated_at': '2016-06-22T22:10:27+03:00',
    'deleted_at': '2016-06-22T22:10:27+03:00',
    'telegram_login': 'telegram_login_2',
    'employment_date': '2016-06-01',
    'mentor_login': 'supervisor@unit.test',
}

OP_5 = {
    'id': 5,
    'login': 'login3@unit.test',
    'yandex_uid': 'uid3',
    'agent_id': '1000000002',
    'state': 'ready',
    'first_name': 'name3',
    # 'middle_name': None,
    'last_name': 'surname',
    'callcenter_id': 'cc2',
    'roles': ['operator'],
    'roles_info': [{'role': 'operator', 'source': 'admin'}],
    'name_in_telephony': 'login3_unit.test',
    'phone_number': '+333',
    'supervisor_login': 'admin@unit.test',
    'staff_login': 'login3_staff',
    # 'timezone': None,
    'created_at': '2016-06-01T22:10:25+03:00',
    'updated_at': '2016-06-22T22:10:28+03:00',
    # 'deleted_at': None,
    'telegram_login': 'telegram_login_3',
    'employment_date': '2016-06-01',
}


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_updated_seq_insert(pgsql):
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        ' SELECT yandex_uid, updated_seq'
        ' FROM callcenter_auth.operators_access'
        ' ORDER BY updated_seq ASC',
    )
    db_rows = cursor.fetchall()
    cursor.close()
    assert db_rows == [
        ('admin_uid', 1),
        ('supervisor_uid', 2),
        ('uid1', 3),
        ('uid2', 4),
        ('uid3', 5),
    ]


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_updated_seq_update(pgsql):
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        ' UPDATE callcenter_auth.operators_access'
        ' SET middle_name = \'aaadmin_ogly\''
        ' WHERE yandex_uid = \'admin_uid\'',
    )

    cursor.execute(
        ' SELECT yandex_uid, updated_seq'
        ' FROM callcenter_auth.operators_access'
        ' ORDER BY updated_seq ASC',
    )
    db_rows = cursor.fetchall()
    cursor.close()
    assert db_rows == [
        ('supervisor_uid', 2),
        ('uid1', 3),
        ('uid2', 4),
        ('uid3', 5),
        ('admin_uid', 6),
    ]


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': 'хелп',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'corp': {
            'metaqueues': ['corp'],
            'display_name': 'корп',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp': {
            'metaqueues': ['disp'],
            'display_name': 'дисп',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'god': {
            'metaqueues': ['help', 'corp', 'disp'],
            'display_name': 'гад',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {
            'project': 'help',
            'group': 'Operators',
            'local_name': 'оператор',
        },
        'supervisor': {
            'project': 'help',
            'group': 'Supervisors',
            'local_name': 'супервизор',
        },
        'admin': {'project': 'help', 'group': 'Admins', 'local_name': 'админ'},
    },
)
@pytest.mark.parametrize(
    ['req', 'expected_status', 'expected_response'],
    [
        pytest.param({}, 400, None, id='{}'),
        pytest.param({'limit': -1}, 400, None, id='limit=-1'),
        pytest.param({'cursor': -1}, 400, None, id='cursor=-1'),
        pytest.param(
            {'limit': 0},
            200,
            {'next_cursor': 0, 'operators': []},
            id='limit=0',
        ),
        pytest.param(
            {'limit': 1},
            200,
            {'next_cursor': 1, 'operators': [OP_1]},
            id='limit=1',
        ),
        pytest.param(
            {'limit': 1, 'cursor': 1},
            200,
            {'next_cursor': 2, 'operators': [OP_2]},
            id='limit=1,cursor=1',
        ),
        pytest.param(
            {'limit': 1, 'cursor': 2},
            200,
            {'next_cursor': 3, 'operators': [OP_3]},
            id='limit=1,cursor=2',
        ),
        pytest.param(
            {'limit': 100, 'cursor': 2},
            200,
            {'next_cursor': 5, 'operators': [OP_3, OP_4, OP_5]},
            id='limit=100,cursor=2',
        ),
        pytest.param(
            {'limit': 100, 'cursor': 5},
            200,
            {'next_cursor': 5, 'operators': []},
            id='limit=100,cursor=5',
        ),
        pytest.param(
            {'limit': 100},
            200,
            {'next_cursor': 5, 'operators': [OP_1, OP_2, OP_3, OP_4, OP_5]},
            id='limit=100',
        ),
        pytest.param(
            {'limit': 100, 'cursor': 0},
            200,
            {'next_cursor': 5, 'operators': [OP_1, OP_2, OP_3, OP_4, OP_5]},
            id='limit=100,cursor=0',
        ),
    ],
)
async def test_operator_list(
        taxi_callcenter_operators_web, req, expected_status, expected_response,
):
    response = await taxi_callcenter_operators_web.post(
        '/v1/operators/list', json=req,
    )
    assert response.status == expected_status
    if expected_response:
        json_response = await response.json()
        assert json_response == expected_response
