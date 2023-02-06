import pytest
from tests_stq_agent import helpers


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'bar',
            'task_id': 'task',
            'eta': '2018-12-01T14:00:01.123456Z',
        },
        {
            'queue_name': 'foo',
            'task_id': 'no_task',
            'eta': '2018-12-01T14:00:01.123456Z',
        },
    ],
)
async def test_queues_api_reschedule_not_found(
        taxi_stq_agent, stqs, request_body,
):
    stqs.get_shard('foo', 0).add_task('task')

    response = await taxi_stq_agent.post(
        'queues/api/reschedule', json=request_body,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'eta', ['2018-12-01T15:00:00Z', '2018-12-01T17:00:00Z'],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_reschedule(taxi_stq_agent, now, stqs, eta):
    eta_orig = '2018-12-01T16:00:00Z'

    stq_shard = stqs.get_shard('foo', 0)

    stq_shard.add_task('task', e=helpers.to_timestamp(eta_orig))

    response = await taxi_stq_agent.post(
        'queues/api/reschedule',
        json={'queue_name': 'foo', 'task_id': 'task', 'eta': eta},
    )
    assert response.status_code == 200
    assert response.json() == {}

    task = stq_shard.get_task('task')
    assert task['eu'] == helpers.to_timestamp(now)
    assert task['e'] == min(
        helpers.to_timestamp(eta), helpers.to_timestamp(eta_orig),
    )
    assert task['rc'] == 1


async def test_queues_api_reschedule_inc_r(taxi_stq_agent, stqs):
    stq_shard = stqs.get_shard('foo', 0)

    stq_shard.add_task('task', rc=123)

    response = await taxi_stq_agent.post(
        'queues/api/reschedule',
        json={
            'queue_name': 'foo',
            'task_id': 'task',
            'eta': '2018-12-01T17:00:00Z',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    task = stq_shard.get_task('task')
    assert task['rc'] == 124


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_reschedule_wrong_cluster(taxi_stq_agent, stqs):
    eta_orig = '2018-12-01T16:00:00Z'
    eta = '2018-12-01T15:00:00Z'
    queue_name = 'queue_wrong_cluster'
    task_id = 'task_1'
    request_body = {'queue_name': queue_name, 'task_id': task_id, 'eta': eta}
    stq_shard = stqs.get_shard(queue_name, shard_id=0)
    stq_shard.add_task(task_id, e=(helpers.to_timestamp(eta_orig)))

    response = await taxi_stq_agent.post(
        'queues/api/reschedule', json=request_body,
    )
    assert response.status_code == 200
    assert response.headers['X-Redirect-Queue-Cluster'] == 'not-stq-agent'
