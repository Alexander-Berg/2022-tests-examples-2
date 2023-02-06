# pylint: disable=C0302
import copy
import datetime
import typing

import pytest
import pytz

from test_callcenter_operators import params
from test_callcenter_operators import test_utils

EXPECTED_ADMIN_PROFILE = {
    'agent_id': 1777777777,
    'callcenter_id': 'cc1',
    'first_name': 'admin',
    'middle_name': 'adminovich',
    'last_name': 'adminov',
    'name_in_telephony': 'admin_unit.test',
    'login': 'admin@unit.test',
    'phone': '+112',
    'roles': ['admin'],
    'roles_info': [
        {
            'role': 'admin',
            'source': 'admin',
            'local_role': 'admin',
            'local_project': 'хелп',
        },
    ],
    'state': 'ready',
    'yandex_uid': 'admin_uid',
    'staff_login': 'ultra_staff',
    'timezone': 'Europe/Moscow',
    'telegram_login': 'telegram_login_admin',
    'employment_date': '2016-06-01',
    'mentor_login': 'admin@unit.test',
}
EXPECTED_OP_2_PROFILE = {
    'agent_id': 1000000001,
    'callcenter_id': 'cc1',
    'first_name': 'name2',
    'middle_name': 'middlename',
    'last_name': 'surname',
    'name_in_telephony': 'login2_unit.test',
    'login': 'login2@unit.test',
    'phone': '+222',
    'roles': ['operator'],
    'roles_info': [
        {
            'role': 'operator',
            'source': 'admin',
            'local_role': 'operator',
            'local_project': 'хелп',
        },
    ],
    'state': 'deleted',
    'supervisor_login': 'admin@unit.test',
    'yandex_uid': 'uid2',
    'telegram_login': 'telegram_login_2',
    'employment_date': '2016-06-01',
    'mentor_login': 'supervisor@unit.test',
}
EXPECTED_OP_3_PROFILE = {
    'agent_id': 1000000002,
    'callcenter_id': 'cc2',
    'first_name': 'name3',
    'last_name': 'surname',
    'name_in_telephony': 'login3_unit.test',
    'login': 'login3@unit.test',
    'phone': '+333',
    'roles': ['operator'],
    'roles_info': [
        {
            'role': 'operator',
            'source': 'admin',
            'local_role': 'operator',
            'local_project': 'хелп',
        },
    ],
    'state': 'ready',
    'supervisor_login': 'admin@unit.test',
    'yandex_uid': 'uid3',
    'staff_login': 'login3_staff',
    'telegram_login': 'telegram_login_3',
    'employment_date': '2016-06-01',
}
OPERATOR_NOT_FOUND = {'code': 'not_found', 'message': 'Operator not found'}


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.parametrize(
    ['yandex_uid', 'response_status', 'expected_response'],
    (
        ('admin_uid', 200, EXPECTED_ADMIN_PROFILE),
        ('uid2', 200, EXPECTED_OP_2_PROFILE),
        ('uid3', 200, EXPECTED_OP_3_PROFILE),
        ('uid_unknown', 404, OPERATOR_NOT_FOUND),
    ),
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
        'operator': {'project': 'help', 'group': 'Operators'},
        'supervisor': {'project': 'help', 'group': 'Supervisors'},
        'admin': {'project': 'help', 'group': 'Admins'},
    },
)
async def test_get_operator_profile_old(
        taxi_callcenter_operators_web,
        yandex_uid,
        response_status,
        expected_response,
):
    response = await taxi_callcenter_operators_web.get(
        f'/v1/admin/operator/profile/?yandex_uid={yandex_uid}',
    )
    assert response.status == response_status
    content = await response.json()
    assert content == expected_response


