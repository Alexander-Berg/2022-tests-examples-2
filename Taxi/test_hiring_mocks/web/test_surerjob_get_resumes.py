async def test_superjob_get_resumes(web_app_client):
    headers = {'X-Api-App-Id': 'client_secret', 'Authorization': 'oauth_token'}
    response = await web_app_client.get(
        path='/superjob-ru/2.0/resumes', headers=headers,
    )
    assert response.status == 200
    content = await response.json()
    assert content
