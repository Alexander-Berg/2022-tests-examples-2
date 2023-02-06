import requests
import pytest


def test_daemon_starts():
    response = requests.get('http://localhost:1180/ping')
    assert response.status_code == 200

    # this header is set by userver
    assert 'X-YaRequestId' in response.headers


@pytest.mark.stq_agent_queue('foo')
def test_simple_task():
    response = requests.post(
        'http://localhost:1180/queues/api/add/foo',
        headers={'X-YaTaxi-API-Key': 'InferniaOverkill'},
        json={
            'task_id': '123456',
            'eta': '2022-03-31T16:42:00.00000Z',
            'args': [],
            'kwargs': {},
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = requests.post(
        'http://localhost:1180/queues/api/take',
        headers={'X-YaTaxi-API-Key': 'InferniaOverkill'},
        json={
            'queue_name': 'foo',
            'shard_id': 0,
            'node_id': 'localhost',
            'max_tasks': 10,
        },
    )
    assert response.status_code == 200
    tasks = response.json()['tasks']
    assert len(tasks) == 1
    assert tasks[0]['task_id'] == '123456'
