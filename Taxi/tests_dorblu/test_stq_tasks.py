import copy
import itertools
import logging
import socket
import struct
import threading

# pylint: disable=import-error
import dorblu_pb2
import pytest


logger = logging.getLogger(__name__)

EXPECTED_AGENT_RESPONSE = [
    {
        'seconds': '60',
        'version': '2',
        'groupName': 'PLACEHOLDER',
        'project': '',
        'datacenter': 'test_dc',
        'rules': [
            {
                'filter': {'type': 'Dummy'},
                'name': 'TOTAL',
                'stats': {
                    'timings': [
                        {'prefix': 'maps_ok_request_timings', 'type': 'req'},
                        {'prefix': 'maps_ok_upstream_timings', 'type': 'ups'},
                        {'prefix': 'maps_ok_ssl_timings', 'type': 'ssl'},
                    ],
                    'requests': [
                        {
                            'first': 400,
                            'last': 400,
                            'count': '0',
                            'prefix': 'maps_400_rps.rps',
                        },
                        {
                            'first': 401,
                            'last': 401,
                            'count': '0',
                            'prefix': 'maps_401_rps.rps',
                        },
                        {
                            'first': 404,
                            'last': 404,
                            'count': '0',
                            'prefix': 'maps_404_rps.rps',
                        },
                        {
                            'first': 499,
                            'last': 499,
                            'count': '0',
                            'prefix': 'maps_timeouts_rps.rps',
                        },
                        {
                            'first': 500,
                            'last': 599,
                            'count': '0',
                            'prefix': 'maps_errors_rps.rps',
                        },
                        {
                            'first': 200,
                            'last': 299,
                            'count': '0',
                            'prefix': 'maps_ok_rps.rps',
                        },
                        {
                            'first': 431,
                            'last': 431,
                            'count': '0',
                            'prefix': 'maps_errors_431_rps.rps',
                        },
                        {
                            'first': 405,
                            'last': 407,
                            'count': '0',
                            'prefix': 'maps_405_407_rps.rps',
                        },
                    ],
                    'bytesCounters': [{'prefix': 'bps.bps', 'counter': '0'}],
                    'cacheRates': [
                        {
                            'prefix': 'cache',
                            'entries': [
                                {'cacheStatus': 'HIT', 'count': '0'},
                                {'cacheStatus': 'MISS', 'count': '0'},
                                {'cacheStatus': 'EXPIRED', 'count': '0'},
                                {'cacheStatus': 'BYPASS', 'count': '0'},
                                {'cacheStatus': 'STALE', 'count': '0'},
                                {'cacheStatus': 'UPDATING', 'count': '0'},
                                {'cacheStatus': 'REVALIDATED', 'count': '0'},
                                {'cacheStatus': 'NONE', 'count': '0'},
                            ],
                        },
                    ],
                },
            },
        ],
    },
]


class TCPServer:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.should_fail = False

    def __enter__(self):
        self._sock.bind(('127.0.0.1', 3033))
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._sock.close()

    def prepare_error(self):
        self.should_fail = True

    def listen_for_traffic(self):
        while True:
            try:
                self._sock.listen(5)
                connection, address = self._sock.accept()
                logger.info('Connected from: %s', str(address))

                size = struct.unpack('i', connection.recv(4))[0]
                data = connection.recv(size)
                msg = dorblu_pb2.MainMessage()
                msg.ParseFromString(data)
                logger.info('Received message: %s', str(msg))

                size_out = size  # TODO
                msg_out = msg  # TODO
                data_out = msg_out.SerializeToString()

                logger.info('Sending message: %s', str(msg_out))
                connection.send(struct.pack('i', size_out))
                if self.should_fail:
                    logger.info('Failing network connection')
                    connection.close()
                    self.should_fail = False
                    continue
                connection.send(data_out)

                logger.info('sleeping')

                connection.close()
            except IOError:
                logger.error('Exception in mock server', exc_info=True)
                break


@pytest.fixture(scope='module', name='mock_dorblu_agent')
def fixture_mock_dorblu_agent():
    tcp_server = TCPServer()
    with tcp_server as example_server:
        thread = threading.Thread(target=example_server.listen_for_traffic)
        thread.daemon = True
        thread.start()
        yield example_server


