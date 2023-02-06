import pytest
from tests_stq_agent import helpers

# Generated via `tvmknife unittest service -s 444 -d 25115365`
ALLOWED_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggIvAMQ'
    '5fX8Cw:WjOpFltPovu_j9yf52A6TONn'
    'X5lKANHwYWY-lBRXi0dj-6glZ_CddmY'
    'KoXu-ZT6AsfyQdX5iCDnCwcDoc7-gvW'
    '2rLwIa8kA5Iz50kJVmDfxHWWed7Nx_5'
    'DSgqSGNsBtiAH67KPZlmMvdGSdfVg_N'
    'oHkEYmg4AnWnGRp4Hzms0YE'
)

# Generated via `tvmknife unittest service -s 111 -d 25115365`
NOT_ALLOWED_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIbxD'
    'l9fwL:AmkcGQGDJOqa6taL52JG7Of8'
    'BcRF5CoyYfJ4TWmHtTeXxYIdU8CHOT'
    'EZcWNTzIjo6aB4P5ebr8hTVzn4AhRp'
    'rtMh4bIiV3OQPO6dMSfs241bjNBmxT'
    '7zLc1u3pDmHGPYuJ-mvo0LKfuxNhme'
    'GELLf3L5RVswKcQ9vdlfq1POLZM'
)


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'allowed', 'dst': 'stq-agent'},
        {'src': 'not-allowed', 'dst': 'stq-agent'},
    ],
    TVM_SERVICES={
        'stq-agent': 25115365,
        'allowed': 444,
        'not-allowed': 111,
        'statistics': 333,
    },
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 2,
            'ensure_enabled': True,
        },
    },
)
@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.tvm2_ticket(
    {444: ALLOWED_SERVICE_TICKET, 111: NOT_ALLOWED_SERVICE_TICKET},
)
@pytest.mark.parametrize(
    'expected_code, expected_body, tvm_ticket, queue',
    [
        pytest.param(200, {}, ALLOWED_SERVICE_TICKET, 'ban_is_disabled'),
        pytest.param(200, {}, NOT_ALLOWED_SERVICE_TICKET, 'ban_is_disabled'),
        pytest.param(200, {}, ALLOWED_SERVICE_TICKET, 'ban_is_enabled'),
        pytest.param(
            403,
            {
                'code': '403',
                'message': (
                    'The service that adds task is '
                    'forbidden for queue, source service: not-allowed'
                ),
            },
            NOT_ALLOWED_SERVICE_TICKET,
            'ban_is_enabled',
        ),
    ],
)
async def test_post_separation(
        taxi_stq_agent, expected_code, expected_body, tvm_ticket, queue,
):
    await taxi_stq_agent.invalidate_caches()
    request_body = {
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }
    response = await taxi_stq_agent.post(
        'queues/api/add/' + queue,
        json=request_body,
        headers={'X-Ya-Service-Ticket': tvm_ticket},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'allowed', 'dst': 'stq-agent'},
        {'src': 'not-allowed', 'dst': 'stq-agent'},
    ],
    TVM_SERVICES={
        'stq-agent': 25115365,
        'allowed': 444,
        'not-allowed': 111,
        'statistics': 333,
    },
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 2,
            'ensure_enabled': True,
        },
    },
)
@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.tvm2_ticket(
    {444: ALLOWED_SERVICE_TICKET, 111: NOT_ALLOWED_SERVICE_TICKET},
)
@pytest.mark.parametrize(
    'expected_code, expected_body, tvm_ticket, queue',
    [
        pytest.param(200, {}, ALLOWED_SERVICE_TICKET, 'ban_is_disabled'),
        pytest.param(200, {}, NOT_ALLOWED_SERVICE_TICKET, 'ban_is_disabled'),
        pytest.param(200, {}, ALLOWED_SERVICE_TICKET, 'ban_is_enabled'),
        pytest.param(
            403,
            {
                'code': 'FORBIDDEN',
                'message': (
                    'The service that reschedules task is '
                    'forbidden for queue, source service: not-allowed'
                ),
            },
            NOT_ALLOWED_SERVICE_TICKET,
            'ban_is_enabled',
        ),
    ],
)
async def test_reschedule_separation(
        taxi_stq_agent, stqs, expected_code, expected_body, tvm_ticket, queue,
):
    await taxi_stq_agent.invalidate_caches()
    eta_orig = '2018-12-01T16:00:00Z'

    stq_shard = stqs.get_shard(queue, 0)

    stq_shard.add_task('task', e=helpers.to_timestamp(eta_orig))
    eta = '2018-12-01T15:00:00Z'
    response = await taxi_stq_agent.post(
        'queues/api/reschedule',
        json={'queue_name': queue, 'task_id': 'task', 'eta': eta},
        headers={'X-Ya-Service-Ticket': tvm_ticket},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[
        {'src': 'allowed', 'dst': 'stq-agent'},
        {'src': 'not-allowed', 'dst': 'stq-agent'},
    ],
    TVM_SERVICES={
        'stq-agent': 25115365,
        'allowed': 444,
        'not-allowed': 111,
        'statistics': 333,
    },
    STQ_AGENT_BUFFERING_SETTINGS={
        'db': {
            'max_bulk_size': 3,
            'bulk_workers_count': 2,
            'ensure_enabled': True,
        },
    },
)
@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.tvm2_ticket(
    {444: ALLOWED_SERVICE_TICKET, 111: NOT_ALLOWED_SERVICE_TICKET},
)
@pytest.mark.parametrize(
    'expected_code, expected_body, tvm_ticket, queue',
    [
        pytest.param(
            200,
            {'tasks': [{'add_result': {'code': 200}, 'task_id': 'ololo1'}]},
            ALLOWED_SERVICE_TICKET,
            'ban_is_disabled',
        ),
        pytest.param(
            200,
            {'tasks': [{'add_result': {'code': 200}, 'task_id': 'ololo1'}]},
            NOT_ALLOWED_SERVICE_TICKET,
            'ban_is_disabled',
        ),
        pytest.param(
            200,
            {'tasks': [{'add_result': {'code': 200}, 'task_id': 'ololo1'}]},
            ALLOWED_SERVICE_TICKET,
            'ban_is_enabled',
        ),
        pytest.param(
            403,
            {
                'code': '403',
                'message': (
                    'The service that adds bulk is '
                    'forbidden for queue, source service: not-allowed'
                ),
            },
            NOT_ALLOWED_SERVICE_TICKET,
            'ban_is_enabled',
        ),
    ],
)
async def test_add_bulk_separation(
        taxi_stq_agent, stqs, expected_code, expected_body, tvm_ticket, queue,
):
    await taxi_stq_agent.invalidate_caches()
    request_body = {
        'tasks': [
            {
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
        ],
    }
    response = await taxi_stq_agent.post(
        'queues/api/add/' + queue + '/bulk',
        json=request_body,
        headers={'X-Ya-Service-Ticket': tvm_ticket},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_body


@pytest.mark.parametrize(
    'expected_code, expected_body, queue',
    [
        pytest.param(200, {}, 'ban_is_disabled'),
        pytest.param(
            403,
            {
                'code': '403',
                'message': (
                    'The service that adds task is '
                    'forbidden for queue, source service: not available'
                ),
            },
            'ban_is_enabled',
        ),
    ],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_post_separation_without_service_name(
        taxi_stq_agent, queue, expected_code, expected_body,
):
    await taxi_stq_agent.invalidate_caches()
    request_body = {
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }
    response = await taxi_stq_agent.post(
        'queues/api/add/' + queue, json=request_body,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_body
