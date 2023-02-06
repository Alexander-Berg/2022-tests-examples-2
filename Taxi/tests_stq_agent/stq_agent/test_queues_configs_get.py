import pytest


@pytest.mark.parametrize(
    'request_body',
    [
        ({},),
        ({'queues': ['azaza11']},),
        ({'host': 'host1'},),
        ({'ghost': 'ghost1'},),
        ({'host': 'host1', 'queues': 'queue1'},),
    ],
)
async def test_queues_configs_get_bad_request(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post('queues/configs', json=request_body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza11']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza15']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    'azaza15': {
                        'shards_count': 3,
                        'shards': [{'index': 0}, {'index': 2}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza13']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [{'index': 0}, {'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        ({'host': 'host1', 'queues': ['azaza13']}, {'queues': {}}),
        ({'host': 'host1', 'queues': []}, {'queues': {}}),
        (
            {'host': 'host100500', 'queues': ['azaza11']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        (
            {'host': 'host1050', 'queues': ['azaza11', 'azaza12', 'azaza15']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    'azaza12': {
                        'shards_count': 5,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    'azaza15': {
                        'shards_count': 3,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
    ],
)
async def test_queues_configs_get(
        request_body, expected_response, get_stq_config_old,
):
    assert (
        await get_stq_config_old(request_body['host'], request_body['queues'])
        == expected_response
    )


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['azaza11', 'azaza12', 'azaza15']},
            {
                'queues': {
                    'azaza11': {
                        'shards_count': 2,
                        'shards': [{'index': 1}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    'azaza12': {
                        'shards_count': 3,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                    'azaza15': {
                        'shards_count': 1,
                        'shards': [{'index': 0}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 0.1,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
    ],
)
@pytest.mark.filldb(stq_config='with_disabled')
async def test_queues_configs_get_with_disabled(
        request_body, expected_response, get_stq_config_old,
):
    assert (
        await get_stq_config_old(request_body['host'], request_body['queues'])
        == expected_response
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_configs_get_redis(
        taxi_stq_agent, mocked_time, get_stq_config_old, redis_store,
):
    def _check_hostqueue_seen(expected_hostqueue_seen):
        hostqueue_seen = {
            key.decode('utf-8'): value.decode('utf-8')
            for key, value in redis_store.hgetall('hostqueue-seen').items()
        }
        assert hostqueue_seen == expected_hostqueue_seen

    await taxi_stq_agent.invalidate_caches()

    await get_stq_config_old(
        'host3', ['azaza11', 'azaza12', 'azaza100500', 'azaza12'],
    )
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:00+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
        },
    )

    await get_stq_config_old('host1', [])
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:00+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
        },
    )

    mocked_time.sleep(10)
    await taxi_stq_agent.invalidate_caches(clean_update=False)

    await get_stq_config_old('host3', ['azaza15', 'azaza12'])
    _check_hostqueue_seen(
        {
            'host3:azaza11': '2018-12-01T14:00:00+0000',
            'host3:azaza12': '2018-12-01T14:00:10+0000',
            'host3:azaza15': '2018-12-01T14:00:10+0000',
            'host3:azaza100500': '2018-12-01T14:00:00+0000',
        },
    )

    await get_stq_config_old('host1050', ['azaza1050'])
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
async def test_queues_configs_get_empty_balancer(
        taxi_stq_agent, get_stq_config_old,
):
    expected_response = {
        'queues': {
            'foo': {
                'shards_count': 2,
                'shards': [{'index': 0}],
                'worker_configs': {
                    'max_tasks': 1,
                    'instances': 1,
                    'max_execution_time': 0.1,
                    'polling_interval': 0.1,
                },
            },
        },
    }

    result = await get_stq_config_old('host1', ['foo'])
    assert result == expected_response


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'host': 'host1', 'queues': ['foo']},
            {
                'queues': {
                    'foo': {
                        'shards_count': 2,
                        'shards': [{'index': 1, 'max_tasks': 1005001}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        (
            {'host': 'host2', 'queues': ['foo']},
            {
                'queues': {
                    'foo': {
                        'shards_count': 2,
                        'shards': [{'index': 0, 'max_tasks': 1005002}],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 2,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
        (
            {'host': 'host3', 'queues': ['foo']},
            {
                'queues': {
                    'foo': {
                        'shards_count': 2,
                        'shards': [],
                        'worker_configs': {
                            'max_tasks': 1,
                            'instances': 1,
                            'max_execution_time': 60,
                            'polling_interval': 0.1,
                        },
                    },
                },
            },
        ),
    ],
)
@pytest.mark.filldb(stq_config='with_balancer')
async def test_queues_configs_get_balancer(
        request_body, expected_response, get_stq_config_old,
):
    result = await get_stq_config_old(
        request_body['host'], request_body['queues'],
    )
    assert result == expected_response


@pytest.mark.filldb(stq_config='with_balancer')
async def test_queues_configs_get_balancer_disabled(
        taxi_stq_agent, mongodb, get_stq_config_old,
):
    expected_response = {
        'queues': {
            'foo': {
                'shards_count': 2,
                'shards': [{'index': 1}],
                'worker_configs': {
                    'max_tasks': 1,
                    'instances': 1,
                    'max_execution_time': 60,
                    'polling_interval': 0.1,
                },
            },
        },
    }

    mongodb.stq_config.update(
        {'_id': 'foo'}, {'$set': {'balancing_enabled': False}},
    )
    await taxi_stq_agent.invalidate_caches()

    result = await get_stq_config_old('host3', ['foo'])
    assert result == expected_response


async def test_queues_configs_get_invalid_config(
        taxi_stq_agent, mongodb, get_stq_config_old,
):
    async def _get_stq_config(expected_response):
        assert (
            await get_stq_config_old(
                'host1', ['azaza11', 'azaza12', 'azaza15'],
            )
            == expected_response
        )

    await _get_stq_config(
        {
            'queues': {
                'azaza11': {
                    'shards_count': 2,
                    'shards': [{'index': 0}, {'index': 1}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                'azaza12': {
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                'azaza15': {
                    'shards_count': 3,
                    'shards': [{'index': 0}, {'index': 2}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            },
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
            'queues': {
                'azaza11': {
                    'shards_count': 1,
                    'shards': [{'index': 0}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                'azaza12': {
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                'azaza15': {
                    'shards_count': 3,
                    'shards': [{'index': 0}, {'index': 2}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            },
        },
    )


async def test_queues_configs_get_remove_config(
        taxi_stq_agent, mongodb, get_stq_config_old,
):
    async def _get_stq_config(expected_response):
        assert (
            await get_stq_config_old('host1', ['azaza11', 'azaza12'])
            == expected_response
        )

    await _get_stq_config(
        {
            'queues': {
                'azaza11': {
                    'shards_count': 2,
                    'shards': [{'index': 0}, {'index': 1}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
                'azaza12': {
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            },
        },
    )

    mongodb.stq_config.remove({'_id': 'azaza11'})
    await taxi_stq_agent.invalidate_caches()

    await _get_stq_config(
        {
            'queues': {
                'azaza12': {
                    'shards_count': 5,
                    'shards': [{'index': 0}, {'index': 4}],
                    'worker_configs': {
                        'max_tasks': 1,
                        'instances': 1,
                        'max_execution_time': 0.1,
                        'polling_interval': 0.1,
                    },
                },
            },
        },
    )
