import datetime
import json

import pytest


_NOW_DATE = datetime.date(year=2007, month=1, day=1)


OPERATORS = [
    {
        'id': 1,
        'agent_id': '111',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1001',
        'queues': [],
        'roles': ['ru_disp_operator', 'ru_support_operator'],
        'roles_info': [
            {'role': 'ru_disp_operator', 'source': 'admin'},
            {'role': 'ru_support_operator', 'source': 'idm'},
        ],
        'state': 'ready',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'agent_id': '222',
        'callcenter_id': 'krasnodar_cc',
        'yandex_uid': '1002',
        'queues': [],
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'state': 'ready',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 3,
        'agent_id': '333',
        'callcenter_id': 'volgograd_cc',
        'yandex_uid': '1003',
        'queues': [],
        'roles': ['ru_disp_operator'],
        'roles_info': [{'role': 'ru_disp_operator', 'source': 'admin'}],
        'state': 'deleting',
        'employment_date': _NOW_DATE.isoformat(),
    },
    {
        'id': 2,
        'agent_id': '222',
        'callcenter_id': 'krasnodar_cc_new',
        'yandex_uid': '1002_new',
        'queues': [],
        'roles': ['ru_disp_operator_new'],
        'roles_info': [{'role': 'ru_disp_operator_new', 'source': 'admin'}],
        'state': 'deleted',
        'employment_date': _NOW_DATE.isoformat(),
    },
]
MOCK_OPERATORS = [
    {
        'id': op['id'],
        'login': f'operator_{op["id"]}',
        'yandex_uid': op['yandex_uid'],
        'agent_id': op['agent_id'],
        'state': op['state'],
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': op['callcenter_id'],
        'roles': op['roles'],
        'roles_info': op['roles_info'],
        'name_in_telephony': f'operator_{op["id"]}',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': op['employment_date'],
    }
    for op in OPERATORS
]

FIRST_UPDATE_CACHE_VALUE = {
    'data': {
        'operatorByIdMap': {'1': MOCK_OPERATORS[0], '2': MOCK_OPERATORS[1]},
        'operatorActiveByIdMap': {
            '1': MOCK_OPERATORS[0],
            '2': MOCK_OPERATORS[1],
        },
        'operatorByAgentIdMap': {
            '111': MOCK_OPERATORS[0],
            '222': MOCK_OPERATORS[1],
        },
        'operatorByLoginMap': {
            'operator_1': MOCK_OPERATORS[0],
            'operator_2': MOCK_OPERATORS[1],
        },
    },
}


@pytest.mark.config(
    CALLCENTER_STATS_CACHES={
        'operators-cache': {
            'full-update-interval-ms': 86400000,
            'request-limit': 2,
            'update-interval-ms': 100,
            'update-jitter-ms': 0,
        },
    },
)
@pytest.mark.parametrize(
    ['idx', 'expected_cache_value'],
    [
        pytest.param(None, FIRST_UPDATE_CACHE_VALUE, id='only full'),
        pytest.param(1, FIRST_UPDATE_CACHE_VALUE, id='full+inc no changes'),
        pytest.param(
            2,
            {
                'data': {
                    'operatorByIdMap': {
                        '1': MOCK_OPERATORS[0],
                        '2': MOCK_OPERATORS[1],
                        '3': MOCK_OPERATORS[2],
                    },
                    'operatorActiveByIdMap': {
                        '1': MOCK_OPERATORS[0],
                        '2': MOCK_OPERATORS[1],
                    },
                    'operatorByAgentIdMap': {
                        '111': MOCK_OPERATORS[0],
                        '222': MOCK_OPERATORS[1],
                        '333': MOCK_OPERATORS[2],
                    },
                    'operatorByLoginMap': {
                        'operator_1': MOCK_OPERATORS[0],
                        'operator_2': MOCK_OPERATORS[1],
                        'operator_3': MOCK_OPERATORS[2],
                    },
                },
            },
            id='full+inc new operator',
        ),
        pytest.param(
            3,
            {
                'data': {
                    'operatorByIdMap': {
                        '1': MOCK_OPERATORS[0],
                        '2': MOCK_OPERATORS[3],
                    },
                    'operatorActiveByIdMap': {'1': MOCK_OPERATORS[0]},
                    'operatorByAgentIdMap': {
                        '111': MOCK_OPERATORS[0],
                        '222': MOCK_OPERATORS[3],
                    },
                    'operatorByLoginMap': {
                        'operator_1': MOCK_OPERATORS[0],
                        'operator_2': MOCK_OPERATORS[3],
                    },
                },
            },
            id='full+inc operator changed',
        ),
    ],
)
async def test_operators_cache(
        taxi_callcenter_stats,
        mockserver,
        testpoint,
        expected_cache_value,
        idx,
):
    @testpoint('operators-cache-finish')
    def operators_cache_finish(data):
        pass

    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(http_request):
        request_json = json.loads(http_request.get_data())
        if request_json.get('consumer') != 'callcenter_ids_caches':
            assert request_json['limit'] == 2
        else:
            assert request_json['limit'] == 1000
        cursor = request_json.get('cursor')
        # full update begin
        if cursor is None:
            return mockserver.make_response(
                status=200,
                json={'next_cursor': 0, 'operators': MOCK_OPERATORS[:2]},
            )
        # full update end
        if cursor == 0:
            return mockserver.make_response(
                status=200, json={'next_cursor': 2, 'operators': []},
            )
        # incremental update
        if idx is not None and cursor == 2:
            return mockserver.make_response(
                status=200,
                json={'next_cursor': 3, 'operators': [MOCK_OPERATORS[idx]]},
            )
        # nothing more to update
        return mockserver.make_response(
            status=200, json={'next_cursor': cursor, 'operators': []},
        )

    await taxi_callcenter_stats.enable_testpoints()
    # we need to do full update again and reset testpoints,
    # because cache could have used operators_list mock from conftest
    while operators_cache_finish.times_called > 0:
        await operators_cache_finish.wait_call()
    await taxi_callcenter_stats.invalidate_caches()

    # full
    value = await operators_cache_finish.wait_call()
    assert value == FIRST_UPDATE_CACHE_VALUE

    # incremental
    await taxi_callcenter_stats.invalidate_caches(
        clean_update=False, cache_names=['operators-cache'],
    )
    value = await operators_cache_finish.wait_call()
    assert value == expected_cache_value
