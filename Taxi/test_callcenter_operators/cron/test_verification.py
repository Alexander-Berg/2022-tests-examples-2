import json

import aiohttp
import aiohttp.web
import pytest

from callcenter_operators import models
from callcenter_operators import utils
from callcenter_operators.storage.postgresql import db
from test_callcenter_operators import params

ACCESS_CONTROL_ROLES_MAP = {
    'operator': {'project': 'cc', 'group': 'Operators', 'tags': ['operator']},
    'supervisor': {'project': 'cc', 'group': 'Supervisors'},
    'admin': {'project': 'cc', 'group': 'Admins', 'tags': ['admin']},
}


@pytest.fixture(name='mock_staff_persons')
def _mock_staff_persons(mock_staff):
    class Context:
        @staticmethod
        @mock_staff('/v3/persons')
        async def handle(request, *args, **kwargs):
            body = {'result': [{}]}
            for login in request.query['login'].split(','):
                if login.startswith('staff'):
                    body['result'].append({'login': login})
            return aiohttp.web.Response(status=200, body=json.dumps(body))

    return Context()


@pytest.fixture(name='mock_staff_persons_fail')
def _mock_staff_persons_fail(mock_staff):
    class Context:
        @staticmethod
        @mock_staff('/v3/persons')
        async def handle(request, *args, **kwargs):
            return aiohttp.web.Response(status=500)

    return Context()


async def _check_ticket(context, ticket):
    query = (
        'SELECT '
        '    operators_access.id, '
        '    operators_access.yandex_uid, '
        '    operator_id::VARCHAR AS agent_id, '
        '    last_name, '
        '    first_name, '
        '    middle_name, '
        '    yandex_login, '
        '    working_domain, '
        '    callcenter_id, '
        '    staff_login, '
        '    staff_login_state, '
        '    COALESCE(operators_roles.roles, \'{}\') as roles '
        'FROM callcenter_auth.operators_access '
        'LEFT JOIN callcenter_auth.operators_roles '
        'ON operators_access.yandex_uid = operators_roles.yandex_uid '
        f'WHERE yandex_login = \'{ticket["loginKonnekta"].split("@")[0]}\''
    )
    pool = await db.OperatorsRepo.get_ro_pool(context)
    async with pool.acquire() as conn:
        op_info = await utils.execute_query(query, conn, 'fetchrow')

    assert ticket['queue'] == 'TASK'
    assert (
        ticket['loginKonnekta']
        == op_info['yandex_login'] + '@' + op_info['working_domain']
    )
    assert ticket['type'] == 'staffErr'
    assert ticket.get('agentId') == op_info['agent_id']
    assert ticket['lastName'] == op_info['last_name']
    assert ticket['name'] == op_info['first_name']
    assert ticket.get('patronymic') == op_info['middle_name']
    assert ticket['plosadka'] == op_info['callcenter_id']
    assert ticket['role'] == ', '.join(op_info['roles'])
    assert ticket['loginStaff'] == op_info['staff_login'] or 'отсутствует'
    assert ticket['uid'] == op_info['yandex_uid']
    assert (
        ticket['summary'] == f'Staff логин не найден {ticket["loginKonnekta"]}'
    )
    assert f'Фамилия: {ticket["lastName"]}' in ticket['description']
    assert f'Имя: {ticket["name"]}' in ticket['description']
    assert (
        f'Отчество: {ticket.get("patronymic") or ""}' in ticket['description']
    )
    assert (
        f'Логин Коннекта: {ticket["loginKonnekta"]}' in ticket['description']
    )
    assert f'agent_id: {ticket["agentId"]}' in ticket['description']
    assert f'yandex_uid: {ticket["uid"]}' in ticket['description']
    assert (
        f'Call-центр: {params.CALLCENTER_INFO_MAP[ticket["plosadka"]]["name"]}'
        in ticket['description']
    )
    assert f'Роль: {ticket["role"]}' in ticket['description']
    assert f'Стафф-логин: {ticket["loginStaff"]}' in ticket['description']


@pytest.fixture(name='mock_api_tracker_issues')
def _mock_api_tracker_issues(mock_api_tracker, cron_context):
    class Context:
        @staticmethod
        @mock_api_tracker('/v2/issues')
        async def handle(request, *args, **kwargs):
            assert request.headers['Authorization'] == 'OAuth 123'
            assert request.headers['OrgId'] == '12345'
            await _check_ticket(cron_context, request.json)
            return aiohttp.web.Response(
                status=201, body='{"id": "task_1", "key": "TASK-1"}',
            )

    return Context()


@pytest.fixture(name='mock_api_tracker_issues_fail')
def _mock_api_tracker_issues_fail(mock_api_tracker):
    class Context:
        @staticmethod
        @mock_api_tracker('/v2/issues')
        async def handle(request, *args, **kwargs):
            return aiohttp.web.Response(status=500)

    return Context()


async def _select_staff_login_states(context):
    pool = await db.OperatorsRepo.get_ro_pool(context)

    async with pool.acquire() as conn:
        query = (
            'SELECT yandex_uid, staff_login, staff_login_state '
            'FROM callcenter_auth.operators_access'
        )
        result = await utils.execute_query(query, conn, 'fetch')
    return {op_info['yandex_uid']: op_info for op_info in result}


