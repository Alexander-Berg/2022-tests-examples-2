import pytest


# This config is duplicated in global config 'config.json' to prevent
# flap of this test in case when update metrics job already finished and
# we need to wait 60 seconds for a new start
@pytest.mark.config(CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1)
@pytest.mark.config(CALLCENTER_STATS_HOUR_REPORT_OPERATOR_PAST_VIEW_DEPTH=300)
@pytest.mark.pgsql(
    'callcenter_stats',
    files=[
        'callcenter_stats_call_history.sql',
        'callcenter_stats_operator_history.sql',
    ],
)
@pytest.mark.parametrize(
    ['request_body', 'expected_code', 'expected_response'],
    [
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:30:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': [],
            },
            400,
            'expected_response_400_not_rounded_hour_start.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:30:00Z',
                'metaqueues': [],
            },
            400,
            'expected_response_400_not_rounded_hour_end.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T08:00:00Z',
                'metaqueues': [],
            },
            400,
            'expected_response_400_bad_timepoints.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-24T10:00:00Z',
                'metaqueues': [],
            },
            400,
            'expected_response_400_too_big_timedelta.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support', 'null'],
            },
            200,
            'expected_response_all_plus_null.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support'],
            },
            200,
            'expected_response_all.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support'],
                'wait_sla_period': 7,
            },
            200,
            'expected_response_all_other_wait_sla_period.json',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': [],
            },
            200,
            'expected_response_empty.json',
        ),
    ],
)
async def test_hour_report(
        taxi_callcenter_stats,
        load_json,
        request_body,
        expected_code,
        expected_response,
):
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/statistics/hour_report', json=request_body,
    )
    assert response.status_code == expected_code
    if expected_response:
        response_json = response.json()
        print(response_json)
        assert response_json == load_json(expected_response)


@pytest.mark.config(CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1)
@pytest.mark.config(CALLCENTER_STATS_HOUR_REPORT_OPERATOR_PAST_VIEW_DEPTH=300)
@pytest.mark.pgsql(
    'callcenter_stats',
    files=[
        'callcenter_stats_call_history.sql',
        'callcenter_stats_operator_history.sql',
    ],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['disp'],
            'display_name': '',
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'god': {
            'metaqueues': ['disp', 'support'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status_code', 'expected_response'],
    (
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support'],
                'project': 'god',
            },
            200,
            'expected_response_all.json',
            id='god-mode project',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support'],
                'project': 'disp',
            },
            409,
            None,
            id='disp project',
        ),
        pytest.param(
            {
                'start_timepoint': '2020-06-23T09:00:00Z',
                'end_timepoint': '2020-06-23T10:00:00Z',
                'metaqueues': ['disp', 'support'],
                'project': 'heeelp',
            },
            500,
            None,
            id='non-existent project',
        ),
    ),
)
async def test_project_filtering(
        taxi_callcenter_stats,
        mock_personal,
        load_json,
        request_body,
        expected_status_code,
        expected_response,
):
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v2/statistics/hour_report', json=request_body,
    )
    assert response.status_code == expected_status_code
    if expected_response:
        response_json = response.json()
        assert response_json == load_json(expected_response)
