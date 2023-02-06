#  pylint: disable=unused-variable, protected-access
import pytest

from generated.clients import taxi_agglomerations

import agglomeration_cache.components


async def test_base(library_context):
    cache = library_context.agglomerations_cache
    await cache.refresh_cache()
    nodes = cache.get_nodes_by_tariff_zone('moscow')
    assert [node.get_name() for node in nodes] == [
        'br_moscow_adm',
        'br_moscow',
        'br_moskovskaja_obl',
        'br_tsentralnyj_fo',
        'br_russia',
        'br_root',
    ]
    node = cache.get_geo_node('br_moscow')
    assert node.get_name() == 'br_moscow'
    assert node.get_name_ru() == 'Москва'
    assert node.get_name_en() == 'Moscow'
    assert node.get_region_id() is None
    assert node.get_tanker_key() == 'name.br_moscow'
    assert node.get_node_type().value == 'agglomeration'
    assert node.get_parent().get_name() == 'br_moskovskaja_obl'
    assert list(node.all_tariff_zones) == ['boryasvo', 'moscow', 'vko']
    assert node.get_tariff_zones() == []
    assert [i.get_name() for i in node.ancestors] == [
        'br_moskovskaja_obl',
        'br_tsentralnyj_fo',
        'br_russia',
        'br_root',
    ]
    assert [i.get_name() for i in node.descendants] == [
        'br_moscow_adm',
        'br_moscow_middle_region',
    ]


async def test_errors(library_context, mockserver, patch):
    geo_nodes = agglomeration_cache.components.Data({}, {}, None, [])

    @patch('taxi.util.aiohttp_kit.context.FileCacheHandler.save_to_file')
    def save_cache(body):
        assert body == geo_nodes

    @patch('taxi.util.aiohttp_kit.context.FileCacheHandler.load_from_file')
    def load_from_file(*args, **kwargs):
        return geo_nodes

    @mockserver.json_handler('/taxi-agglomerations/v1/br-geo-nodes/')
    def _handler(*args, **kwargs):
        return mockserver.make_response('internal error', status=500)

    library_context.agglomerations_cache._first_launch = True

    #  on the first launch cache have to be loaded from file
    await library_context.agglomerations_cache.refresh_cache()

    #  after first launch should fail refresh
    with pytest.raises(taxi_agglomerations.NotDefinedResponse):
        await library_context.agglomerations_cache.refresh_cache()
