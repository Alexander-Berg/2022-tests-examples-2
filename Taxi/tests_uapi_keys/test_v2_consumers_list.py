ENDPOINT_URL = '/v2/consumers/list'


async def test_ok(taxi_uapi_keys, load_json):
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL, headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('response.json')
