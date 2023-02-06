# pylint: disable=redefined-outer-name, unused-variable, protected-access
import operator

import pytest


from stq_agent_py3.common import stq_config
from stq_agent_py3.crontasks import tune_stq_config


@pytest.mark.parametrize(
    'queue_name, expected_shards',
    [
        pytest.param(
            'queue_1_extra',
            None,
            marks=pytest.mark.filldb(stq_config='queue_1_extra'),
        ),
        pytest.param(
            'queue_1_extra_on_host',
            None,
            marks=pytest.mark.filldb(stq_config='queue_1_extra_on_host'),
        ),
        pytest.param(
            'queue_test_min_prestable',
            None,
            marks=pytest.mark.filldb(stq_config='queue_test_min_prestable'),
        ),
        pytest.param(
            'queue_3_short',
            None,
            marks=pytest.mark.filldb(stq_config='queue_3_short'),
        ),
        pytest.param(
            'queue_3_shards',
            None,
            marks=pytest.mark.filldb(stq_config='queue_3_shards'),
        ),
        pytest.param(
            'queue_all_ok',
            None,
            marks=pytest.mark.filldb(stq_config='queue_all_ok'),
        ),
        pytest.param(
            'queue_to_init',
            [
                {
                    'collection': 'queue_to_init_0',
                    'connection': 'stq',
                    'database': 'dbstq',
                },
            ],
            marks=pytest.mark.filldb(stq_config='queue_to_init'),
        ),
        pytest.param(
            'queue_old_host',
            None,
            marks=[
                pytest.mark.filldb(stq_config='queue_old_host'),
                pytest.mark.filldb(stq_hosts='queue_old_host'),
            ],
        ),
        pytest.param(
            'queue_no_hosts_alive',
            None,
            marks=pytest.mark.filldb(stq_config='queue_no_hosts_alive'),
        ),
        pytest.param(
            'queue_many_extra_uniformly',
            None,
            marks=pytest.mark.filldb(stq_config='queue_many_extra_uniformly'),
        ),
        pytest.param(
            'queue_max_tasks_changed',
            None,
            marks=pytest.mark.filldb(stq_config='queue_max_tasks_changed'),
        ),
    ],
)
@pytest.mark.now('2019-01-01T21:00:00Z')
async def test_maintain_workers_guarantee_isolated(
        queue_name,
        cron_context,
        expected_shards,
        mockserver,
        mock_conductor,
        db,
        load_json,
        monkeypatch,
        mock_clownductor,
):
    expected_settings = load_json(
        f'maintain_{queue_name}_expected_settings.json',
    )

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return load_json(f'maintain_alive_hosts_mock_{queue_name}.json')

    mock_conductor(
        hosts_info=[
            {
                'hostname': 'host1_dc1',
                'datacenter': 'dc1',
                'group': 'taxi_prestable_stq',
            },
            {
                'hostname': 'host1_dc2',
                'datacenter': 'dc2',
                'group': 'taxi_stq',
            },
            {
                'hostname': 'host1_dc3',
                'datacenter': 'dc3',
                'group': 'taxi_stq',
            },
            {
                'hostname': 'host2_dc1',
                'datacenter': 'dc1',
                'group': 'taxi_stq',
            },
            {
                'hostname': 'host2_dc2',
                'datacenter': 'dc2',
                'group': 'taxi_stq',
            },
        ],
    )

    @mock_clownductor('/v1/hosts/')
    def handler(request):
        hosts_info = {
            'host3_dc1': {
                'name': 'host3_dc1',
                'datacenter': 'dc1',
                'group': 'taxi_stq',
                'branch_id': 1,
            },
            'host3_dc2': {
                'name': 'host3_dc2',
                'datacenter': 'dc2',
                'group': 'taxi_stq',
                'branch_id': 1,
            },
            'host2_dc3': {
                'name': 'host2_dc3',
                'datacenter': 'dc3',
                'group': 'taxi_stq',
                'branch_id': 1,
            },
        }
        if request.args['fqdn'] in hosts_info:
            return [hosts_info[request.args['fqdn']]]
        return []

    if queue_name == 'queue_test_min_prestable':
        monkeypatch.setattr(
            'stq_agent_py3.crontasks.tune_stq_config.MIN_PRESTABLE_INSTANCES',
            2,
        )
    current_doc = await _run_maintain(cron_context, db, queue_name)
    if expected_shards:
        assert current_doc['shards'] == expected_shards
    assert current_doc['balancer_settings']['hosts'] == sorted(
        expected_settings, key=operator.itemgetter('name'),
    )


@pytest.mark.filldb(stq_config='queue_dc_imbalance')
async def test_level_dc_shares(
        cron_context, mockserver, mock_conductor, db, monkeypatch,
):
    queue_name = 'queue_dc_imbalance'
    alive_hosts = [
        'host1_dc1',
        'host1_dc2',
        'host2_dc1',
        'host2_dc2',
        'host3_dc1',
        'host3_dc2',
        'host1_dc3',
        'host2_dc3',
        'host3_dc3',
    ]

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {'hosts': [{'queue_name': queue_name, 'hosts': alive_hosts}]}

    hosts_info = []
    for host in alive_hosts:
        if host == 'host1_dc1':
            group = 'taxi_prestable_stq'
        else:
            group = 'taxi_stq'
        _, host_dc = host.rsplit('_', 1)
        hosts_info.append(
            {'group': group, 'datacenter': host_dc, 'hostname': host},
        )

    mock_conductor(hosts_info=hosts_info)
    current_doc = await _run_maintain(cron_context, db, queue_name)
    dc_instances = {}
    for host in current_doc['balancer_settings']['hosts']:
        _, host_dc = host['name'].rsplit('_', 1)
        dc_instances.setdefault(host_dc, 0)
        dc_instances[host_dc] += host['worker_configs']['instances']
    assert dc_instances == {'dc1': 2, 'dc2': 2, 'dc3': 2}


@pytest.fixture(autouse=True)
def use_url_mocks(fake_grafana_url, mock_conductor_url):
    pass


@pytest.mark.filldb(stq_config='by_total')
@pytest.mark.now('2019-01-01T21:00:00Z')
async def test_maintain_workers_guarantee_total(
        cron_context,
        mockserver,
        mock_conductor,
        db,
        load_json,
        monkeypatch,
        mock_clownductor,
):
    expected_settings = load_json(f'maintain_by_total_expected_settings.json')

    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return load_json(f'maintain_alive_hosts_mock.json')

    mock_conductor(
        hosts_info=[
            {
                'hostname': 'host1_dc1',
                'datacenter': 'dc1',
                'group': 'taxi_prestable_stq',
            },
            {
                'hostname': 'host1_dc2',
                'datacenter': 'dc1',
                'group': 'taxi_stq',
            },
        ],
    )

    @mock_clownductor('/v1/hosts/')
    def handler(request):
        return []

    await _run_maintain(cron_context, db, queue_name=None)
    docs = await db.stq_config.find().to_list(None)
    for doc in docs:
        doc['balancer_settings']['hosts'].sort(key=operator.itemgetter('name'))
        doc.pop('updated')
    assert sorted(docs, key=operator.itemgetter('_id')) == sorted(
        expected_settings, key=operator.itemgetter('_id'),
    )


async def _run_maintain(cron_context, db, queue_name):
    alive_by_queue = await cron_context.stq_client.get_alive_hosts()
    state = await stq_config.get_hosts_load_info(cron_context, alive_by_queue)
    await tune_stq_config._maintain_workers_guarantee(
        cron_context, alive_by_queue, state,
    )
    if queue_name:
        return await db.stq_config.find_one(queue_name)
