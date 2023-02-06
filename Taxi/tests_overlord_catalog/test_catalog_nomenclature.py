import pytest

from . import catalog_wms_config


def wmsify(category_id_in, suffix):
    return category_id_in.replace('-', '') + suffix


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'wms_generate_stocks.sql',
        'update_picture_url_wms.sql',
        'mark_depots_as_wms.sql',
        'wmsify_ids.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.now('2020-06-09T14:00:00Z')
async def test_basic_wms(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': wmsify(
                        'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'WMSCAT',
                    ),
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    await taxi_overlord_catalog.invalidate_caches()

    response = await taxi_overlord_catalog.get(
        '/v1/catalog/nomenclature/87840',
    )

    assert response.status_code == 200

    json_result = response.json()

    assert len(json_result['groups']) == 142
    assert len(json_result['products']) == 151
    for group in json_result['groups']:
        assert not catalog_wms_config.is_uuid(group['id'])
    for product in json_result['products']:
        assert not catalog_wms_config.is_uuid(product['id'])
        if product['code'] == '2770':
            assert product['images'] == [
                'grocery-pics://grocery/65694/'
                'c1bc37c053364fb0ac403a5dc3012378',
            ]
    assert json_result['success'] == 1


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'wms_generate_stocks.sql',
        'update_picture_url_wms.sql',
        'mark_depots_as_wms.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.now('2020-06-09T14:00:00Z')
async def test_18(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': 'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae',
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    response = await taxi_overlord_catalog.get(
        '/v1/catalog/nomenclature/87840',
    )

    assert response.status_code == 200

    json_result = response.json()

    assert len(json_result['groups']) == 142
    assert len(json_result['products']) == 151
    for product in json_result['products']:
        if product['name'] == '№1 Очень 18+ товар':
            assert product['ageGroup'] == '18'
    for product in json_result['groups']:
        if product['name'] == 'Очень надо!':
            assert product['ageGroup'] == '18'
    assert json_result['success'] == 1


@catalog_wms_config.GET_EVERYTHING_FROM_WMS
@pytest.mark.pgsql(
    'overlord_catalog',
    files=[
        'catalog_wms_test_depots.sql',
        'wms_menu_data.sql',
        'wms_generate_stocks.sql',
        'update_picture_url_wms.sql',
        'mark_depots_as_wms.sql',
        'wmsify_ids.sql',
        'refresh_wms_views.sql',
    ],
)
@pytest.mark.now('2020-06-09T14:00:00Z')
@pytest.mark.translations(
    wms_items={
        'ddec7f73689f11e9b7fdac1f6b8566c7WMSGOOD_ingredients': {
            'ru': 'ingredients',
        },
        'ddec7f73689f11e9b7fdac1f6b8566c7WMSGOOD_long_title': {
            'ru': 'ru_long_title',
        },
    },
)
async def test_description_in_response(
        taxi_overlord_catalog, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-catalog_wms_test_depots.json',
        'gdepots-zones-catalog_wms_test_depots.json',
        replace_at_depots=[
            [
                ['90213', '87840'],
                {
                    'root_category_id': wmsify(
                        'd9ef3613-c0ed-40d2-9fdc-3eed67f55aae', 'WMSCAT',
                    ),
                    'assortment_id': (
                        '63d5c9a4-7f11-47d8-8510-578d70ad149dASTMNT'
                    ),
                    'price_list_id': (
                        'a9aef011-11c5-44bf-a41b-6e5002365f7ePRLIST'
                    ),
                },
            ],
        ],
    )
    await taxi_overlord_catalog.invalidate_caches()

    response = await taxi_overlord_catalog.get(
        '/v1/catalog/nomenclature/87840',
    )

    assert response.status_code == 200

    json_result = response.json()
    for product in json_result['products']:
        if product['id'] == 'ddec7f73689f11e9b7fdac1f6b8566c7WMSGOOD':
            assert (
                product['description']
                == 'ingredientsЖиры: 100 г.Калории: 100 ККал.'
            )
