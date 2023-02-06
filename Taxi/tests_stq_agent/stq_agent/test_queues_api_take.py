import datetime

import bson
import dateutil.parser
import pytest
from tests_stq_agent import helpers

from tests_plugins import utils
from testsuite.utils import ordered_object

HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}

SET_RPS_LIMITER_TESTSUITE_TIMEOUTS = pytest.mark.config(
    STATISTICS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 1000}},
    STATISTICS_RPS_LIMITER_PER_LIMITER_SETTINGS={
        '__default__': {'wait_request_duration': 2000},
    },
)


def _eta_response_from_float_seconds(float_seconds):
    datetime_format = '%Y-%m-%dT%H:%M:%S%z'
    return datetime.datetime.strftime(
        datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        + datetime.timedelta(seconds=float_seconds),
        datetime_format,
    )


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'azaza1',
            'shard_id': -1,
            'node_id': 'stq-worker.yandex.net',
            'max_tasks': 5,
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'max_tasks': 0,
        },
    ],
)
async def test_queues_api_take_bad_request(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'queue_name': 'azaza2',
            'shard_id': 0,
            'node_id': 'stq-worker.yandex.net',
            'max_tasks': 5,
        },
        {
            'queue_name': 'azaza1',
            'shard_id': 2,
            'node_id': 'stq-worker.yandex.net',
            'max_tasks': 5,
        },
    ],
)
async def test_queues_api_take_not_found(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.config(STQ_AGENT_LOG_TAKE_IDS_QUEUES_ENABLED=['azaza1'])
@pytest.mark.config(
    STQ_AGENT_SEPARATE_MDB_PROCESSING={
        'enabled': True,
        'main_tp_databases': ['stq12'],
    },
)
async def test_queues_api_take(taxi_stq_agent, now, stqs):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 10,
    }

    now_timestamp = helpers.to_timestamp(now)

    ready_tasks = []
    for i in range(5):
        ready_tasks.append('task' + str(i))
    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    stq_shard.add_task(ready_tasks[0])
    stq_shard.add_task(ready_tasks[1], e=now_timestamp)
    stq_shard.add_task(ready_tasks[2], t=now_timestamp)
    stq_shard.add_task(
        ready_tasks[3],
        x='stuck-worker.yandex.net',
        e=helpers.FAR_FUTURE_TIMESTAMP,
        e_dup=(now_timestamp - 10),
        t=(now_timestamp - 1),
    )
    stq_shard.add_task(
        ready_tasks[4],
        x='stuck-worker.yandex.net',
        e=helpers.FAR_FUTURE_TIMESTAMP,
        e_dup=(now_timestamp - 5),
        t=now_timestamp,
    )

    stq_shard.add_task('task1001', e=(now_timestamp + 1))
    stq_shard.add_task('task1002', t=(now_timestamp + 1))
    stq_shard.add_task(
        'task1003',
        x='non-stuck-worker.yandex.net',
        e=helpers.FAR_FUTURE_TIMESTAMP,
        e_dup=(now_timestamp - 5),
        t=(now_timestamp + 1),
    )

    expected_response = {
        'tasks': [
            {
                'task_id': ready_task,
                'args': [],
                'kwargs': {},
                'exec_tries': 0,
                'reschedule_counter': 0,
                'eta': _eta_response_from_float_seconds(
                    stq_shard.get_task(ready_task)['e_dup'],
                ),
            }
            for ready_task in ready_tasks
        ],
    }

    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200

    ordered_object.assert_eq(response.json(), expected_response, ['tasks'])

    _check_tasks(
        stq_shard, ready_tasks, request_body['node_id'], now_timestamp,
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
@pytest.mark.config(STQ_AGENT_LOG_TAKE_IDS_QUEUES_ENABLED=['azaza1'])
@pytest.mark.config(
    STQ_AGENT_SEPARATE_MDB_PROCESSING={
        'enabled': True,
        'main_tp_databases': ['stq12'],
    },
)
async def test_queues_api_take_by_tag(taxi_stq_agent, now, stqs):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 10,
        'tags': ['taxi_1'],
    }

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )
    stq_shard.add_task('tagged_task', tag='taxi_1')

    expected_response = {
        'tasks': [
            {
                'task_id': 'tagged_task',
                'args': [],
                'kwargs': {},
                'exec_tries': 0,
                'reschedule_counter': 0,
                'eta': '1970-01-01T00:00:00+0000',
                'tag': 'taxi_1',
            },
        ],
    }
    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(response.json(), expected_response, ['tasks'])


