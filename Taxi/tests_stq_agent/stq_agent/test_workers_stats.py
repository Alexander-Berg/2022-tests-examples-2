import copy
import json


async def test_workers_stats(taxi_stq_agent, redis_store):
    test_stat = {
        'total': {'cpu_used': {'value': 30}},
        'queues': [
            {'queue': 'test_queue_2', 'stat': {'cpu_used': {'value': 20}}},
            {'queue': 'test_queue_1', 'stat': {'cpu_used': {'value': 10}}},
        ],
    }

    test_host = 'test_host_1.yandex.net'

    request_json = copy.deepcopy(test_stat)
    request_json.update(
        {'datetime': '2019-10-02T19:34:11.123+0300', 'host': test_host},
    )
    response = await taxi_stq_agent.post('workers/stats', json=request_json)
    assert response.status_code == 200
    assert response.json() == {}

    keys = [key.decode('utf-8') for key in redis_store.keys('workers-stat:*')]
    assert keys == ['workers-stat:2019-10-02T16:34']

    stats = {
        field.decode('utf-8'): json.loads(value.decode('utf-8'))
        for field, value in redis_store.hgetall(keys[0]).items()
    }

    assert len(stats) == 1

    queues_hash = '823c4021a6afc03be7de43779e3a0b4ea37b770b'
    datetime = '2019-10-02T16:34:11'
    assert stats[f'{test_host}:{queues_hash}:{datetime}'] == test_stat


async def test_workers_stats_multiple_hosts(taxi_stq_agent, redis_store):
    def _get_test_stat(num):
        return {
            'total': {'cpu_used': {'value': num * 20}},
            'queues': [
                {
                    'queue': 'test_queue_1',
                    'stat': {'cpu_used': {'value': num * 10}},
                },
            ],
        }

    def _get_test_host(num):
        return f'test_host_{num}.yandex.net'

    for i in range(1, 3):
        request_json = _get_test_stat(i)
        request_json.update(
            {
                'datetime': f'2019-10-02T19:34:11.123+0300',
                'host': _get_test_host(i),
            },
        )
        response = await taxi_stq_agent.post(
            'workers/stats', json=request_json,
        )
        assert response.status_code == 200
        assert response.json() == {}

    keys = [key.decode('utf-8') for key in redis_store.keys('workers-stat:*')]
    assert keys == ['workers-stat:2019-10-02T16:34']

    stats = {
        field.decode('utf-8'): json.loads(value.decode('utf-8'))
        for field, value in redis_store.hgetall(keys[0]).items()
    }

    assert len(stats) == 2

    for i in range(1, 3):
        host = _get_test_host(i)
        queues_hash = '7e56cb95a60b44a3339d62ef417531792d986080'
        datetime = '2019-10-02T16:34:11'
        assert stats[f'{host}:{queues_hash}:{datetime}'] == _get_test_stat(i)


async def test_workers_stats_multiple_masters(taxi_stq_agent, redis_store):
    def _get_test_stat(num):
        return {
            'total': {'cpu_used': {'value': num * 20}},
            'queues': [
                {
                    'queue': f'test_queue_{num}',
                    'stat': {'cpu_used': {'value': num * 10}},
                },
            ],
        }

    test_host = 'test_host_1.yandex.net'

    for i in range(1, 3):
        request_json = _get_test_stat(i)
        request_json.update(
            {'datetime': f'2019-10-02T19:34:11.123+0300', 'host': test_host},
        )
        response = await taxi_stq_agent.post(
            'workers/stats', json=request_json,
        )
        assert response.status_code == 200
        assert response.json() == {}

    keys = [key.decode('utf-8') for key in redis_store.keys('workers-stat:*')]
    assert keys == ['workers-stat:2019-10-02T16:34']

    stats = {
        field.decode('utf-8'): json.loads(value.decode('utf-8'))
        for field, value in redis_store.hgetall(keys[0]).items()
    }

    assert len(stats) == 2

    for i, queues_hash in enumerate(
            (
                '7e56cb95a60b44a3339d62ef417531792d986080',
                '6dae6bfff37516bd6dfeb0759b86325d2af32373',
            ),
            1,
    ):
        datetime = '2019-10-02T16:34:11'
        assert stats[
            f'{test_host}:{queues_hash}:{datetime}'
        ] == _get_test_stat(i)
