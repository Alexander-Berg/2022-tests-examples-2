import copy
import json

import aiohttp
import pytest

from test_callcenter_operators import params
from test_callcenter_operators import test_utils

ADD_BULK_URL = '/v3/admin/operators/internal/add_bulk/'

EXISTED_STAFF_LOGIN = 'login1'

OPERATOR_1 = {
    'callcenter_id': 'cc1',
    'login': EXISTED_STAFF_LOGIN,
    'roles': [],
}
BAD_CC_OPERATOR = {
    'callcenter_id': 'cc2',
    'login': EXISTED_STAFF_LOGIN,
    'roles': [],
}
WARNING_BAD_SUPERVISOR = {
    'code': 'bad_supervisor_login',
    'login': EXISTED_STAFF_LOGIN + '@yandex-team.ru',
}


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
@pytest.mark.parametrize(
    ['request_json', 'response_status', 'expected_response'],
    (
        pytest.param(
            {'operators': [copy.deepcopy(OPERATOR_1)]},
            200,
            {'warnings': []},
            id='ok',
        ),
        pytest.param(
            {'operators': [copy.deepcopy(BAD_CC_OPERATOR)]},
            200,
            {'warnings': [{'login': 'login1', 'code': 'bad_callcenter_id'}]},
            id='bad_cc',
        ),
    ),
)
async def test_admin_bulk_add(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        expected_response,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=request_json,
    )
    assert response.status == response_status
    if response_status == 400:
        text_content = await response.text()
        assert text_content
    elif response_status == 200:
        content = await response.json()
        assert {tuple(warn.items()) for warn in content['warnings']} == {
            tuple(warn.items()) for warn in expected_response['warnings']
        }
    else:
        content = await response.json()
        assert content == expected_response


@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'bad_domain.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_not_internal_cc(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json={'operators': [copy.deepcopy(OPERATOR_1)]},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'warnings': [
            {'login': 'login1@bad_domain.ru', 'code': 'bad_callcenter_id'},
        ],
    }


@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_staff_error(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        return aiohttp.web.Response(status=500)

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json={'operators': [copy.deepcopy(OPERATOR_1)]},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'warnings': [
            {'login': 'login1@yandex-team.ru', 'code': 'not_found_in_staff'},
        ],
    }


@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_staff_not_found(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json={'operators': [copy.deepcopy(OPERATOR_1)]},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'warnings': [
            {'login': 'login1@yandex-team.ru', 'code': 'not_found_in_staff'},
        ],
    }


@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_bad_supervisor(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        web_context,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    request = {
        'operators': [
            {
                'callcenter_id': 'cc1',
                'login': EXISTED_STAFF_LOGIN,
                'roles': [],
                'supervisor_login': 'chief-another@yandex-team.ru',
            },
        ],
    }

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=request,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'warnings': [WARNING_BAD_SUPERVISOR]}


