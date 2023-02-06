async def test_get_polygons_data(web_app_client, test_polygon):
    response = await web_app_client.post(
        '/api/polygons/data',
        json={
            '_ids': [
                '5bc06be494c1420934994ab4',
                '5aa6655d8d8d1404a30ff44b',
                '5bc06be494c1420934994ab3',  # nonexistent _id
                '5e9efcfae280e46e8ae00a09',  # default user polygon
            ],
            'user': 'vladivostok_user',
        },
    )
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])
    assert len(content) == 2
    assert content[0]['name'] == 'many_cities'
    assert content[1] == test_polygon


async def test_get_polygons_data_all_ids(web_app_client):
    response = await web_app_client.post('/api/polygons/data', json={})
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])
    assert len(content) == 2  # get polygons with __default__ user
