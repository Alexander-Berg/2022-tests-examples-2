import pytest
from tests_stq_agent import helpers


HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.parametrize(
    'request_params',
    [{}, {'queue_name': 123}, {'queue_name': ['test_queue']}],
)
async def test_queues_api_cleanup_bad_request(taxi_stq_agent, request_params):
    response = await taxi_stq_agent.post(
        'queues/api/cleanup', headers=HEADERS, json=request_params,
    )
    assert response.status_code == 400


async def test_queues_api_cleanup_not_found(taxi_stq_agent):
    response = await taxi_stq_agent.post(
        'queues/api/cleanup',
        headers=HEADERS,
        json={'queue_name': 'queue_does_not_exist'},
    )
    assert response.status_code == 404


async def test_queues_api_cleanup(taxi_stq_agent, stqs):
    queues = ('foobar11', 'foobar12')

    for queue in queues:
        for shard_id in range(2):
            stq_shard = stqs.get_shard(queue, shard_id)

            stq_shard.add_task(
                'not_finished_1',
                x='stq-worker',
                e=helpers.FAR_FUTURE_TIMESTAMP,
            )
            stq_shard.add_task(
                'not_finished_2', x=None, e=(helpers.FAR_FUTURE_TIMESTAMP - 1),
            )
            stq_shard.add_task(
                'finished_1', x=None, e=helpers.FAR_FUTURE_TIMESTAMP,
            )
            stq_shard.add_task(
                'finished_2', x=None, e=(helpers.FAR_FUTURE_TIMESTAMP + 1),
            )

    for queue in queues:
        response = await taxi_stq_agent.post(
            'queues/api/cleanup', headers=HEADERS, json={'queue_name': queue},
        )
        assert response.status_code == 200
        assert response.json() == {}

    for queue in queues:
        for shard_id in range(2):
            stq_shard = stqs.get_shard(queue, shard_id)

            assert stq_shard.get_task('not_finished_1') is None
            assert stq_shard.get_task('not_finished_2') is None
            assert stq_shard.get_task('finished_1') is None
            assert stq_shard.get_task('finished_2') is None
