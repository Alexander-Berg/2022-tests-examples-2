import copy
import json

import pytest

from tests_order_events_producer import pipeline_tools


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.parametrize(
    'consumer_name', ['communal-events', 'cron-kd-drivers'],
)
async def test_invalid_value_in_communal_topic_pipeline(
        taxi_order_events_producer,
        consumer_name,
        testpoint,
        taxi_config,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_events_producer,
        pipeline_tools.get_default_pipelines_config(),
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('call::log_sink::process')
    def log_sink_process(data):
        pass

    await taxi_order_events_producer.run_task('invalidate-seq_num')
    await taxi_order_events_producer.enable_testpoints()
    await taxi_order_events_producer.invalidate_caches()

    for i in range(10):
        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': consumer_name,
                    'data': '}{asdasd' + str(i) + '}{',
                    'topic': 'smth',
                    'cookie': 'cookie_parsing_failed',
                },
            ),
        )
        assert response.status_code == 200

    expected_cookies = ['cookie_parsing_failed'] * 10

    cookies = []
    for i in range(10):
        cookies.append((await commit.wait_call())['data'])
    assert cookies == expected_cookies
    assert not log_sink_process.times_called


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.parametrize(
    'consumer_name', ['communal-events', 'cron-kd-drivers'],
)
async def test_communal_topic_pipeline(
        taxi_order_events_producer,
        consumer_name,
        testpoint,
        taxi_config,
        mockserver,
        taxi_eventus_orchestrator_mock,
):
    await taxi_eventus_orchestrator_mock.set_pipelines_config(
        testpoint,
        taxi_order_events_producer,
        pipeline_tools.get_default_pipelines_config(),
    )

    @testpoint('logbroker_commit')
    def commit(data):
        pass

    @testpoint('call::log_sink::process')
    def log_sink_process(data):
        pass

    await taxi_order_events_producer.run_task('invalidate-seq_num')
    await taxi_order_events_producer.enable_testpoints()
    await taxi_order_events_producer.invalidate_caches()

    expected_log_sink_data = []
    expected_cookies = []

    data_obj = {
        'event': {
            'created': '2019-01-01T00:00:00+00:00',
            'statistics': {
                'host': 'localhost',
                'no_tvm_events': 0,
                'services': [],
            },
            'idempotency_token': '',
            'name': 'statistics',
        },
        'source': 'eventus-proxy',
        'topic': '/topic/statistics',
    }

    for i in range(10):
        data_obj['event']['idempotency_token'] = str(i)
        cookie = 'cookie' + str(i)
        data_str = json.dumps(data_obj)

        response = await taxi_order_events_producer.post(
            '/tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': consumer_name,
                    'data': data_str,
                    'topic': 'smth',
                    'cookie': cookie,
                },
            ),
        )

        assert response.status_code == 200

        for_expected = copy.deepcopy(data_obj)
        for_expected['internal_seq_num'] = i
        for_expected['oep_processing_time'] = 1546300800.0
        expected_log_sink_data.append(for_expected)
        expected_cookies.append(cookie)

    log_sink_data = []
    cookies = []
    for i in range(10):
        log_sink_data.append((await log_sink_process.wait_call())['data'])
        cookies.append((await commit.wait_call())['data'])

    assert (
        sorted(
            log_sink_data, key=lambda msg: msg['event']['idempotency_token'],
        )
        == expected_log_sink_data
    )
    assert cookies == expected_cookies
