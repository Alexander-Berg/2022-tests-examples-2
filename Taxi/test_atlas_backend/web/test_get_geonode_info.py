import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_not_found(web_app_client):
    response = await web_app_client.get(
        '/api/atlas/geo_hierarchy/node_info',
        params={'hierarchy_type': 'br', 'node_id': 'not_existed'},
    )
    assert response.status == 404


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_geonode_info(web_app_client):
    response = await web_app_client.get(
        '/api/atlas/geo_hierarchy/node_info',
        params={'hierarchy_type': 'br', 'node_id': 'br_leningradskaja_obl'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'bounding_box': {
            'br': [59.54492029685772, 30.624719384271142],
            'tl': [59.98661270814935, 29.760368809658015],
        },
        'name_en': 'Leningrad Region',
        'name_ru': 'Ленинградская область',
        'node_id': 'br_leningradskaja_obl',
        'node_type': 'node',
        'parent_node_id': 'br_severo_zapadnyj_fo',
        'population_group': 'RU_SPB',
        'tariff_zones': ['spb', 'kolpino'],
        'timezone': 'Europe/Moscow',
    }
