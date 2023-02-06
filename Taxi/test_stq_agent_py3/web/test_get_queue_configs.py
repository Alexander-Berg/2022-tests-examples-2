import pytest


@pytest.mark.parametrize(
    'params, expected, status',
    [
        (
            {'queue_name': 'example_queue'},
            {
                'queue_name': 'example_queue',
                'grafana_url': 'grafana/example_queue',
                'updated': '2019-01-02T03:00:00+03:00',
                'hosts_alive': [
                    'taxi-stq-sas-06.taxi.yandex.net',
                    'taxi-stq-vla-13.taxi.yandex.net',
                    'taxi-stq-vla-14.taxi.yandex.net',
                ],
                'changing_database_meta_data': {
                    'backup_collections': [
                        {
                            'backup_shard': {
                                'collection': 'example_queue1_0_backup',
                                'connection_name': 'stq',
                                'database': 'dbstq',
                            },
                            'old_shard': {
                                'collection': 'example_queue1_0',
                                'connection_name': 'stq',
                                'database': 'dbstq',
                            },
                        },
                    ],
                    'database_change_status': 'MOVING_TASKS',
                    'moved_shards': [0, 2],
                    'old_shards': {
                        '0': {
                            'collection': 'example_queue1_0',
                            'connection_name': 'stq',
                            'database': 'dbstq',
                        },
                    },
                },
                'is_critical': True,
                'monitoring_thresholds': {
                    'total': {'warning': 20, 'critical': 30},
                },
                'queue_stats': {
                    'abandoned': 10,
                    'failed': 4,
                    'no_data': True,
                    'status': 'WARN',
                },
                'shards': [
                    {
                        'collection': 'example_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-sas-10.taxi.yandex.net',
                            'taxi-stq-vla-14.taxi.yandex.net',
                        ],
                        'state': 'enabled',
                    },
                    {
                        'collection': 'example_queue_1',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-13.taxi.yandex.net',
                            'taxi-stq-vla-14.taxi.yandex.net',
                        ],
                        'state': 'disabled',
                    },
                ],
                'state': 'enabled',
                'version': 3,
                'write_concern': False,
                'disable_tracing_capturing': False,
                'worker_configs': {
                    'instances': 5,
                    'max_tasks': 15,
                    'max_execution_time': 100,
                },
            },
            200,
        ),
        (
            {'queue_name': 'another_queue'},
            {
                'queue_name': 'another_queue',
                'balancer_settings': {
                    'hosts': [
                        {
                            'name': 'taxi-stq-sas-06.taxi.yandex.net',
                            'shards': [{'index': 0, 'max_tasks': 135}],
                            'status': 'down',
                            'worker_configs': {'instances': 6},
                        },
                        {
                            'name': 'taxi-stq-sas-05.taxi.yandex.net',
                            'shards': [{'index': 0, 'max_tasks': 135}],
                            'status': 'down',
                            'worker_configs': {'instances': 6},
                        },
                    ],
                },
                'grafana_url': 'grafana/another_queue',
                'updated': '2019-01-02T03:00:00+03:00',
                'monitoring_thresholds': {
                    'total': {'warning': 1, 'critical': 20},
                },
                'shards': [
                    {
                        'collection': 'another_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [],
                        'state': 'enabled',
                    },
                ],
                'state': 'enabled',
                'version': 1,
                'worker_configs': {
                    'instances': 5,
                    'max_tasks': 15,
                    'max_execution_time': 100,
                },
                'workers_guarantee': 6,
                'balancing_enabled': True,
                'write_concern': False,
                'disable_tracing_capturing': True,
            },
            200,
        ),
        ({'queue_name': 'non_existent_queue'}, None, 404),
    ],
)
async def test_get_queue_config(
        web_app_client, params, expected, status, mockserver,
):
    @mockserver.json_handler('/stq-agent/queues/retrieve_alive_hosts')
    async def _retrieve_alive_hosts(request):
        return {
            'hosts': [
                {
                    'queue_name': 'example_queue',
                    'hosts': [
                        'taxi-stq-sas-06.taxi.yandex.net',
                        'taxi-stq-vla-13.taxi.yandex.net',
                        'taxi-stq-vla-14.taxi.yandex.net',
                    ],
                },
            ],
        }

    response = await web_app_client.get('/queue/get/', params=params)
    assert response.status == status
    if status == 200:
        content = await response.json()
        assert content == expected