# pylint: disable=W0102
def make_put_request(
        first_name: str = 'name1',
        last_name: str = 'surname',
        middle_name: typing.Optional[str] = 'middlename',
        callcenter_id: str = 'cc1',
        roles: typing.Optional[typing.List[str]] = ['operator'],
        phone: typing.Optional[str] = '+111',
        supervisor_login: typing.Optional[str] = 'admin@unit.test',
        staff_login: typing.Optional[str] = 'login1_staff',
        timezone: typing.Optional[str] = 'Europe/Moscow',
        employment_date: str = '2016-06-01',
        mentor_login: typing.Optional[str] = 'supervisor@unit.test',
):
    request_dict: typing.Dict[str, typing.Any] = {
        'first_name': first_name,
        'last_name': last_name,
        'callcenter_id': callcenter_id,
        'employment_date': employment_date,
    }
    if middle_name is not None:
        request_dict['middle_name'] = middle_name
    if roles is not None:
        request_dict['roles'] = roles
    if phone is not None:
        request_dict['phone'] = phone
    if supervisor_login is not None:
        request_dict['supervisor_login'] = supervisor_login
    if staff_login is not None:
        request_dict['staff_login'] = staff_login
    if timezone is not None:
        request_dict['timezone'] = timezone
    if mentor_login is not None:
        request_dict['mentor_login'] = mentor_login
    return request_dict


