import pymongo.errors
import pytest


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_remove_all_tasks_200(stq_db, web_app_client):
    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'test_queue',
            'dev_team': 'some_team',
            'tasks_type': 'all',
        },
    )
    assert response.status == 200, await response.text()

    for shard in stq_db.iter_shards():
        docs = {doc['_id'] for doc in await shard.find({}).to_list(None)}
        assert not docs


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_remove_failed_tasks_200(stq_db, web_app_client):
    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'test_queue',
            'dev_team': 'some_team',
            'tasks_type': 'failed',
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'removed_tasks_count': 3}

    expected_tasks = [{'task_id1', 'task_id3'}, {'task_id5'}]

    for shard, expected_tasks in zip(stq_db.iter_shards(), expected_tasks):
        docs = {doc['_id'] for doc in await shard.find({}).to_list(None)}
        assert docs == expected_tasks


@pytest.mark.now('2022-07-07T14:00:00.0')
@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_remove_abandoned_tasks_200(stq_db, web_app_client):
    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'test_queue',
            'dev_team': 'some_team',
            'tasks_type': 'abandoned',
            'abandoned_timeout': 60,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {'removed_tasks_count': 2}

    expected_tasks = [{'task_id2', 'task_id3'}, {'task_id4', 'task_id6'}]

    for shard, expected_tasks in zip(stq_db.iter_shards(), expected_tasks):
        docs = {doc['_id'] for doc in await shard.find({}).to_list(None)}
        assert docs == expected_tasks


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_remove_all_tasks_with_errors(stq_db, web_app_client, patch):
    @patch('motor.motor_asyncio.AsyncIOMotorCollection.drop')
    async def _drop(*args, **kwargs):
        raise pymongo.errors.PyMongoError('Something bad happened')

    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'test_queue',
            'dev_team': 'some_team',
            'tasks_type': 'all',
        },
    )
    assert response.status == 500
    assert (await response.json()) == {
        'code': 'internal-error',
        'message': 'Errors occurred while removing tasks',
        'details': [
            {
                'shard': 'dbstq.test_queue_0',
                'error_msg': 'Removal failed: Something bad happened',
            },
            {
                'shard': 'dbstq.test_queue_1',
                'error_msg': 'Removal failed: Something bad happened',
            },
        ],
    }


async def test_bulk_remove_tasks_400(web_app_client):
    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'test_queue',
            'dev_team': 'some_wrong_team',
            'tasks_type': 'all',
        },
    )
    assert response.status == 400
    assert (await response.json())['message'] == (
        'Queue test_queue does not belong to the dev team '
        'some_wrong_team provided in request'
    )


async def test_remove_tasks_without_tasks_type_400(web_app_client):
    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={'queue_name': 'test_queue', 'dev_team': 'some_team'},
    )
    assert response.status == 400
    assert (await response.json())['message'] == 'Some parameters are invalid'


@pytest.mark.parametrize(
    'queue, namespace',
    [('with_tplatform', 'lavka'), ('without_tplatform', None)],
)
async def test_check_remove_all_tasks_with_tplatform(
        web_app_client, queue, namespace,
):
    data = {
        'queue_name': queue,
        'dev_team': 'some_team',
        'tasks_type': 'failed',
    }
    response = await web_app_client.post('/tasks/remove_all/check/', json=data)
    assert response.status == 200
    result = await response.json()
    assert result.get('tplatform_namespace') == namespace
    assert result.get('data') == data
