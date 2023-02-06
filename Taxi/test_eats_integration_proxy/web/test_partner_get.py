from eats_integration_proxy.internal import crypt


async def test_post_and_get_partner(web_app_client, web_context):
    request_data = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'http',
        'host': 'test.test',
        'port': 80,
        'login': 'test_login',
        'token': 'test_token',
    }

    response = await web_app_client.post('/partner', json=request_data)
    assert response.status == 200
    inserted_id = (await response.json())['id']

    response = await web_app_client.get('/partner', params={'id': inserted_id})
    assert response.status == 200

    response_data = await response.json()

    for field in ('protocol', 'host', 'port'):
        assert request_data[field] == response_data[field]
    for field in ('login', 'password', 'token'):
        if request_data.get(field):
            assert response_data[field] == crypt.SECRET_MASK
