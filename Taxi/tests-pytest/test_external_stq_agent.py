import datetime
import json
import random
import string

import bson
import pytest

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.external import stq_agent
from taxi.external import tvm


@pytest.mark.config(
    TVM_RULES=[{'src': 'test-service', 'dst': 'stq-agent'}],
    TVM_ENABLED=True,
)
@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('with_src_tvm_service', [False, True])
@pytest.inline_callbacks
def test_put(patch, monkeypatch, with_src_tvm_service):
    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '{}/{}'.format(settings.STQ_AGENT_BASE_URL, 'queues/api/add/tst_queue')
        if with_src_tvm_service:
            assert kwargs['headers'] == {
                'X-YaRequestId': 'request_id',
                'X-Ya-Service-Ticket': 'test_ticket',
            }
        assert json.loads(kwargs['data']) == {
            'eta': '2018-12-27T13:12:36.446295Z',
            'args': [
                'foo',
                {'bar': {'$date': 1545829956446}},
            ],
            'task_id': '822c8f4dbcb9451697636a583336ba60',
            'kwargs': {
                'quux': {'$oid': '5c24d070820f9e89326109c3'},
            },
        }
        assert kwargs['json'] is None

        yield async.return_value(arequests.Response(status_code=200, content='{}'))

    monkeypatch.setattr(
        settings,
        'CLIENT_APIKEYS',
        {'stq_agent': {'stq_agent': 'stq_agent_token'}},
    )

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == 'test-service'
        assert dst_service_name == 'stq-agent'
        yield async.return_value('test_ticket')

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    yield stq_agent.put(
        queue='tst_queue',
        eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
        task_id='822c8f4dbcb9451697636a583336ba60',
        args=(
            'foo',
            {'bar': datetime.datetime(2018, 12, 26, 13, 12, 36, 446295)}
        ),
        kwargs={'quux': bson.ObjectId('5c24d070820f9e89326109c3')},
        log_extra={'_link': 'request_id'},
        src_tvm_service='test-service' if with_src_tvm_service else None,
    )


@pytest.mark.config(
STQ_AGENT_CLUSTER_SETTINGS={
        'other-stq-agent': {
            'url': 'http://other-stq-agent.taxi.tst.yandex.net',
            'tvm_name': 'other-stq-agent',
            'queues_in_process_of_cluster_switching': {
                'tst_queue': {
                    'percent': 50,
                }
            }
        }
    },
    TVM_RULES=[{'src': 'test-service', 'dst': 'stq-agent'}, {'src': 'test-service', 'dst': 'other-stq-agent'}],
    TVM_ENABLED=True,
)
@pytest.mark.parametrize('with_src_tvm_service', [False, True])
@pytest.inline_callbacks
def test_put_with_cluster_change(patch, monkeypatch, with_src_tvm_service):
    percent = 50

    BASE_CLUSTER = {
        'url': 'http://stq-agent.taxi.tst.yandex.net/queues/api/add/tst_queue',
        'dst_service_name': 'stq-agent'
    }
    OTHER_CLUSTER = {
        'url': 'http://other-stq-agent.taxi.tst.yandex.net/queues/api/add/tst_queue',
        'dst_service_name': 'other-stq-agent'
    }

    BASE_HEADERS = {'X-Redirect-Queue-Cluster': 'stq-agent'}
    OTHER_HEADERS = {'X-Redirect-Queue-Cluster': 'other-stq-agent'}

    put_kwargs = {
            'queue': 'tst_queue',
            'eta': datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
            'task_id': 'task_id1',
            'args': (),
            'kwargs': {},
            'log_extra': {'_link': 'request_id'},
            'src_tvm_service': 'test-service' if with_src_tvm_service else None
    }

    class Mockserver(object):
        def __init__(self):
            self._url = 'http://stq-agent.taxi.tst.yandex.net/queues/api/add/tst_queue'
            self._headers = {}
            self._dst_service_name = 'stq-agent'

        def set_target_cluster(self, cluster):
            self._url = cluster['url']
            self._dst_service_name = cluster['dst_service_name']

        def set_headers(self, headers):
            self._headers = headers

        @async.inline_callbacks
        def _request(self, url):
            assert url == self._url
            yield async.return_value(arequests.Response(status_code=200, content='{}', headers=self._headers))

        @async.inline_callbacks
        def _get_ticket(self, src_service_name, dst_service_name, log_extra=None):
            assert src_service_name == 'test-service'
            assert dst_service_name == self._dst_service_name
            yield async.return_value('test_ticket')

    mockserver = Mockserver()

    @patch('taxi.core.arequests.request')
    def request(method, url, **kwargs):
        return mockserver._request(url)

    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        return mockserver._get_ticket(src_service_name, dst_service_name, log_extra=None)

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    mockserver.set_target_cluster(BASE_CLUSTER)
    mockserver.set_headers(OTHER_HEADERS)
    yield stq_agent.put(**put_kwargs)

    for _ in range(8):
        put_kwargs['task_id'] = ''.join(
            random.choice(string.ascii_letters + string.digits)
            for __ in range(6)
        )
        if stq_agent._should_send_to_cluster_from_config(percent, put_kwargs['task_id']):
            mockserver.set_target_cluster(OTHER_CLUSTER)
            mockserver.set_headers({})
        else:
            mockserver.set_target_cluster(BASE_CLUSTER)
            mockserver.set_headers(OTHER_HEADERS)
        yield stq_agent.put(**put_kwargs)

    mockserver.set_target_cluster(OTHER_CLUSTER)
    mockserver.set_headers(BASE_HEADERS)
    put_kwargs['task_id'] = 'dhUak13'  # this value is designed to pass the hash test;
    yield stq_agent.put(**put_kwargs)

    mockserver.set_target_cluster(BASE_CLUSTER)
    mockserver.set_headers({})
    put_kwargs['task_id'] = 'dhUak13'
    yield stq_agent.put(**put_kwargs)
