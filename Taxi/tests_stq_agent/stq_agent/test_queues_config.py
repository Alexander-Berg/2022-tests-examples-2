import pytest

from testsuite.utils import ordered_object


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza11']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza15']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza15',
                        'shards_count': 3,
                        'shards': [{'index': 0}, {'index': 2}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza13']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        ({'host': 'host1', 'queues': ['azaza13']}, {'queues': []}),
        (
            {'host': 'host100500', 'queues': ['azaza11']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        (
            {'host': 'host1050', 'queues': ['azaza11', 'azaza12', 'azaza15']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza12',
                        'shards_count': 5,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza15',
                        'shards_count': 3,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_queues_config(request_body, expected_response, get_stq_config):
    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {
                'host': 'host1',
                'queues': [
                    'test_critical_queue_1',
                    'test_nonexistent_queue_1',
                    'test_normal_queue_1',
                ],
            },
            {
                'queues': [
                    {
                        'queue': 'test_critical_queue_1',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                        'cluster': 'test_critical_cluster',
                    },
                    {
                        'queue': 'test_normal_queue_1',
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                        'cluster': 'test_normal_cluster',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.filldb(stq_config='cluster_settings')
@pytest.mark.config(
    STQ_AGENT_CLUSTER_SETTINGS={
        'test_normal_cluster': {
            'url': 'normal_cluster.url',
            'tvm_name': 'normal_tvm_name',
        },
        'test_critical_cluster': {
            'url': 'critical_cluster.url',
            'tvm_name': 'critical_tvm_name',
            'queues_in_process_of_cluster_switching': {
                'test_queue': {'percent': 50},
            },
        },
    },
)
async def test_queues_config_cluster_settings(
        request_body, expected_response, get_stq_config,
):
    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza12', 'azaza15']},
            {
                'queues': [
                    {
                        'queue': 'azaza11',
                        'shards_count': 2,
                        'shards': [{'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza12',
                        'shards_count': 3,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    {
                        'queue': 'azaza15',
                        'shards_count': 1,
                        'shards': [{'index': 0}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.filldb(stq_config='with_disabled')
async def test_queues_config_with_disabled(
        get_stq_config, request_body, expected_response,
):
    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_config_redis(
        taxi_stq_agent, mocked_time, get_stq_config, redis_store,
):
    def _check_hostqueue_seen(expected_hostqueue_seen):
        hostqueue_seen = {
            key.decode('utf-8'): value.decode('utf-8')
            for key, value in redis_store.hgetall('hostqueue-seen').items()
        }
        assert hostqueue_seen == expected_hostqueue_seen

    await taxi_stq_agent.invalidate_caches()

    await get_stq_config(
        'host3', ['azaza11', 'azaza12', 'azaza100500', 'azaza12'],
    )
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:00+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
        },
    )

    mocked_time.sleep(10)
    await taxi_stq_agent.invalidate_caches(clean_update=False)

    await get_stq_config('host3', ['azaza15', 'azaza12'])
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:10+0000',
            'host3:azaza15': '2018-12-01T14:00:10+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
        },
    )

    await get_stq_config('host1050', ['azaza1050'])
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:10+0000',
            'host3:azaza15': '2018-12-01T14:00:10+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
            'host1050:azaza1050': '2018-12-01T14:00:10+0000',
        },
    )


@pytest.mark.filldb(stq_config='with_empty_balancer')
async def test_queues_config_empty_balancer(get_stq_config):
    request_body = {'host': 'host1', 'queues': ['foo']}
    expected_response = {
        'queues': [
            {
                'queue': 'foo',
                'shards_count': 2,
                'shards': [{'index': 0}],
                'worker_configs': {
                    'max_tasks': 1,
                    'instances': 1,
                    'max_execution_time': 0.1,
                    'polling_interval': 0.1,
                },
            },
        ],
    }

    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['foo']},
            {
                'queues': [
                    {
                        'queue': 'foo',
                        'shards_count': 2,
                        'shards': [{'index': 1, 'max_tasks': 1005001}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        (
            {'host': 'host2', 'queues': ['foo']},
            {
                'queues': [
                    {
                        'queue': 'foo',
                        'shards_count': 2,
                        'shards': [{'index': 0, 'max_tasks': 1005002}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 2,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
        (
            {'host': 'host3', 'queues': ['foo']},
            {
                'queues': [
                    {
                        'queue': 'foo',
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.filldb(stq_config='with_balancer')
async def test_queues_config_balancer(
        get_stq_config, request_body, expected_response,
):
    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


@pytest.mark.filldb(stq_config='with_balancer')
async def test_queues_config_balancer_disabled(
        taxi_stq_agent, mongodb, get_stq_config,
):
    request_body = {'host': 'host3', 'queues': ['foo']}
    expected_response = {
        'queues': [
            {
                'queue': 'foo',
                'shards_count': 2,
                'shards': [{'index': 1}],
                'worker_configs': {
                    'max_tasks': 1,
                    'instances': 1,
                    'max_execution_time': 60,
                    'polling_interval': 0.1,
                },
            },
        ],
    }

    mongodb.stq_config.update(
        {'_id': 'foo'}, {'$set': {'balancing_enabled': False}},
    )
    await taxi_stq_agent.invalidate_caches()

    response = await get_stq_config(
        request_body['host'], request_body['queues'],
    )
    ordered_object.assert_eq(response, expected_response, ['queues'])


async def test_queues_config_invalid_config(
        taxi_stq_agent, mongodb, get_stq_config,
):
    async def _get_stq_config(expected_response):
        response = await get_stq_config(
            'host1', ['azaza11', 'azaza12', 'azaza15'],
        )
        ordered_object.assert_eq(response, expected_response, ['queues'])

    await _get_stq_config(
        {
            'queues': [
                {
                    'queue': 'azaza11',
                    'shards_count': 2,
                    'shards': [{'index': 0}, {'index': 1}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                {
                    'queue': 'azaza12',
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                {
                    'queue': 'azaza15',
                    'shards_count': 3,
                    'shards': [{'index': 0}, {'index': 2}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            ],
        },
    )

    mongodb.stq_config.update(
        {'_id': 'azaza11'},
        {
            '$set': {
                'shards': [
                    {
                        'connection': 'stq11',
                        'database': 'db',
                        'collection': 'azaza11_0',
                        'hosts': ['host1'],
                    },
                ],
            },
        },
    )
    mongodb.stq_config.update(
        {'_id': 'azaza12'},
        {
            '$set': {
                'shards': [
                    {
                        'database': 'db',
                        'collection': 'azaza12_0',
                        'hosts': ['host2'],
                    },
                ],
            },
        },
    )
    await taxi_stq_agent.invalidate_caches()

    await _get_stq_config(
        {
            'queues': [
                {
                    'queue': 'azaza11',
                    'shards_count': 1,
                    'shards': [{'index': 0}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                {
                    'queue': 'azaza12',
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                {
                    'queue': 'azaza15',
                    'shards_count': 3,
                    'shards': [{'index': 0}, {'index': 2}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            ],
        },
    )


async def test_queues_config_remove_config(
        taxi_stq_agent, mongodb, get_stq_config,
):
    async def _get_stq_config(expected_response):
        response = await get_stq_config('host1', ['azaza11', 'azaza12'])
        ordered_object.assert_eq(response, expected_response, ['queues'])

    await _get_stq_config(
        {
            'queues': [
                {
                    'queue': 'azaza11',
                    'shards_count': 2,
                    'shards': [{'index': 0}, {'index': 1}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                {
                    'queue': 'azaza12',
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            ],
        },
    )

    mongodb.stq_config.remove({'_id': 'azaza11'})
    await taxi_stq_agent.invalidate_caches()

    await _get_stq_config(
        {
            'queues': [
                {
                    'queue': 'azaza12',
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            ],
        },
    )
