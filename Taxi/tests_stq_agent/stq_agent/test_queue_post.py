import datetime
import json

import bson
import dateutil.parser
import pytest

from tests_plugins import utils

from tests_stq_agent.stq_agent import utils as test_utils

HEADERS = {'X-YaTaxi-API-Key': 'InferniaOverkill'}


@pytest.mark.parametrize(
    'request_body, expected_response_message',
    [
        ({}, 'Request BSON does not contain some of the required fields'),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
                'Infernia': 'Overkill',
            },
            'Request BSON contains an unexpected field',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'etata': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON contains an unexpected field',
        ),
        (
            '{'
            '    "queue_name": "azaza",'
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
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 100500,
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Field \'queue_name\' is of a wrong type. Expected: UTF8, actual: '
            'INT32',
        ),
        (
            {
                'queue_name': 'azaza',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 100500,
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Field \'task_id\' is of a wrong type. Expected: UTF8, actual: '
            'INT32',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': {'a': 'b'},
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Malformed request BSON: args is not an array',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': ['a', 'b', 'c'],
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Malformed request BSON: kwargs is not a document',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
            },
            'Request BSON does not contain some of the required fields',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': '2018.12.01T14:00:01.123456Z',
            },
            'Can\'t parse datetime: 2018.12.01T14:00:01.123456Z',
        ),
        (
            {
                'queue_name': 'azaza',
                'task_id': 'ololo',
                'args': [1, 2, 3],
                'kwargs': {'a': {'b': 'c'}, 'd': 1},
                'eta': 100500,
            },
            'Field \'eta\' is of a wrong type. Expected: UTF8, actual: INT32',
        ),
        (
            {
                'queue_name': 'azaza11',
                'task_id': 'ololo2',
                'args': [1, 2, 3],
                'kwargs': {'a': {'$b': 'c'}, 'd': 1},
                'eta': '2018-12-01T14:00:01.123456Z',
            },
            'Error updating documents: The dollar ($) prefixed field \'$b\' '
            'in \'k.a.$b\' is not valid for storage.',
        ),
    ],
)
async def test_queue_post_bad_request(
        taxi_stq_agent, request_body, expected_response_message, db_extra,
):
    expected_response_body = {
        'code': '400',
        'message': expected_response_message,
    }

    response = await taxi_stq_agent.post(
        'queue',
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
            'queue_name': 'azaza11',
            'task_id': 'ololo1',
            'args': [1, 2, 3],
            'kwargs': {'a': {'b': 'c'}, 'd': 1},
            'eta': '2018-12-01T14:00:01.123456Z',
        },
        {
            'queue_name': 'azaza11',
            'task_id': 'ololo2',
            'args': ['1', '2', '3'],
            'kwargs': {1: 2, 3: 4},
            'eta': '2018-12-01T14:00:01.123456+0300',
        },
        {
            'queue_name': 'azaza11',
            'task_id': 'ololo3',
            'args': [],
            'kwargs': {},
            'eta': '2018-12-1T14:00:1Z',
        },
    ],
)
async def test_queue_post_not_bad_request(taxi_stq_agent, request_body):
    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_queue_post_wrong_cluster(taxi_stq_agent):
    request_body = {
        'queue_name': 'queue_wrong_cluster_1',
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }

    response = await taxi_stq_agent.post('queue', json=request_body)
    assert response.status_code == 200
    assert response.headers['X-Redirect-Queue-Cluster'] == 'not-stq-agent'


