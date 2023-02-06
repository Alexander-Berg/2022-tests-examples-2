import pytest


async def test_create_polygon(web_app_client, test_polygon, db):
    polygon = await db.atlas_polygons.find_one({'name': 'new_name'})
    assert polygon is None

    del test_polygon['_id']
    test_polygon['name'] = 'new_name'
    response = await web_app_client.post(
        '/api/polygons/create', json=test_polygon,
    )
    assert response.status == 200

    content = await response.json()
    assert content['code'] == 0
    assert content['desc'] == 'ok'

    test_polygon['_id'] = content['_id']

    created_polygon = await db.atlas_polygons.find_one({'name': 'new_name'})
    created_polygon['_id'] = str(created_polygon['_id'])

    assert created_polygon == test_polygon


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_create_polygon_geo(web_app_client, test_polygon, db):
    polygon = await db.atlas_polygons.find_one({'name': 'new_name'})
    assert polygon is None

    del test_polygon['_id']
    test_polygon['name'] = 'new_name'
    del test_polygon['city']
    test_polygon['geonodes'] = [
        {'name': 'br_vladivostok', 'type': 'agglomeration'},
    ]
    response = await web_app_client.post(
        '/api/polygons/create', json=test_polygon,
    )
    assert response.status == 200

    content = await response.json()
    assert content['code'] == 0
    assert content['desc'] == 'ok'

    test_polygon['_id'] = content['_id']

    created_polygon = await db.atlas_polygons.find_one({'name': 'new_name'})
    created_polygon['_id'] = str(created_polygon['_id'])
    test_polygon['city'] = 'Владивосток'
    assert created_polygon == test_polygon
