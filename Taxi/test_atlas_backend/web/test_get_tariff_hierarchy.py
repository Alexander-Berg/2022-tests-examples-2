import json

import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=[
        'insert_geo_hierarchy_nodes.sql',
        'insert_tariff_hierarchy_nodes.sql',
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_result_file, use_default',
    [
        (
            {
                'geo_node': {'name': 'voronezh', 'type': 'tariff_zone'},
                'language': 'ru',
                'hierarchy_type': 'br',
            },
            'expected_result_geo_node_voronezh_tariff_zone.json',
            False,
        ),
        (
            {
                'geo_node': {'name': 'br_voronezh', 'type': 'agglomeration'},
                'language': 'en',
                'hierarchy_type': 'br',
            },
            'expected_result_geo_node_br_voronezh_agglomeration.json',
            False,
        ),
        (
            {
                'geo_node': {'name': 'moscow', 'type': 'tariff_zone'},
                'language': 'en',
            },
            'expected_result_geo_node_moscow_tariff_zone.json',
            False,
        ),
        (
            {
                'geo_node': {'name': 'br_moscow', 'type': 'agglomeration'},
                'language': 'ru',
            },
            None,
            True,
        ),
        (
            {
                'geo_node': {'name': 'br_russia', 'type': 'country'},
                'language': 'ru',
            },
            None,
            True,
        ),
        (
            {'city': 'Воронеж', 'language': 'en', 'hierarchy_type': 'sp'},
            'expected_result_city_sp_voronezh.json',
            False,
        ),
        (
            {'city': 'Москва', 'language': 'ru', 'hierarchy_type': 'op'},
            'expected_result_city_op_moscow.json',
            False,
        ),
        (
            {
                'city': 'Санкт-Петербург',
                'language': 'en',
                'hierarchy_type': 'br',
            },
            None,
            True,
        ),
        (
            {'city': 'Самара', 'language': 'ru', 'hierarchy_type': 'fi'},
            None,
            True,
        ),
    ],
)
async def test_get_tariff_hierarchy_on_success(
        web_app_client,
        atlas_blackbox_mock,
        web_context,
        open_file,
        request_body,
        expected_result_file,
        use_default,
) -> None:
    response = await web_app_client.post(
        '/api/v1/tariff_hierarchy', json=request_body,
    )
    assert response.status == 200
    response_data = await response.json()

    if expected_result_file:
        with open_file(expected_result_file) as json_file:
            expected_result = json.load(json_file)
    else:
        expected_result = []

    assert response_data['items'] == expected_result
    assert response_data['use_default'] is use_default


async def test_get_tariff_hierarchy_conditional_request_params(
        web_app_client, atlas_blackbox_mock, web_context,
) -> None:
    response = await web_app_client.post(
        '/api/v1/tariff_hierarchy',
        json={'language': 'ru', 'hierarchy_type': 'br'},
    )
    assert response.status == 400
    response_data = await response.json()
    assert (
        response_data['message']
        == 'Either geo_node or city should be specified'
    )
