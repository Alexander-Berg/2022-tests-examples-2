import pytest


@pytest.mark.config(
    ATLAS_GEOSUBVENTIONS_PRESETS={
        'moscow_and_mo': {
            'name_ru': 'Москва кастом',
            'name_en': 'Moscow custom',
            'items': [
                {'name': 'moscow', 'type': 'tariff_zone'},
                {'name': 'br_moscow_near_region', 'type': 'geo_node'},
            ],
        },
    },
)
async def test_v1_geosubventions_tasks_run(web_app_client):
    response = await web_app_client.get(f'/v1/geosubventions/presets/')
    await response.text()
    expected = {
        'items': [
            {
                'node_id': 'geotool_moscow_and_mo',
                'name': 'Москва кастом',
                'node_type': 'geotool_preset',
            },
            {
                'node_id': 'moscow',
                'name': 'moscow',
                'node_type': 'tariff_zone',
                'parent_node_id': 'geotool_moscow_and_mo',
            },
            {
                'node_id': 'br_moscow_near_region',
                'name': 'br_moscow_near_region',
                'node_type': 'geo_node',
                'parent_node_id': 'geotool_moscow_and_mo',
            },
        ],
    }

    assert await response.json() == expected
