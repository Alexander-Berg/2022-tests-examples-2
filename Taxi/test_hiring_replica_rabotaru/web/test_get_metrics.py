async def test_metrics(web_app_client, load_json):
    reqdata = load_json('request.json')
    response = await web_app_client.post('/v1/resume', json=reqdata)
    assert response.status == 200
    content = await response.json()
    assert content['resume_id'] == 1

    response = await web_app_client.get('/v1/resumes/metrics')
    assert response.status == 200
    content = await response.json()

    assert content['created'] == 1
    assert content['is_suitable'] == 1
    assert content['has_phones'] == 1
    assert content['need_processing'] == 1
