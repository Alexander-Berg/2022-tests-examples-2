import datetime

import pytest


_NOW_DATE = datetime.date(year=2007, month=1, day=1)


OPERATORS = [
    {
        'id': 1,
        'login': 'operator_1',
        'agent_id': 'agent01',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1001',
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'name_in_telephony': 'operator_1',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'login': 'operator_2',
        'agent_id': 'agent02',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'krasnodar_cc',
        'yandex_uid': '1002',
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'idm'}],
        'name_in_telephony': 'operator_2',
        'supervisor_login': 'operator_4',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 3,
        'login': 'operator_3',
        'agent_id': 'agent03',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1003',
        'roles': ['ru_support_operator'],
        'roles_info': [{'role': 'ru_support_operator', 'source': 'admin'}],
        'name_in_telephony': 'operator_3',
        'supervisor_login': 'operator_5',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 4,
        'login': 'operator_4',
        'agent_id': 'agent04',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1004',
        'roles': ['ru_disp_head'],
        'roles_info': [{'role': 'ru_disp_head', 'source': 'idm'}],
        'name_in_telephony': 'operator_3',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 10,
        'login': 'operator_10',
        'agent_id': 'agent10',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1010',
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'name_in_telephony': 'operator_10',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 11,
        'login': 'operator_11',
        'agent_id': 'agent11',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1011',
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'idm'}],
        'name_in_telephony': 'operator_11',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 12,
        'login': 'operator_12',
        'agent_id': 'agent12',
        'state': 'deleted',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1012',
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'name_in_telephony': 'operator_12',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
]


@pytest.mark.parametrize(
    'use_new_data',
    [
        pytest.param(
            True,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=True)],
        ),
        pytest.param(
            False,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=False)],
        ),
    ],
)
@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'ru_support_operator': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'ru_disp_operator': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'ru_disp_head': {
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
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'disp': {
            'display_name': 'Диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'disp_intl': {
            'display_name': 'Международная диспетчерская',
            'metaqueues': ['ru_taxi_test'],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'disp_kavkaz': {
            'display_name': 'Кавказ',
            'metaqueues': ['ru_taxi_test'],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'disp_slavyansk': {
            'display_name': 'Славянск',
            'metaqueues': [],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'market_support': {
            'display_name': 'Поддержка Маркета',
            'metaqueues': ['by_market_support'],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
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
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
    },
)
@pytest.mark.pgsql(
    'callcenter_stats',
    files=[
        'insert_operator_status.sql',
        'insert_call_history.sql',
        'insert_operator_history.sql',
    ],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_response'],
    [pytest.param({'limit': 100}, 'all_agents.json', id='all agents')],
)
async def test_values(
        taxi_callcenter_stats,
        mockserver,
        load_json,
        request_body,
        expected_response,
        use_new_data,
):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        return mockserver.make_response(
            status=200, json={'next_cursor': 2, 'operators': OPERATORS},
        )

    await taxi_callcenter_stats.invalidate_caches()

    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/dashboards/operators/', json=request_body,
    )
    assert response.status_code == 200
    response_json = response.json()
    if use_new_data:
        for operator in response_json['operators']:
            assert 'tel_status' in operator['status']
            operator['status'].pop('tel_status')
    assert response_json == load_json(expected_response)


@pytest.mark.parametrize(
    'use_new_data',
    [
        pytest.param(
            True,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=True)],
        ),
        pytest.param(
            False,
            marks=[pytest.mark.config(CALLCENTER_STATS_USE_NEW_DATA=False)],
        ),
    ],
)
@pytest.mark.now('2020-06-22T10:00:01.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'pr1': {
            'metaqueues': ['queue1'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'pr2': {
            'metaqueues': ['queue2'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.pgsql(
    'callcenter_stats',
    files=[
        'insert_operator_status.sql',
        'insert_call_history.sql',
        'insert_operator_history.sql',
    ],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_agents'],
    [
        pytest.param({'limit': 1}, [2], id='limit=1'),
        pytest.param({'limit': 2}, [2, 1], id='limit=2'),
        pytest.param(
            {'limit': 10, 'project': 'pr1'}, [1, 3, 11, 10, 4], id='project',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'supervisor_ids': [4]}},
            [2],
            id='supervisor_ids',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'callcenter_ids': ['krasnodar_cc']}},
            [2],
            id='callcenter_ids',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'subclusters': ['1']}},
            [1],
            id='subcluster: 1',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'subclusters': ['2']}},
            [2, 3],
            id='subcluster: 2',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'metaqueues': ['queue1']}},
            [1, 3],
            id='metaqueue: queue1',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'metaqueues': ['queue2']}},
            [2, 3],
            id='metaqueue: queue2',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'roles': ['ru_disp_head']}},
            [4],
            id='roles',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'statuses': ['paused']}},
            [2],
            id='statuses',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'substatuses': ['talking']}},
            [1],
            id='substatuses',
        ),
        pytest.param(
            {'limit': 10, 'filter': {'operator_ids': [1, 3]}},
            [1, 3],
            id='operator_ids',
        ),
        pytest.param(
            {
                'limit': 10,
                'filter': {'subclusters': ['2'], 'metaqueues': ['queue1']},
            },
            [3],
            id='subcluster: 2, metaqueue: queue1',
        ),
    ],
)
async def test_filtering(
        taxi_callcenter_stats,
        mockserver,
        request_body,
        expected_agents,
        use_new_data,
):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(request):
        return mockserver.make_response(
            status=200, json={'next_cursor': 2, 'operators': OPERATORS},
        )

    await taxi_callcenter_stats.invalidate_caches()

    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/dashboards/operators/', json=request_body,
    )
    assert response.status_code == 200
    response_json = response.json()
    agents = [op['profile']['id'] for op in response_json['operators']]
    assert set(agents) == set(expected_agents)
