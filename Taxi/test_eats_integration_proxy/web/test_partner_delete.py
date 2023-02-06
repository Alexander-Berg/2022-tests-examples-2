async def test_delete_partner(web_app_client, web_context):
    data = {
        'brand_id': 'test_brand_id',
        'slug': 'test_slug',
        'protocol': 'http',
        'host': 'test.test',
        'port': 80,
        'token': 'test_token',
    }

    response = await web_app_client.post('/partner', json=data)
    assert response.status == 200
    inserted_id = (await response.json())['id']

    response = await web_app_client.delete(
        '/partner', params={'id': inserted_id},
    )
    assert response.status == 200

    sql, binds = web_context.sqlt.partner_get_all()
    rows = await web_context.pg.master.fetch(sql, *binds)
    assert not rows


async def test_delete_nonexistent(web_app_client):
    response = await web_app_client.delete('/partner', params={'id': 0})
    assert response.status == 404
