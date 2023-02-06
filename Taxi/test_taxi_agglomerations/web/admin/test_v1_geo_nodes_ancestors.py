import pytest


@pytest.mark.parametrize(
    'tariff_zone, expected_status, expected_data',
    (
        pytest.param(
            'moscow',
            200,
            {
                'items': [
                    {
                        'name': 'br_moscow_adm',
                        'name_en': 'Moscow (adm)',
                        'name_ru': 'Москва (адм)',
                        'node_type': 'node',
                        'parent_name': 'br_moscow',
                        'region_id': '213',
                        'tanker_key': 'name.br_moscow_adm',
                        'tariff_zones': ['boryasvo', 'moscow', 'vko'],
                    },
                    {
                        'name': 'br_moscow',
                        'name_en': 'Moscow',
                        'name_ru': 'Москва',
                        'node_type': 'agglomeration',
                        'parent_name': 'br_moskovskaja_obl',
                        'tanker_key': 'name.br_moscow',
                    },
                    {
                        'name': 'br_moskovskaja_obl',
                        'name_en': 'Moscow Region',
                        'name_ru': 'Московская область',
                        'region_id': '1',
                        'node_type': 'node',
                        'parent_name': 'br_tsentralnyj_fo',
                        'tanker_key': 'name.br_moskovskaja_obl',
                    },
                    {
                        'name': 'br_tsentralnyj_fo',
                        'name_en': 'Central Federal District',
                        'name_ru': 'Центральный ФО',
                        'region_id': '3',
                        'node_type': 'node',
                        'parent_name': 'br_russia',
                        'tanker_key': 'name.br_tsentralnyj_fo',
                    },
                    {
                        'name': 'br_russia',
                        'name_en': 'Russia',
                        'name_ru': 'Россия',
                        'region_id': '225',
                        'node_type': 'country',
                        'parent_name': 'br_root',
                        'tanker_key': 'name.br_russia',
                    },
                    {
                        'name': 'br_root',
                        'name_en': 'Basic Hierarchy',
                        'name_ru': 'Базовая иерархия',
                        'node_type': 'root',
                        'tanker_key': 'name.br_root',
                    },
                ],
            },
            id='moscow',
        ),
        pytest.param(
            'invalid',
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'Not found GeoNode with name="invalid"',
            },
            id='invalid',
        ),
    ),
)
@pytest.mark.filldb()
async def test_v1_geo_nodes_ancestors(
        web_app_client, tariff_zone, expected_status, expected_data,
):
    response = await web_app_client.get(
        'v1/geo-nodes/ancestors', params={'tariff_zone': tariff_zone},
    )
    assert response.status == expected_status
    assert await response.json() == expected_data
