import json

import pytest

import atlas_backend.internal.geo_hierarchy as geo_lib


@pytest.mark.parametrize('username', ['test_user1', 'test_user2'])
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'hierarchy_type, expected_data_path',
    [('br', 'test_br_data.json'), ('fi', 'test_fi_data.json')],
)
async def test_get_geohierarchy(
        web_app_client,
        atlas_blackbox_mock,
        username,
        open_file,
        hierarchy_type,
        expected_data_path,
):
    response = await web_app_client.get(
        '/api/atlas/geo_hierarchy', params={'hierarchy_type': hierarchy_type},
    )
    assert response.status == 200
    items = (await response.json())['items']
    items_sorted = sorted(items, key=lambda x: x['node_id'])
    with open_file(expected_data_path) as fin:
        test_data = json.load(fin)
    expected = sorted(
        test_data['COMMON'] + test_data[username], key=lambda x: x['node_id'],
    )
    assert items_sorted == expected


@pytest.mark.parametrize('username', ['test_user1', 'test_user2'])
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_get_all_geohierarchy_nodes(
        web_app_client, atlas_blackbox_mock, username, open_file,
):
    response = await web_app_client.get('/api/atlas/geo_hierarchy')
    assert response.status == 200
    items = (await response.json())['items']
    items_sorted = sorted(items, key=lambda x: x['node_id'])
    with open_file('test_data.json') as fin:
        test_data = json.load(fin)
    expected = sorted(
        test_data['COMMON'] + test_data[username], key=lambda x: x['node_id'],
    )
    assert items_sorted == expected


@pytest.mark.parametrize(
    'parent_node, tariff_zones, expected',
    [
        [None, None, ['kolpino', 'moscow', 'spb']],
        [['br_saintpetersburg'], None, ['spb']],
        [['br_saintpetersburg'], ['kolpino'], ['kolpino', 'spb']],
        [None, ['kolpino'], ['kolpino']],
        [['br_saintpetersburg', 'br_moscow'], None, ['moscow', 'spb']],
        [['br_saintpetersburg'], None, ['spb']],
        [['fi_russia_macro'], None, ['kolpino', 'spb']],
    ],
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
async def test_tariff_zones(web_context, parent_node, tariff_zones, expected):
    result = await geo_lib.get_tariff_zones(
        web_context,
        'test_user1',
        parent_geo_nodes=parent_node,
        initial_tariff_zones=tariff_zones,
    )
    assert set(result) == set(expected)
