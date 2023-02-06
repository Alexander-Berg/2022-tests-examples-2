async def test_cursor(web_app_client, load_json):
    reqdata = load_json('resumes_chunk.json')
    for item in reqdata:
        await web_app_client.post('/v1/resume', json=item)

    params = {'cursor': 1}
    response = await web_app_client.get('/v1/resumes', params=params)
    assert response.status == 200
    content = await response.json()
    assert content['cursor'] == '2'
    assert len(content['resumes']) == 2