@pytest.mark.config(
    STQ_DEFAULT_MONITORING_THRESHOLDS={'total': {'warning': 1, 'critical': 5}},
)
async def test_list_queue_configs(web_app_client):
    response = await web_app_client.get('/queue/list/')
    assert response.status == 200
    content = await response.json()
    assert content == {
        'items': [
            {
                'queue_name': 'example_queue',
                'is_critical': True,
                'monitoring_thresholds': {
                    'total': {'warning': 20, 'critical': 30},
                },
                'grafana_url': 'grafana/example_queue',
                'updated': '2019-01-02T03:00:00+03:00',
                'changing_database_meta_data': {
                    'backup_collections': [
                        {
                            'backup_shard': {
                                'collection': 'example_queue1_0_backup',
                                'connection_name': 'stq',
                                'database': 'dbstq',
                            },
                            'old_shard': {
                                'collection': 'example_queue1_0',
                                'connection_name': 'stq',
                                'database': 'dbstq',
                            },
                        },
                    ],
                    'database_change_status': 'MOVING_TASKS',
                    'moved_shards': [0, 2],
                    'old_shards': {
                        '0': {
                            'collection': 'example_queue1_0',
                            'connection_name': 'stq',
                            'database': 'dbstq',
                        },
                    },
                },
                'queue_stats': {
                    'abandoned': 10,
                    'failed': 4,
                    'no_data': True,
                    'status': 'WARN',
                },
                'shards': [
                    {
                        'collection': 'example_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-sas-10.taxi.yandex.net',
                            'taxi-stq-vla-14.taxi.yandex.net',
                        ],
                        'state': 'enabled',
                    },
                    {
                        'collection': 'example_queue_1',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [
                            'taxi-stq-sas-06.taxi.yandex.net',
                            'taxi-stq-vla-13.taxi.yandex.net',
                            'taxi-stq-vla-14.taxi.yandex.net',
                        ],
                        'state': 'disabled',
                    },
                ],
                'state': 'enabled',
                'version': 3,
                'worker_configs': {
                    'instances': 5,
                    'max_tasks': 15,
                    'max_execution_time': 100,
                },
                'write_concern': False,
                'disable_tracing_capturing': False,
            },
            {
                'balancer_settings': {
                    'hosts': [
                        {
                            'name': 'taxi-stq-sas-06.taxi.yandex.net',
                            'shards': [{'index': 0, 'max_tasks': 135}],
                            'worker_configs': {'instances': 6},
                        },
                        {
                            'name': 'taxi-stq-sas-05.taxi.yandex.net',
                            'shards': [{'index': 0, 'max_tasks': 135}],
                            'worker_configs': {'instances': 6},
                        },
                    ],
                },
                'workers_guarantee': 6,
                'balancing_enabled': True,
                'queue_name': 'another_queue',
                'grafana_url': 'grafana/another_queue',
                'updated': '2019-01-02T03:00:00+03:00',
                'monitoring_thresholds': {
                    'total': {'warning': 1, 'critical': 5},
                },
                'shards': [
                    {
                        'collection': 'another_queue_0',
                        'connection_name': 'stq',
                        'database': 'dbstq',
                        'hostnames': [],
                        'state': 'enabled',
                    },
                ],
                'state': 'enabled',
                'version': 1,
                'worker_configs': {
                    'instances': 5,
                    'max_tasks': 15,
                    'max_execution_time': 100,
                },
                'write_concern': False,
                'disable_tracing_capturing': True,
            },
        ],
    }
