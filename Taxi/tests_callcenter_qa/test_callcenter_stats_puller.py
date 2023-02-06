import pytest


def get_config(
        enabled=True, check_interval=100, minimal_duration=1, task_delay=0,
):
    return {
        'enabled': enabled,
        'check_interval': check_interval,
        'minimal_duration': minimal_duration,
        'task_delay': task_delay,
    }


@pytest.mark.parametrize(
    ['expected_testpoint_calls', 'expected_config'],
    (
        pytest.param(
            {'start': 1, 'enabled': 1, 'disabled': 0},
            get_config(enabled=True),
            id='puller enabled',
            marks=pytest.mark.config(
                CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                    enabled=True,
                ),
            ),
        ),
        pytest.param(
            {'start': 1, 'enabled': 0, 'disabled': 1},
            get_config(enabled=False),
            id='puller disabled',
            marks=pytest.mark.config(
                CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                    enabled=False,
                ),
            ),
        ),
    ),
)
async def test_activation(
        taxi_callcenter_qa,
        testpoint,
        expected_testpoint_calls,
        expected_config,
):
    calls = {'start': 0, 'enabled': 0, 'disabled': 0}

    @testpoint('callcenter-stats-puller::start')
    def handle_puller_start(data):
        calls['start'] = 1

    @testpoint('callcenter-stats-puller::enabled')
    def handle_puller_enabled(data):
        calls['enabled'] = 1

    @testpoint('callcenter-stats-puller::disabled')
    def handle_puller_disabled(data):
        calls['disabled'] = 1

    async with taxi_callcenter_qa.spawn_task(
            'distlock/callcenter-stats-puller',
    ):
        await handle_puller_start.wait_call()
        if expected_config['enabled']:
            await handle_puller_enabled.wait_call()
        else:
            await handle_puller_disabled.wait_call()

    assert calls == expected_testpoint_calls


@pytest.mark.pgsql('callcenter_qa', files=['insert_cursor.sql'])
@pytest.mark.parametrize(
    ['cc_stats_calls_count', 'expected_task_count', 'expected_last_cursor'],
    (
        pytest.param(
            5,
            3,
            5,
            id='minimal duration - 1 sec',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=1,
                    ),
                ),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter.json',
                ),
            ],
        ),
        pytest.param(
            5,
            2,
            5,
            id='minimal duration - 5 sec',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=5,
                    ),
                ),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter.json',
                ),
            ],
        ),
        pytest.param(
            5,
            0,
            5,
            id='minimal duration - 999 sec',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=999,
                    ),
                ),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter.json',
                ),
            ],
        ),
        pytest.param(
            4,
            3,
            5,
            id='minimal duration - 1 sec with last_cursor = 1',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=1,
                    ),
                ),
                pytest.mark.pgsql('callcenter_qa', files=['cursor_1.sql']),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter.json',
                ),
            ],
        ),
        pytest.param(
            4,
            2,
            5,
            id='minimal duration - 5 sec with last_cursor = 1',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=5,
                    ),
                ),
                pytest.mark.pgsql('callcenter_qa', files=['cursor_1.sql']),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter.json',
                ),
            ],
        ),
        pytest.param(
            5,
            0,
            5,
            id='filtered percent',
            marks=[
                pytest.mark.config(
                    CALLCENTER_QA_CC_STAT_PULLER_SETTINGS_V2=get_config(
                        minimal_duration=5,
                    ),
                ),
                pytest.mark.experiments3(
                    filename='exp3_callcenter_qa_calls_filter_percent.json',
                ),
            ],
        ),
    ),
)
async def test_get_calls(
        taxi_callcenter_qa,
        testpoint,
        cc_stats_calls_count,
        expected_task_count,
        expected_last_cursor,
        mock_cc_stats,
        pgsql,
):
    @testpoint('callcenter-stats-puller::get-calls-end')
    def handle_calls_count(data):
        assert data == {
            'call_count': cc_stats_calls_count,
            'task_count': expected_task_count,
        }

    async with taxi_callcenter_qa.spawn_task(
            'distlock/callcenter-stats-puller',
    ):
        await handle_calls_count.wait_call()

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT last_cursor FROM callcenter_qa.cc_stats_cursor LIMIT 1',
    )
    last_cursor = cursor.fetchone()[0]
    cursor.close()

    assert last_cursor == expected_last_cursor
