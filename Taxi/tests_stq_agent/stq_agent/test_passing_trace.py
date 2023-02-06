import pytest

HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}

ETAS_TRACE_ID_POSTFIX = [
    ('2018-12-01T14:00:01Z', '1'),
    ('2018-12-01T14:00:02Z', '2'),
    ('2018-12-01T14:00:03Z', '3'),
]

TASK_ID = 'ololo1'


async def mark_as_done(taxi_stq_agent):
    mark_as_done_request_body = {
        'queue_name': 'azaza11',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': TASK_ID,
    }

    response = await taxi_stq_agent.post(
        'queues/api/mark_as_done',
        json=mark_as_done_request_body,
        headers=HEADERS,
    )
    assert response.status_code == 200


async def free_task(taxi_stq_agent):
    free_request_body = {
        'queue_name': 'azaza11',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': TASK_ID,
    }

    response = await taxi_stq_agent.post(
        'queues/api/free', json=free_request_body, headers=HEADERS,
    )
    assert response.status_code == 200


async def take_task(taxi_stq_agent, queue_name='azaza11'):
    take_request_body = {
        'queue_name': queue_name,
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 1,
    }
    response = await taxi_stq_agent.post(
        'queues/api/take', json=take_request_body, headers=HEADERS,
    )
    assert response.status_code == 200

    assert response.json()['tasks']
    return response.json()['tasks'][0]


async def add_task(taxi_stq_agent, i, reschedule=False, queue_name='azaza11'):
    trace_headers = [
        {
            'X-YaTaxi-API-Key': 'InferniaOverkill',
            'X-YaRequestId': '1234567890-link',
            'X-YaTraceId': f'trace-id-{postfix}',
            'X-YaSpanId': '1234567890-parent-id',
        }
        for (_, postfix) in ETAS_TRACE_ID_POSTFIX
    ]

    if reschedule:
        trace_request_bodies = [
            {'queue_name': queue_name, 'task_id': TASK_ID, 'eta': eta}
            for (eta, _) in ETAS_TRACE_ID_POSTFIX
        ]

        response = await taxi_stq_agent.post(
            'queues/api/reschedule',
            json=trace_request_bodies[i],
            headers=trace_headers[i],
        )
    else:
        trace_request_bodies = [
            {
                'task_id': TASK_ID,
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': eta,
            }
            for (eta, _) in ETAS_TRACE_ID_POSTFIX
        ]

        response = await taxi_stq_agent.post(
            f'queues/api/add/{queue_name}',
            json=trace_request_bodies[i],
            headers=trace_headers[i],
        )

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.parametrize(
    'add_order',
    [[0, 1, 2], [2, 1, 0], [0, 1, 0], [2, 0, 1], [1, 0, 2], [2, 1, 2]],
)
@pytest.mark.parametrize(
    'reschedule_order',
    [
        [False, False, False],
        [False, True, False],
        [False, False, True],
        [False, True, True],
    ],
)
@pytest.mark.now('2018-12-01T14:00:05Z')
async def test_add_take_with_min_eta(
        add_order, reschedule_order, taxi_stq_agent,
):
    for i, reschedule in zip(add_order, reschedule_order):
        await add_task(taxi_stq_agent, i, reschedule=reschedule)

    taken_task = await take_task(taxi_stq_agent)

    await mark_as_done(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[min(add_order)][1]}'
    )


@pytest.mark.parametrize('add_take_order', [[0, 1, 2], [2, 1, 0]])
@pytest.mark.now('2018-12-01T14:00:05Z')
async def test_consequent_add_take(add_take_order, taxi_stq_agent):
    async def add_take_task(eta_id):
        await add_task(taxi_stq_agent, eta_id)

        taken_task = await take_task(taxi_stq_agent)

        assert (
            taken_task['tracing']['trace_id']
            == f'trace-id-{ETAS_TRACE_ID_POSTFIX[eta_id][1]}'
        )

        await mark_as_done(taxi_stq_agent)

    for i in add_take_order:
        await add_take_task(i)


@pytest.mark.config(STQ_AGENT_REPEAT_AFTER_RAND_RATE=0)
@pytest.mark.config(STQ_AGENT_MAX_REPEAT_AFTER=2)
@pytest.mark.now('2018-12-01T14:00:05Z')
async def test_mark_as_failed(taxi_stq_agent, mocked_time):
    mark_as_failed_request_body = {
        'queue_name': 'azaza11',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'task_id': TASK_ID,
        'exec_tries': 2,
    }

    # Add task
    await add_task(taxi_stq_agent, 0)

    # Take task, to mark it failed
    await take_task(taxi_stq_agent)

    # Make task fail, reschedules it forward
    response = await taxi_stq_agent.post(
        'queues/api/mark_as_failed',
        json=mark_as_failed_request_body,
        headers=HEADERS,
    )
    assert response.status_code == 200

    mocked_time.sleep(2)
    await taxi_stq_agent.invalidate_caches()

    # Add same task again
    await add_task(taxi_stq_agent, 1)

    # Take first added task
    taken_task = await take_task(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[0][1]}'
    )

    await mark_as_done(taxi_stq_agent)


@pytest.mark.parametrize('first,second', [(2, 0), (0, 2)])
@pytest.mark.now('2018-12-01T14:00:05Z')
async def test_add_while_execute(first, second, taxi_stq_agent):
    await add_task(taxi_stq_agent, first)

    taken_task = await take_task(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[first][1]}'
    )

    await add_task(taxi_stq_agent, second)

    await mark_as_done(taxi_stq_agent)

    taken_task = await take_task(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[second][1]}'
    )

    await mark_as_done(taxi_stq_agent)


@pytest.mark.parametrize('first,second', [(2, 0), (0, 2)])
@pytest.mark.now('2018-12-01T14:00:05Z')
async def test_free_task(first, second, taxi_stq_agent):
    await add_task(taxi_stq_agent, first)

    taken_task = await take_task(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[first][1]}'
    )

    await free_task(taxi_stq_agent)

    await add_task(taxi_stq_agent, second)

    taken_task = await take_task(taxi_stq_agent)

    assert (
        taken_task['tracing']['trace_id']
        == f'trace-id-{ETAS_TRACE_ID_POSTFIX[first][1]}'
    )

    await mark_as_done(taxi_stq_agent)


async def test_disable_tracing(taxi_stq_agent):
    queue = 'without_tracing'
    await add_task(taxi_stq_agent, 0, queue_name=queue)
    taken_task = await take_task(taxi_stq_agent, queue_name=queue)
    assert 'tracing' not in taken_task
