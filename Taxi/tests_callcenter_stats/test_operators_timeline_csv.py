import pytest


@pytest.mark.config(
    CALLCENTER_STATS_HOUR_REPORT_OPERATOR_PAST_VIEW_DEPTH=300,
)  # 5 hours
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['disp'],
            'display_name': '',
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
    },
)
@pytest.mark.config(
    CALLCENTER_STATS_OPERATOR_TIMELINE_CSV={
        'status_map': {'connected': 'C', 'disconnected': 'D', 'paused': 'P'},
        'substatus_map': {'break': 'B'},
    },
)  # 5 hours
@pytest.mark.pgsql('callcenter_stats', files=['insert_operator_history.sql'])
@pytest.mark.parametrize(
    [
        'request_body',
        'expected_code',
        'expected_content_type',
        'expected_content_disposition',
        'expected_text',
    ],
    [
        pytest.param({}, 400, 'text/html', None, None),
        pytest.param(
            {
                'time_range_filter': {
                    'from': '2020-01-01T05:00:00Z',
                    'to': '2020-01-01T05:10:00Z',
                },
            },
            200,
            'text/csv',
            'attachment; filename="operator_timeline__'
            '2020-01-01T08:00:00+0300_2020-01-01T08:10:00+0300.csv"',
            'response.csv',
        ),
        pytest.param(
            {
                'project': 'disp',
                'time_range_filter': {
                    'from': '2020-01-01T05:00:00Z',
                    'to': '2020-01-01T05:10:00Z',
                },
            },
            200,
            'text/csv',
            'attachment; filename="operator_timeline_disp_'
            '2020-01-01T08:00:00+0300_2020-01-01T08:10:00+0300.csv"',
            'response_disp.csv',
        ),
    ],
)
async def test_operators_timeline_csv(
        taxi_callcenter_stats,
        load,
        request_body,
        expected_code,
        expected_content_type,
        expected_content_disposition,
        expected_text,
):
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v1/reports/operators_timeline_csv',
        json=request_body,
    )
    assert response.status_code == expected_code
    if expected_content_type is not None:
        assert response.content_type == expected_content_type
    if expected_content_disposition is not None:
        assert (
            response.headers['Content-Disposition']
            == expected_content_disposition
        )
    if expected_text is not None:
        assert response.text == load(expected_text)
