async def test_superjob_get_resumes(web_app_client, load_json):
    data = load_json('survey.json')
    headers = {'token': 'my_token', 'Content-Type': 'application/json'}
    response = await web_app_client.post(
        path='/infranaim-api/submit/test', headers=headers, json=data,
    )
    assert response.status == 200
    content = await response.json()
    assert content
