from grabber.generated.service.swagger.models import api


async def test_get_tasks_by_empty_filter(web_app_client):
    response = await web_app_client.get('/v1/tasks/data-request-types')
    assert response.status == 200

    response_json = await response.json()
    api.TaskDataRequestTypesResponse.deserialize(response_json)
