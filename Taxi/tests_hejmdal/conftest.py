# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from hejmdal_plugins import *  # noqa: F403 F401


@pytest.fixture(autouse=True, name='mock_solomon_api')
def _mock_solomon_api(mockserver):
    @mockserver.json_handler('/api/v2/projects/taxi/sensors/labels')
    def _mock_solomon_sensors_labels(request, *args, **kwargs):
        return {
            'labels': [
                {
                    'name': 'host',
                    'values': [
                        'host1.taxi.yandex.net',
                        'host2.taxi.yandex.net',
                    ],
                    'absent': False,
                    'truncated': False,
                },
                {
                    'name': 'sensor',
                    'values': ['sensor1', 'sensor2'],
                    'absent': False,
                    'truncated': False,
                },
            ],
        }

    @mockserver.json_handler(
        '/solomon-sensors/api/v2/projects/taxi/sensors/data',
    )
    def _mock_solomon_sensors_data(request, *args, **kwargs):
        return {
            'vector': [
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'cluster': 'production',
                            'application': 'mongo-stats',
                            'service': 'app',
                            'host': 'host1.taxi.yandex.net',
                            'project': 'taxi',
                            'sensor': 'test-query-find-one-oplog-duration-ms',
                            'group': 'test_shard1',
                        },
                        'timestamps': [
                            1570643161000,
                            1570643221000,
                            1570643281000,
                            1570643341000,
                            1570643402000,
                            1570643462000,
                            1570643521000,
                            1570643581000,
                            1570643641000,
                            1570643701000,
                        ],
                        'values': [
                            0.916,
                            0.94,
                            26.916,
                            1.376,
                            5.084,
                            1.441,
                            1.27,
                            1.063,
                            0.731,
                            0.882,
                        ],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'cluster': 'production',
                            'application': 'mongo-stats',
                            'service': 'app',
                            'host': 'host1.taxi.yandex.net',
                            'project': 'taxi',
                            'sensor': 'test-query-find-one-oplog-failure',
                            'group': 'test_shard1',
                        },
                        'timestamps': [
                            1570643161000,
                            1570643221000,
                            1570643281000,
                            1570643341000,
                            1570643402000,
                            1570643462000,
                            1570643521000,
                            1570643581000,
                            1570643641000,
                            1570643701000,
                        ],
                        'values': [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'cluster': 'production',
                            'application': 'mongo-stats',
                            'service': 'app',
                            'host': 'host2.taxi.yandex.net',
                            'project': 'taxi',
                            'sensor': 'test-query-find-one-oplog-duration-ms',
                            'group': 'test_shard1',
                        },
                        'timestamps': [
                            1570643161000,
                            1570643221000,
                            1570643281000,
                            1570643341000,
                            1570643402000,
                        ],
                        'values': [0.916, 0.94, 26.916, 1.376, 5.084],
                    },
                },
                {
                    'timeseries': {
                        'alias': '',
                        'kind': 'DGAUGE',
                        'labels': {
                            'cluster': 'production',
                            'application': 'mongo-stats',
                            'service': 'app',
                            'host': 'host2.taxi.yandex.net',
                            'project': 'taxi',
                            'sensor': 'test-query-find-one-oplog-failure',
                            'group': 'test_shard1',
                        },
                        'timestamps': [
                            1570643161000,
                            1570643221000,
                            1570643281000,
                            1570643341000,
                            1570643402000,
                        ],
                        'values': [0.0, 0.0, 0.0, 0.0, 0.0],
                    },
                },
            ],
        }


@pytest.fixture(autouse=True, name='mock_juggler_push')
def _mock_juggler_push(mockserver):
    @mockserver.json_handler('/events')
    def _mock_juggler_push_events(request, *args, **kwargs):
        return {
            'accepted_events': 1,
            'events': [{'code': 200}],
            'success': True,
        }


@pytest.fixture(autouse=True, name='mock_clownductor')
def _mock_clownductor(mockserver):
    @mockserver.json_handler('/clownductor/v1/services/search/')
    def _mock_clownductor_services_search(request, *args, **kwargs):
        return {'projects': []}


@pytest.fixture(autouse=True, name='mock_sticker')
def _mock_sticker(mockserver):
    @mockserver.handler('/sticker/send-internal/')
    def _mock_sticker_send_internal(request, *args, **kwargs):
        return mockserver.make_response('https://nda.ya.ru/t/hCEoAaTh3VyfBN')


@pytest.fixture(autouse=True, name='mock_nda')
def _mock_nda(mockserver):
    @mockserver.handler('/--/')
    def _mock_nda_shortener(request, *args, **kwargs):
        return mockserver.make_response()


@pytest.fixture(autouse=True, name='mock_grafana')
def _mock_grafana(mockserver):
    @mockserver.handler('/api/search')
    def _mock_grafana_search(request, *args, **kwargs):
        return mockserver.make_response()


@pytest.fixture(autouse=True, name='mock_dorblu')
def _mock_dorblu(mockserver):
    @mockserver.json_handler('/api/groups/')
    def _mock_dorblu_groups(request, *args, **kwargs):
        return {'result': {}}