@pytest.mark.config(
    CALLCENTER_OPERATORS_PROFILES_VERIFICATION_SETTINGS={
        'enabled': True,
        'tracker_queue': 'TASK',
        'max_hours_unverified': 24,
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=ACCESS_CONTROL_ROLES_MAP,
)
@pytest.mark.now('2018-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_staff_login_verification(
        cron_runner, cron_context, mock_staff_persons, mock_api_tracker_issues,
):
    await cron_runner.operators_profiles_verification()
    new_operators_info = await _select_staff_login_states(cron_context)
    yandex_uids = [
        'uid1',
        'uid2',
        'uid3',
        'uid4',
        'uid5',
        'uid6',
        'uid7',
        'uid8',
        'uid9',
    ]
    expected_staff_logins = [
        None,
        'staff_login2',
        'not_staff_login3',
        'not_staff_login4',
        None,
        'staff_login6',
        'staff_login7',
        'staff_login8',
        'staff_login9',
    ]
    expected_staff_login_states = [
        models.OperatorStaffLoginInfo.VERIFIED,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
    ]
    for yandex_uid, expected_staff_login, expected_staff_login_state in zip(
            yandex_uids, expected_staff_logins, expected_staff_login_states,
    ):
        assert (
            new_operators_info[yandex_uid]['staff_login']
            == expected_staff_login
        )
        assert (
            new_operators_info[yandex_uid]['staff_login_state']
            == expected_staff_login_state
        )
    assert mock_staff_persons.handle.times_called == 1
    assert mock_api_tracker_issues.handle.times_called == 2


@pytest.mark.config(
    CALLCENTER_OPERATORS_PROFILES_VERIFICATION_SETTINGS={
        'enabled': True,
        'tracker_queue': 'TASK',
        'max_hours_unverified': 24,
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=ACCESS_CONTROL_ROLES_MAP,
)
@pytest.mark.now('2018-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth',
    files=['callcenter_auth_test_internal_staff_verification.psql'],
)
async def test_internal_staff_login_verification(
        cron_runner, cron_context, mock_staff_persons, mock_api_tracker_issues,
):
    await cron_runner.operators_profiles_verification()
    new_operators_info = await _select_staff_login_states(cron_context)
    assert (
        new_operators_info['uid1']['staff_login_state']
        == models.OperatorStaffLoginInfo.VERIFIED
    )
    assert not mock_api_tracker_issues.handle.times_called


@pytest.mark.config(
    CALLCENTER_OPERATORS_PROFILES_VERIFICATION_SETTINGS={
        'enabled': True,
        'tracker_queue': 'TASK',
        'max_hours_unverified': 24,
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=ACCESS_CONTROL_ROLES_MAP,
)
@pytest.mark.now('2018-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_staff_login_verification_fail(
        cron_runner,
        cron_context,
        mock_staff_persons_fail,
        mock_api_tracker_issues_fail,
):
    await cron_runner.operators_profiles_verification()
    new_operators_info = await _select_staff_login_states(cron_context)
    yandex_uids = [
        'uid1',
        'uid2',
        'uid3',
        'uid4',
        'uid5',
        'uid6',
        'uid7',
        'uid8',
        'uid9',
    ]
    expected_staff_login_states = [
        models.OperatorStaffLoginInfo.VERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
    ]
    for yandex_uid, expected_staff_login_state in zip(
            yandex_uids, expected_staff_login_states,
    ):
        assert (
            new_operators_info[yandex_uid]['staff_login_state']
            == expected_staff_login_state
        )
    assert mock_staff_persons_fail.handle.times_called > 0
    assert mock_api_tracker_issues_fail.handle.times_called > 0


@pytest.mark.config(
    CALLCENTER_OPERATORS_PROFILES_VERIFICATION_SETTINGS={
        'enabled': False,
        'tracker_queue': 'TASK',
        'max_hours_unverified': 24,
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=ACCESS_CONTROL_ROLES_MAP,
)
@pytest.mark.now('2018-06-22 19:10:00+00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_hanged_operators.psql'],
)
async def test_staff_login_verification_disabled(
        cron_runner, cron_context, mock_staff_persons, mock_api_tracker_issues,
):
    await cron_runner.operators_profiles_verification()
    new_operators_info = await _select_staff_login_states(cron_context)
    yandex_uids = [
        'uid1',
        'uid2',
        'uid3',
        'uid4',
        'uid5',
        'uid6',
        'uid7',
        'uid8',
        'uid9',
    ]
    expected_staff_logins = [
        None,
        'staff_login2',
        'not_staff_login3',
        'not_staff_login4',
        None,
        None,
        'staff_login7',
        'staff_login8',
        'staff_login9',
    ]
    expected_staff_login_states = [
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.REPORT_SENT,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.UNVERIFIED,
        models.OperatorStaffLoginInfo.VERIFIED,
    ]
    for yandex_uid, expected_staff_login, expected_staff_login_state in zip(
            yandex_uids, expected_staff_logins, expected_staff_login_states,
    ):
        assert (
            new_operators_info[yandex_uid]['staff_login']
            == expected_staff_login
        )
        assert (
            new_operators_info[yandex_uid]['staff_login_state']
            == expected_staff_login_state
        )
    assert mock_staff_persons.handle.times_called == 0
    assert mock_api_tracker_issues.handle.times_called == 0
