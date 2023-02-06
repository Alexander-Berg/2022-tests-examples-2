import asyncio
import time

import pytest

from tests_stq_agent.stq_agent import utils as test_utils


HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.config(
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 3,
            'ensure_enabled': True,
        },
    },
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_bulk_execution(taxi_stq_agent, mongodb, db_extra, now):
    await taxi_stq_agent.invalidate_caches()
    coros = []
    expected_tasks = []
    for request_body in [
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.133456Z',
            },
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo4',
                'args': ['1', '2', '3'],
                'kwargs': {'1': 2, '3': 4},
                'eta': '2018-12-01T14:00:01.123456+0300',
            },
    ]:
        coros.append(
            taxi_stq_agent.post('queue', json=request_body, headers=HEADERS),
        )
        if (request_body['task_id'], request_body['eta']) != (
                'ololo1',
                '2018-12-01T14:00:01.133456Z',
        ):
            expected_tasks.append(
                test_utils.make_expected_task(request_body, now),
            )
    results = await asyncio.gather(*coros)
    for response in results:
        assert response.status_code == 200
        assert response.json() == {}
    test_utils.check_mongo(mongodb, db_extra, expected_tasks, 'azaza11')


@pytest.mark.filldb(stq_config='for_expired_tasks')
@pytest.mark.config(
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 1,
            'ensure_enabled': True,
            'additional_loginfo_enabled': True,
            'future_wait_timeout_ms': 3,
        },
    },
)
async def test_bulk_execution_of_expired_task(
        taxi_stq_agent, mongodb, db_extra, now, mocked_time, testpoint,
):
    await taxi_stq_agent.invalidate_caches()

    @testpoint('bulk_worker::check_waiting_time')
    async def _move_time(data):
        time.sleep(0.01)

    @testpoint('bulk_worker::not_add_to_bulk')
    def _not_added(data):
        pass

    request = {
        'queue_name': 'with_expired_tasks',
        'task_id': 'ololo12',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }
    response = await taxi_stq_agent.post(
        'queue', json=request, headers=HEADERS,
    )
    await _move_time.wait_call()
    await _not_added.wait_call()
    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Bulk execution timeout',
    }


@pytest.mark.config(
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 3,
            'ensure_enabled': True,
        },
    },
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_bulk_execution_by_few_workers(
        taxi_stq_agent, mongodb, db_extra, now,
):
    await taxi_stq_agent.invalidate_caches()
    coros = []
    expected_tasks = []
    for request_body in [
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo5',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo6',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo7',
                'args': ['1', '2', '3'],
                'kwargs': {'1': 2, '3': 4},
                'eta': '2018-12-01T14:00:01.123456+0300',
            },
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo8',
                'args': ['1', '2', '3'],
                'kwargs': {'1': 2, '3': 4},
                'eta': '2018-12-01T14:00:01.123476+0300',
            },
    ]:
        coros.append(
            taxi_stq_agent.post('queue', json=request_body, headers=HEADERS),
        )
        expected_tasks.append(test_utils.make_expected_task(request_body, now))
    results = await asyncio.gather(*coros)
    for response in results:
        assert response.status_code == 200
        assert response.json() == {}
    test_utils.check_mongo(mongodb, db_extra, expected_tasks, 'azaza11')


@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.config(
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 2,
            'ensure_enabled': True,
        },
    },
)
async def test_changing_workers_count(
        taxi_stq_agent, mongodb, db_extra, now, taxi_config, testpoint,
):
    await taxi_stq_agent.invalidate_caches()

    @testpoint('bulk_worker::construction_of_worker')
    async def _create_worker(data):
        pass

    @testpoint('bulk_worker::destruction_of_worker')
    async def _remove_worker(data):
        pass

    expected_tasks = []
    params = [
        {'db': {'max_bulk_size': 3, 'bulk_workers_count': 1}},
        {'db': {'max_bulk_size': 3, 'bulk_workers_count': 2}},
    ]
    requests = [
        {
            'queue_name': 'azaza11',
            'args': [1, 2, 3],
            'kwargs': {'a': {'b': 'c'}, 'd': 1},
            'eta': '2018-12-01T14:00:01.123456Z',
        },
        {
            'queue_name': 'azaza11',
            'args': [1, 2, 3],
            'kwargs': {'a': {'b': 'c'}, 'd': 1},
            'eta': '2018-12-01T14:00:01.123456Z',
        },
        {
            'queue_name': 'azaza11',
            'args': ['1', '2', '3'],
            'kwargs': {'1': 2, '3': 4},
            'eta': '2018-12-01T14:00:01.123456+0300',
        },
        {
            'queue_name': 'azaza11',
            'args': ['1', '2', '3'],
            'kwargs': {'1': 2, '3': 4},
            'eta': '2018-12-01T14:00:01.123456+0300',
        },
    ]
    i = 0
    removes = 0
    creates = 0
    results = []
    for j in range(5):
        coros = []
        taxi_config.set_values({'STQ_AGENT_BUFFERING_SETTINGS': params[j % 2]})
        await taxi_stq_agent.invalidate_caches()
        if j % 2 == 0:
            removes += 1
        else:
            creates += 1
        assert _create_worker.times_called == creates
        assert _remove_worker.times_called == removes
        for request_body in requests:
            request_body['task_id'] = 'ololo' + str(i)
            coros.append(
                taxi_stq_agent.post(
                    'queue', json=request_body, headers=HEADERS,
                ),
            )
            expected_tasks.append(
                test_utils.make_expected_task(request_body, now),
            )
            i += 1
        results += await asyncio.gather(*coros)
    for response in results:
        assert response.status_code == 200
        assert response.json() == {}
    test_utils.check_mongo(mongodb, db_extra, expected_tasks, 'azaza11')
