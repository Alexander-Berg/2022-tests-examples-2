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
)
async def test_post_remove_role_for_idm(taxi_callcenter_operators_web, stq):
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
                    {
                        'callcenter_stuff': 'disp_slavyansk',
                        'role': 'ru_disp_slavyansk_operator',
                    },
                ],
            },
        ],
    }

    assert stq.callcenter_operators_sync_roles.times_called == 0
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/remove-role',
        data={
            'login': 'login2',
            'role': '{"disp_slavyansk": "operator"}',
            'path': '/direct/manager',
        },
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
                    {
                        'callcenter_stuff': 'disp_slavyansk',
                        'role': 'ru_disp_slavyansk_operator',
                    },
                ],
            },
        ],
    }

    # check idempotency for remove-role
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/remove-role',
        data={
            'login': 'login2',
            'role': '{"disp_slavyansk": "operator"}',
            'path': '/direct/manager',
        },
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
                    {
                        'callcenter_stuff': 'disp_slavyansk',
                        'role': 'ru_disp_slavyansk_operator',
                    },
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
async def test_post_remove_role_for_idm_with_fired(
        taxi_callcenter_operators_web,
        stq,
        mock_telephony_api_full,
        pgsql,
        mock_staff,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
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
                    {
                        'callcenter_stuff': 'disp_slavyansk',
                        'role': 'ru_disp_slavyansk_operator',
                    },
                ],
            },
        ],
    }

    assert stq.callcenter_operators_sync_roles.times_called == 0
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/remove-role',
        data={
            'login': 'login2',
            'role': '{"disp_slavyansk": "operator"}',
            'path': '/direct/manager',
            'fired': 1,
        },
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {'code': 0}
    assert stq.callcenter_operators_sync_roles.times_called == 1

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'some_random_role', 'admin'),
        ('admin_uid', 'admin', 'idm'),
        ('supervisor_uid', 'some_random_role', 'admin'),
        ('supervisor_uid', 'supervisor', 'idm'),
        ('uid1', 'some_random_role', 'admin'),
        ('uid1', 'operator', 'idm'),
        ('uid2', 'ru_disp_slavyansk_operator', 'idm'),  # not deleted
        ('uid2', 'operator', 'idm'),  # not deleted
        ('uid2', 'some_random_role', 'admin'),  # not deleted
        ('uid3', 'some_random_role', 'admin'),
        ('uid3', 'operator', 'idm'),
    ]

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

    # check idempotency for remove-role for deleted operator
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/remove-role',
        data={
            'login': 'login2',
            'role': '{"disp_slavyansk": "ru_disp_slavyansk_operator"}',
            'path': '/direct/manager',
            'fired': 1,
        },
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
        ],
    }

    # test if add deleted operator delete preffer roles
    @mock_staff('/v3/persons')
    async def _handle(request, *args, **kwargs):
        assert request.query['login'].split(',') == ['login2']
        body = {
            'result': [
                {
                    'login': 'login2',
                    'uid': 'uid2',
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
                },
            ],
        }
        return aiohttp.web.Response(status=200, body=json.dumps(body))

    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"direct": "operator"}'},
    )
    assert stq.callcenter_operators_sync_roles.times_called == 2
    assert resp.status == 200
    assert await resp.json() == {'code': 0}

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

    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        'SELECT yandex_uid, role, source '
        'FROM callcenter_auth.m2m_operators_roles '
        'ORDER BY yandex_uid',
    )
    assert cursor.fetchall() == [
        ('admin_uid', 'admin', 'idm'),
        ('admin_uid', 'some_random_role', 'admin'),
        ('supervisor_uid', 'some_random_role', 'admin'),
        ('supervisor_uid', 'supervisor', 'idm'),
        ('uid1', 'operator', 'idm'),
        ('uid1', 'some_random_role', 'admin'),
        ('uid2', 'operator', 'idm'),  # only new role
        ('uid3', 'some_random_role', 'admin'),
        ('uid3', 'operator', 'idm'),
    ]

    # test second add role for deleted operator
    resp = await taxi_callcenter_operators_web.post(
        '/v1/idm/add-role',
        data={'login': 'login2', 'role': '{"cargo": "cargo_operator"}'},
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {'code': 0}
    assert stq.callcenter_operators_sync_roles.times_called == 3

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
                    {'callcenter_stuff': 'cargo', 'role': 'cargo_operator'},
                ],
            },
        ],
    }