@pytest.fixture(name='mock_conductor')
def fixture_mock_conductor(mockserver):
    @mockserver.json_handler(
        '/conductor/api/groups2hosts/test_service_conductor',
    )
    def _foo_handler(request):
        return [{'fqdn': 'localhost', 'root_datacenter_name': 'test_dc'}]

    @mockserver.json_handler(
        '/conductor/api/groups2hosts/test_service2_conductor',
    )
    def _foo_handler2(request):
        return [{'fqdn': 'localhost', 'root_datacenter_name': 'test_dc'}]


@pytest.fixture(name='mock_nanny')
def fixture_mock_nanny(mockserver):
    @mockserver.json_handler(
        '/nanny/v2/services/test_service_rtc/current_state/instances/',
    )
    def _foo_handler(request):
        return {
            'result': [
                {
                    'container_hostname': 'localhost',
                    'engine': '',
                    'hostname': 'sas2-9812.search.yandex.net',
                    'itags': [
                        'a_geo_sas',
                        'a_dc_test_dc',
                        'a_itype_hejmdal',
                        'a_ctype_stable',
                        'a_prj_taxi_hejmdal_stable',
                        'a_metaprj_taxi',
                        'a_tier_none',
                        'use_hq_spec',
                        'enable_hq_report',
                        'enable_hq_poll',
                    ],
                    'network_settings': 'MTN_ENABLED',
                    'port': 80,
                },
            ],
        }

    @mockserver.json_handler(
        '/nanny/v2/services/test_service2_rtc/current_state/instances/',
    )
    def _foo_handler2(request):
        return {
            'result': [
                {
                    'container_hostname': 'localhost',
                    'engine': '',
                    'hostname': 'sas2-9812.search.yandex.net',
                    'itags': [
                        'a_geo_sas',
                        'a_dc_test_dc',
                        'a_itype_hejmdal',
                        'a_ctype_stable',
                        'a_prj_taxi_hejmdal_stable',
                        'a_metaprj_taxi',
                        'a_tier_none',
                        'use_hq_spec',
                        'enable_hq_report',
                        'enable_hq_poll',
                    ],
                    'network_settings': 'MTN_ENABLED',
                    'port': 80,
                },
            ],
        }

    @mockserver.json_handler(
        '/nanny/v2/services/test_service_tcp_err_rtc/current_state/instances/',
    )
    def _foo_handler3(request):
        return {
            'result': [
                {
                    'container_hostname': 'localhost',
                    'engine': '',
                    'hostname': 'sas2-9812.search.yandex.net',
                    'itags': [
                        'a_geo_sas',
                        'a_dc_test_dc',
                        'a_itype_hejmdal',
                        'a_ctype_stable',
                        'a_prj_taxi_hejmdal_stable',
                        'a_metaprj_taxi',
                        'a_tier_none',
                        'use_hq_spec',
                        'enable_hq_report',
                        'enable_hq_poll',
                    ],
                    'network_settings': 'MTN_ENABLED',
                    'port': 80,
                },
            ],
        }


