import pytest


@pytest.mark.now('2020-07-07T12:00:00+03:00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.parametrize(
    ['handler'],
    [
        pytest.param(
            '/cc/v1/callcenter-operators/v1/operators/find',
            id='find_for_new_admin',
        ),
        pytest.param('/v1/admin/operators/find', id='find_for_old_admin'),
    ],
)
@pytest.mark.parametrize(
    ['req', 'expected_ids', 'expected_yandex_uids'],
    [
        pytest.param(
            {},
            {1, 2, 3, 4, 5},
            {'admin_uid', 'uid3', 'uid1', 'uid2', 'supervisor_uid'},
            id='not empty db without filters',
        ),
        pytest.param(
            {'filter': {}},
            {1, 2, 3, 4, 5},
            {'admin_uid', 'uid3', 'uid1', 'uid2', 'supervisor_uid'},
            id='not empty db without filters',
        ),
        pytest.param(
            {'filter': {'callcenter_ids': ['cc1']}},
            {1, 2, 3, 4},
            {'supervisor_uid', 'uid2', 'admin_uid', 'uid1'},
            id='cc request',
        ),
        pytest.param(
            {'filter': {'callcenter_ids': ['cc3']}},
            set(),
            set(),
            id='bad cc request',
        ),
        pytest.param(
            {'filter': {'roles': ['operator']}},
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='role request',
        ),
        pytest.param(
            {'filter': {'roles': ['odmen']}},
            set(),
            set(),
            id='bad role request',
        ),
        pytest.param(
            {'filter': {'states': ['deleted']}},
            {4},
            {'uid2'},
            id='state request',
        ),
        pytest.param(
            {'project': 'disp'},
            {1, 2, 4, 5},
            {'supervisor_uid', 'admin_uid', 'uid3', 'uid2'},
            id='project request',
        ),
        pytest.param(
            {'project': 'help'},
            {1, 2, 3},
            {'admin_uid', 'uid1', 'supervisor_uid'},
            id='project request on multi project operator',
        ),
        pytest.param(
            {
                'filter': {
                    'callcenter_ids': ['cc1', 'cc2'],
                    'roles': ['operator'],
                },
                'project': 'god',
            },
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='all params request',
        ),
        pytest.param(
            {'search': {}},
            {1, 2, 3, 4, 5},
            {'admin_uid', 'uid3', 'uid1', 'uid2', 'supervisor_uid'},
            id='empty search',
        ),
        pytest.param(
            {'search': {'name_prefix': 'name'}},
            set(),
            set(),
            id='name_prefix=name',
        ),
        pytest.param(
            {'search': {'name_prefix': 'surna'}},
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='name_prefix=surna',
        ),
        pytest.param(
            {'search': {'name_infix': 'name'}},
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='name_infix=name',
        ),
        pytest.param(
            {'search': {'name_prefix': 'name', 'name_infix': 'name'}},
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='name_prefix+name_infix=name',
        ),
        pytest.param(
            {'search': {'login_prefix': 'log'}},
            {3, 4, 5},
            {'uid2', 'uid3', 'uid1'},
            id='login_prefix=log',
        ),
        pytest.param(
            {'search': {'login_infix': 'unit'}},
            {1, 2, 3, 4, 5},
            {'uid1', 'admin_uid', 'supervisor_uid', 'uid2', 'uid3'},
            id='login_infix=unit',
        ),
        pytest.param(
            {'search': {'login_prefix': 'name'}},
            set(),
            set(),
            id='login_prefix=name',
        ),
        pytest.param(
            {'search': {'login_infix': 'name'}},
            set(),
            set(),
            id='login_infix=name',
        ),
        pytest.param(
            {
                'filter': {'callcenter_ids': ['cc1']},
                'search': {'name_infix': 'middlename'},
            },
            {3, 4},
            {'uid1', 'uid2'},
            id='intersection of search+filter',
        ),
        pytest.param(
            {'search': {'name_infix': 'middlename', 'login_prefix': 'sup'}},
            {2, 3, 4},
            {'supervisor_uid', 'uid1', 'uid2'},
            id='union of name_infix+login_prefix',
        ),
        pytest.param(
            {'search': {'yandex_uid': 'uid'}},
            set(),
            set(),
            id='yandex_uid=uid',
        ),
        pytest.param(
            {'search': {'yandex_uid': 'uid1'}},
            {3},
            {'uid1'},
            id='yandex_uid=uid1',
        ),
        pytest.param(
            {'search': {'agent_id': 'uid'}}, set(), set(), id='agent_id=uid',
        ),
        pytest.param(
            {'search': {'agent_id': '1000000001'}},
            {4},
            {'uid2'},
            id='agent_id=1000000001',
        ),
    ],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['help'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'corp': {
            'metaqueues': ['corp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp': {
            'metaqueues': ['disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'god': {
            'metaqueues': ['help', 'corp', 'disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
async def test_find_operators(
        taxi_callcenter_operators_web,
        handler,
        req,
        expected_ids,
        expected_yandex_uids,
):
    req['limit'] = 10
    resp = await taxi_callcenter_operators_web.post(handler, json=req)
    assert resp.status == 200
    resp_body = await resp.json()
    resp_ids = {op['id'] for op in resp_body['operators']}
    assert resp_ids == expected_ids
    assert {
        op['yandex_uid'] for op in resp_body['operators']
    } == expected_yandex_uids


@pytest.mark.now('2020-07-07T12:00:00+03:00')
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.parametrize(
    ['handler'],
    [
        pytest.param(
            '/cc/v1/callcenter-operators/v1/operators/find',
            id='find_for_new_admin',
        ),
        pytest.param('/v1/admin/operators/find', id='find_for_old_admin'),
    ],
)
@pytest.mark.parametrize(
    ['req', 'expected_uids_count'],
    [
        pytest.param({'limit': 0}, 0),
        pytest.param({'limit': 3}, 3),
        pytest.param({'limit': 100}, 5),
    ],
)
async def test_find_operators_limit(
        taxi_callcenter_operators_web, handler, req, expected_uids_count,
):
    resp = await taxi_callcenter_operators_web.post(handler, json=req)
    assert resp.status == 200
    resp_body = await resp.json()
    assert len(resp_body['operators']) == expected_uids_count