@pytest.mark.parametrize(
    'queue_num, eta',
    [('1', '2018-12-01T14:00:01.123456Z'), ('2', '2010-10-01T14:00:00Z')],
)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post(
        taxi_stq_agent, now, mongodb, db_extra, queue_num, eta,
):
    queue_name = 'azaza1{}'.format(queue_num)
    task_id = 'ololo{}'.format(queue_num)

    request_body = {
        'queue_name': queue_name,
        'task_id': task_id,
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': eta,
    }

    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}

    test_utils.check_mongo(
        mongodb,
        db_extra,
        [test_utils.make_expected_task(request_body, now)],
        request_body['queue_name'],
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_lxc_multi_mongo(
        taxi_stq_agent, now, mongodb, db_extra, taxi_config,
):
    queue_name = 'simple_queue'
    task_id = 'ololo1'

    request_body = {
        'queue_name': queue_name,
        'task_id': task_id,
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }

    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}

    test_utils.check_mongo(
        mongodb,
        db_extra,
        [test_utils.make_expected_task(request_body, now)],
        request_body['queue_name'],
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_bson_types(taxi_stq_agent, now, mongodb, db_extra):
    request_body = {
        'queue_name': 'azaza11',
        'task_id': 'ololo1',
        'args': [{'$oid': '507f1f77bcf86cd799439011'}],
        'kwargs': {
            'a': {'b': 'c', 'd': {'$date': '2018-12-27T16:38:00.123Z'}},
            'e': 1,
        },
        'eta': '2018-12-01T14:00:01.123456Z',
    }

    expected_task = test_utils.make_expected_task(request_body, now)
    expected_task['a'][0] = bson.ObjectId(expected_task['a'][0]['$oid'])
    expected_task['k']['a']['d'] = utils.to_utc(
        dateutil.parser.parse(expected_task['k']['a']['d']['$date']),
    )

    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
    test_utils.check_mongo(
        mongodb, db_extra, [expected_task], request_body['queue_name'],
    )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_reset_task(
        taxi_stq_agent, now, mongodb, db_extra, mocked_time,
):
    request_body = {
        'queue_name': 'azaza11',
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
    }
    eta_str = '2018-12-01T14:00:31.12345{}Z'

    for request, expect in ((6, 6), (7, 6), (5, 5), (6, 5)):
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        await taxi_stq_agent.tests_control(invalidate_caches=False)

        request_body['eta'] = eta_str.format(request)

        expected_task = test_utils.make_expected_task(request_body, now)
        expected_eta = test_utils.to_msec_from_epoch(eta_str.format(expect))
        expected_task['e'] = expected_eta
        expected_task['e_dup'] = expected_eta

        response = await taxi_stq_agent.post(
            'queue', json=request_body, headers=HEADERS,
        )
        assert response.status_code == 200
        assert response.json() == {}
        test_utils.check_mongo(
            mongodb, db_extra, [expected_task], request_body['queue_name'],
        )


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_config_change(
        taxi_stq_agent, now, mongodb, db_extra, mocked_time,
):
    request_body = {
        'queue_name': 'azaza11',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:59:01.123456Z',
    }
    task_id = 'ololo{}'

    shards = [
        [
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_0',
                'hosts': [],
            },
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_1',
                'hosts': [],
            },
        ],
        [
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_0',
                'hosts': [],
            },
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_2',
                'hosts': [],
            },
        ],
        [
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_2',
                'hosts': [],
            },
        ],
        [
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_3',
                'hosts': [],
            },
            {
                'connection': 'stq11',
                'database': 'db',
                'collection': 'azaza11_4',
                'hosts': [],
            },
        ],
    ]

    tasks_count = 5

    for i, shard_i in enumerate(shards):
        now += datetime.timedelta(seconds=1)
        mongodb.stq_config.update(
            {'_id': 'azaza11'},
            {
                '$set': {
                    'shards': shard_i,
                    'updated': utils.to_utc(
                        dateutil.parser.parse(now.isoformat()),
                    ),
                },
            },
            upsert=True,
        )
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        await taxi_stq_agent.invalidate_caches()

        for j in range(tasks_count):
            request_body['task_id'] = task_id.format(str(j))
            response = await taxi_stq_agent.post(
                'queue', json=request_body, headers=HEADERS,
            )
            assert response.status_code == 200
            assert response.json() == {}

        for j, shard_j in enumerate(shards):
            if j == i:
                count = 0
                for shard in shard_j:
                    collection = db_extra.shard_collection(shard)
                    count += collection.count()
                assert count == tasks_count
            else:
                test_utils.check_empty_queue(db_extra, shard_j, shard_i)

        for shards_case in shards:
            for shard in shards_case:
                collection = db_extra.shard_collection(shard)
                collection.remove({})


@pytest.mark.parametrize(
    'queue_num, expected_response_status_code, expected_response_message',
    [('3', 404, 'Config for stq \'azaza13\' not found'), ('4', 500, None)],
)
async def test_queue_post_fail(
        taxi_stq_agent,
        queue_num,
        expected_response_status_code,
        expected_response_message,
):
    queue_name = 'azaza1{}'.format(queue_num)

    request_body = {
        'queue_name': queue_name,
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:01.123456Z',
    }

    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == expected_response_status_code
    if expected_response_message:
        assert response.json()['message'] == expected_response_message