@pytest.fixture(name='mock_solomon')
def fixture_mock_solomon(mockserver):
    @mockserver.json_handler('/solomon/api/v2/push')
    def _foo_handler(request):
        assert request.query['service'] == 'dorblu_testsuite'
        assert request.query['project'] == 'testsuite_metrics'
        assert request.query['cluster'] == 'testsuite'
        group_name = request.json['sensors'][0]['labels']['group']
        assert group_name in [
            'dorblu_test_service_rtc',
            'dorblu_test_service_conductor',
            'dorblu_test_service2_rtc',
            'dorblu_test_service2_conductor',
            'dorblu_test_service3_rtc',
            'dorblu_test_service_tcp_err_rtc',
        ]
        for sensor in request.json['sensors']:
            sensor['labels'] = sensor['labels']

        byte_counters_sensors = [
            {
                'kind': 'DGAUGE',
                'labels': {
                    'group': group_name,
                    'sensor': sensor_name,
                    'object': object_name,
                    'host': host,
                },
                'ts': '2021-07-29T13:52:20+00:00',
                'value': 0.0,
            }
            for sensor_name, object_name, host in itertools.product(
                ['bps'], ['TOTAL'], ['cluster', 'Test_dc'],
            )
        ]
        cache_rates_sensors = [
            {
                'kind': 'DGAUGE',
                'labels': {
                    'group': group_name,
                    'sensor': 'cache',
                    'cache': cache_name,
                    'object': object_name,
                    'host': host,
                },
                'ts': '2021-07-29T13:52:20+00:00',
                'value': 0.0,
            }
            for cache_name, object_name, host in itertools.product(
                [
                    'bypass',
                    'expired',
                    'hit',
                    'miss',
                    'none',
                    'revalidated',
                    'stale',
                    'updating',
                ],
                ['TOTAL'],
                ['cluster', 'Test_dc'],
            )
        ]
        http_requests_sensors = [
            {
                'kind': 'DGAUGE',
                'labels': {
                    'group': group_name,
                    'sensor': sensor_name,
                    'object': object_name,
                    'host': host,
                },
                'ts': '2021-07-29T13:52:20+00:00',
                'value': 0.0,
            }
            for sensor_name, object_name, host in itertools.product(
                [
                    '400_rps',
                    '401_rps',
                    '404_rps',
                    '405_407_rps',
                    '431_rps',
                    'errors_rps',
                    'ok_rps',
                    'timeouts_rps',
                ],
                ['TOTAL'],
                ['cluster', 'Test_dc'],
            )
        ]
        timings_sensors = [
            {
                'kind': 'DGAUGE',
                'labels': {
                    'group': group_name,
                    'sensor': sensor_name,
                    'percentile': pct,
                    'object': object_name,
                    'host': host,
                },
                'ts': '2021-07-29T13:52:20+00:00',
                'value': 0.0,
            }
            for sensor_name, pct, object_name, host in itertools.product(
                [
                    'ok_request_timings',
                    'ok_ssl_timings',
                    'ok_upstream_timings',
                ],
                ['75', '85', '90', '95', '97', '98', '99', '100'],
                ['TOTAL'],
                ['cluster', 'Test_dc'],
            )
        ]
        sensors = (
            byte_counters_sensors
            + cache_rates_sensors
            + http_requests_sensors
            + timings_sensors
        )
        assert sorted(request.json) == sorted({'sensors': sensors})
        return {}


async def test_conductor_service_task(
        stq_runner, testpoint, mock_dorblu_agent, mock_solomon,
):
    @testpoint('incoming-stq-agent-task')
    def _mock_incoming_stq_agent_task(request):
        return {}

    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    args = (
        'sample_task_id',
        'test_service_conductor',
        '2021-07-29T13:52:20+00:00',
    )
    await stq_runner.dorblu_agent_task.call(task_id='sample_task', args=args)
    expected_stq_agent_task = {
        'task_id': 'sample_task_id',
        'service_name': 'test_service_conductor',
        'snapshot_time': '2021-07-29T13:52:20+00:00',
    }
    assert (await _mock_incoming_stq_agent_task.wait_call())[
        'request'
    ] == expected_stq_agent_task

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service_conductor'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response


async def test_rtc_service_task(
        stq_runner, testpoint, mock_dorblu_agent, mock_solomon,
):
    @testpoint('incoming-stq-agent-task')
    def _mock_incoming_stq_agent_task(request):
        return {}

    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    args = ('sample_task_id', 'test_service_rtc', '2021-07-29T13:52:20+00:00')
    await stq_runner.dorblu_agent_task.call(task_id='sample_task', args=args)
    expected_stq_agent_task = {
        'task_id': 'sample_task_id',
        'service_name': 'test_service_rtc',
        'snapshot_time': '2021-07-29T13:52:20+00:00',
    }
    assert (await _mock_incoming_stq_agent_task.wait_call())[
        'request'
    ] == expected_stq_agent_task

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service_rtc'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response


