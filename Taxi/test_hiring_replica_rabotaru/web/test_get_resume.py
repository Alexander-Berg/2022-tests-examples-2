async def test_select(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post('/v1/resume', json=reqdata)
    assert response.status == 200
    content = await response.json()
    assert content['resume_id'] == 1

    params = {'resume_id': 1}
    response = await web_app_client.get('/v1/resume', params=params)
    assert response.status == 200
    content = await response.json()
    assert content['fields']


async def test_not_found(web_app_client):
    params = {'resume_id': 100}
    response = await web_app_client.get('/v1/resume', params=params)
    assert response.status == 404
    content = await response.json()
    assert content['code'] == 'RESUME_NOT_FOUND'


async def test_has_phones(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post('/v1/resume', json=reqdata)
    assert response.status == 200
    content = await response.json()
    assert content['resume_id'] == 1

    params = {'resume_id': 1, 'has_phones': 1}
    response = await web_app_client.get('/v1/resume', params=params)
    assert response.status == 200
