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
            'tags': ['operator', 'cc-reg', 'admin'],
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
            'tags': ['operator', 'cc-reg', 'admin'],
        },
        'ru_disp_slavyansk_team_leader': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'ru_disp_team_leader': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'ru_eats_support_operator': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo', 'ru_cargo_support_courier'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp': {
            'display_name': 'Диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_intl': {
            'display_name': 'Международная диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_kavkaz': {
            'display_name': 'Кавказ',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_slavyansk': {'display_name': 'Славянск', 'metaqueues': []},
        'market_support': {
            'display_name': 'Поддержка Маркета',
            'metaqueues': ['by_market_support'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'support': {
            'display_name': 'Тех поддержка',
            'metaqueues': [
                'ru_taxi_support_another',
                'ru_taxi_support_forgotten',
                'ru_taxi_support_urgent',
                'ru_taxi_support_payment',
                'ru_davos_support_test',
                'ru_davos_support_driver_test',
            ],
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
async def test_get_v1_admin_roles(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.post(
        '/v1/admin/roles', json={'source': 'admin'},
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'roles': [
            {
                'local_project': 'Карго',
                'local_role': '[Карго] Оператор',
                'role': 'cargo_operator',
            },
            {
                'local_project': 'Славянск',
                'local_role': '[Славянск] Оператор диспетчерской',
                'role': 'ru_disp_slavyansk_operator',
            },
            {
                'local_project': 'Common',
                'local_role': 'Оператор саппорта Яндекс.Еды',
                'role': 'ru_eats_support_operator',
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
            'tags': ['operator', 'cc-reg', 'admin'],
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
            'tags': ['operator', 'cc-reg', 'admin'],
        },
        'ru_disp_slavyansk_team_leader': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'ru_disp_team_leader': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'ru_eats_support_operator': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo', 'ru_cargo_support_courier'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp': {
            'display_name': 'Диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_intl': {
            'display_name': 'Международная диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_kavkaz': {
            'display_name': 'Кавказ',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_slavyansk': {'display_name': 'Славянск', 'metaqueues': []},
        'market_support': {
            'display_name': 'Поддержка Маркета',
            'metaqueues': ['by_market_support'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'support': {
            'display_name': 'Тех поддержка',
            'metaqueues': [
                'ru_taxi_support_another',
                'ru_taxi_support_forgotten',
                'ru_taxi_support_urgent',
                'ru_taxi_support_payment',
                'ru_davos_support_test',
                'ru_davos_support_driver_test',
            ],
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
async def test_get_all_roles(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.post('/v1/admin/roles', json={})
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'roles': [
            {
                'local_project': 'Карго',
                'local_role': '[Карго] Оператор',
                'role': 'cargo_operator',
            },
            {
                'local_project': 'Карго',
                'local_role': '[Карго] Специалист по контролю качества',
                'role': 'cargo_qa_specialist',
            },
            {
                'local_project': 'Славянск',
                'local_role': '[Славянск] Оператор диспетчерской',
                'role': 'ru_disp_slavyansk_operator',
            },
            {
                'local_project': 'Славянск',
                'local_role': '[Славянск] Руководитель группы',
                'role': 'ru_disp_slavyansk_team_leader',
            },
            {
                'local_project': 'Диспетчерская',
                'local_role': 'Руководитель группы',
                'role': 'ru_disp_team_leader',
            },
            {
                'local_project': 'Common',
                'local_role': 'Оператор саппорта Яндекс.Еды',
                'role': 'ru_eats_support_operator',
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
            'tags': ['operator', 'cc-reg', 'admin'],
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
            'tags': ['operator', 'cc-reg', 'admin'],
        },
        'ru_disp_slavyansk_team_leader': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'ru_disp_team_leader': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'ru_eats_support_operator': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo', 'ru_cargo_support_courier'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp': {
            'display_name': 'Диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_intl': {
            'display_name': 'Международная диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_kavkaz': {
            'display_name': 'Кавказ',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_slavyansk': {'display_name': 'Славянск', 'metaqueues': []},
        'market_support': {
            'display_name': 'Поддержка Маркета',
            'metaqueues': ['by_market_support'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'support': {
            'display_name': 'Тех поддержка',
            'metaqueues': [
                'ru_taxi_support_another',
                'ru_taxi_support_forgotten',
                'ru_taxi_support_urgent',
                'ru_taxi_support_payment',
                'ru_davos_support_test',
                'ru_davos_support_driver_test',
            ],
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
async def test_filter_by_project(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.post(
        '/v1/admin/roles', json={'project': 'disp_slavyansk'},
    )
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'roles': [
            {
                'local_project': 'Славянск',
                'local_role': '[Славянск] Оператор диспетчерской',
                'role': 'ru_disp_slavyansk_operator',
            },
            {
                'local_project': 'Славянск',
                'local_role': '[Славянск] Руководитель группы',
                'role': 'ru_disp_slavyansk_team_leader',
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
            'project': 'cargo',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
        'cargo_qa_specialist': {
            'group': 'cargo_qa_specialists',
            'local_name': '[Карго] Специалист по контролю качества',
            'project': 'cargo',
        },
        'ru_disp_slavyansk_operator': {
            'group': 'slavyansk_operators',
            'project': 'disp_slavyansk',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
        'ru_disp_slavyansk_team_leader': {
            'group': 'slavyansk_team_leaders',
            'project': 'disp_slavyansk',
        },
        'ru_disp_team_leader': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'ru_eats_support_operator': {
            'group': 'ya_eats_support_operators',
            'project': '',
            'tags': ['operator', 'cc-reg', 'admin'],
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo', 'ru_cargo_support_courier'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_intl': {
            'display_name': 'Международная диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'disp_slavyansk': {
            'display_name': 'Славянск',
            'metaqueues': [],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
        'support': {
            'display_name': 'Тех поддержка',
            'metaqueues': [
                'ru_taxi_support_another',
                'ru_taxi_support_forgotten',
                'ru_taxi_support_urgent',
                'ru_taxi_support_payment',
                'ru_davos_support_test',
                'ru_davos_support_driver_test',
            ],
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
async def test_not_enoth_data_in_configs(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.post('/v1/admin/roles', json={})
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'roles': [
            {
                'local_project': 'Карго',
                'local_role': 'cargo_operator',
                'role': 'cargo_operator',
            },
            {
                'local_project': 'Карго',
                'local_role': '[Карго] Специалист по контролю качества',
                'role': 'cargo_qa_specialist',
            },
            {
                'local_project': 'Славянск',
                'local_role': 'ru_disp_slavyansk_operator',
                'role': 'ru_disp_slavyansk_operator',
            },
            {
                'local_project': 'Славянск',
                'local_role': 'ru_disp_slavyansk_team_leader',
                'role': 'ru_disp_slavyansk_team_leader',
            },
            {
                'local_project': '!Роли нет в конфиге!',
                'local_role': 'Руководитель группы',
                'role': 'ru_disp_team_leader',
            },
            {
                'local_project': 'Common',
                'local_role': 'ru_eats_support_operator',
                'role': 'ru_eats_support_operator',
            },
        ],
    }
