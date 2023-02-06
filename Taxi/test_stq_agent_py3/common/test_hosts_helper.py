# pylint: disable=redefined-outer-name, unused-variable, protected-access
import datetime

import pytest

from testsuite.utils import ordered_object

from stq_agent_py3.common import hosts_helper
from stq_agent_py3.common import stq_config
from stq_agent_py3.crontasks import tune_stq_config


@pytest.mark.now('2019-01-01T21:00:00Z')
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [
                {
                    '_id': 'host1_dc1',
                    'datacenter': 'dc1',
                    'group': 'taxi_prestable_stq',
                    'is_prestable': True,
                    'last_seen': {
                        'queue_all_ok': datetime.datetime(2019, 1, 1, 21, 0),
                        'queue_all_ok_1': datetime.datetime(2019, 1, 1, 21, 0),
                        'some_queue_not_using_hosts': datetime.datetime(
                            2019, 1, 1, 21, 0,
                        ),
                    },
                    'prestable_status_update': datetime.datetime(
                        2019, 1, 1, 20, 0,
                    ),
                    'queues_shards': {
                        'queue_all_ok': [0],
                        'queue_all_ok_1': [0],
                    },
                    'workers_by_queues': {
                        'queue_all_ok': 4,
                        'queue_all_ok_1': 2,
                    },
                },
                {
                    '_id': 'host1_dc2',
                    'datacenter': 'dc2',
                    'group': 'taxi_stq',
                    'is_prestable': False,
                    'last_seen': {
                        'queue_all_ok': datetime.datetime(2019, 1, 1, 21, 0),
                        'queue_all_ok_1': datetime.datetime(2019, 1, 1, 21, 0),
                        'queue_old_host': datetime.datetime(2019, 1, 1, 20, 0),
                    },
                    'prestable_status_update': datetime.datetime(
                        2019, 1, 1, 21, 0,
                    ),
                    'queues_shards': {
                        'queue_all_ok': [0],
                        'queue_all_ok_1': [0],
                    },
                    'workers_by_queues': {
                        'queue_all_ok': 4,
                        'queue_all_ok_1': 2,
                    },
                },
            ],
            marks=[
                pytest.mark.filldb(stq_hosts='hosts_update'),
                pytest.mark.filldb(stq_config='hosts_update'),
            ],
        ),
        pytest.param(
            [
                {
                    '_id': 'host1_dc1',
                    'datacenter': 'dc1',
                    'group': 'taxi_prestable_stq',
                    'is_prestable': True,
                    'last_seen': {
                        'queue_all_ok': datetime.datetime(2019, 1, 1, 21, 0),
                        'queue_all_ok_1': datetime.datetime(2019, 1, 1, 21, 0),
                        'some_queue_not_using_hosts': datetime.datetime(
                            2019, 1, 1, 21, 0,
                        ),
                    },
                    'prestable_status_update': datetime.datetime(
                        2019, 1, 1, 21, 0,
                    ),
                    'queues_shards': {
                        'queue_all_ok': [0],
                        'queue_all_ok_1': [0],
                    },
                    'workers_by_queues': {
                        'queue_all_ok': 4,
                        'queue_all_ok_1': 2,
                    },
                },
                {
                    '_id': 'host1_dc2',
                    'datacenter': 'dc2',
                    'group': 'taxi_stq',
                    'is_prestable': False,
                    'last_seen': {
                        'queue_all_ok': datetime.datetime(2019, 1, 1, 21, 0),
                        'queue_all_ok_1': datetime.datetime(2019, 1, 1, 21, 0),
                    },
                    'prestable_status_update': datetime.datetime(
                        2019, 1, 1, 21, 0,
                    ),
                    'queues_shards': {
                        'queue_all_ok': [0],
                        'queue_all_ok_1': [0],
                    },
                    'workers_by_queues': {
                        'queue_all_ok': 4,
                        'queue_all_ok_1': 2,
                    },
                },
            ],
            marks=[pytest.mark.filldb(stq_config='hosts_update')],
        ),
    ],
)
async def test_hosts_update(
        cron_context,
        db,
        mock_conductor,
        mock_conductor_url,
        mockserver,
        load_json,
        expected,
        mock_clownductor,
):
    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return load_json(f'hosts_update_alive_hosts_mock.json')

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
        ],
    )

    @mock_clownductor('/v1/hosts/')
    def handler(request):
        return []

    alive_by_queue = await cron_context.stq_client.get_alive_hosts()
    result = await stq_config.get_hosts_load_info(cron_context, alive_by_queue)
    await tune_stq_config._maintain_workers_guarantee(
        cron_context, alive_by_queue, result,
    )
    await hosts_helper.cleanup_and_update_hosts(cron_context, result)
    docs = await db.stq_hosts.find().to_list(None)
    ordered_object.assert_eq(
        docs, expected, ['last_seen', 'queues_shards', 'workers_by_queues'],
    )
