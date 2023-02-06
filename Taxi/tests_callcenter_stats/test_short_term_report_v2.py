import json

import pytest


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    return obj


# This config is duplicated in global config 'config.json' to prevent
# flap of this test in case when update metrics job already finished and
# we need to wait 60 seconds for a new start
@pytest.mark.config(CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1)
@pytest.mark.config(CALLCENTER_OPERATORS_PAUSE_TYPES=['break'])
@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.pgsql(
    'callcenter_stats',
    files=['callcenter_stats_create_calls.sql', 'insert_operator_status.sql'],
)
@pytest.mark.parametrize(
    ['request_metaqueues', 'expected_code', 'expected_response'],
    [
        pytest.param(['queue1'], 200, 'expected_response_queue1.json'),
        pytest.param(None, 200, 'expected_response_all.json'),
        pytest.param([], 200, 'expected_response_empty.json'),
    ],
)
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
async def test_short_term_report(
        taxi_callcenter_stats,
        load_json,
        request_metaqueues,
        expected_response,
        expected_code,
        use_new_data,
):
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/statistics/short_term_report',
        json={'metaqueues': request_metaqueues}
        if request_metaqueues is not None
        else {},
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        print(json.dumps(response_json, indent=4))
        assert _ordered(response_json) == _ordered(
            load_json(expected_response),
        )


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
@pytest.mark.config(CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1)
@pytest.mark.config(CALLCENTER_OPERATORS_PAUSE_TYPES=['break'])
@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.pgsql(
    'callcenter_stats',
    files=['callcenter_stats_create_calls.sql', 'insert_operator_status.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'help': {
            'metaqueues': ['queue2', 'queue3'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'corp': {
            'metaqueues': ['queue1'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'god': {
            'metaqueues': ['queue1', 'queue2', 'queue3', 'queue4', 'queue5'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.parametrize(
    [
        'request_body',
        'expected_status_code',
        'expected_metaqueues',
        'expected_response',
    ],
    (
        pytest.param(
            {},
            200,
            ['queue1', 'queue2', 'queue3', 'queue4'],
            'expected_response_all.json',
            id='no project',
        ),
        pytest.param(
            {'project': 'god'},
            200,
            ['queue1', 'queue2', 'queue3', 'queue4', 'queue5'],
            'expected_response_all_god.json',  # queue5 will be empty filled
            id='god-mode project',
        ),
        pytest.param(
            {'project': 'corp'},
            200,
            ['queue1'],
            'expected_response_queue1.json',
            id='corp project',
        ),
        pytest.param(
            {'project': 'disp'}, 500, None, None, id='non-existent project',
        ),
    ),
)
async def test_project_filtering(
        taxi_callcenter_stats,
        mock_personal,
        load_json,
        request_body,
        expected_status_code,
        expected_metaqueues,
        expected_response,
        use_new_data,
):
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/statistics/short_term_report',
        json=request_body,
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        response_json = response.json()
        metaqueues = {
            metaqueue['metaqueue_name']
            for metaqueue in response_json['metaqueues']
        }
        assert metaqueues == set(expected_metaqueues)
        if expected_response:
            print(json.dumps(response_json, indent=4))
            assert _ordered(response_json) == _ordered(
                load_json(expected_response),
            )
