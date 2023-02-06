import datetime
import json
import operator

import dateutil.parser
import pytest

HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.parametrize(
    'request_body, expected_response_message',
    [
        ({}, 'Request BSON does not contain some of the required fields'),
        (
            {
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'etata': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON contains an unexpected field',
        ),
        (
            '{'
            '    "task_id": "ololo",'
            '    "args": [1, 2, 3],'
            '    "kwargs": {"a": {"b": "c"}, "d": 1},'
            '    "eta": "2018-12-01T14:00:01.123456Z",'
            '    "eta": "2018-12-01T14:00:01.654321Z"'
            '}',
            'duplicate key \'eta\' at /',
        ),
        (
            '{'
            '    "task_id": "ololo",'
            '    "task_id": "ololo",'
            '    "task_id": "ololo",'
            '    "task_id": "ololo",'
            '    "task_id": "ololo"'
            '}',
            'duplicate key \'task_id\' at /',
        ),
        (
            {
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ok',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Queue name was provided twice: in body and separately',
        ),
        (
            {
                'task_id': 'ololo',
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
            },
            'Request BSON does not contain some of the required fields',
        ),
    ],
)
async def test_queues_api_add_bad_request(
        taxi_stq_agent, request_body, expected_response_message, db_extra,
):
    expected_response_body = {
        'code': '400',
        'message': expected_response_message,
    }

    response = await taxi_stq_agent.post(
        'queues/api/add/azaza11',
        data=(
            json.dumps(request_body)
            if isinstance(request_body, dict)
            else request_body
        ),
        headers=HEADERS,
    )
    assert response.status_code == 400
    actual_response_body = response.json()
    assert actual_response_body['code'] == expected_response_body['code']
    assert actual_response_body['message'].startswith(
        expected_response_body['message'],
    )
    assert len(actual_response_body) == 2


@pytest.mark.parametrize(
    'request_body',
    [
        {
            'task_id': 'ololo1',
            'args': [1, 2, 3],
            'kwargs': {'a': {'b': 'c'}, 'd': 1},
            'eta': '2018-12-01T14:00:01.123456Z',
        },
        {
            'task_id': 'ololo2',
            'args': ['1', '2', '3'],
            'kwargs': {1: 2, 3: 4},
            'eta': '2018-12-01T14:00:01.123456+0300',
        },
        {
            'task_id': 'ololo3',
            'args': [],
            'kwargs': {},
            'eta': '2018-12-1T14:00:1Z',
        },
        {
            'task_id': 'tagged_task',
            'args': [],
            'kwargs': {},
            'eta': '2022-05-27T00:00:00.000000+0300',
            'tag': 'some-scope_123',
        },
    ],
)
async def test_queues_api_add_not_bad_request(
        taxi_stq_agent, request_body, mongodb, stqs,
):
    response = await taxi_stq_agent.post(
        'queues/api/add/azaza11', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}

    added_task = None
    for shard_id in range(2):
        added_task = stqs.get_shard('azaza11', shard_id).get_task(
            request_body['task_id'],
        )
        if added_task is not None:
            break

    assert added_task is not None
    assert added_task['_id'] == request_body['task_id']
    assert added_task['a'] == request_body['args']
    eta_tstz = dateutil.parser.parse(request_body['eta'])
    eta_double_sec = (
        eta_tstz - datetime.datetime.fromtimestamp(0, tz=eta_tstz.tzinfo)
    ).total_seconds()
    assert added_task['e'] == eta_double_sec
    assert added_task['e_dup'] == eta_double_sec


async def test_queues_api_add_wrong_cluster(taxi_stq_agent):
    request_body = {
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }

    response = await taxi_stq_agent.post(
        'queues/api/add/queue_wrong_cluster', json=request_body,
    )
    assert response.status_code == 200
    assert response.headers['X-Redirect-Queue-Cluster'] == 'not-stq-agent'


async def test_queues_api_add_bulk(taxi_stq_agent, stqs):
    request_body = {
        'tasks': [
            {
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'task_id': 'ololo2',
                'args': ['1', '2', '3'],
                'kwargs': {1: 2, 3: 4},
                'eta': '2018-12-01T14:00:01.123456+0300',
            },
            {
                'task_id': 'ololo3',
                'args': [],
                'kwargs': {},
                'eta': '2018-12-1T14:00:1Z',
            },
        ],
    }
    response = await taxi_stq_agent.post(
        'queues/api/add/azaza11/bulk', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert (
        sorted(response.json()['tasks'], key=operator.itemgetter('task_id'))
        == [
            {'task_id': 'ololo1', 'add_result': {'code': 200}},
            {'task_id': 'ololo2', 'add_result': {'code': 200}},
            {'task_id': 'ololo3', 'add_result': {'code': 200}},
        ]
    )

    for item in request_body['tasks']:
        added_task = None
        for shard_id in range(2):
            added_task = stqs.get_shard('azaza11', shard_id).get_task(
                item['task_id'],
            )
            if added_task is not None:
                break

        assert added_task is not None
        assert added_task['_id'] == item['task_id']
        assert added_task['a'] == item['args']
        eta_tstz = dateutil.parser.parse(item['eta'])
        eta_double_sec = (
            eta_tstz - datetime.datetime.fromtimestamp(0, tz=eta_tstz.tzinfo)
        ).total_seconds()
        assert added_task['e'] == eta_double_sec
        assert added_task['e_dup'] == eta_double_sec


async def test_queues_api_add_bulk_wrong_cluster(taxi_stq_agent, stqs):
    request_body = {
        'tasks': [
            {
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'task_id': 'ololo2',
                'args': ['1', '2', '3'],
                'kwargs': {1: 2, 3: 4},
                'eta': '2018-12-01T14:00:01.123456+0300',
            },
            {
                'task_id': 'ololo3',
                'args': [],
                'kwargs': {},
                'eta': '2018-12-1T14:00:1Z',
            },
        ],
    }
    response = await taxi_stq_agent.post(
        'queues/api/add/queue_wrong_cluster_bulk/bulk',
        json=request_body,
        headers=HEADERS,
    )
    assert response.headers['X-Redirect-Queue-Cluster'] == 'not-stq-agent'
    assert response.status_code == 200
    assert (
        sorted(response.json()['tasks'], key=operator.itemgetter('task_id'))
        == [
            {'task_id': 'ololo1', 'add_result': {'code': 200}},
            {'task_id': 'ololo2', 'add_result': {'code': 200}},
            {'task_id': 'ololo3', 'add_result': {'code': 200}},
        ]
    )

    for item in request_body['tasks']:
        added_task = None
        for shard_id in range(2):
            added_task = stqs.get_shard(
                'queue_wrong_cluster_bulk', shard_id,
            ).get_task(item['task_id'])
            if added_task is not None:
                break

        assert added_task is not None
        assert added_task['_id'] == item['task_id']
        assert added_task['a'] == item['args']
        eta_tstz = dateutil.parser.parse(item['eta'])
        eta_double_sec = (
            eta_tstz - datetime.datetime.fromtimestamp(0, tz=eta_tstz.tzinfo)
        ).total_seconds()
        assert added_task['e'] == eta_double_sec
        assert added_task['e_dup'] == eta_double_sec


async def test_queues_api_add_bulk_failed(taxi_stq_agent, mongodb, stqs):
    request_body = {'tasks': [{}]}
    response = await taxi_stq_agent.post(
        'queues/api/add/azaza11/bulk', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 400


async def test_queues_api_add_bulk_internal_fail(
        taxi_stq_agent, mongodb, stqs, testpoint,
):
    request_body = {
        'tasks': [
            {
                'task_id': 'ololo1',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            {
                'task_id': 'ololo2',
                'args': [],
                'kwargs': {},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
        ],
    }

    @testpoint('stq_shard::add_task')
    async def _add_task(data):
        if data['task_id'] == 'ololo2':
            return {'inject_failure': True}
        return {}

    response = await taxi_stq_agent.post(
        'queues/api/add/azaza11/bulk', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    tasks = sorted(
        response.json()['tasks'], key=operator.itemgetter('task_id'),
    )
    assert tasks[0] == {'task_id': 'ololo1', 'add_result': {'code': 200}}
    assert tasks[1]['task_id'] == 'ololo2'
    assert tasks[1]['add_result']['code'] == 500
    assert tasks[1]['add_result']['description']


async def test_queues_api_add_bulk_queue_not_found(
        taxi_stq_agent, mongodb, stqs, testpoint,
):
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
        'queues/api/add/non_existing_queue/bulk',
        json=request_body,
        headers=HEADERS,
    )
    assert response.status_code == 404