@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_not_empty_supervisor(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        web_context,
        mock_set_status_cc_queues,
        mock_save_status,
        pgsql,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief_another'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    request = {
        'operators': [
            {
                'callcenter_id': 'cc1',
                'login': EXISTED_STAFF_LOGIN,
                'roles': [],
                'supervisor_login': 'chief@yandex-team.ru',
            },
        ],
    }
    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=request,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'warnings': []}

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT supervisor_login'
        f' FROM callcenter_auth.operators_access '
        f'WHERE yandex_login=\'{EXISTED_STAFF_LOGIN}\';',
    )
    result = cursor.fetchall()
    assert result[0][0] == 'chief@yandex-team.ru'


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': [
                'one_metaqueue',
                'second_metaqueue',
                'third_metaqueue',
            ],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'default_metaqueues': ['one_metaqueue', 'second_metaqueue'],
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'second_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'third_metaqueue', 'allowed_clusters': ['1']},
    ],
)
async def test_set_default_metaqueues(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        mockserver,
        pgsql,
        mock_system_info,
        mock_callcenter_queues,
        taxi_config,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

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

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [(1, 'disconnected', None, [])]

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json={
            'operators': [
                {
                    'callcenter_id': 'cc1',
                    'login': EXISTED_STAFF_LOGIN,
                    'roles': [],
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'warnings': []}

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
        (2, 'disconnected', None, ['one_metaqueue', 'second_metaqueue']),
    ]


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'display_name': 'Карго',
            'metaqueues': ['third_metaqueue'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc1': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'default_metaqueues': ['one_metaqueue', 'second_metaqueue'],
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'second_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'third_metaqueue', 'allowed_clusters': ['1']},
    ],
)
async def test_default_metaqueue_in_request(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        mockserver,
        pgsql,
        mock_system_info,
        mock_callcenter_queues,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

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

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [(1, 'disconnected', None, [])]

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL,
        json={
            'operators': [
                {
                    'callcenter_id': 'cc1',
                    'login': EXISTED_STAFF_LOGIN,
                    'roles': [],
                    'default_metaqueue': 'third_metaqueue',
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'warnings': []}

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
        (2, 'disconnected', None, ['third_metaqueue']),
    ]


@pytest.mark.now('2021-03-05T12:00:00.00Z')
@pytest.mark.pgsql('callcenter_auth', files=['chief_in_db.sql'])
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'cc2': {
            'name': 'cc_name_2',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
            'default_metaqueues': [
                'one_metaqueue',
                'metaqueue_which_not_in_CALLCENTER_METAQUEUES',
            ],
        },
    },
    CALLCENTER_METAQUEUES=[
        {'name': 'one_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'second_metaqueue', 'allowed_clusters': ['1']},
        {'name': 'third_metaqueue', 'allowed_clusters': ['1']},
    ],
)
@pytest.mark.parametrize(
    ['request_json', 'response_status'],
    (
        pytest.param(
            {
                'operators': [
                    {
                        'callcenter_id': 'cc2',
                        'login': EXISTED_STAFF_LOGIN,
                        'roles': [],
                    },
                ],
            },
            200,
            id='with_metaqueues_not_in_callcenter_metaqueues',
        ),
    ),
)
async def test_with_metaqueues_not_in_callcenter_metaqueues(
        taxi_callcenter_operators_web,
        request_json,
        response_status,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        mockserver,
        pgsql,
        mock_system_info,
        mock_callcenter_queues,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': list()}
        for login in request.query['login'].split(','):
            if login == EXISTED_STAFF_LOGIN:
                op_info = {
                    'login': EXISTED_STAFF_LOGIN,
                    'uid': 'some_uid',
                    'chief': {'login': 'chief'},
                    'phones': [{'number': '123', 'is_main': True}],
                    'name': {
                        'first': {'ru': 'Иван'},
                        'last': {'ru': 'Иванов'},
                    },
                    'telegram_accounts': [
                        {'value': 'telega', 'private': True},
                    ],
                    'official': {'is_dismissed': False, 'is_robot': False},
                }
                body['result'].append(op_info)
        return aiohttp.web.Response(status=200, body=json.dumps(body))

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

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    for line in data:
        line[3].sort()

    assert data == [(1, 'disconnected', None, [])]

    response = await taxi_callcenter_operators_web.post(
        ADD_BULK_URL, json=request_json,
    )
    assert response.status == response_status

    content = await response.json()
    assert content == {
        'warnings': [{'code': 'db_error', 'login': 'login1@yandex-team.ru'}],
    }

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT id, status, sub_status, metaqueues '
        'FROM callcenter_auth.current_info '
        'ORDER BY id;',
    )
    data = cursor.fetchall()
    assert data == [(1, 'disconnected', None, [])]

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_login ' 'FROM callcenter_auth.operators_access',
    )
    data = cursor.fetchall()
    assert 'login1' not in [one[0] for one in data]
