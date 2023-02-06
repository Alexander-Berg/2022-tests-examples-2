async def test_update_partner(web_app_client, web_context):
    data_start = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'http',
        'host': 'test.test',
        'port': 80,
        'login': 'test_login',
    }

    response = await web_app_client.post('/partner', json=data_start)
    assert response.status == 200
    inserted_id = (await response.json())['id']

    data_update = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'https',
        'host': 'test_2.test',
        'port': 443,
    }
    response = await web_app_client.put(
        '/partner', json=data_update, params={'id': inserted_id},
    )
    assert response.status == 200

    sql, binds = web_context.sqlt.partner_get_all()
    rows = await web_context.pg.master.fetch(sql, *binds)

    assert len(rows) == 1
    row = rows[0]
    for key, value in data_update.items():
        if key not in {'login', 'password', 'token'}:
            assert row[key] == value
    delete_keys = set(data_start) - set(data_update)
    assert all(row[delete_key] is None for delete_key in delete_keys)
