import pytest

from test_callcenter_operators import params


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.parametrize(
    [
        'callcenter_ids',
        'supervisor_uids',
        'mentor_uids',
        'roles',
        'yandex_uids',
        'states',
        'expected_uids',
        'expected_agent_ids',
    ],
    [
        pytest.param(
            ['cc2'],
            None,
            None,
            None,
            None,
            None,
            {'uid3'},
            {1000000002},
            id='callcenter_filter',
        ),
        pytest.param(
            ['cc3'],
            None,
            None,
            None,
            None,
            None,
            set(),
            set(),
            id='bad_callcenter_filter',
        ),
        pytest.param(
            None,
            ['123'],
            None,
            None,
            None,
            None,
            {'uid1', 'supervisor_uid', 'uid3'},
            {1000000000, 1000000002, 1888888888},
            id='supervisor_filter',
        ),
        pytest.param(
            None,
            ['not_exist'],
            None,
            None,
            None,
            None,
            set(),
            set(),
            id='bad_supervisor_filter',
        ),
        pytest.param(
            None,
            None,
            ['123'],
            None,
            None,
            None,
            {'admin_uid', 'supervisor_uid'},
            {1777777777, 1888888888},
            id='mentor_filter',
        ),
        pytest.param(
            None,
            None,
            ['unknown_mentor'],
            None,
            None,
            None,
            set(),
            set(),
            id='bad_mentor_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            ['operator'],
            None,
            None,
            {'uid1', 'uid3'},
            {1000000000, 1000000002},
            id='role_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            ['odmen'],
            None,
            None,
            set(),
            set(),
            id='bad_role_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            ['uid1'],
            None,
            {'uid1'},
            {1000000000},
            id='yandex_uid_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            ['not_exist_yandex_uid'],
            None,
            set(),
            set(),
            id='bad_yandex_uid_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            None,
            ['deleted'],
            {'uid2', '123'},
            {1000000001, 99999},
            id='states_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            None,
            ['deleted'],
            {'uid2', '123'},
            {1000000001, 99999},
            id='states_filter_for_deleted',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            None,
            ['not_exist_state'],
            set(),
            set(),
            id='bad_states_filter',
        ),
        pytest.param(
            None,
            None,
            None,
            None,
            None,
            None,
            {'uid1', 'uid3', 'uid6', 'admin_uid', 'supervisor_uid'},
            {1000000000, 1000000002, 1000000003, 1777777777, 1888888888},
            id='all_data',
        ),
        pytest.param(
            ['cc1'],
            None,
            ['supervisor_uid', '123'],
            ['operator'],
            ['uid1', 'uid3', 'uid6', 'admin_uid'],
            ['ready'],
            {'uid1'},
            {1000000000},
            id='all_filters_except_supervisor_uids',
        ),
    ],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
)
async def test_v2_operators_profiles(
        taxi_callcenter_operators_web,
        callcenter_ids,
        supervisor_uids,
        mentor_uids,
        roles,
        yandex_uids,
        states,
        expected_uids,
        expected_agent_ids,
        mock_passport,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        '/v3/admin/operators/add_bulk/',
        json={'operators': [params.OPERATOR_6]},
    )
    assert response.status == 200

    body = {'filter': {}, 'offset': 0, 'limit': 1000}
    if yandex_uids is not None:
        body['filter']['yandex_uids'] = yandex_uids
    if roles is not None:
        body['filter']['roles'] = roles
    if mentor_uids is not None:
        body['filter']['mentor_uids'] = mentor_uids
    if callcenter_ids is not None:
        body['filter']['callcenter_ids'] = callcenter_ids
    if supervisor_uids is not None:
        body['filter']['supervisor_uids'] = supervisor_uids
    if states is not None:
        body['filter']['states'] = states
    else:
        body['filter']['states'] = ['enlisting', 'ready', 'deleting']

    response = await taxi_callcenter_operators_web.post(
        '/v1/admin/operators/profiles/', json=body,
    )
    content = await response.json()
    ops = content['operators']
    uids = {op['yandex_uid'] for op in ops}
    agent_ids = {op['agent_id'] for op in ops}
    assert uids == expected_uids
    assert agent_ids == expected_agent_ids
    assert content['full_count'] == len(expected_agent_ids)


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'display_name': 'Диспетчерская Такси',
            'metaqueues': ['ru_taxi_disp', 'ar_taxi_disp_er'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
async def test_fields_response(
        taxi_callcenter_operators_web,
        mock_passport,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        '/v3/admin/operators/add_bulk/',
        json={'operators': [params.OPERATOR_6]},
    )
    assert response.status == 200
    body = {
        'filter': {
            'callcenter_ids': ['cc1'],
            'mentor_uids': ['supervisor_uid', '123'],
            'roles': ['operator'],
            'states': ['ready'],
            'yandex_uids': ['uid1', 'uid3', 'uid6', 'admin_uid'],
        },
        'offset': 0,
        'limit': 1000,
    }

    response = await taxi_callcenter_operators_web.post(
        '/v1/admin/operators/profiles/', json=body,
    )
    content = await response.json()
    assert content == {
        'full_count': 1,
        'operators': [
            {
                'agent_id': 1000000000,
                'callcenter_id': 'cc1',
                'employment_date': '2016-06-01',
                'full_name': 'surname name1 middlename',
                'login': 'login1@unit.test',
                'mentor_login': 'supervisor@unit.test',
                'name_in_telephony': 'login1_unit.test',
                'phone': '+111',
                'roles': ['operator'],
                'roles_info': [
                    {
                        'local_project': 'Диспетчерская Такси',
                        'role': 'operator',
                        'source': 'admin',
                        'local_role': 'оператор',
                    },
                ],
                'staff_login': 'login1_staff',
                'state': 'ready',
                'supervisor_login': 'admin@unit.test',
                'telegram_login': 'telegram_login_1',
                'timezone': 'Europe/Moscow',
                'yandex_uid': 'uid1',
            },
        ],
    }


async def test_empty_body(taxi_callcenter_operators_web):
    response = await taxi_callcenter_operators_web.post(
        '/v1/admin/operators/profiles/',
        json={'filter': {}, 'offset': 0, 'limit': 1000},
    )
    assert response.status == 200
    content = await response.json()
    ops = content['operators']
    assert ops == []
    assert content['full_count'] == 0


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP=params.ACCESS_CONTROL_ROLES,
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
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
async def test_pagination(
        taxi_callcenter_operators_web,
        mock_passport,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_system_info,
):
    all_yandex_uids = {'supervisor_uid', 'uid1', 'admin_uid', 'uid3'}
    for offset in range(4):
        response = await taxi_callcenter_operators_web.post(
            '/v1/admin/operators/profiles/',
            json={
                'filter': {'states': ['enlisting', 'ready', 'deleting']},
                'offset': offset,
                'limit': 1,
            },
        )
        content = await response.json()
        ops = content['operators']
        uids = {op['yandex_uid'] for op in ops}
        assert len(uids) == 1
        assert [*uids][0] in all_yandex_uids
        all_yandex_uids.remove(uids.pop())
        assert content['full_count'] == 4
    assert all_yandex_uids == set()


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
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
            'project': '',
            'group': 'operators',
            'local_name': 'оператор',
        },
    },
    CALLCENTER_OPERATORS_CALLCENTER_INFO_MAP=params.CALLCENTER_INFO_MAP,
    CALLCENTER_OPERATORS_ORGANIZATIONS_TOKENS=params.ORGANIZATIONS_TOKENS,
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'display_name': 'Диспетчерская Такси',
            'metaqueues': ['ru_taxi_disp', 'ar_taxi_disp_er'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
    CALLCENTER_OPERATORS_IDM_SYNC={
        'default_name_of_callcenter': 'yandex_team',
        'name_for_slug': 'callcenter_stuff',
        'human_readable_name_for_common_project': 'Common',
    },
)
async def test_common_project(
        taxi_callcenter_operators_web,
        mock_passport,
        mock_connect_create_user,
        mock_connect_change_user_info,
        mock_access_control_users,
        mock_telephony_api_full,
        mock_set_status_cc_queues,
        mock_save_status,
        mock_system_info,
):
    response = await taxi_callcenter_operators_web.post(
        '/v3/admin/operators/add_bulk/',
        json={'operators': [params.OPERATOR_6]},
    )
    assert response.status == 200
    body = {
        'filter': {
            'callcenter_ids': ['cc1'],
            'mentor_uids': ['supervisor_uid', '123'],
            'roles': ['operator'],
            'states': ['ready'],
            'yandex_uids': ['uid1', 'uid3', 'uid6', 'admin_uid'],
        },
        'offset': 0,
        'limit': 1000,
    }

    response = await taxi_callcenter_operators_web.post(
        '/v1/admin/operators/profiles/', json=body,
    )
    content = await response.json()
    assert content == {
        'full_count': 1,
        'operators': [
            {
                'agent_id': 1000000000,
                'callcenter_id': 'cc1',
                'employment_date': '2016-06-01',
                'full_name': 'surname name1 middlename',
                'login': 'login1@unit.test',
                'mentor_login': 'supervisor@unit.test',
                'name_in_telephony': 'login1_unit.test',
                'phone': '+111',
                'roles': ['operator'],
                'roles_info': [
                    {
                        'local_project': 'Common',
                        'role': 'operator',
                        'source': 'admin',
                        'local_role': 'оператор',
                    },
                ],
                'staff_login': 'login1_staff',
                'state': 'ready',
                'supervisor_login': 'admin@unit.test',
                'telegram_login': 'telegram_login_1',
                'timezone': 'Europe/Moscow',
                'yandex_uid': 'uid1',
            },
        ],
    }
