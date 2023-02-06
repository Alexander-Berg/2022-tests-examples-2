# pylint: disable=unused-variable

import copy
import datetime
import hashlib
import random
import string

import aiohttp
import aiohttp.web
import bson
import pytest

from taxi import config
from taxi.clients import stq_agent
from taxi.clients import tvm
from taxi.pytest_plugins import fixtures_content as conftest


@pytest.fixture(autouse=True)
def enable_tvm_for_agent(monkeypatch):
    async def _get_auth_headers(self, tvm_name='stq-agent', log_extra=None):
        if self._tvm_client is not None and self._tvm_client.check_rules(
                tvm_name,
        ):
            return await self._tvm_client.get_auth_headers(
                tvm_name, log_extra=log_extra,
            )
        if self._apikey is not None:
            return {'X-YaTaxi-API-Key': self._apikey}
        return {'X-Ya-Service-Ticket': 'xxx'}

    monkeypatch.setattr(
        stq_agent.StqAgentClient, '_get_auth_headers', _get_auth_headers,
    )


@pytest.mark.parametrize('no_tvm', [True, False])
async def test_put_task(unittest_settings, mockserver, patch, no_tvm):
    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'test_ticket'

    @mockserver.json_handler('/stq-agent/queues/api/add/tst_queue')
    def stq_agent_put_task(request):
        assert request.method == 'POST'
        assert request.json == {
            'task_id': '822c8f4dbcb9451697636a583336ba60',
            'args': ['foo', {'bar': {'$date': 1545829956446}}],
            'kwargs': {
                'quux': {'$oid': '5c24d070820f9e89326109c3'},
                'log_extra': {'_link': 'request_id'},
            },
            'eta': '2018-12-27T13:12:36.446295Z',
        }

        assert request.headers.get('X-YaRequestId') == 'request_id'
        if no_tvm:
            assert (
                request.headers.get('X-YaTaxi-API-Key') == 'stq-agent-apikey'
            )
        else:
            assert request.headers.get('X-Ya-Service-Ticket') == 'test_ticket'
        return {}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)/bulk', regex=True,
    )
    async def _mock_stq_agent_api_add_bulk(request, queue_name):
        assert request.method == 'POST'
        assert queue_name == 'tst_queue'
        task_id = request.json['tasks'][0]['task_id']
        if task_id == 'task_from_bulk_ok':
            assert request.json == {
                'tasks': [
                    {
                        'task_id': 'task_from_bulk_ok',
                        'eta': '2018-12-27T13:12:36.446295Z',
                        'args': [123],
                        'kwargs': {'key': 'value'},
                    },
                ],
            }
            response = {
                'tasks': [
                    {
                        'task_id': 'task_from_bulk_ok',
                        'add_result': {'code': 200},
                    },
                ],
            }
        elif task_id == 'task_from_bulk_fail':
            response = {
                'tasks': [
                    {
                        'task_id': 'task_from_bulk_fail',
                        'add_result': {
                            'code': 500,
                            'description': 'some fail reason',
                        },
                    },
                ],
            }
        return response

    if no_tvm:
        secdist = {'client_apikeys': copy.deepcopy(conftest.CLIENT_APIKEYS)}
    else:
        secdist = {}
    cfg = config.Config()
    cfg.TVM_RULES = [{'src': 'test-service', 'dst': 'stq-agent'}]
    cfg.TVM_ENABLED = True

    async with aiohttp.ClientSession() as session:
        if no_tvm:
            tvm_client = None
        else:
            tvm_client = tvm.TVMClient('test-service', secdist, cfg, session)
        stq_agent_client = stq_agent.StqAgentClient(
            session, secdist, cfg, unittest_settings, tvm_client,
        )

        await stq_agent_client.put_task(
            queue='tst_queue',
            eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
            task_id='822c8f4dbcb9451697636a583336ba60',
            args=(
                'foo',
                {'bar': datetime.datetime(2018, 12, 26, 13, 12, 36, 446295)},
            ),
            kwargs={
                'quux': bson.ObjectId('5c24d070820f9e89326109c3'),
                'log_extra': {'_link': 'request_id'},
            },
        )

        await stq_agent_client.put_tasks(
            queue_name='tst_queue',
            tasks=[
                stq_agent_client.TaskAddRequest(
                    eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
                    task_id='task_from_bulk_ok',
                    args=(123,),
                    kwargs={'key': 'value'},
                ),
            ],
            log_extra={'_link': 'request_id'},
        )

        with pytest.raises(stq_agent.BaseError) as exc:
            await stq_agent_client.put_tasks(
                queue_name='tst_queue',
                tasks=[
                    stq_agent_client.TaskAddRequest(
                        task_id='task_from_bulk_fail', kwargs={'key': 'value'},
                    ),
                ],
                log_extra={'_link': 'request_id'},
            )
        assert 'some fail reason' in str(exc)


