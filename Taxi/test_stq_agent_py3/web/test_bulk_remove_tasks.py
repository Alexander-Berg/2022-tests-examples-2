import pymongo.errors
import pytest


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_bulk_remove_tasks_200(stq_db, web_app_client):
    to_remove = ['task_id', 'some_other_task_id', 'already_removed_task_id']
    response = await web_app_client.post(
        '/tasks/bulk_remove/',
        json={
            'queue_name': 'test_queue',
            'task_ids': to_remove,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 200
    body = await response.json()
    assert body['status'] == 'partially_completed'
    assert body['errors'] == [
        {'id': 'already_removed_task_id', 'error_msg': 'not_found'},
    ]

    for shard in stq_db.iter_shards():
        docs = {
            doc['_id']
            for doc in await shard.find({'_id': {'$in': to_remove}}).to_list(
                None,
            )
        }
        for doc_id in to_remove:
            assert doc_id not in docs


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_bulk_remove_tasks_404(stq_db, web_app_client):
    to_remove = ['already_removed_task_id']
    response = await web_app_client.post(
        '/tasks/bulk_remove/',
        json={
            'queue_name': 'test_queue',
            'task_ids': to_remove,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 404
    response = await web_app_client.post(
        '/tasks/bulk_remove/',
        json={
            'queue_name': 'non_existent_queue',
            'task_ids': to_remove,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 404


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'test_queue_0'),
        ('stq', 'dbstq', 'test_queue_1'),
    ],
)
async def test_bulk_remove_tasks_500(stq_db, web_app_client, patch):
    to_remove = ['task_id']

    @patch('motor.motor_asyncio.AsyncIOMotorCollection.delete_one')
    async def _delete_one(query, *args, **kwargs):
        raise pymongo.errors.PyMongoError('Something bad happened')

    response = await web_app_client.post(
        '/tasks/bulk_remove/',
        json={
            'queue_name': 'test_queue',
            'task_ids': to_remove,
            'dev_team': 'some_team',
        },
    )
    assert response.status == 500
    assert (await response.json())['details'] == [
        {
            'id': 'task_id',
            'error_msg': 'Removal failed: Something bad happened',
        },
    ]


async def test_bulk_remove_tasks_400(web_app_client):
    response = await web_app_client.post(
        '/tasks/bulk_remove/',
        json={
            'queue_name': 'test_queue',
            'task_ids': ['task_id'],
            'dev_team': 'some_wrong_team',
        },
    )
    assert response.status == 400
    assert (await response.json())['message'] == (
        'Queue test_queue does not belong to the dev team '
        'some_wrong_team provided in request'
    )


@pytest.mark.parametrize(
    'queue, namespace',
    [('with_tplatform', 'lavka'), ('without_tplatform', None)],
)
async def test_check_bulk_remove_with_tplatform(
        web_app_client, queue, namespace,
):
    data = {'queue_name': queue, 'task_ids': ['lala'], 'dev_team': 'some_team'}
    response = await web_app_client.post(
        '/tasks/bulk_remove/check/', json=data,
    )
    assert response.status == 200
    result = await response.json()
    assert result.get('tplatform_namespace') == namespace
    assert result.get('data') == data