async def check_db_operator(
        yandex_uid,
        expected_operator_data,
        staff_login_validation_reset,
        web_context,
):
    expected_operator_data['yandex_uid'] = yandex_uid
    expected_operator_data['phone_number'] = (
        expected_operator_data.pop('phone')
        if 'phone' in expected_operator_data
        else None
    )
    cc_timezone = params.CALLCENTER_INFO_MAP[
        expected_operator_data['callcenter_id']
    ]['timezone']
    expected_operator_data['timezone'] = pytz.timezone(
        expected_operator_data.get('timezone') or cc_timezone,
    ).zone
    db_operator = await test_utils.get_operator(yandex_uid, web_context)
    expected_roles = set(expected_operator_data.pop('roles'))
    for key, value in expected_operator_data.items():
        if isinstance(db_operator[key], datetime.date):
            assert value == str(db_operator[key])
        else:
            assert value == db_operator[key]
    assert set(db_operator['roles']) == expected_roles
    assert db_operator['staff_login_state'] == (
        'unverified' if staff_login_validation_reset else 'verified'
    )


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.parametrize(
    [
        'yandex_uid',
        'request_json',
        'response_status',
        'expected_response',
        'expected_stq_times_called',
        'connect_times_called',
        'staff_login_validation_reset',
    ],
    (
        pytest.param(
            'uid1', make_put_request(), 200, {}, 1, 0, 0, id='no changes',
        ),
        pytest.param(
            'unknown_uid',
            make_put_request(),
            404,
            {'code': 'not_found', 'message': 'Operator not found'},
            0,
            0,
            False,
            id='not found',
        ),
        pytest.param(
            'uid2',
            make_put_request(),
            406,
            {'code': 'deleted', 'message': 'Cannot update deleted operator'},
            0,
            0,
            False,
            id='deleted',
        ),
        pytest.param(
            'uid1',
            make_put_request(callcenter_id='cc1'),
            406,
            {
                'code': 'telegram_login_required',
                'message': 'Callcenter requires telegram_login for operator',
            },
            0,
            0,
            False,
            marks=pytest.mark.config(
                CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
                    'cc1': {
                        'name': 'cc_name_1',
                        'domain': 'unit.test',
                        'staff_login_required': False,
                        'telegram_login_required': True,
                        'timezone': 'Europe/Moscow',
                        'connect_department_id': '1',
                    },
                },
            ),
            id='telegram login required, but not provided',
        ),
        pytest.param(
            'uid1',
            make_put_request(first_name='name11'),
            200,
            {},
            1,
            1,
            False,
            id='new first name',
        ),
        pytest.param(
            'uid1',
            make_put_request(
                first_name='name11', middle_name=None, last_name='lastname',
            ),
            200,
            {},
            1,
            1,
            False,
            id='fully new name',
        ),
        pytest.param(
            'uid1',
            make_put_request(callcenter_id='cc2'),
            200,
            {},
            1,
            0,
            False,
            id='new callcenter',
        ),
        pytest.param(
            'uid1',
            make_put_request(callcenter_id='cc2'),
            406,
            {
                'code': 'bad_callcenter_id',
                'message': (
                    'Could not set provided callcenter_id because '
                    'working domain would have changed'
                ),
            },
            0,
            0,
            False,
            marks=pytest.mark.config(
                CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
                    'cc1': {
                        'name': 'cc_name_1',
                        'domain': 'unit.test',
                        'staff_login_required': False,
                        'timezone': 'Europe/Moscow',
                        'connect_department_id': '1',
                    },
                    'cc2': {
                        'name': 'cc_name_2',
                        'domain': 'drvrc.com',
                        'staff_login_required': False,
                        'timezone': 'Europe/Moscow',
                        'connect_department_id': '2',
                    },
                },
            ),
            id='new callcenter in other domain',
        ),
        pytest.param(
            'uid1',
            make_put_request(
                callcenter_id='bad_bad_callcenter', staff_login=None,
            ),
            406,
            {
                'code': 'bad_callcenter_id',
                'message': 'Callcenter with provided id does not exist',
            },
            0,
            0,
            False,
            id='bad callcenter',
        ),
        pytest.param(
            'uid1',
            make_put_request(roles=['operator', 'supervisor']),
            200,
            {},
            1,
            0,
            False,
            id='new role',
        ),
        pytest.param(
            'uid1',
            make_put_request(roles=['supervisor', 'superadmin']),
            406,
            {'code': 'bad_role', 'message': 'Incorrect role provided'},
            0,
            0,
            False,
            id='bad new role',
        ),
        pytest.param(
            'uid1',
            make_put_request(phone='+12123123'),
            200,
            {},
            1,
            0,
            False,
            id='new phone',
        ),
        pytest.param(
            'uid1',
            make_put_request(phone=None),
            200,
            {},
            1,
            0,
            False,
            id='delete phone',
        ),
        pytest.param(
            'uid1',
            make_put_request(supervisor_login='supervisor@unit.test'),
            200,
            {},
            1,
            0,
            False,
            id='new supervisor',
        ),
        pytest.param(
            'uid1',
            make_put_request(supervisor_login=None),
            200,
            {},
            1,
            0,
            False,
            id='delete supervisor',
        ),
        pytest.param(
            'uid1',
            make_put_request(supervisor_login='superadmin@unit.test'),
            406,
            {
                'code': 'bad_supervisor_login',
                'message': 'Supervisor with provided login was not found',
            },
            0,
            0,
            False,
            id='bad supervisor',
        ),
        pytest.param(
            'uid1',
            make_put_request(mentor_login='supervisor@unit.test'),
            200,
            {},
            1,
            0,
            False,
            id='new mentor',
        ),
        pytest.param(
            'uid1',
            make_put_request(mentor_login=None),
            200,
            {},
            1,
            0,
            False,
            id='delete mentor',
        ),
        pytest.param(
            'uid1',
            make_put_request(mentor_login='superadmin@unit.test'),
            406,
            {
                'code': 'bad_mentor_login',
                'message': 'Mentor with provided login was not found',
            },
            0,
            0,
            False,
            id='bad supervisor',
        ),
        pytest.param(
            'uid1',
            make_put_request(staff_login='new_login_staff'),
            200,
            {},
            1,
            0,
            True,
            id='new staff_login',
        ),
        pytest.param(
            'uid1',
            make_put_request(staff_login=None),
            200,
            {},
            1,
            0,
            True,
            id='delete staff_login',
        ),
        pytest.param(
            'uid1',
            make_put_request(staff_login='new_login'),
            200,
            {},
            1,
            0,
            True,
            id='bad staff_login',
        ),
        pytest.param(
            'supervisor_uid',
            make_put_request(
                callcenter_id='cc2',
                staff_login=None,
                first_name='supervisor',
                middle_name=None,
                last_name='supervisorov',
                roles=['supervisor'],
            ),
            200,
            {},
            1,
            0,
            True,
            id='new callcenter with required staff',
        ),
        pytest.param(
            'uid1',
            make_put_request(timezone='Europe/Volgograd'),
            200,
            {},
            1,
            0,
            False,
            id='new timezone',
        ),
        pytest.param(
            'uid1',
            make_put_request(timezone='europe/volgograd'),
            200,
            {},
            1,
            0,
            False,
            id='new timezone, unformatted',
        ),
        pytest.param(
            'uid1',
            make_put_request(timezone=None),
            200,
            {},
            1,
            0,
            False,
            id='delete timezone',
        ),
        pytest.param(
            'uid1',
            make_put_request(timezone='Ochen/Daleko'),
            406,
            {'code': 'bad_timezone', 'message': 'Invalid timezone name'},
            0,
            0,
            False,
            id='bad timezone',
        ),
    ),
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
        {'domain': 'drvrc.com', 'token_alias': 'DRVRC_CONNECT_OAUTH'},
    ],
)
async def test_update_operator_profile(
        taxi_callcenter_operators_web,
        web_context,
        yandex_uid,
        request_json,
        response_status,
        expected_response,
        expected_stq_times_called,
        connect_times_called,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
        staff_login_validation_reset,
):
    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid={yandex_uid}',
        json=request_json,
    )
    assert response.status == response_status
    content = await response.json()
    assert content == expected_response

    if response.status != 200:
        expected_operator_data = make_put_request()
        expected_operator_data['roles'] = {}
        await check_db_operator(
            'uid1',
            expected_operator_data,
            staff_login_validation_reset,
            web_context,
        )
    else:
        expected_operator_data = copy.deepcopy(request_json)
        await check_db_operator(
            yandex_uid,
            expected_operator_data,
            staff_login_validation_reset,
            web_context,
        )

    assert (
        stq.callcenter_operators_sync_roles.times_called
        == expected_stq_times_called
    )
    assert mock_connect_change_user_info.times_called == connect_times_called


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['one_metaqueue', 'second_metaqueue'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc2': {
            'name': 'cc_name_2',
            'domain': 'unit.test',
            'staff_login_required': False,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'connect_department_id': 1,
            'default_metaqueues': ['one_metaqueue', 'second_metaqueue'],
        },
    },
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
        {'domain': 'drvrc.com', 'token_alias': 'DRVRC_CONNECT_OAUTH'},
    ],
    CALLCENTER_METAQUEUES=[
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'second_metaqueue', 'allowed_clusters': ['1']},
    ],
)
async def test_change_metaqueue_when_change_cc(
        taxi_callcenter_operators_web,
        web_context,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        mock_callcenter_queues,
        pgsql,
):
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (1, 'disconnected', None, []),
        (2, 'disconnected', None, []),
        (3, 'disconnected', None, ['corp', 'help']),
        (4, 'disconnected', None, ['disp']),
        (5, 'connected', None, ['disp']),
    ]

    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid=uid1',
        json=make_put_request(callcenter_id='cc2'),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    expected_operator_data = make_put_request(callcenter_id='cc2')
    await check_db_operator('uid1', expected_operator_data, False, web_context)

    assert stq.callcenter_operators_sync_roles.times_called == 1
    assert mock_connect_change_user_info.times_called == 0

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (1, 'disconnected', None, []),
        (2, 'disconnected', None, []),
        (3, 'disconnected', None, ['one_metaqueue', 'second_metaqueue']),
        (4, 'disconnected', None, ['disp']),
        (5, 'connected', None, ['disp']),
    ]


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc2': {
            'name': 'cc_name_2',
            'domain': 'unit.test',
            'staff_login_required': False,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'connect_department_id': 1,
            'default_metaqueues': [
                'one_metaqueue',
                'metaqueue_which_not_in_CALLCENTER_METAQUEUES',
            ],
        },
    },
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
        {'domain': 'drvrc.com', 'token_alias': 'DRVRC_CONNECT_OAUTH'},
    ],
    CALLCENTER_METAQUEUES=[
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
    ],
)
async def test_not_change_metaqueue_when_change_cc(
        taxi_callcenter_operators_web,
        web_context,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        mock_callcenter_queues,
        pgsql,
):
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (1, 'disconnected', None, []),
        (2, 'disconnected', None, []),
        (3, 'disconnected', None, ['corp', 'help']),
        (4, 'disconnected', None, ['disp']),
        (5, 'connected', None, ['disp']),
    ]

    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid=uid1',
        json=make_put_request(callcenter_id='cc2'),
    )
    assert response.status == 500
    content = await response.json()
    assert content['code'] == 'metaqueue_not_found'

    expected_operator_data = make_put_request()
    expected_operator_data['roles'] = {}
    await check_db_operator('uid1', expected_operator_data, False, web_context)

    assert stq.callcenter_operators_sync_roles.times_called == 0
    assert mock_connect_change_user_info.times_called == 0

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [
        (1, 'disconnected', None, []),
        (2, 'disconnected', None, []),
        (3, 'disconnected', None, ['corp', 'help']),
        (4, 'disconnected', None, ['disp']),
        (5, 'connected', None, ['disp']),
    ]


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['unit.test'],
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
    ],
)
async def test_update_operator_profile_internal_domain(
        taxi_callcenter_operators_web,
        web_context,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
):
    yandex_uid = 'uid1'
    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid={yandex_uid}',
        json=make_put_request(
            first_name='name11', middle_name=None, last_name='lastname',
        ),
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}

    expected_operator_data = copy.deepcopy(
        make_put_request(
            first_name='name11', middle_name=None, last_name='lastname',
        ),
    )
    await check_db_operator(
        yandex_uid, expected_operator_data, False, web_context,
    )

    assert stq.callcenter_operators_sync_roles.times_called == 1
    assert not mock_connect_change_user_info.times_called


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth',
    files=['callcenter_auth_existing_operators_source_idm.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['unit.test'],
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
    ],
)
async def test_update_operator_profile_dont_overwrite_idm(
        taxi_callcenter_operators_web,
        web_context,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
        pgsql,
):
    yandex_uid = 'uid1'
    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid={yandex_uid}',
        json=make_put_request(
            first_name='name11', middle_name=None, last_name='lastname',
        ),
    )
    assert response.status == 200
    assert await response.json() == {}

    expected_operator_data = copy.deepcopy(
        make_put_request(
            first_name='name11', middle_name=None, last_name='lastname',
        ),
    )
    await check_db_operator(
        yandex_uid, expected_operator_data, False, web_context,
    )

    assert stq.callcenter_operators_sync_roles.times_called == 1
    assert not mock_connect_change_user_info.times_called

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'admin', 'admin'),
        ('supervisor_uid', 'supervisor', 'admin'),
        ('uid1', 'operator', 'idm'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql(
    'callcenter_auth',
    files=['callcenter_auth_existing_operators_source_idm.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_INTERNAL_DOMAINS=['unit.test'],
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'operator': {'project': 'cc', 'group': 'Operators'},
        'supervisor': {'project': 'cc', 'group': 'Supervisors'},
        'admin': {'project': 'cc', 'group': 'Admins'},
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
    ],
)
async def test_update_operator_profile_cant_delete_idm_role(
        taxi_callcenter_operators_web,
        web_context,
        stq,
        mock_connect_change_user_info,
        mock_access_control_users,
        pgsql,
):
    yandex_uid = 'uid1'
    response = await taxi_callcenter_operators_web.put(
        f'/v1/admin/operator/profile/?yandex_uid={yandex_uid}',
        json=make_put_request(
            first_name='name11',
            middle_name=None,
            last_name='lastname',
            roles=(),
        ),
    )
    assert response.status == 406
    assert await response.json() == {
        'code': '406',
        'message': 'Попытка удалить из админки роли idm: {\'operator\'}',
    }

    assert stq.callcenter_operators_sync_roles.times_called == 0
    assert not mock_connect_change_user_info.times_called

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'admin', 'admin'),
        ('supervisor_uid', 'supervisor', 'admin'),
        ('uid1', 'operator', 'idm'),
        ('uid2', 'operator', 'admin'),
        ('uid3', 'operator', 'admin'),
    ]
