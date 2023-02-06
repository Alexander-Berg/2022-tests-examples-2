def sorted_requirements(source):
    return sorted(source, key=lambda req: req['name'])


async def test_get_all(web_app_client, load_json):
    expected_response = load_json('api_all_requirements.json')

    response = await web_app_client.get('/v2/all_requirements/')
    assert response.status == 200

    response_json = await response.json()
    assert sorted_requirements(response_json['data']) == sorted_requirements(
        expected_response['data'],
    )
