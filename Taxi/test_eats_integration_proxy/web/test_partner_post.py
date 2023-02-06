async def test_create_partner(web_app_client, web_context):
    data = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'http',
        'host': 'test.test',
        'port': 80,
        'login': 'test_login',
    }

    response = await web_app_client.post('/partner', json=data)
    assert response.status == 200

    sql, binds = web_context.sqlt.partner_get_all()
    rows = await web_context.pg.master.fetch(sql, *binds)

    assert len(rows) == 1
    row = rows[0]
    for secret_key in {'login', 'password', 'token'}:
        post_value = data.get(secret_key)
        if post_value is None:
            assert row[secret_key] is None
        else:
            assert row[secret_key] != post_value
    for key in {'brand_id', 'slug', 'protocol', 'host', 'port'}:
        assert row[key] == data[key]


async def test_conflict_create_partner(web_app_client):
    data = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'http',
        'host': 'test.test',
        'port': 80,
        'login': 'test_login',
    }

    response = await web_app_client.post('/partner', json=data)
    assert response.status == 200
    response = await web_app_client.post('/partner', json=data)
    assert response.status == 409
