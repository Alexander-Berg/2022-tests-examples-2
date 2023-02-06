import pytest
from tests_stq_agent import helpers

from testsuite.utils import ordered_object


HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'azaza1',
            'shard_id': -1,
            'node_id': 'stq-worker.yandex.net',
            'task_ids': ['task1', 'task2', 'task3', 'task4'],
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'task_ids': [],
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'task_ids': None,
        },
    ],
)
async def test_queues_api_prolong_bad_request(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post(
        'queues/api/prolong', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'azaza2',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'task_ids': ['task1', 'task2', 'task3', 'task4'],
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 2,
            'node_id': 'stq-worker.yandex.net',
            'task_ids': ['task1', 'task2', 'task3', 'task4'],
        },
    ],
)
async def test_queues_api_prolong_not_found(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post(
        'queues/api/prolong', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_prolong(taxi_stq_agent, now, stqs):
    our_tasks = ['our_task1', 'our_task2', 'our_task3']
    not_our_tasks = ['not_our_task1', 'not_our_task2', 'not_our_task3']
    not_exists_tasks = ['not_exists_task1', 'not_exists_task2']

    other_node_id = 'other-stq-worker.yandex.net'

    conflict_tasks = not_our_tasks + not_exists_tasks
    all_tasks = our_tasks + conflict_tasks

    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_ids': all_tasks,
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    for node_id, tasks in (
            (request_body['node_id'], our_tasks),
            (other_node_id, not_our_tasks),
    ):
        for i, task in enumerate(tasks):
            stq_shard.add_task(
                task,
                x=node_id,
                e=helpers.FAR_FUTURE_TIMESTAMP,
                t=(now_timestamp - 1 + i),
                f=i,
            )

    response = await taxi_stq_agent.post(
        'queues/api/prolong', json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200

    expected_response = {'conflict_ids': conflict_tasks}
    ordered_object.assert_eq(
        response.json(), expected_response, ['conflict_ids'],
    )

    _check_tasks(
        stq_shard, our_tasks, request_body['node_id'], now_timestamp, True,
    )
    _check_tasks(stq_shard, not_our_tasks, other_node_id, now_timestamp, False)


def _check_tasks(stq_shard, tasks, node_id, now_timestamp, prolonged):
    for i, task_id in enumerate(tasks):
        task = stq_shard.get_task(task_id)
        assert task['x'] == node_id
        assert task['e'] == helpers.FAR_FUTURE_TIMESTAMP
        assert task['t'] == (
            now_timestamp + helpers.STQ_TASKS_EXECUTION_TIMEOUT
            if prolonged
            else now_timestamp - 1 + i
        )
        assert task['f'] == i
