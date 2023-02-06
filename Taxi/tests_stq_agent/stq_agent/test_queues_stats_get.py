import pytest
from tests_stq_agent import helpers


@pytest.mark.parametrize(
    'request_body',
    [
        {'queues': 'azaza'},
        {'queues': ['azaza'], 'metrics': 'total'},
        {'queues': ['azaza'], 'metrics': ['ololo']},
    ],
)
async def test_queues_stats_get_bad_request(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'queues': ['azaza11']},
            {
                'queues': {
                    'azaza11': {
                        'total': 0,
                        'total_with_done': 0,
                        'running': 0,
                        'failed': 0,
                        'abandoned': 0,
                    },
                },
            },
        ),
        (
            {'queues': ['azaza11'], 'metrics': []},
            {
                'queues': {
                    'azaza11': {
                        'total': 0,
                        'total_with_done': 0,
                        'running': 0,
                        'failed': 0,
                        'abandoned': 0,
                    },
                },
            },
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['total']},
            {'queues': {'azaza11': {'total': 0}}},
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['running']},
            {'queues': {'azaza11': {'running': 0}}},
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['failed']},
            {'queues': {'azaza11': {'failed': 0}}},
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['abandoned']},
            {'queues': {'azaza11': {'abandoned': 0}}},
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['total', 'running']},
            {'queues': {'azaza11': {'total': 0, 'running': 0}}},
        ),
        (
            {'queues': ['azaza11'], 'metrics': ['total_with_done']},
            {'queues': {'azaza11': {'total_with_done': 0}}},
        ),
    ],
)
@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
async def test_queues_stats_get_metrics(
        taxi_stq_agent, stqs, request_body, expected_response,
):
    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            {'metrics': ['total']},
            {
                'queues': {
                    'azaza11': {'total': 0},
                    'azaza12': {'total': 0},
                    'azaza15': {'total': 0},
                },
            },
        ),
        (
            {'queues': [], 'metrics': ['total']},
            {
                'queues': {
                    'azaza11': {'total': 0},
                    'azaza12': {'total': 0},
                    'azaza15': {'total': 0},
                },
            },
        ),
        ({'queues': ['azaza100500']}, {'queues': {}}),
        (
            {'queues': ['azaza11', 'azaza100500'], 'metrics': ['total']},
            {'queues': {'azaza11': {'total': 0}}},
        ),
        (
            {'queues': ['azaza11', 'azaza12'], 'metrics': ['total']},
            {'queues': {'azaza11': {'total': 0}, 'azaza12': {'total': 0}}},
        ),
    ],
)
@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
async def test_queues_stats_get_queues(
        taxi_stq_agent, stqs, request_body, expected_response,
):
    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_stats_get_total(taxi_stq_agent, now, stqs):
    request_body = {
        'queues': ['azaza11'],
        'metrics': ['total', 'total_with_done'],
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard('azaza11', 0)
    stq_shard.add_task('yes11', x='stq-worker', e=helpers.FAR_FUTURE_TIMESTAMP)
    stq_shard.add_task('yes12', e=now_timestamp)

    stq_shard.add_task('no11', e=helpers.FAR_FUTURE_TIMESTAMP)

    stq_shard = stqs.get_shard('azaza11', 1)
    stq_shard.add_task('yes21', e=now_timestamp)

    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == {
        'queues': {'azaza11': {'total': 3, 'total_with_done': 4}},
    }


@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_stats_get_running(taxi_stq_agent, now, stqs):
    request_body = {'queues': ['azaza11'], 'metrics': ['running']}

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard('azaza11', 0)
    stq_shard.add_task('yes11', x='stq-worker', e=helpers.FAR_FUTURE_TIMESTAMP)

    stq_shard.add_task('no11', e=now_timestamp)
    stq_shard.add_task('no12', e=helpers.FAR_FUTURE_TIMESTAMP)

    stq_shard = stqs.get_shard('azaza11', 1)
    stq_shard.add_task('yes21', x='stq-worker', e=helpers.FAR_FUTURE_TIMESTAMP)

    stq_shard.add_task('no21', e=now_timestamp)

    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == {'queues': {'azaza11': {'running': 2}}}


@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_stats_get_failed(taxi_stq_agent, stqs):
    request_body = {'queues': ['azaza11'], 'metrics': ['failed']}

    stq_shard = stqs.get_shard('azaza11', 0)
    stq_shard.add_task('yes11', f=helpers.FAILS_COUNT_THRESHOLD)
    stq_shard.add_task('yes12', f=(helpers.FAILS_COUNT_THRESHOLD + 1))

    stq_shard.add_task('no11', f=(helpers.FAILS_COUNT_THRESHOLD - 1))
    stq_shard.add_task(
        'no12', x='stq-worker', f=(helpers.FAILS_COUNT_THRESHOLD + 1),
    )

    stq_shard = stqs.get_shard('azaza11', 1)
    stq_shard.add_task('yes21', f=helpers.FAILS_COUNT_THRESHOLD)

    stq_shard.add_task(
        'no21', x='stq-worker', f=(helpers.FAILS_COUNT_THRESHOLD + 1),
    )

    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == {'queues': {'azaza11': {'failed': 3}}}


@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_stats_get_abandoned(taxi_stq_agent, now, stqs):
    request_body = {'queues': ['azaza11'], 'metrics': ['abandoned']}

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard('azaza11', 0)
    stq_shard.add_task(
        'ready_no11',
        x='stq-worker',
        e=(now_timestamp - helpers.ABANDONED_TIMEOUT),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'ready_no12',
        e=(now_timestamp - helpers.ABANDONED_TIMEOUT + 1),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'ready_no13', t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'ready_no14',
        e=(now_timestamp - helpers.ABANDONED_TIMEOUT),
        t=now_timestamp,
    )

    stq_shard.add_task(
        'dead_no11',
        e=now_timestamp,
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'dead_no12',
        x='stq-worker',
        e=(now_timestamp - 1),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'dead_no13',
        x='stq-worker',
        e=now_timestamp,
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT + 1),
    )

    stq_shard.add_task(
        'ready_yes11',
        e=(now_timestamp - helpers.ABANDONED_TIMEOUT),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )
    stq_shard.add_task(
        'dead_yes11',
        x='stq-worker',
        e=now_timestamp,
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT),
    )

    stq_shard = stqs.get_shard('azaza11', 1)
    stq_shard.add_task(
        'ready_yes21',
        e=(now_timestamp - helpers.ABANDONED_TIMEOUT - 1),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT - 1),
    )
    stq_shard.add_task(
        'dead_yes21',
        x='stq-worker',
        e=(now_timestamp + 1),
        t=(now_timestamp - helpers.ABANDONED_TIMEOUT - 1),
    )

    response = await taxi_stq_agent.post('queues/stats', json=request_body)
    assert response.status_code == 200
    assert response.json() == {'queues': {'azaza11': {'abandoned': 4}}}


@pytest.mark.config(STQ_AGENT_ASYNC_STATS_REQUESTS_TIMEOUT_MS=1000)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_abandoned_timeout(taxi_stq_agent, stqs, now, testpoint):
    @testpoint('stq_shard::get-abandoned-tasks-count')
    def testpoint_get_abandoned(data):
        pass

    now_timestamp = helpers.to_timestamp(now)
    stq_shard = stqs.get_shard('foo', 0)
    stq_shard.add_task('ok', e=now_timestamp - 15)
    stq_shard.add_task('abandoned', e=now_timestamp - 5)

    response = await taxi_stq_agent.post(
        'queues/stats', json={'queues': ['foo'], 'metrics': ['abandoned']},
    )
    assert response.status_code == 200
    assert response.json() == {'queues': {'foo': {'abandoned': 1}}}

    assert testpoint_get_abandoned.times_called == 1
    assert testpoint_get_abandoned.next_call() == {
        'data': {'abandoned_timeout': 10},
    }
