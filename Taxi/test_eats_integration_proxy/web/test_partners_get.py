from eats_integration_proxy.internal import crypt


async def test_post_and_get_partners(web_app_client, web_context):
    brand_id = 'test_brand_id'
    brand_data = [
        {
            'brand_id': brand_id,
            'slug': 'slug_1',
            'protocol': 'http',
            'host': 'test.test',
            'port': 80,
            'login': 'test_login',
        },
        {
            'brand_id': brand_id,
            'slug': 'slug_2',
            'protocol': 'https',
            'host': 'test.test',
            'port': 443,
            'password': 'test_password',
        },
    ]
    requests_data = brand_data + [
        {
            'brand_id': 'test_brand_id_2',
            'slug': 'slug_1',
            'protocol': 'https',
            'host': 'test.test',
            'port': 443,
            'password': 'test_password',
        },
    ]

    for data in requests_data:
        response = await web_app_client.post('/partner', json=data)
        assert response.status == 200

    response = await web_app_client.get(
        '/partners', params={'brand_id': brand_id},
    )
    assert response.status == 200

    response_partners = (await response.json())['partners']

    for request_data, response_data in zip(brand_data, response_partners):
        for field in ('brand_id', 'slug', 'protocol', 'host', 'port'):
            assert request_data[field] == response_data[field]
        for field in ('login', 'password', 'token'):
            if request_data.get(field):
                assert response_data[field] == crypt.SECRET_MASK
