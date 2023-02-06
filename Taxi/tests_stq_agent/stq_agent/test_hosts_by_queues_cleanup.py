import pytest


@pytest.mark.redis_store(
    [
        'hset',
        'hostqueue-seen',
        'host_not_too_old:some_queue',
        '2020-06-01T00:00:00.000Z',
    ],
    [
        'hset',
        'hostqueue-seen',
        'host_too_old:some_queue',
        '2020-05-01T00:00:00.000Z',
    ],
)
@pytest.mark.now('2020-06-01T11:00:00.000Z')
async def test_periodic_task(taxi_stq_agent, redis_store):
    await taxi_stq_agent.run_periodic_task('stq-agent-cleanup-hosts-by-queues')
    current = redis_store.hgetall('hostqueue-seen')
    assert current == {
        b'host_not_too_old:some_queue': b'2020-06-01T00:00:00.000Z',
    }
