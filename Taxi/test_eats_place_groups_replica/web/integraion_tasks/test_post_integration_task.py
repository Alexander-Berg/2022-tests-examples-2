import uuid

from eats_place_groups_replica.internal import entities


async def test_post_task(web_app_client, mock_processing, stq):
    request_data = {
        'id': uuid.uuid4().hex,
        'type': 'price',
        'place_id': uuid.uuid4().hex,
    }

    with stq.flushing():
        response = await web_app_client.post('/v1/tasks', json=request_data)

        assert response.status == 200
        response_data = await response.json()
        assert {**request_data, 'status': 'created'} == response_data

        assert stq.eats_place_groups_replica_create_task.has_calls
        task = stq.eats_place_groups_replica_create_task.next_call()
        assert task['kwargs']['task'] == request_data
        assert stq.is_empty


async def test_post_with_response_409(web_app_client):

    exist_task_id = 'task'

    request_data = {
        'id': exist_task_id,
        'type': 'price',
        'place_id': 'place_id__1',
    }

    response = await web_app_client.post('/v1/tasks', json=request_data)
    response_data = await response.json()
    assert response.status == 409
    assert response_data['status'] == entities.StatusTask.FINISHED.value
