async def test_done(taxi_stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done(request):
        return {}

    should_send_task = True
    take_id = None

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready(request):
        nonlocal take_id
        take_id = request.json['idempotency_token']
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_done_py3')
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_done_task_id',
                        'args': [],
                        'kwargs': {},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                        'eta': '2018-12-01T14:00:01.123456Z',
                    },
                ],
            }
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {
            'queues': [
                {
                    'queue': 'sample_queue_done_py3',
                    'shards_count': 1,
                    'shards': [{'index': 0, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_runner.invalidate_caches()
    await taxi_stq_runner.run_periodic_task('configs_fetcher')

    mark_done_request = await _clear_mark_request(_mock_mark_done)
    assert mark_done_request == {
        'queue_name': 'sample_queue_done_py3',
        'shard_id': 0,
        'task_id': 'test_done_task_id',
        'take_id': take_id,
    }


async def test_done_multiworker(taxi_stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/mark_as_done')
    def _mock_mark_done(request):
        return {}

    should_send_task = True
    take_id = None

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready(request):
        nonlocal should_send_task
        nonlocal take_id
        take_id = request.json['idempotency_token']
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_done_py3')
                and (request.json['shard_id'] == 1)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_done_multiworker_task_id_1',
                        'args': [],
                        'kwargs': {},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                        'eta': '2018-12-01T14:00:01.123456Z',
                    },
                    {
                        'task_id': 'test_done_multiworker_task_id_2',
                        'args': [],
                        'kwargs': {},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                    },
                ],
            }
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {
            'queues': [
                {
                    'queue': 'sample_queue_done_py3',
                    'shards_count': 1,
                    'shards': [{'index': 1, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 2,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_runner.invalidate_caches()
    await taxi_stq_runner.run_periodic_task('configs_fetcher')

    mark_done_requests = []
    mark_done_requests.append(await _clear_mark_request(_mock_mark_done))
    mark_done_requests.append(await _clear_mark_request(_mock_mark_done))
    mark_done_requests.sort(key=lambda item: item['task_id'])
    assert mark_done_requests == [
        {
            'queue_name': 'sample_queue_done_py3',
            'shard_id': 1,
            'task_id': 'test_done_multiworker_task_id_1',
            'take_id': take_id,
        },
        {
            'queue_name': 'sample_queue_done_py3',
            'shard_id': 1,
            'task_id': 'test_done_multiworker_task_id_2',
            'take_id': take_id,
        },
    ]


async def test_failed(taxi_stq_runner, mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/mark_as_failed')
    def _mock_mark_failed(request):
        return {}

    should_send_task = True

    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready(request):
        nonlocal should_send_task
        if (
                should_send_task
                and (request.json['queue_name'] == 'sample_queue_failed_py3')
                and (request.json['shard_id'] == 0)
                and (request.json['max_tasks'] == 100)
        ):
            should_send_task = False
            return {
                'tasks': [
                    {
                        'task_id': 'test_failed_task_id',
                        'args': [],
                        'kwargs': {},
                        'exec_tries': 1,
                        'reschedule_counter': 0,
                        'eta': '2018-12-01T14:00:01.123456Z',
                    },
                ],
            }
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {
            'queues': [
                {
                    'queue': 'sample_queue_failed_py3',
                    'shards_count': 1,
                    'shards': [{'index': 0, 'max_tasks': 100}],
                    'worker_configs': {
                        'instances': 1,
                        'max_tasks': 100,
                        'max_execution_time': 100.0,
                    },
                },
            ],
        }

    await taxi_stq_runner.invalidate_caches()
    await taxi_stq_runner.run_periodic_task('configs_fetcher')

    mark_failed_request = await _clear_mark_request(_mock_mark_failed)
    assert mark_failed_request == {
        'queue_name': 'sample_queue_failed_py3',
        'shard_id': 0,
        'task_id': 'test_failed_task_id',
        'exec_tries': 2,
    }


async def _clear_mark_request(mock_mark_handler, exec_time=True):
    mark_request = await mock_mark_handler.wait_call()
    mark_request_data = mark_request['request'].json

    assert mark_request_data.pop('node_id') is not None
    if exec_time:
        assert mark_request_data.pop('exec_time') is not None

    return mark_request_data
