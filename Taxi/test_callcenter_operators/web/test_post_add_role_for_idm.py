import json

import aiohttp
import pytest


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'cargo_operator': {
            'group': 'cargo_operators',
            'local_name': '[Карго] Оператор',
            'project': 'cargo',
            'tags': ['operator', 'cc-reg'],
        },
        'cargo_qa_specialist': {
            'group': 'cargo_qa_specialists',
            'local_name': '[Карго] Специалист по контролю качества',
            'project': 'cargo',
        },
        'ru_disp_slavyansk_operator': {
            'group': 'slavyansk_operators',
            'local_name': '[Славянск] Оператор диспетчерской',
            'project': 'disp_slavyansk',
            'tags': ['operator', 'cc-reg'],
        },
        'operator': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'supervisor': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'admin': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg'],
        },
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'yandex_team': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_post_add_role_for_idm(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        stq,
        mock_system_info,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        body = {'result': []}
        for login in request.query['login'].split(','):
            if login == 'login2':
                op_info = {
                    'login': 'login2',
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

    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()

    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
        ],
    }

    assert stq.callcenter_operators_sync_roles.times_called == 0
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"direct": "operator"}'},
    )
    assert stq.callcenter_operators_sync_roles.times_called == 1
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {'code': 0}

    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()

    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
            {
                'login': 'login2',
                'roles': [
                    {'callcenter_stuff': 'disp_slavyansk', 'role': 'operator'},
                ],
            },
        ],
    }

    # check idempotency of add role
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"direct": "operator"}'},
    )
    assert stq.callcenter_operators_sync_roles.times_called == 2
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {'code': 0}

    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
            {
                'login': 'login2',
                'roles': [
                    {'callcenter_stuff': 'disp_slavyansk', 'role': 'operator'},
                ],
            },
        ],
    }

    # adding role for user that already exists
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"direct": "supervisor"}'},
    )
    assert stq.callcenter_operators_sync_roles.times_called == 3
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {'code': 0}

    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
            {
                'login': 'login2',
                'roles': [
                    {'callcenter_stuff': 'disp_slavyansk', 'role': 'operator'},
                    {'callcenter_stuff': 'disp', 'role': 'supervisor'},
                ],
            },
        ],
    }


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'cargo_operator': {
            'group': 'cargo_operators',
            'local_name': '[Карго] Оператор',
            'project': 'cargo',
            'tags': ['operator', 'cc-reg'],
        },
        'cargo_qa_specialist': {
            'group': 'cargo_qa_specialists',
            'local_name': '[Карго] Специалист по контролю качества',
            'project': 'cargo',
        },
        'ru_disp_slavyansk_operator': {
            'group': 'slavyansk_operators',
            'local_name': '[Славянск] Оператор диспетчерской',
            'project': 'disp_slavyansk',
            'tags': ['operator', 'cc-reg'],
        },
        'operator': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'supervisor': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'admin': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg'],
        },
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP={
        'yandex_team': {
            'name': 'cc_name_1',
            'domain': 'yandex-team.ru',
            'staff_login_required': True,
            'telegram_login_required': False,
            'timezone': 'Europe/Moscow',
        },
    },
)
async def test_error_if_warning(
        taxi_callcenter_operators_web,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        stq,
):
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        return aiohttp.web.Response(status=500, body=json.dumps({}))

    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()

    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
        ],
    }

    assert stq.callcenter_operators_sync_roles.times_called == 0
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"direct": "operator"}'},
    )
    assert stq.callcenter_operators_sync_roles.times_called == 0
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'code': 1,
        'error': (
            'bulk_add_internal_operators_v3 return status=200, '
            'warnings=[AddOperatorWarning(login=\'login2@yandex-team.ru\', '
            'code=\'not_found_in_staff\')]'
        ),
    }
