async def test_create(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post('/v1/resume', json=reqdata)
    assert response.status == 200
    content = await response.json()
    assert content['resume_id'] == 1


async def test_duplicate(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post('/v1/resume', json=reqdata)
    for _ in range(3):
        response = await web_app_client.post('/v1/resume', json=reqdata)
    content = await response.json()
    assert response.status == 409
    assert content['code'] == 'RESUME_ALREADY_EXISTS'
