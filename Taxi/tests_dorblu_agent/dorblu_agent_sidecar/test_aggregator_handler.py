import copy
import datetime as dt
import json
import tempfile

from google.protobuf import json_format
import pytest
import yaml


def normalize_pb_message(message):
    message = copy.deepcopy(message)

    for rule in message['rules']:
        for cache_rate in rule['stats']['cacheRates']:
            cache_rate['entries'] = sorted(
                cache_rate['entries'], key=lambda x: x['cacheStatus'],
            )

        for key, stats in rule['stats'].items():
            rule['stats'][key] = sorted(stats, key=lambda x: x['prefix'])

    message['monitoring']['checks'] = sorted(
        message['monitoring']['checks'], key=lambda x: x['name'],
    )

    return message


def pb_messages_equal(lhs, rhs):
    return normalize_pb_message(lhs) == normalize_pb_message(rhs)


def normalize_solomon_request(request_json):
    request_json = copy.deepcopy(request_json)

    request_json['metrics'] = sorted(request_json['metrics'], key=json.dumps)

    return request_json


def solomon_requests_equal(lhs, rhs):
    return normalize_solomon_request(lhs) == normalize_solomon_request(rhs)


def normalize_juggler_request(request_json):
    request_json = copy.deepcopy(request_json)

    for item in request_json['events']:
        assert 'host' in item
        del item['host']

    request_json['events'] = sorted(request_json['events'], key=json.dumps)

    return request_json


def juggler_requests_equal(lhs, rhs):
    return normalize_juggler_request(lhs) == normalize_juggler_request(rhs)


async def test_simple(
        taxi_dorblu_agent_sidecar,
        taxi_dorblu_agent_sidecar_monitor,
        mocked_time,
        load_json,
        mockserver,
        load_json_message,
        testpoint,
        start_dorblu_agent,
        reset_agent_metrics,
        request_agent,
        fill_default_access_log,
        fill_default_log_format,
):
    await start_dorblu_agent()

    @testpoint('aggregator_request_completed')
    def _aggregator_request_completed(data):
        pass

    await taxi_dorblu_agent_sidecar.enable_testpoints()

    fill_default_log_format('log_format.conf')

    @mockserver.json_handler('/juggler/events')
    def _juggler_agent_mock(request):
        assert juggler_requests_equal(
            request.json, load_json('expected_juggler_request.json'),
        )

        return {
            'events': [{'code': 200}],
            'accepted_events': 777,
            'success': True,
        }

    @mockserver.json_handler('/solomon-agent/dorblu_agent')
    def _solomon_agent_mock(request):
        solomon_requests_equal(
            request.json, load_json('expected_solomon_request.json'),
        )

        return mockserver.make_response(status=200)

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 13))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('empty_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('simple_nginx_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14, 10))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    response_message = await request_agent(
        load_json_message('simple_aggregator_request.json'),
    )

    assert pb_messages_equal(
        json_format.MessageToDict(response_message),
        load_json('expected_agent_resp.json'),
    )

    await _aggregator_request_completed.wait_call()
    assert _solomon_agent_mock.times_called == 1
    assert _juggler_agent_mock.times_called == 1

    assert await taxi_dorblu_agent_sidecar_monitor.get_metric(
        'aggregator-handler',
    ) == load_json('expected_metrics.json')


@pytest.fixture(name='fill_envoy_access_log')
def fill_envoy_access_log_fixture(
        load, dorblu_config_path, default_log_path, default_log_format_path,
):
    with tempfile.NamedTemporaryFile(
            'w',
    ) as log_file, tempfile.NamedTemporaryFile('w') as log_format_file:
        dorblu_config = {
            'primary_log': {
                'log_file': {
                    'log_path': str(default_log_path),
                    'log_format_path': str(default_log_format_path),
                    'juggler_service_prefix': '',
                    'solomon_service': 'dorblu_agent',
                },
            },
            'secondary_logs': {
                'processing_timeout': '10s',
                'log_files': [
                    {
                        'log_path': log_file.name,
                        'log_format_path': log_format_file.name,
                        'juggler_service_prefix': 'envoy-',
                        'solomon_service': 'dorblu_agent_envoy',
                    },
                ],
            },
        }

        with dorblu_config_path.open('w') as dorblu_config_file:
            yaml.dump(dorblu_config, dorblu_config_file)

        log_format_file.write(load('envoy_log_format.conf'))
        log_format_file.flush()

        def _impl(fname):
            log_file.write(load(fname))
            log_file.flush()

        yield _impl


async def test_envoy(
        taxi_dorblu_agent_sidecar,
        taxi_dorblu_agent_sidecar_monitor,
        mocked_time,
        load_json,
        mockserver,
        load_json_message,
        testpoint,
        start_dorblu_agent,
        reset_agent_metrics,
        request_agent,
        fill_default_access_log,
        fill_default_log_format,
        fill_envoy_access_log,
):
    await start_dorblu_agent()

    @testpoint('aggregator_request_completed')
    def _aggregator_request_completed(data):
        pass

    await taxi_dorblu_agent_sidecar.enable_testpoints()

    fill_default_log_format('log_format.conf')

    juggler_envoy_times_called = 0
    juggler_nginx_times_called = 0

    @mockserver.json_handler('/juggler/events')
    def _juggler_agent_mock(request):
        nonlocal juggler_envoy_times_called
        nonlocal juggler_nginx_times_called

        if request.json['events'][0]['service'].startswith('envoy-'):
            juggler_envoy_times_called += 1
            expected_juggler_request = 'expected_juggler_request_envoy.json'
        else:
            juggler_nginx_times_called += 1
            expected_juggler_request = 'expected_juggler_request.json'

        assert juggler_requests_equal(
            request.json, load_json(expected_juggler_request),
        )

        return {
            'events': [{'code': 200}],
            'accepted_events': 777,
            'success': True,
        }

    @mockserver.json_handler('/solomon-agent/dorblu_agent_envoy')
    def _solomon_agent_envoy_mock(request):
        solomon_requests_equal(
            request.json, load_json('expected_solomon_request_envoy.json'),
        )

        return mockserver.make_response(status=200)

    @mockserver.json_handler('/solomon-agent/dorblu_agent')
    def _solomon_agent_mock(request):
        solomon_requests_equal(
            request.json, load_json('expected_solomon_request.json'),
        )

        return mockserver.make_response(status=200)

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 13))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('empty_access.log')
    fill_envoy_access_log('empty_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    fill_default_access_log('simple_nginx_access.log')
    fill_envoy_access_log('simple_envoy_access.log')
    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    mocked_time.set(dt.datetime(2021, 9, 17, 13, 14, 10))
    await taxi_dorblu_agent_sidecar.invalidate_caches()
    response_message = await request_agent(
        load_json_message('simple_aggregator_request.json'),
    )

    assert pb_messages_equal(
        json_format.MessageToDict(response_message),
        load_json('expected_agent_resp.json'),
    )

    await _aggregator_request_completed.wait_call()
    assert _solomon_agent_mock.times_called == 1
    assert _solomon_agent_envoy_mock.times_called == 1
    assert _juggler_agent_mock.times_called == 2
    assert juggler_nginx_times_called == 1
    assert juggler_envoy_times_called == 1

    assert await taxi_dorblu_agent_sidecar_monitor.get_metric(
        'aggregator-handler',
    ) == load_json('expected_metrics.json')
