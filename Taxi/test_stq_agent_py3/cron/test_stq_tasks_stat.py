# pylint: disable=redefined-outer-name
import pytest

from stq_agent_py3.common import stq_config
from stq_agent_py3.crontasks import stq_agent_stat
from stq_agent_py3.generated.cron import run_cron
from stq_agent_py3.generated.service.swagger.models import api as models


async def test_stq_tasks_stat(monkeypatch, mockserver):
    async def no_sleep(delay):
        pass

    async def get_cached_config(*args, **kwargs):
        return models.QueueDescription(
            queue_name='processing',
            description='description',
            grafana_url='grafana_url',
            state=stq_config.STATE_ENABLED,
            workers_guarantee=None,
            balancing_enabled=None,
            balancer_settings=None,
            dev_team='processing_dev_team',
            abandoned_timeout=None,
            write_concern=False,
            shards=[
                models.ShardDescription(**item)
                for item in [
                    {
                        'collection': 'processing_0',
                        'connection_name': 'stq',
                        'database': 'dbstqorder0',
                        'hostnames': [],
                    },
                    {
                        'collection': 'processing_1',
                        'connection_name': 'stq',
                        'database': 'dbstqorder0',
                        'hostnames': [],
                    },
                ]
            ],
            worker_configs=models.MandatoryWorkerConfigs(
                instances=2, max_execution_time=100, max_tasks=90,
            ),
            created=None,
            updated=None,
            version=0,
            is_critical=False,
            monitoring_thresholds=models.AllMonitoringThresholds(
                total=models.MonitoringThresholds(),
            ),
            rate_limit=1,
            taken_increase_limit=1,
            hosts_alive=[],
        )

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {
            'hosts': [
                {
                    'queue_name': 'processing',
                    'hosts': ['host1', 'host2', 'host3'],
                },
            ],
        }

    @mockserver.json_handler('/stq-agent/queues/stats')
    async def _queues_stats(request):
        return {
            'queues': {
                'processing': {
                    'total': 10,
                    'total_with_done': 11,
                    'failed': 2,
                    'running': 1,
                    'abandoned': 3,
                },
            },
        }

    monkeypatch.setattr(stq_agent_stat, '_sleep', no_sleep)
    monkeypatch.setattr(stq_config, 'get_cached_config', get_cached_config)

    @mockserver.json_handler('/solomon/stq')
    async def _solomon_mock(request):
        data = request.json
        assert data['sensors']
        for item in data['sensors']:
            if item['labels']['queue'] == '__all__':
                continue
            assert 'workers_group' in item['labels']
            assert item['labels']['workers_group'] == 'taxi_stq'
            assert item['labels']['dev_team'] == 'processing_dev_team'

    await run_cron.main(['stq_agent_py3.crontasks.stq_tasks_stat', '-t', '0'])


async def test_stq_tasks_stat_with_failed(monkeypatch, mockserver):
    async def no_sleep(delay):
        pass

    bad_db_queue = 'processing_in_bad_db'
    ok_db_queue = 'processing'

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {
            'hosts': [
                {
                    'queue_name': ok_db_queue,
                    'hosts': ['host1', 'host2', 'host3'],
                },
                {
                    'queue_name': bad_db_queue,
                    'hosts': ['host1', 'host2', 'host3'],
                },
            ],
        }

    @mockserver.json_handler('/stq-agent/queues/stats')
    async def _queues_stats(request):
        queues = request.json.get('queues', [])
        if bad_db_queue in queues:
            return mockserver.make_response('', status=500)
        return {
            'queues': {
                ok_db_queue: {
                    'total': 10,
                    'total_with_done': 11,
                    'failed': 2,
                    'running': 1,
                    'abandoned': 3,
                },
            },
        }

    monkeypatch.setattr(stq_agent_stat, '_sleep', no_sleep)
    no_all = True
    sent_ok_stats = False
    sent_bad_stats = False

    @mockserver.json_handler('/solomon/stq')
    async def _solomon_mock(request):
        data = request.json
        assert data['sensors']
        for item in data['sensors']:
            queue_name = item['labels']['queue']
            if queue_name == '__all__':
                nonlocal no_all
                no_all = False
                continue
            elif queue_name == bad_db_queue:
                nonlocal sent_bad_stats
                sent_bad_stats = True
            elif queue_name == ok_db_queue:
                nonlocal sent_ok_stats
                sent_ok_stats = True

    with pytest.raises(RuntimeError):
        await run_cron.main(
            ['stq_agent_py3.crontasks.stq_tasks_stat', '-t', '0'],
        )
    assert no_all
    assert sent_ok_stats
    assert not sent_bad_stats
