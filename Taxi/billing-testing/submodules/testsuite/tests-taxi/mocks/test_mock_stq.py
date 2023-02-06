import datetime
import json

import pytest


@pytest.fixture
def stq_mocked_queues():
    return ['test_queue']


async def test_mock_stq(stq, mockserver_client):
    task_args = {
        'task_id': 'id',
        'args': ['a'],
        'kwargs': {'b': 1},
        'eta': '2019-09-18T04:40:00+0000',
    }
    await mockserver_client.post(
        'stq-agent/queues/api/add/test_queue', data=json.dumps(task_args),
    )

    assert stq['test_queue'] is stq.test_queue
    assert stq.test_queue.times_called == 1
    assert stq.test_queue.next_call() == {
        'args': ['a'],
        'eta': datetime.datetime(2019, 9, 18, 4, 40),
        'kwargs': {'b': 1},
        'queue': 'test_queue',
        'id': 'id',
    }
    await mockserver_client.post(
        'stq-agent/queues/api/add/test_queue', data=json.dumps(task_args),
    )
    with stq.flushing():
        assert stq.is_empty
        await mockserver_client.post(
            'stq-agent/queues/api/add/test_queue', data=json.dumps(task_args),
        )
    assert stq.is_empty
