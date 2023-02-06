import asyncio
import copy
import json
import time

import pytest


from tests_eventus_sample import pipeline_tools

_OEP_PIPELINES = {
    'description': '',
    'st_ticket': '',
    'source': {'name': 'lbkx_test_events'},
    'root': {
        'output': {'sink_name': 'bulk-sink', 'error_handling_policy': {}},
        'operations': [],
    },
    'name': 'lbkx_test_events',
}

_RETRY_CFG_LIMITED = {
    'max_attempts': 5,
    'min_delay_ms': 0,
    'max_delay_ms': 180001,
    'delay_factor': 1,
}

_RETRY_CFG_UNLIMITED = {
    'min_delay_ms': 0,
    'max_delay_ms': 180001,
    'delay_factor': 1,
}


@pytest.mark.parametrize(
    'pipeline_retry_policy, '
    'count_of_fails, count_of_retries_to_rms, expect_error',
    [
        pytest.param(
            {'attempts': 5},
            3,
            4,
            False,
            id='pipeline retry policy success after retry',
        ),
        pytest.param(
            {'attempts': 5},
            10,
            5,
            True,
            id='pipeline retry policy error after retry',
        ),
        pytest.param(
            None,
            10,
            5,
            True,
            marks=[
                pytest.mark.config(
                    EVENTUS_PIPELINE_DEFAULT_RETRY_POLICY=_RETRY_CFG_LIMITED,
                ),
            ],
            id='cfg retry policy error after retry',
        ),
        pytest.param(
            None,
            10,
            5,
            True,
            marks=[
                pytest.mark.config(
                    EVENTUS_PIPELINE_DEFAULT_RETRY_POLICY=_RETRY_CFG_LIMITED,
                ),
            ],
            id='cfg retry policy error after retry',
        ),
        pytest.param(
            None,
            10,
            11,
            False,
            marks=[
                pytest.mark.config(
                    EVENTUS_PIPELINE_DEFAULT_RETRY_POLICY=_RETRY_CFG_UNLIMITED,
                ),
            ],
            id='unlimited cfg retry policy success after retry',
        ),
    ],
)
async def test_error_handling(
        taxi_eventus_sample,
        metrics_snapshot,
        testpoint,
        count_of_fails,
        count_of_retries_to_rms,
        expect_error,
        taxi_eventus_orchestrator_mock,
        pipeline_retry_policy,
        taxi_config,
):
    await metrics_snapshot.take_snapshot()

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    counter = count_of_fails

    @testpoint('bulk-sink::error-injector')
    def sink_error_testpoint(data):
        nonlocal counter
        if counter:
            counter = counter - 1
            return {'inject_failure': True}

        return {'inject_failure': False}

    pipeline_config = copy.deepcopy(_OEP_PIPELINES)

    if pipeline_retry_policy:
        pipeline_config['root']['output']['error_handling_policy'][
            'retry_policy'
        ] = pipeline_retry_policy

    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_eventus_sample,
        [pipeline_config],
        force_pipeline_update=True,
    )
    await taxi_eventus_sample.run_task('invalidate-seq_num')

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(1)),
                'topic': 'smth',
                'cookie': 'cookie_for_rms_sink_0',
            },
        ),
    )
    assert response.status_code == 200

    assert (await commit.wait_call())['data'] == 'cookie_for_rms_sink_0'

    deadline = time.time() + 1.0
    while (
            time.time() < deadline
            and sink_error_testpoint.times_called < count_of_retries_to_rms
    ):
        await asyncio.sleep(0.05)

    assert sink_error_testpoint.times_called == count_of_retries_to_rms

    metrics = await metrics_snapshot.get_metrics_diff()
    sink_metrics_diff = metrics['pipeline-statistics']['lbkx_test_events'][
        'sink_stats'
    ]['bulk-sink'].get_diff()

    assert sink_metrics_diff['retry_count'] == count_of_retries_to_rms - 1

    if expect_error:
        assert sink_metrics_diff['success_count'] == 0
        assert sink_metrics_diff['error_count'] == 1
    else:
        assert sink_metrics_diff['success_count'] == 1
        assert sink_metrics_diff['error_count'] == 0
