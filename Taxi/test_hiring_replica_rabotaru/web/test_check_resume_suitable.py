async def test_check_not_suitable(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post(
        '/v1/resume/is_suitable', json=reqdata,
    )
    assert response.status == 200
    content = await response.json()
    assert not content['is_suitable']


async def test_check_suitable(web_app_client, load_json):
    reqdata = load_json('suitable.json')
    response = await web_app_client.post(
        '/v1/resume/is_suitable', json=reqdata,
    )
    assert response.status == 200
    content = await response.json()
    assert content['is_suitable']