@pytest.mark.parametrize('no_tvm', [True, False])
async def test_cluster_switch(
        unittest_settings, mockserver, taxi_config, patch, no_tvm,
):
    percent = 50

    def _should_send_to_cluster_from_config(percent, split_id):
        if percent is None:
            return True
        hash_str = hashlib.sha1(split_id.encode('utf-8')).hexdigest()
        hash_num = int(hash_str[0:4], 16) % 100
        return hash_num < percent

    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'test_ticket'

    @mockserver.json_handler('/stq-agent/queues/api/add/clusters_tst_queue')
    def _mock_stq_agent_put_task_clusters(request):
        return mockserver.make_response(
            status=200,
            headers={'X-Redirect-Queue-Cluster': 'other-stq-agent'},
            json={},
        )

    @mockserver.json_handler(
        '/other-stq-agent/queues/api/add/clusters_tst_queue',
    )
    def _mock_other_stq_agent_put_task_clusters(request):
        return {}

    if no_tvm:
        secdist = {'client_apikeys': copy.deepcopy(conftest.CLIENT_APIKEYS)}
    else:
        secdist = {}
    cfg = config.Config()
    cfg.TVM_RULES = [
        {'src': 'test-service', 'dst': 'stq-agent'},
        {'src': 'test-service', 'dst': 'other-stq-agent'},
    ]
    cfg.TVM_ENABLED = True

    cfg.STQ_AGENT_CLUSTER_SETTINGS = {
        'other-stq-agent': {
            'url': mockserver.url('/other-stq-agent'),
            'tvm_name': 'other-stq-agent',
            'queues_in_process_of_cluster_switching': {
                'clusters_tst_queue': {'percent': percent},
            },
        },
    }

    async with aiohttp.ClientSession() as session:
        if no_tvm:
            tvm_client = None
        else:
            tvm_client = tvm.TVMClient('test-service', secdist, cfg, session)
        stq_agent_client = stq_agent.StqAgentClient(
            session, secdist, cfg, unittest_settings, tvm_client,
        )

        await stq_agent_client.put_task(
            queue='clusters_tst_queue',
            eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
            task_id='task_id_1',
            args=(),
            kwargs={},
        )
        await _mock_stq_agent_put_task_clusters.wait_call()
        for _ in range(8):
            task_id = ''.join(
                random.choice(string.ascii_letters + string.digits)
                for __ in range(6)
            )
            await stq_agent_client.put_task(
                queue='clusters_tst_queue',
                eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
                task_id=task_id,
                args=(),
                kwargs={},
            )
            if _should_send_to_cluster_from_config(percent, task_id):
                await _mock_other_stq_agent_put_task_clusters.wait_call()
            else:
                await _mock_stq_agent_put_task_clusters.wait_call()

        @mockserver.json_handler(
            '/other-stq-agent/queues/api/add/clusters_tst_queue',
        )
        def _mock_other_stq_agent_put_task_clusters(request):
            return mockserver.make_response(
                status=200,
                headers={'X-Redirect-Queue-Cluster': 'stq-agent'},
                json={},
            )

        @mockserver.json_handler(
            '/stq-agent/queues/api/add/clusters_tst_queue',
        )
        def _mock_stq_agent_put_task_clusters(request):
            return {}

        await stq_agent_client.put_task(
            queue='clusters_tst_queue',
            eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
            task_id='dhUak13',  # this value is designed to pass the hash test
            args=(),
            kwargs={},
        )
        await _mock_other_stq_agent_put_task_clusters.wait_call()
        await stq_agent_client.put_task(
            queue='clusters_tst_queue',
            eta=datetime.datetime(2018, 12, 27, 13, 12, 36, 446295),
            task_id='task_id_4',
            args=(),
            kwargs={},
        )
        await _mock_stq_agent_put_task_clusters.wait_call()


async def test_list_stqs(unittest_settings, mockserver):
    # pylint: disable=unused-variable
    @mockserver.handler('/stq-agent/queues/list')
    async def stq_agent_queues_list(request):
        assert request.method == 'GET'
        assert request.headers.get('X-YaRequestId') == 'request_id'
        return aiohttp.web.json_response({'queues': ['queue1', 'queue2']})

    secdist = {'client_apikeys': copy.deepcopy(conftest.CLIENT_APIKEYS)}
    async with aiohttp.ClientSession() as session:
        stq_agent_client = stq_agent.StqAgentClient(
            session, secdist, config.Config(), unittest_settings,
        )
        queues = await stq_agent_client.list_stqs(
            log_extra={'_link': 'request_id'},
        )
    assert queues == ['queue1', 'queue2']


async def test_cleanup_stq(unittest_settings, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/stq-agent/queues/api/cleanup')
    def stq_agent_queue_cleanup(request):
        assert request.method == 'POST'
        assert request.json == {'queue_name': 'tst_queue'}
        assert request.headers.get('X-YaRequestId') == 'request_id'
        assert request.headers.get('X-YaTaxi-API-Key') == 'stq-agent-apikey'
        return {}

    secdist = {'client_apikeys': copy.deepcopy(conftest.CLIENT_APIKEYS)}
    async with aiohttp.ClientSession() as session:
        stq_agent_client = stq_agent.StqAgentClient(
            session, secdist, config.Config(), unittest_settings,
        )

        await stq_agent_client.cleanup_stq(
            queue='tst_queue', log_extra={'_link': 'request_id'},
        )
