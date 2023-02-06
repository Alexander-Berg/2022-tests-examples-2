import json

import pytest

from testsuite.utils import callinfo

from tests_eventus_sample import pipeline_tools


OEP_PIPELINES = [
    {
        'description': 'description_test',
        'st_ticket': '',
        'source': {'name': 'lbkx_test_events'},
        'root': {'sink_name': 'log_sink'},
        'name': 'order-events',
    },
]


async def test_pipeline_disabled(
        taxi_eventus_sample,
        testpoint,
        taxi_config,
        taxi_eventus_orchestrator_mock,
):
    pipeline_disabled = True

    @testpoint('call::log_sink::process')
    def tp_await(data):
        nonlocal pipeline_disabled
        assert not pipeline_disabled

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    pipelines = OEP_PIPELINES

    pipelines[0]['is_disabled'] = pipeline_disabled
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, pipelines,
    )

    response = await taxi_eventus_sample.post(
        '/tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'lbkx_test_events',
                'data': json.dumps(pipeline_tools.create_event(1)),
                'topic': 'smth',
                'cookie': 'cookie_for_order_events',
            },
        ),
    )

    assert response.status_code == 200

    with pytest.raises(callinfo.CallQueueTimeoutError):
        await tp_await.wait_call(timeout=2.0)
    assert tp_await.times_called == 0
    assert commit.times_called == 0

    pipeline_disabled = False
    pipelines[0]['is_disabled'] = pipeline_disabled
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint, taxi_eventus_sample, pipelines,
    )

    await tp_await.wait_call()
    await commit.wait_call()
