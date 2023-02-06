import bson


async def test_update_polygon(web_app_client, db, test_polygon):
    polygon = await db.atlas_polygons.find_one(
        {'_id': bson.ObjectId(test_polygon['_id'])},
    )
    assert polygon['name'] == 'pol1'

    test_polygon['name'] = 'pol2'

    response = await web_app_client.post(
        '/api/polygons/update', json=test_polygon,
    )
    assert response.status == 200

    content = await response.json()
    assert content['code'] == 0
    assert content['desc'] == 'ok'

    changed_polygon = await db.atlas_polygons.find_one(
        {'_id': bson.ObjectId(test_polygon['_id'])},
    )
    changed_polygon['_id'] = str(changed_polygon['_id'])

    assert changed_polygon == test_polygon