async def test_conductor_service_task_update_service_cache(
        taxi_dorblu,
        stq_runner,
        testpoint,
        mock_dorblu_agent,
        mock_conductor,
        mock_nanny,
        mock_solomon,
):
    @testpoint('incoming-stq-agent-task')
    def _mock_incoming_stq_agent_task(request):
        return {}

    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    await taxi_dorblu.run_periodic_task('update-services-periodic-task')
    await taxi_dorblu.invalidate_caches(
        clean_update=False, cache_names=['mongo-taxi-dorblu-instances-cache'],
    )

    args = (
        'sample_task_id',
        'test_service2_conductor',
        '2021-07-29T13:52:20+00:00',
    )
    await stq_runner.dorblu_agent_task.call(task_id='sample_task', args=args)
    expected_stq_agent_task = {
        'task_id': 'sample_task_id',
        'service_name': 'test_service2_conductor',
        'snapshot_time': '2021-07-29T13:52:20+00:00',
    }
    assert (await _mock_incoming_stq_agent_task.wait_call())[
        'request'
    ] == expected_stq_agent_task

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service2_conductor'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response


async def test_rtc_service_task_update_service_cache(
        taxi_dorblu,
        stq_runner,
        testpoint,
        mock_dorblu_agent,
        mock_conductor,
        mock_nanny,
        mock_solomon,
):
    @testpoint('incoming-stq-agent-task')
    def _mock_incoming_stq_agent_task(request):
        return {}

    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    await taxi_dorblu.run_periodic_task('update-services-periodic-task')
    await taxi_dorblu.invalidate_caches(
        clean_update=False, cache_names=['mongo-taxi-dorblu-instances-cache'],
    )

    args = ('sample_task_id', 'test_service2_rtc', '2021-07-29T13:52:20+00:00')
    await stq_runner.dorblu_agent_task.call(task_id='sample_task', args=args)
    expected_stq_agent_task = {
        'task_id': 'sample_task_id',
        'service_name': 'test_service2_rtc',
        'snapshot_time': '2021-07-29T13:52:20+00:00',
    }
    assert (await _mock_incoming_stq_agent_task.wait_call())[
        'request'
    ] == expected_stq_agent_task

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service2_rtc'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response


async def test_rtc_service_task_update_rules_cache(
        taxi_dorblu,
        stq_runner,
        testpoint,
        mock_dorblu_agent,
        mock_conductor,
        mock_nanny,
        mock_solomon,
):
    @testpoint('incoming-stq-agent-task')
    def _mock_incoming_stq_agent_task(request):
        return {}

    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    rules = {
        'rules': [
            {
                'Options': {'CustomHttp': [431, [405, 407]]},
                'filter': {'type': 'Dummy'},
                'name': 'TOTAL',
                'rule_id': 2,
            },
        ],
    }
    response = await taxi_dorblu.put(
        'v1/rules/group/update?group=test_service3_rtc&group_type=rtc', rules,
    )
    assert response.status_code == 200
    await taxi_dorblu.invalidate_caches(
        clean_update=False, cache_names=['mongo-taxi-dorblu-groups-cache'],
    )

    args = ('sample_task_id', 'test_service3_rtc', '2021-07-29T13:52:20+00:00')
    await stq_runner.dorblu_agent_task.call(task_id='sample_task', args=args)
    expected_stq_agent_task = {
        'task_id': 'sample_task_id',
        'service_name': 'test_service3_rtc',
        'snapshot_time': '2021-07-29T13:52:20+00:00',
    }
    assert (await _mock_incoming_stq_agent_task.wait_call())[
        'request'
    ] == expected_stq_agent_task

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service3_rtc'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response


async def test_rtc_service_task_with_network_error(
        stq_runner, testpoint, mock_dorblu_agent, mock_solomon,
):
    @testpoint('internal-agent-response')
    def _mock_internal_agent_response(request):
        return {}

    mock_dorblu_agent.prepare_error()

    args = (
        'network_error_task_id',
        'test_service_tcp_err_rtc',
        '2021-07-29T13:52:20+00:00',
    )
    await stq_runner.dorblu_agent_task.call(
        task_id='network_error_task', args=args,
    )

    agent_response = copy.deepcopy(EXPECTED_AGENT_RESPONSE)
    agent_response[0]['groupName'] = 'test_service_tcp_err_rtc'

    assert (await _mock_internal_agent_response.wait_call())[
        'request'
    ] == agent_response
