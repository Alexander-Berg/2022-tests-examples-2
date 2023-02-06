# pylint: disable=redefined-outer-name
import operation_calculations.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = ['operation_calculations.generated.service.pytest_plugins']


GEO_NODES = [
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
        'name': 'br_samara',
        'name_ru': 'Самара',
        'name_en': 'Samara',
        'node_type': 'agglomeration',
        'tariff_zones': ['samara'],
        'parent_name': 'br_russia',
        'region_id': '51',
    },
    {
        'name': 'br_moscow',
        'name_ru': 'Москва',
        'name_en': 'Moscow',
        'node_type': 'agglomeration',
        'tariff_zones': ['moscow', 'himki', 'dolgoprudny', 'reutov'],
        'parent_name': 'br_russia',
    },
    {
        'name': 'br_spb',
        'name_ru': 'Питер',
        'name_en': 'Spb',
        'node_type': 'agglomeration',
        'tariff_zones': ['spb', 'lomonosov'],
        'parent_name': 'br_russia',
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


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'services_responses(file): services_responses',
    )
    config.addinivalue_line('markers', 'ch_data(file): ch_data')