@pytest.mark.parametrize('minimal_quota', [10, 3])
@pytest.mark.parametrize('increase_limiter_enabled', [False, True])
@pytest.mark.now('2018-12-01T14:00:00Z')
@SET_RPS_LIMITER_TESTSUITE_TIMEOUTS
async def test_queues_api_take_limiter_new(
        taxi_stq_agent,
        now,
        stqs,
        mockserver,
        taxi_config,
        minimal_quota,
        increase_limiter_enabled,
):
    taxi_config.set_values(
        {
            'STQ_AGENT_RPS_LIMITER_SETTINGS': {
                'use_rps_limiter_lib': False,
                'minimal_quota': minimal_quota,
            },
        },
    )

    if increase_limiter_enabled:
        queue = 'azaza1_smoothly_limited'
    else:
        queue = 'azaza1_limited'
    request_body = {
        'queue_name': queue,
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 10,
    }

    ready_tasks = []
    for i in range(5):
        ready_tasks.append('task' + str(i))

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )
    for task in ready_tasks:
        stq_shard.add_task(task)

    @mockserver.json_handler('/statistics/v1/rps-quotas')
    def _rps_quotas(request):
        requests = request.json['requests']
        assert request.args['service'] == 'stq-tasks-taken'
        for req in requests:
            if req['resource'] == 'azaza1_limited':
                assert req['limit'] == 4
                assert req['interval'] == 1
                assert 'max-increase-step' not in req
                assert req['minimal-quota'] == min(minimal_quota, 4)
            elif req['resource'] == 'azaza1_smoothly_limited':
                assert req['limit'] == 4
                assert req['interval'] == 1
                assert req['max-increase-step'] == 3
                assert req['minimal-quota'] == 0
            else:
                raise RuntimeError('Wrong resource: %s' % req['resource'])
        return {
            'quotas': [
                {'resource': 'azaza1_limited', 'assigned-quota': 3},
                {'resource': 'azaza1_smoothly_limited', 'assigned-quota': 3},
            ],
        }

    # TODO: remove after redone on common `list` for caches and components
    # rps-limiter's `Invalidate` works after
    # stq_dispatcher's `Invalidate` and we have to do it
    await taxi_stq_agent.get('ping')  # for invalidate_caches call
    await taxi_stq_agent.invalidate_caches(cache_names=['stqs-config'])

    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200
    assert len(response.json()['tasks']) == 3


