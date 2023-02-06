import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Арск'),
        pytest.param(
            'geonodes',
            [
                {'name': 'br_moscow', 'type': 'agglomeration'},
                {'name': 'br_vladivostok', 'type': 'agglomeration'},
                {'name': 'br_arsk', 'type': 'agglomeration'},
            ],
        ),
    ],
)
async def test_get_polygons_list(web_app_client, key, value):
    request_json = {'user': 'vladivostok_user', key: value}
    response = await web_app_client.post(
        '/api/polygons/list', json=request_json,
    )
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])
    assert content == [
        {
            '_id': '59cb5ead8d8d141a4f9fe7dd',
            'city': 'Москва',
            'name': '__default__',
        },
        {
            '_id': '5e9efcfae280e46e8ae00a09',
            'city': ['Москва', 'Казань', 'Владивосток'],
            'name': 'many_cities',
        },
        {
            '_id': '5bc06be494c1420934994ab4',
            'city': 'Владивосток',
            'name': 'pol1',
        },
    ]


async def test_get_polygons_list_all_default(web_app_client):
    response = await web_app_client.post('/api/polygons/list', json={})
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])

    assert len(content) == 2
    assert content[0]['name'] == '__default__'
    assert content[1]['name'] == 'many_cities'


async def test_get_polygons_list_all_for_user(web_app_client):
    request_json = {'user': 'kazan_user'}
    response = await web_app_client.post(
        '/api/polygons/list', json=request_json,
    )
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['name'])

    assert len(content) == 3
    assert content[0]['name'] == '__default__'
    assert content[1]['name'] == 'many_cities'
    assert content[2]['name'] == 'megak'
