import uuid


async def test_get(web_app_client, load_json, create_workflow, get_workflow):
    data = load_json('workflow.json')
    data['request_id'] = uuid.uuid4().hex
    exists = await create_workflow(data)
    workflow = await get_workflow(exists['workflow_id'])
    assert workflow['workflow_id'] == exists['workflow_id']


async def test_not_exists(web_app_client):
    data = {'workflow_id': uuid.uuid4().hex}
    response = await web_app_client.get('/v1/workflow', params=data)
    assert response.status == 404, await response.text()
    content = await response.json()
    assert content['code'] == 'WORKFLOW_NOT_FOUND'


async def test_required(web_app_client):
    data = {}
    response = await web_app_client.get('/v1/workflow', params=data)
    assert response.status == 400, await response.text()
