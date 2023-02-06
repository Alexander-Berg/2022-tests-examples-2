import pytest

CALLS_EVENTS_HISTORY_URL = (
    '/ivr-dispatcher/v1/ivr-framework/get-calls-events-history'
)
GENERAL_CALL_HISTORY_URL = '/cc/v1/callcenter-stats/v1/general-call-history'
DISTLOCK_TASK_NAME = 'call-events-history-loader'


@pytest.mark.config(
    CALLCENTER_STATS_CALL_EVENTS_HISTORY_LOADER={
        'call_events_limit': 128,
        'enabled': True,
        'period_ms': 1000,
    },
)
@pytest.mark.parametrize(
    ['events_data', 'expected_data'],
    [
        pytest.param(
            'events_data_1.json', 'expected_data_1.json', id='originate',
        ),
        pytest.param(
            'events_data_2.json',
            'expected_data_2.json',
            id='answer playback error',
        ),
        pytest.param(
            'events_data_3.json', 'expected_data_3.json', id='answer success',
        ),
        pytest.param(
            'events_data_4.json',
            'expected_data_4.json',
            id='answer ask hangup',
        ),
    ],
)
async def test(
        taxi_callcenter_stats,
        load_json,
        mock_personal,
        testpoint,
        mockserver,
        events_data,
        expected_data,
):
    @mockserver.json_handler(CALLS_EVENTS_HISTORY_URL)
    def calls_events_history(request):
        cursor = int(request.query['cursor'])
        data = load_json(events_data)
        if cursor < data['next_cursor']:
            return mockserver.make_response(status=200, json=data)
        return mockserver.make_response(
            status=200, json={'events': [], 'next_cursor': cursor},
        )

    @testpoint('load-call-events-history-finished')
    def calls_events_history_finished(data):
        pass

    await taxi_callcenter_stats.enable_testpoints()

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_stats.spawn_task(DISTLOCK_TASK_NAME):
        await calls_events_history_finished.wait_call()

    # Check result
    assert calls_events_history.next_call()
    response = await taxi_callcenter_stats.post(
        GENERAL_CALL_HISTORY_URL, json={},
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_data)
