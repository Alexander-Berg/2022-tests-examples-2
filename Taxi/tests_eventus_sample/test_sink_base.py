import datetime as dt
import json
from typing import Any
from typing import Dict

import pytest

_NOW = dt.datetime(2022, 5, 1, 13, 57, 8, tzinfo=dt.timezone.utc)

_TEST_PARK_ID = 'test_park_id'
_TEST_PROFILE_ID = 'test_profile_id'
_TEST_UDID = 'test_udid'


@pytest.mark.parametrize(
    'inject_error, expected_attempts_count',
    [
        pytest.param(False, 1, id='commit no error'),
        pytest.param(True, 1, id='commit on errors'),
    ],
)
async def test_sink_commit(
        taxi_eventus_sample,
        testpoint,
        stq,
        taxi_eventus_orchestrator_mock,
        inject_error: bool,
        expected_attempts_count: int,
):
    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('sink::error-injector')
    def sink_error_testpoint(data):
        return {'inject_failure': inject_error}

    @testpoint('sink::send')
    def sink_send_testpoint(data):
        pass

    attempts_count = 10

    pipeline_sink_config: Dict[str, Any] = {'sink_name': 'sink'}

    pipeline_sink_config['error_handling_policy'] = {
        'retry_policy': {
            'attempts': attempts_count,
            'min_delay_ms': 1,
            'max_delay_ms': 10,
            'delay_factor': 2,
        },
        'erroneous_statistics_level': 'error',
    }

    pipeline_config = [
        {
            'name': 'lbkx_test_events',
            'description': '',
            'st_ticket': '',
            'source': {'name': 'lbkx_test_events'},
            'root': {'operations': [], 'output': pipeline_sink_config},
        },
    ]

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, pipeline_config,
    )

    event = {
        'topic': 'priority',
        'park_id': _TEST_PARK_ID,
        'profile_id': _TEST_PROFILE_ID,
        'unique_driver_id': _TEST_UDID,
    }

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(event),
                'topic': 'smth',
                'cookie': 'cookie_for_sink_0',
            },
        ),
    )

    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_sink_0'

    if inject_error:
        expected_attempts_count = attempts_count
    else:
        expected_attempts_count = 1

    assert sink_error_testpoint.times_called == expected_attempts_count
    assert sink_send_testpoint.times_called == expected_attempts_count
    for _ in range(expected_attempts_count):
        send_event = sink_send_testpoint.next_call()['data']['event']
        assert send_event == event
