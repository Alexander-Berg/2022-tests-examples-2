import bson


async def test_delete_polygon(web_app_client, db, test_polygon):
    assert await db.atlas_polygons.find_one(
        {'_id': bson.ObjectId(test_polygon['_id'])},
    )
    response = await web_app_client.post(
        '/api/polygons/delete', json={'_id': test_polygon['_id']},
    )
    assert response.status == 200

    content = await response.json()
    assert content['code'] == 0
    assert content['desc'] == 'ok'

    assert not await db.atlas_polygons.find_one(
        {'_id': bson.ObjectId(test_polygon['_id'])},
    )
