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
            'tags': ['operator', 'cc-reg', 'idm'],
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
            'tags': ['operator', 'cc-reg', 'idm'],
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
            'tags': ['operator', 'cc-reg', 'idm'],
        },
    },
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo', 'ru_cargo_support_courier'],
            'reg_groups': ['ru'],
            'should_use_internal_queue_service': True,
        },
        'disp': {
            'display_name': 'Диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'reg_groups': ['ru'],
            'should_use_internal_queue_service': True,
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
async def test_get_info_for_idm(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.get('/v1/idm/info', json={})
    assert resp.status == 200
    resp_body = await resp.json()
    assert resp_body == {
        'code': 0,
        'roles': {
            'name': {'en': 'Call center Taxi', 'ru': 'Колл-центр Такси'},
            'slug': 'callcenter_stuff',
            'values': {
                'cargo': {
                    'name': {'en': 'cargo', 'ru': 'Карго'},
                    'roles': {
                        'name': {'en': 'Role', 'ru': 'Роль'},
                        'slug': 'role',
                        'values': {
                            'cargo_operator': {
                                'name': {
                                    'en': 'cargo_operator',
                                    'ru': '[Карго] Оператор',
                                },
                            },
                        },
                    },
                },
                'common': {
                    'name': {'en': 'common', 'ru': 'Common'},
                    'roles': {
                        'name': {'en': 'Role', 'ru': 'Роль'},
                        'slug': 'role',
                        'values': {
                            'ru_eats_support_operator': {
                                'name': {
                                    'en': 'ru_eats_support_operator',
                                    'ru': 'Оператор саппорта Яндекс.Еды',
                                },
                            },
                        },
                    },
                },
                'disp_slavyansk': {
                    'name': {'en': 'disp_slavyansk', 'ru': 'Славянск'},
                    'roles': {
                        'name': {'en': 'Role', 'ru': 'Роль'},
                        'slug': 'role',
                        'values': {
                            'ru_disp_slavyansk_operator': {
                                'name': {
                                    'en': 'ru_disp_slavyansk_operator',
                                    'ru': '[Славянск] Оператор диспетчерской',
                                },
                            },
                        },
                    },
                },
            },
        },
    }
