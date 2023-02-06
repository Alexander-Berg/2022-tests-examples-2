import pytest
from tests_stq_agent import helpers


HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.parametrize(
    'url_path, specific_request_params',
    [
        ('mark_as_done', {}),
        ('mark_as_failed', {'exec_tries': 1}),
        ('free', {}),
    ],
)
async def test_queues_api_mark_task_bad_request(
        taxi_stq_agent, url_path, specific_request_params,
):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': -1,
        'node_id': 'stq-worker.yandex.net',
        'task_id': 'task1',
    }
    request_body.update(specific_request_params)

    response = await taxi_stq_agent.post(
        'queues/api/' + url_path, json=request_body, headers=HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'specific_request_params', [{}, {'exec_tries': 0}, {'exec_tries': -1}],
)
async def test_queues_api_mark_as_failed_bad_request(
        taxi_stq_agent, specific_request_params,
):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': 'task1',
    }
    request_body.update(specific_request_params)

    response = await taxi_stq_agent.post(
        'queues/api/mark_as_failed', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'url_path, specific_request_params',
    [
        ('mark_as_done', {}),
        ('mark_as_failed', {'exec_tries': 1}),
        ('free', {}),
    ],
)
@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'azaza2',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'task_id': 'task1',
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 2,
            'node_id': 'stq-worker.yandex.net',
            'task_id': 'task1',
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'task_id': 'task100500',
        },
    ],
)
async def test_queues_api_mark_task_not_found(
        taxi_stq_agent, url_path, specific_request_params, request_body,
):
    request_body.update(specific_request_params)

    response = await taxi_stq_agent.post(
        'queues/api/' + url_path, json=request_body, headers=HEADERS,
    )
    assert response.status_code == 404


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'x, t, f, m, status_code',
    [
        (None, 0.0, 0, None, 200),
        ('other-stq-worker.yandex.net', 0.0, 0, None, 404),
        (None, 100500.0, 0, None, 404),
        (None, 0.0, 100500, None, 404),
        (None, 0.0, 0, 'azaza_ololo', 404),
    ],
)
async def test_queues_api_mark_as_done_found_or_not_found(
        taxi_stq_agent, now, stqs, x, t, f, m, status_code,
):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': 'task1',
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    stq_shard.add_task(
        request_body['task_id'], x=x, t=t, f=f, eu=now_timestamp, m=m,
    )

    response = await taxi_stq_agent.post(
        'queues/api/mark_as_done', json=request_body, headers=HEADERS,
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'url_path, specific_request_params, e, t, f, ff',
    [
        (
            'mark_as_done',
            {'ff': 232313},
            helpers.FAR_FUTURE_TIMESTAMP,
            0.0,
            0,
            None,
        ),
        ('mark_as_failed', {'exec_tries': 10}, None, None, 3, 1543672800),
        ('free', {}, 1543672800, 0.0, 2, None),
        ('free', {'is_expired': True}, 1543672800, 0.0, 3, None),
    ],
)
@pytest.mark.config(STQ_AGENT_REPEAT_AFTER_RAND_RATE=0)
@pytest.mark.config(STQ_AGENT_MAX_REPEAT_AFTER=10)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_mark_task(
        taxi_stq_agent,
        now,
        taxi_config,
        stqs,
        url_path,
        specific_request_params,
        e,
        t,
        f,
        ff,
):
    task_id = 'task1'

    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': task_id,
    }

    request_body.update(specific_request_params)

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )
    stq_shard.add_task(
        task_id,
        x=request_body['node_id'],
        e=helpers.FAR_FUTURE_TIMESTAMP,
        t=(now_timestamp + helpers.STQ_TASKS_EXECUTION_TIMEOUT),
        f=3,
        eu=(now_timestamp - 3),
    )

    response = await taxi_stq_agent.post(
        'queues/api/' + url_path, json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {}

    if 'exec_tries' in specific_request_params:
        new_timestamp = now_timestamp + taxi_config.get(
            'STQ_AGENT_MAX_REPEAT_AFTER',
        )
        e = new_timestamp
        t = new_timestamp

    task = stq_shard.get_task(task_id)
    if ff is None:
        assert 'ff' not in task
    else:
        assert task.get('ff') == ff

    assert not task['x']
    assert task['e'] == e
    assert task['t'] == t
    assert task['f'] == f
    assert task['eu'] == now_timestamp
    assert 'm' not in task
    assert 's' not in task


@pytest.mark.parametrize(
    'exec_tries, repeat_eta',
    [
        (1, 1543672802),
        (2, 1543672804),
        (3, 1543672808),
        (4, 1543672810),
        (5, 1543672810),
    ],
)
@pytest.mark.config(STQ_AGENT_REPEAT_AFTER_RAND_RATE=0)
@pytest.mark.config(STQ_AGENT_MAX_REPEAT_AFTER=10)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_mark_as_failed_with_exec_tries(
        taxi_stq_agent, now, stqs, exec_tries, repeat_eta,
):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': 'task1',
        'exec_tries': exec_tries,
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    stq_shard.add_task(
        request_body['task_id'],
        x=request_body['node_id'],
        e=helpers.FAR_FUTURE_TIMESTAMP,
        t=now_timestamp + helpers.STQ_TASKS_EXECUTION_TIMEOUT,
        f=exec_tries,
    )

    response = await taxi_stq_agent.post(
        'queues/api/mark_as_failed', json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {}

    task = stq_shard.get_task(request_body['task_id'])
    assert task['e'] == repeat_eta
    assert task['t'] == repeat_eta


@pytest.mark.parametrize(
    'request_params, expected_code',
    [({'take_id': 'correct-id'}, 200), ({'take_id': 'wrong-id'}, 404)],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_mark_as_done_with_take_id(
        taxi_stq_agent, now, stqs, request_params, expected_code,
):
    task_id = 'task1'

    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': task_id,
    }
    request_body.update(request_params)

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    stq_shard.add_task(
        task_id,
        x=request_body['node_id'],
        e=helpers.FAR_FUTURE_TIMESTAMP,
        t=(now_timestamp + helpers.STQ_TASKS_EXECUTION_TIMEOUT),
        f=3,
        eu=(now_timestamp - 3),
        m='stq-worker.yandex.net#correct-id',
    )
    task_before = stq_shard.get_task(task_id)

    response = await taxi_stq_agent.post(
        'queues/api/mark_as_done', json=request_body, headers=HEADERS,
    )

    assert response.status_code == expected_code

    task = stq_shard.get_task(task_id)
    if expected_code == 200:
        assert not task['x']
        assert task['e'] == helpers.FAR_FUTURE_TIMESTAMP
        assert task['t'] == 0.0
        assert task['f'] == 0
        assert task['eu'] == now_timestamp
        assert 'm' not in task
        assert 's' not in task
    else:
        assert task == task_before
