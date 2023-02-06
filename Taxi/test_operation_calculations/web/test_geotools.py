import pytest

from operation_calculations.geosubventions import geo_tools


GEO_NODES = [
    {
        'name': 'br_moscow_near_region',
        'name_ru': 'Ближнее МО',
        'name_en': 'Near MO',
        'node_type': 'node',
        'tariff_zones': ['himki', 'korolev'],
        'parent_name': 'br_moscow',
    },
    {
        'name': 'br_moscow',
        'name_ru': 'Москва',
        'name_en': 'Moscow',
        'node_type': 'agglomeration',
        'tariff_zones': ['moscow'],
        'parent_name': 'br_russia',
    },
    {
        'name': 'br_saratov',
        'name_ru': 'Саратов',
        'name_en': 'Saratov',
        'node_type': 'agglomeration',
        'tariff_zones': ['saratov', 'engels'],
        'parent_name': 'br_russia',
        'region_id': '194',
    },
    {
        'name': 'br_russia',
        'name_ru': 'Россия',
        'name_en': 'Russia',
        'node_type': 'country',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
]


@pytest.mark.parametrize(
    'zones, output',
    [
        [['himki'], 'br_moscow_near_region'],
        [['himki', 'moscow'], 'br_moscow'],
        [['engels', 'himki'], 'br_russia'],
    ],
)
@pytest.mark.geo_nodes(GEO_NODES)
def test_geo_lca(zones, output, web_context):
    result = geo_tools.get_geo_lca_name(
        web_context.agglomerations_cache, zones,
    )
    assert result == output