@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_config_update_fail(
        taxi_stq_agent, now, mongodb, db_extra, mocked_time,
):
    queue_name = 'azaza15'

    shards = mongodb.stq_config.find_one(queue_name)['shards']

    await taxi_stq_agent.invalidate_caches()

    mongodb.stq_config.update(
        {'_id': queue_name},
        {
            '$set': {
                'shards': [
                    {
                        'connection': 'stq100500',
                        'database': 'db',
                        'collection': 'azaza15_1',
                        'hosts': [],
                    },
                ],
                'updated': utils.to_utc(
                    dateutil.parser.parse('2018-12-01T14:00:01Z'),
                ),
            },
        },
        upsert=True,
    )

    now += datetime.timedelta(seconds=2)
    mocked_time.set(now)
    await taxi_stq_agent.invalidate_caches()

    request_body = {
        'queue_name': queue_name,
        'task_id': 'ololo1',
        'args': [1, 2, 3],
        'kwargs': {'a': {'b': 'c'}, 'd': 1},
        'eta': '2018-12-01T14:00:03.123456Z',
    }

    response = await taxi_stq_agent.post(
        'queue', json=request_body, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}
    test_utils.check_queue_with_tasks(
        db_extra, shards, [test_utils.make_expected_task(request_body, now)],
    )


async def test_queue_post_mongo_limits_ok(taxi_stq_agent, testpoint):
    def get_request(queue_name, task_id):
        return {
            'queue_name': queue_name,
            'task_id': task_id,
            'args': [],
            'kwargs': {},
            'eta': '2018-12-01T14:00:01.123456Z',
        }

    called = False

    @testpoint('stq_shard::add_task')
    async def _add_task(data):
        nonlocal called
        if not called:
            called = True
            response = await taxi_stq_agent.post(
                'queue', json=get_request('azaza12', 'task2'),
            )
            assert response.status_code == 200

    response = await taxi_stq_agent.post(
        'queue', json=get_request('azaza11', 'task1'),
    )
    assert response.status_code == 200


@pytest.mark.config(STQ_AGENT_MONGO_POOL_LIMIT=1)
@pytest.mark.config(STQ_AGENT_MONGO_POOL_LIMIT_TIMEOUT_MS=1)
async def test_queue_post_mongo_limits_fail(taxi_stq_agent, testpoint):
    def get_request(queue_name, task_id):
        return {
            'queue_name': queue_name,
            'task_id': task_id,
            'args': [],
            'kwargs': {},
            'eta': '2018-12-01T14:00:01.123456Z',
        }

    called = False

    @testpoint('stq_shard::add_task')
    async def _add_task(data):
        nonlocal called
        assert not called
        called = True
        response = await taxi_stq_agent.post(
            'queue', json=get_request('azaza11', 'task2'),
        )
        assert response.status_code == 500

    response = await taxi_stq_agent.post(
        'queue', json=get_request('azaza11', 'task1'),
    )
    assert response.status_code == 200


@pytest.mark.config(STQ_AGENT_MONGO_POOL_LIMIT_TIMEOUT_MS=1)
@pytest.mark.now('2018-12-01T14:00:00Z')
async def test_queue_post_mongo_limits_change(
        taxi_stq_agent, taxi_config, testpoint, mocked_time,
):
    def get_request(queue_name, task_id):
        return {
            'queue_name': queue_name,
            'task_id': task_id,
            'args': [],
            'kwargs': {},
            'eta': '2018-12-01T14:00:01.123456Z',
        }

    for i in range(1, 4):

        def _get_task_id(num, i=i):
            return 'task{}{}'.format(i, num)

        taxi_config.set(STQ_AGENT_MONGO_POOL_LIMIT=i)
        mocked_time.sleep(10)
        await taxi_stq_agent.invalidate_caches()

        called_count = 1

        @testpoint('stq_shard::add_task')
        async def _add_task(data, i=i):
            nonlocal called_count

            assert called_count <= i

            called_count += 1
            response = await taxi_stq_agent.post(
                'queue',
                json=get_request('azaza11', _get_task_id(called_count)),
            )
            expected_status_code = 200 if called_count <= i else 500
            assert response.status_code == expected_status_code
            called_count -= 1

        response = await taxi_stq_agent.post(
            'queue', json=get_request('azaza11', _get_task_id(called_count)),
        )
        assert response.status_code == 200


async def test_queue_post_reset_rc(taxi_stq_agent, stqs):
    stq_shard = stqs.get_shard('simple_queue', 0)

    stq_shard.add_task('task', rc=100500)

    response = await taxi_stq_agent.post(
        'queue',
        json={
            'queue_name': 'simple_queue',
            'task_id': 'task',
            'args': [],
            'kwargs': {},
            'eta': '2019-10-29T17:15:00Z',
        },
    )
    assert response.status_code == 200

    task = stq_shard.get_task('task')
    assert 'rc' not in task