@pytest.mark.parametrize(
    'num_of_ready_tasks, num_of_stuck_tasks', [(5, 0), (0, 5), (2, 2), (1, 1)],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_take_max_tasks(
        taxi_stq_agent, now, stqs, num_of_ready_tasks, num_of_stuck_tasks,
):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 3,
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    for i in range(num_of_ready_tasks):
        stq_shard.add_task('ready_task' + str(i), e=now_timestamp)

    for i in range(num_of_stuck_tasks):
        stq_shard.add_task(
            'stuck_task' + str(i),
            x='stuck-worker.yandex.net',
            e=helpers.FAR_FUTURE_TIMESTAMP,
            t=now_timestamp,
        )

    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200
    expected_tasks_count = min(
        request_body['max_tasks'], num_of_ready_tasks + num_of_stuck_tasks,
    )
    assert len(response.json()['tasks']) == expected_tasks_count


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_take_task_fields(taxi_stq_agent, stqs):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 3,
    }

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    stq_shard.add_task(
        'task1',
        a=[bson.ObjectId('507f1f77bcf86cd799439011'), 777, 'opa-pa'],
        k={
            'azaza': {
                'ololo': bson.ObjectId('507f1f77bcf86cd799439011'),
                'alya_ulyu': utils.to_utc(
                    dateutil.parser.parse('2018-05-02T12:54:42Z'),
                ),
            },
            'b': True,
        },
        f=100500,
        rc=200600,
    )

    response = await taxi_stq_agent.post(
        'queues/api/take', json=request_body, headers=HEADERS,
    )

    assert response.status_code == 200
    tasks = response.json()['tasks']
    assert len(tasks) == 1
    assert tasks[0] == {
        'task_id': 'task1',
        'args': [{'$oid': '507f1f77bcf86cd799439011'}, 777, 'opa-pa'],
        'kwargs': {
            'azaza': {
                'ololo': {'$oid': '507f1f77bcf86cd799439011'},
                'alya_ulyu': {'$date': '2018-05-02T12:54:42Z'},
            },
            'b': True,
        },
        'exec_tries': 100500,
        'reschedule_counter': 200600,
        'eta': '1970-01-01T00:00:00+0000',
    }


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queues_api_take_idempotency(taxi_stq_agent, now, stqs):
    request_body = {
        'queue_name': 'azaza1',
        'shard_id': 0,
        'node_id': 'stq-worker.yandex.net',
        'max_tasks': 10,
        'idempotency_token': '100500',
        'first_try': True,
    }

    now_timestamp = helpers.to_timestamp(now)

    stq_shard = stqs.get_shard(
        request_body['queue_name'], request_body['shard_id'],
    )

    ready_tasks = []
    for i in range(5):
        ready_task = 'task_{}'.format(i)
        ready_tasks.append(ready_task)
        stq_shard.add_task(ready_task, e=now_timestamp, eu=now_timestamp)

    async def _check_take(tasks, idempotency_token):
        response = await taxi_stq_agent.post(
            'queues/api/take', json=request_body, headers=HEADERS,
        )

        assert response.status_code == 200
        expected_response = {
            'tasks': [
                {
                    'task_id': task,
                    'args': [],
                    'kwargs': {},
                    'exec_tries': 0,
                    'reschedule_counter': 0,
                    'eta': _eta_response_from_float_seconds(
                        stq_shard.get_task(task)['e_dup'],
                    ),
                }
                for task in tasks
            ],
        }
        ordered_object.assert_eq(response.json(), expected_response, ['tasks'])

        _check_tasks(
            stq_shard,
            tasks,
            request_body['node_id'],
            now_timestamp,
            idempotency_token,
        )

    await _check_take(ready_tasks, request_body['idempotency_token'])

    new_tasks = []
    for i in range(5, 10):
        new_task = 'task_{}'.format(i)
        new_tasks.append(new_task)
        stq_shard.add_task(new_task, e=now_timestamp, eu=now_timestamp)

    request_body['first_try'] = False

    await _check_take(ready_tasks, request_body['idempotency_token'])

    for new_task in new_tasks:
        task = stq_shard.get_task(new_task)
        assert task['x'] is None
        assert task['e'] == now_timestamp
        assert task['t'] == 0.0
        assert task['f'] == 0
        assert 'm' not in task
        assert 's' not in task

    request_body['idempotency_token'] = '500100'

    await _check_take(new_tasks, request_body['idempotency_token'])


def _check_tasks(
        stq_shard, ready_tasks, node_id, now_timestamp, idempotency_token=None,
):
    for ready_task in ready_tasks:
        task = stq_shard.get_task(ready_task)
        assert task['x'] == node_id
        assert task['e'] == helpers.FAR_FUTURE_TIMESTAMP
        assert task['t'] == now_timestamp + helpers.STQ_TASKS_EXECUTION_TIMEOUT
        assert task['f'] == 1
        m_begin = '{}#'.format(node_id)
        if idempotency_token:
            assert task['m'] == m_begin + idempotency_token
        else:
            assert task['m'].startswith(m_begin)
        assert task['s'] == now_timestamp
