import pytest

GEO_NODES = [
    {
        'name': 'br_kazakhstan',
        'name_en': 'Kazakhstan',
        'name_ru': 'Казахстан',
        'node_type': 'country',
        'parent_name': 'br_root',
        'tanker_key': 'name.br_kazakhstan',
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
        'name': 'br_moscow_adm',
        'name_en': 'Moscow (adm)',
        'name_ru': 'Москва (адм)',
        'node_type': 'node',
        'parent_name': 'br_moscow',
        'tariff_zones': ['boryasvo', 'moscow', 'vko'],
        'tanker_key': 'name.br_moscow_adm',
    },
    {
        'name': 'br_moscow_middle_region',
        'name_en': 'Moscow (Middle Region)',
        'name_ru': 'Москва (среднее)',
        'node_type': 'node',
        'parent_name': 'br_moscow',
        'tanker_key': 'name.br_moscow_middle_region',
    },
    {
        'name': 'br_moskovskaja_obl',
        'name_en': 'Moscow Region',
        'name_ru': 'Московская область',
        'node_type': 'node',
        'parent_name': 'br_tsentralnyj_fo',
        'tanker_key': 'name.br_moskovskaja_obl',
    },
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_russia',
        'name_en': 'Russia',
        'name_ru': 'Россия',
        'node_type': 'country',
        'parent_name': 'br_root',
        'tanker_key': 'name.br_russia',
    },
    {
        'name': 'br_tsentralnyj_fo',
        'name_en': 'Central Federal District',
        'name_ru': 'Центральный ФО',
        'node_type': 'node',
        'parent_name': 'br_russia',
        'tanker_key': 'name.br_tsentralnyj_fo',
    },
]


def pytest_configure(config):
    config.addinivalue_line('markers', 'geo_nodes: geo nodes')


@pytest.fixture(autouse=True)
def _agglomerations_mockserver(request, mockserver):
    marker = request.node.get_closest_marker('geo_nodes')
    geo_nodes = GEO_NODES

    if marker:
        geo_nodes = marker.args[0]

    @mockserver.json_handler('/taxi_agglomerations/v1/br-geo-nodes')
    def _handler(request):
        return {'items': geo_nodes}


@pytest.fixture
def _agglomeration_config(config):
    config.set_values(
        dict(
            AGGLOMERATIONS_CACHE_SETTINGS={
                '__default__': {
                    'enabled': False,
                    'log_errors': True,
                    'verify_on_updates': True,
                },
            },
        ),
    )
