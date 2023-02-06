# pylint: disable=too-many-lines
import copy
import datetime
import json
import urllib.parse as parse

from aiohttp import web
import pytest

from callcenter_operators import models
from test_callcenter_operators import params
from test_callcenter_operators import test_utils

ADD_BULK_URL = '/v3/admin/operators/add_bulk/'


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
@pytest.mark.parametrize(
    [
        'request_json',
        'response_status',
        'expected_response',
        'expected_stq_times_called',
    ],
    (
        pytest.param(
            params.NORMAL_REQUEST,
            200,
            {'warnings': []},
            2,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='normal request',
        ),
        pytest.param(
            params.REQUEST_WITH_NOT_PASSPORT_OPERATOR,
            200,
            {
                'warnings': [
                    {'login': 'login4@unit.test', 'code': 'not_found_in_bb'},
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='not in passport',
        ),
        pytest.param(
            params.INVALID_REQUEST,
            400,
            {'code': 'invalid_request', 'message': 'Неверный запрос'},
            0,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='invalid request',
        ),
        pytest.param(
            params.ALL_OPERATORS_NOT_FOUND_REQUEST,
            200,
            {
                'warnings': [
                    {'login': 'login4@unit.test', 'code': 'not_found_in_bb'},
                    {'login': 'login5@unit.test', 'code': 'not_found_in_bb'},
                ],
            },
            0,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='all not found in bb',
        ),
        pytest.param(
            params.REQUEST_OPERATOR_WO_PASSWORD,
            200,
            {'warnings': []},
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='without password',
        ),
        pytest.param(
            params.REQUEST_BAD_LOGIN,
            200,
            {
                'warnings': [
                    {
                        'login': 'login6@unit.test@unit.test',
                        'code': 'bad_login_format',
                    },
                ],
            },
            0,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='bad login format',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_SUPERVISOR_LOGIN_1,
            200,
            {
                'warnings': [
                    {
                        'login': 'login6@unit.test',
                        'code': 'bad_supervisor_login',
                    },
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='unknown supervisor',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_SUPERVISOR_LOGIN_2,
            200,
            {
                'warnings': [
                    {
                        'login': 'login6@unit.test',
                        'code': 'bad_supervisor_login',
                    },
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='bad supervisor login format',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_MENTOR_LOGIN_1,
            200,
            {
                'warnings': [
                    {'login': 'login6@unit.test', 'code': 'bad_mentor_login'},
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='unknown mentor',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_MENTOR_LOGIN_2,
            200,
            {
                'warnings': [
                    {'login': 'login6@unit.test', 'code': 'bad_mentor_login'},
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='bad mentor login format',
        ),
        pytest.param(
            params.DIFFERENT_SUPERVISORS_REQUEST,
            200,
            {
                'warnings': [
                    {
                        'login': 'login1@unit.test',
                        'code': 'bad_supervisor_login',
                    },
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_deleted_admin.sql'],
            ),
            id='deleted supervisor',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_CALLCENTER_ID,
            200,
            {'warnings': [{'login': 'login6', 'code': 'bad_callcenter_id'}]},
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='bad callcenter_id',
        ),
        pytest.param(
            params.REQUEST_WITH_BAD_TIMEZONE,
            200,
            {
                'warnings': [
                    {'login': 'login6@unit.test', 'code': 'bad_timezone'},
                ],
            },
            1,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='bad timezone',
        ),
        pytest.param(
            params.REQUEST_WITH_MISSING_STAFF_LOGIN,
            200,
            {'warnings': []},
            2,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='missing required staff_login',
        ),
        pytest.param(
            params.REQUEST_WITH_UNKNOWN_STAFF_LOGIN,
            200,
            {'warnings': []},
            2,
            marks=pytest.mark.pgsql(
                'callcenter_auth', files=['callcenter_auth_admin_only.sql'],
            ),
            id='unknown staff_login',
        ),
        pytest.param(
            params.BIG_NORMAL_REQUEST,
            200,
            {
                'warnings': [
                    {'login': 'login1@unit.test', 'code': 'already_activated'},
                    {'login': 'login3@unit.test', 'code': 'already_activated'},
                    {'login': 'login4@unit.test', 'code': 'not_found_in_bb'},
                    {'login': 'login5@unit.test', 'code': 'not_found_in_bb'},
                ],
            },
            2,
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
            id='big request',
        ),
        pytest.param(
            params.NORMAL_REQUEST,
            200,
            {
                'warnings': [
                    {
                        'login': 'login1@unit.test',
                        'code': 'telegram_login_required',
                    },
                    {
                        'login': 'login2@unit.test',
                        'code': 'telegram_login_required',
                    },
                ],
            },
            0,
            marks=[
                pytest.mark.pgsql(
                    'callcenter_auth',
                    files=['callcenter_auth_admin_only.sql'],
                ),
                pytest.mark.config(
                    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
                        'cc1': {
                            'name': 'cc_name_1',
                            'domain': 'unit.test',
                            'staff_login_required': False,
                            'telegram_login_required': True,
                            'timezone': 'Europe/Moscow',
                            'connect_department_id': 1,
                        },
                    },
                ),
            ],
            id='no telegram_login request',
        ),
    ),
)
async def test_admin_bulk_add(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
        expected_stq_times_called,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mock_telephony_api_full,
        stq,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=request_json,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == response_status
    assert (
        stq.callcenter_operators_sync_roles.times_called
        == expected_stq_times_called
    )
    if response_status == 400:
        text_content = await response.text()
        assert text_content
    elif response_status == 200:
        content = await response.json()
        warning_logins = [
            warn['login'].split('@')[0]
            for warn in expected_response['warnings']
        ]
        expected_sec = []
        for (i, operator) in enumerate(request_json['operators']):
            if operator['login'].split('@')[0] not in warning_logins:
                expected_sec.append(i + 1)
        assert len(expected_sec) == expected_stq_times_called
        stq_calls = []
        for _ in range(expected_stq_times_called):
            stq_calls.append(stq.callcenter_operators_sync_roles.next_call())
        assert set(call['eta'] for call in stq_calls) == {
            datetime.datetime(2021, 3, 5, 12, 0, sec) for sec in expected_sec
        }
        assert {tuple(warn.items()) for warn in content['warnings']} == {
            tuple(warn.items()) for warn in expected_response['warnings']
        }
    else:
        content = await response.json()
        assert content == expected_response


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=[
        {'domain': 'unit.test', 'token_alias': 'UNITTESTS_CONNECT_OAUTH'},
        {'domain': 'drvrc.com', 'token_alias': 'DRVRC_CONNECT_OAUTH'},
    ],
)
@pytest.mark.parametrize(
    ['request_json', 'expected_domain'],
    (
        pytest.param(
            {
                'operators': [
                    {
                        'login': 'login1',
                        'first_name': 'name1',
                        'last_name': 'surname',
                        'callcenter_id': 'cc1',
                        'password': 'aaaaaaaaaa',
                        'supervisor_login': 'admin@unit.test',
                        'roles': ['ru_disp_operator'],
                        'phone_number': '+111',
                    },
                ],
            },
            'unit.test',
            id='empty_config',
            marks=pytest.mark.config(
                CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,  # noqa: E501
            ),
        ),
        pytest.param(
            {
                'operators': [
                    {
                        'login': 'login1',
                        'first_name': 'name1',
                        'last_name': 'surname',
                        'callcenter_id': 'cc1',
                        'password': 'aaaaaaaaaa',
                        'supervisor_login': 'admin@unit.test',
                        'roles': ['ru_disp_operator'],
                        'phone_number': '+111',
                    },
                ],
            },
            'drvrc.com',
            id='full_config',
            marks=pytest.mark.config(
                CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
                    'cc1': {
                        'name': 'cc_name_1',
                        'domain': 'drvrc.com',
                        'staff_login_required': False,
                        'timezone': 'Europe/Moscow',
                        'connect_department_id': 1,
                    },
                    'cc2': {
                        'name': 'cc_name_2',
                        'domain': 'unit.test',
                        'staff_login_required': False,
                        'timezone': 'Europe/Moscow',
                        'connect_department_id': 2,
                    },
                },
            ),
        ),
    ),
)
async def test_admin_bulk_add_domain(
        taxi_callcenter_operators_web,
        request_json,
        expected_domain,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_access_control_users,
        mockserver,
        web_context,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    @mockserver.json_handler('/blackbox', prefix=True)
    async def _handle_urls(*args, **kwargs):
        # return uid1 always
        body = {
            'users': [
                {
                    'login': {'value': 'login1@' + expected_domain},
                    'uid': {'value': 'uid1'},
                },
            ],
        }
        return web.Response(text=json.dumps(body))

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=request_json,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200

    db_operator = models.Operator.from_db(
        await test_utils.get_operator('uid1', web_context),
    )

    assert db_operator.working_domain == expected_domain


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_admin_bulk_add_name(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        web_context,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.NORMAL_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'warnings': []}

    records = await test_utils.get_operators(['uid1', 'uid2'], web_context)
    operators = [models.Operator.from_db(record) for record in records]
    for operator in operators:
        assert operator.first_name == 'name' + operator.yandex_uid[3]
        assert operator.last_name == 'surname'
        if operator.middle_name:
            assert operator.middle_name == 'middlename'
            assert operator.full_name == ' '.join(
                [
                    operator.last_name,
                    operator.first_name,
                    operator.middle_name,
                ],
            )
        else:
            assert operator.full_name == ' '.join(
                [operator.last_name, operator.first_name],
            )


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_admin_bulk_add_tel_error(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mock_telephony_api_exception,
        web_context,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.NORMAL_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    content = await response.json()
    expected_response = {
        'warnings': [
            {'login': 'login1@unit.test', 'code': 'tel_error'},
            {'login': 'login2@unit.test', 'code': 'tel_error'},
        ],
    }
    assert {tuple(warn.items()) for warn in content['warnings']} == {
        tuple(warn.items()) for warn in expected_response['warnings']
    }

    records = await test_utils.get_operators(['uid1', 'uid2'], web_context)
    assert not records


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_new_tel_user(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    tel_calls = {'workphone_calls': 0, 'other_calls': 0}

    # use OPERATOR_1 from params
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            tel_calls['workphone_calls'] += 1
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        tel_calls['other_calls'] += 1
        return test_utils.make_tel_response()

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.SINGLE_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    assert tel_calls['workphone_calls'] == 1


@pytest.mark.parametrize(
    ['first_name', 'last_name', 'expected_first_name', 'expected_last_name'],
    (
        pytest.param(
            'Оксана', 'Митронова-Слободская', 'Оксана', 'Митронова-Слободская',
        ),
        pytest.param('Юлия', 'Мышкина (Кошкина)', 'Юлия', 'Мышкина Кошкина'),
        pytest.param('Youson', 'M`Bembe (II)', 'Youson', 'M Bembe II'),
    ),
    ids=['leave_minus', 'remove_parenthesis', 'remove_apostrophe'],
)
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_new_tel_user_bad_symbols(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
        first_name,
        last_name,
        expected_first_name,
        expected_last_name,
):
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        path = request.path_qs
        if 'work_phone' in path.lower():
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        if 'agent' in path.lower():
            assert parse.unquote(
                path.split('/')[-1].split('&')[0],
            ) == ' '.join([expected_last_name, expected_first_name])
            return test_utils.make_show_response(200, ['ololo'])
        if '_create' in path.lower():
            req_data = request.json['_DATA']
            assert req_data['FIRSTNAME'] == expected_first_name
            assert req_data['LASTNAME'] == expected_last_name
            return {
                'PARAM': {'REQ': ''},
                'DATA': {
                    'WORK_PHONE': req_data.get('WORKPHONE'),
                    'USERNAME': 'login1_unit.test',
                    'MAIL': 'login1_unit.test@yandex.ru',
                    'USERTYPE': '50',
                    'REALM': 'yandex.ru',
                    'EXPDATE': 1630487727,
                    'GRANTER': 2,
                    'LASTUPDATE': 1598951727,
                    'LASTCHANGE': 1598951727,
                    'ENABLED': 1,
                    'DISABLEREASON': '',
                    'GROUP': 'P_C_AUTH',
                },
                'TYPE': 'REPLY',
                'STATUSCODE': 200,
                'STATUSMSG': '',
                'STATUSDESC': None,
                'STATUS': True,
            }

    my_operator = copy.deepcopy(params.OPERATOR_1)
    my_operator['first_name'] = first_name
    my_operator['last_name'] = last_name

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json={'operators': [my_operator]},
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_inconsistent_workphone(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        web_context,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    tel_calls = {'workphone_calls': 0, 'other_calls': 0}
    inconsistent_agent_id = '123'
    # use OPERATOR_1 from params

    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            tel_calls['workphone_calls'] += 1
            return {
                'PARAM': {'REQ': ''},
                'DATA': {
                    'WORK_PHONE': inconsistent_agent_id,
                    'USERNAME': 'login1_unit.test',
                    'MAIL': 'login1_unit.test@yandex.ru',
                    'USERTYPE': '50',
                    'REALM': 'yandex.ru',
                    'EXPDATE': 1630487727,
                    'GRANTER': 2,
                    'LASTUPDATE': 1598951727,
                    'LASTCHANGE': 1598951727,
                    'ENABLED': 1,
                    'DISABLEREASON': '',
                    'GROUP': 'P_C_AUTH',
                },
                'TYPE': 'REPLY',
                'STATUSCODE': 200,
                'STATUSMSG': '',
                'STATUSDESC': None,
                'STATUS': True,
            }

        tel_calls['other_calls'] += 1
        return test_utils.make_tel_response()

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.SINGLE_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    assert tel_calls['workphone_calls'] == 1
    res_op = models.Operator.from_db(
        await test_utils.get_operator('uid1', web_context),
    )
    assert res_op.agent_id == inconsistent_agent_id  # change agent_id in db


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['disp_cc'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=[
        {'name': 'disp_cc', 'number': '123', 'allowed_clusters': ['1', '2']},
    ],
)
async def test_default_queue(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        pgsql,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    # use OPERATOR_1 from params
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        return test_utils.make_tel_response()

    req_json = copy.deepcopy(params.SINGLE_REQUEST)
    # add metaqueue to request
    req_json['operators'][0]['default_metaqueue'] = 'disp_cc'

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=req_json, headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT metaqueues FROM callcenter_auth.current_info WHERE id = 3;',
    )
    record = cursor.fetchall()
    metaqueues = record[0][0]
    assert 'disp_cc' in metaqueues


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_METAQUEUES=[
        {'name': 'disp_cc', 'number': '123', 'allowed_clusters': ['1', '2']},
    ],
)
async def test_bad_queue(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        pgsql,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    # use OPERATOR_1 from params
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        return test_utils.make_tel_response()

    req_json = copy.deepcopy(params.SINGLE_REQUEST)
    # add metaqueue to request
    req_json['operators'][0]['default_metaqueue'] = 'some_metaqueue'

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=req_json, headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    assert await response.json() == {
        'warnings': [{'login': 'login1', 'code': 'bad_metaqueue'}],
    }


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['one_metaqueue'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=[
        {
            'name': 'one_metaqueue',
            'number': '123',
            'allowed_clusters': ['1', '2'],
        },
    ],
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'unit.test',
            'staff_login_required': False,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'connect_department_id': 1,
            'default_metaqueues': ['one_metaqueue'],
        },
    },
)
async def test_default_metaqueue_from_config(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        pgsql,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    # use OPERATOR_1 from params
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        return test_utils.make_tel_response()

    req_json = copy.deepcopy(params.SINGLE_REQUEST)

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=req_json, headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f'SELECT metaqueues FROM callcenter_auth.current_info WHERE id = 3;',
    )
    record = cursor.fetchall()
    metaqueues = record[0][0]
    assert 'one_metaqueue' in metaqueues


@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_METAQUEUES=[
        {
            'name': 'one_metaqueue',
            'number': '123',
            'allowed_clusters': ['1', '2'],
        },
    ],
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'unit.test',
            'staff_login_required': False,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'connect_department_id': 1,
            'default_metaqueues': ['one_metaqueue', 'unexpected_metaqueue'],
        },
    },
)
async def test_unexpected_metaqueue_in_default_metaqueues(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mockserver,
        pgsql,
        mock_save_status,
        mock_set_status_cc_queues,
        mock_system_info,
):
    # use OPERATOR_1 from params
    @mockserver.json_handler('/yandex-tel/', prefix=True)
    async def _tel(request):
        if 'work_phone' in request.path_qs.lower():
            return {
                'PARAM': {},
                'DATA': False,
                'TYPE': 'REPLY',
                'STATUSCODE': 404,
                'STATUSMSG': 'User not found in AU database',
                'STATUSDESC': None,
                'STATUS': 'FALSE',
            }
        return test_utils.make_tel_response()

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.SINGLE_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'warnings': [{'code': 'db_error', 'login': 'login1@unit.test'}],
    }

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f'SELECT metaqueues FROM callcenter_auth.current_info WHERE id = 3;',
    )
    records = cursor.fetchall()
    assert not records

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute('SELECT staff_login FROM callcenter_auth.operators_access')
    data = cursor.fetchall()
    assert 'login1_staff' not in [one[0] for one in data]


@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_staff_login_verification_reset(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        pgsql,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json=params.NORMAL_REQUEST,
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT staff_login_state'
        f' FROM callcenter_auth.operators_access'
        f' WHERE yandex_uid=\'uid2\';',
    )
    record = cursor.fetchone()
    assert record[0] == 'unverified'


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql('callcenter_auth', files=['callcenter_auth_admin_only.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_delete_preffer_roles_when_add_operator(
        taxi_callcenter_operators_web,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_passport,
        mock_access_control_users,
        mock_telephony_api_full,
        stq,
        mock_set_status_cc_queues,
        mock_save_status,
        pgsql,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json={'operators': [params.OPERATOR_1]},
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    assert stq.callcenter_operators_sync_roles.times_called == 1

    content = await response.json()
    assert content == {'warnings': []}

    response = await taxi_callcenter_operators_web.post(
        '/v2/admin/operators/delete_bulk/',
        json={'logins': ['login1@unit.test']},
    )
    assert response.status == 200
    assert stq.callcenter_operators_sync_roles.times_called == 2

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'ru_disp_call_center_head', 'admin'),
        ('supervisor_uid', 'ru_disp_team_leader', 'admin'),
        ('uid1', 'ru_disp_operator', 'admin'),  # not deleted
    ]

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json={
            'operators': [
                {
                    'login': 'login1',
                    'first_name': 'name1',
                    'last_name': 'surname',
                    'callcenter_id': 'cc1',
                    'password': 'aaaaaaaaaa',
                    'supervisor_login': 'admin@unit.test',
                    'roles': ['ru_support_operator'],
                    'phone_number': '+111',
                    'timezone': 'Europe/Moscow',
                    'staff_login': 'login1_staff',
                },
            ],
        },
        headers={'X-Ya-User-Ticket': 'ticket'},
    )
    assert response.status == 200
    assert stq.callcenter_operators_sync_roles.times_called == 3

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'ru_disp_call_center_head', 'admin'),
        ('supervisor_uid', 'ru_disp_team_leader', 'admin'),
        ('uid1', 'ru_support_operator', 'admin'),  # only new role
    ]
