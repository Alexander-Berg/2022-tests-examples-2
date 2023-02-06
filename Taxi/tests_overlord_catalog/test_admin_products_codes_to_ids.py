import pytest

from . import catalog_wms_config

SQL_SCRIPTS_TO_POPULATE_BASE = [
    '1c_menu_data.sql',
    '1c_stocks.sql',
    'catalog_wms_test_depots.sql',
    'wms_menu_data.sql',
    'wmsify_ids.sql',
    'wms_generate_stocks.sql',
    'refresh_wms_views.sql',
]


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql('overlord_catalog', files=SQL_SCRIPTS_TO_POPULATE_BASE)
async def test_happy_path(taxi_overlord_catalog, load_json):
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products/codes-to-ids',
        json=load_json('simple_request_data.json'),
    )
    assert response.json() == load_json('expected_response.json')


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql('overlord_catalog', files=SQL_SCRIPTS_TO_POPULATE_BASE)
async def test_no_such_good(taxi_overlord_catalog, load_json):
    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/products/codes-to-ids',
        json={'code_list': ['0000']},
    )
    assert response.json() == {
        'matched_ids': [{'id_1c': '', 'id_wms': '', 'code': '0000'}],
    }
