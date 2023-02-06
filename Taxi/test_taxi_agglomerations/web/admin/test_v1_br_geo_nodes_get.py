import pytest


@pytest.mark.filldb()
async def test_v1_br_geo_nodes_get(web_app_client):
    response = await web_app_client.get('v1/br-geo-nodes/')
    assert response.status == 200
    assert await response.json() == {
        'items': [
            {
                'name': 'br_kazakhstan',
                'name_en': 'Kazakhstan',
                'name_ru': 'Казахстан',
                'region_id': '159',
                'tanker_key': 'name.br_kazakhstan',
                'node_type': 'country',
                'parent_name': 'br_root',
            },
            {
                'name': 'br_moscow',
                'name_en': 'Moscow',
                'name_ru': 'Москва',
                'tanker_key': 'name.br_moscow',
                'node_type': 'agglomeration',
                'parent_name': 'br_moskovskaja_obl',
            },
            {
                'name': 'br_moscow_adm',
                'name_en': 'Moscow (adm)',
                'name_ru': 'Москва (адм)',
                'region_id': '213',
                'tanker_key': 'name.br_moscow_adm',
                'node_type': 'node',
                'parent_name': 'br_moscow',
                'tariff_zones': ['boryasvo', 'moscow', 'vko'],
            },
            {
                'name': 'br_moscow_middle_region',
                'name_en': 'Moscow (Middle Region)',
                'name_ru': 'Москва (среднее)',
                'tanker_key': 'name.br_moscow_middle_region',
                'node_type': 'node',
                'parent_name': 'br_moscow',
            },
            {
                'name': 'br_moskovskaja_obl',
                'name_en': 'Moscow Region',
                'name_ru': 'Московская область',
                'region_id': '1',
                'tanker_key': 'name.br_moskovskaja_obl',
                'node_type': 'node',
                'parent_name': 'br_tsentralnyj_fo',
            },
            {
                'name': 'br_root',
                'name_en': 'Basic Hierarchy',
                'name_ru': 'Базовая иерархия',
                'tanker_key': 'name.br_root',
                'node_type': 'root',
            },
            {
                'name': 'br_russia',
                'name_en': 'Russia',
                'name_ru': 'Россия',
                'region_id': '225',
                'tanker_key': 'name.br_russia',
                'node_type': 'country',
                'parent_name': 'br_root',
            },
            {
                'name': 'br_tsentralnyj_fo',
                'name_en': 'Central Federal District',
                'name_ru': 'Центральный ФО',
                'region_id': '3',
                'tanker_key': 'name.br_tsentralnyj_fo',
                'node_type': 'node',
                'parent_name': 'br_russia',
            },
        ],
    }
