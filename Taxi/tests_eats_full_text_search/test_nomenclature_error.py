import pytest

from . import utils

PLACE_SLUG = 'my_place_slug'

ITEM = {
    'place_id': 1,
    'place_slug': PLACE_SLUG,
    'categories': [100],
    'nomenclature_item_id': 'N_10',
    'origin_id': 'N_10',
    'title': 'My Search Item',
    'in_stock': 2,
    'price': 100,
    'weight': '100 g',
    'adult': False,
    'shipping_type': 0,
    'gallery': [{'url': 'URL'}],
    'description': 'Some item description',
    'parent_categories': [
        {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
    ],
}

ITEM_URL = '/{}/items/{}'.format(
    ITEM['place_id'], ITEM['nomenclature_item_id'],
)

USE_PRICE_FROM_SAAS_CONFIG = {
    'EATS_FULL_TEXT_SEARCH_ITEMS_AVAILABILITY_SETTINGS': {
        'nomenclature_pool_size': 100,
        'use_price_from_saas': True,
    },
}


@pytest.mark.parametrize('handlers_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'cache_price,fts_success',
    [
        pytest.param(
            True,
            True,
            marks=pytest.mark.config(**USE_PRICE_FROM_SAAS_CONFIG),
            id='cached price used',
        ),
        pytest.param(True, False, id='cached price not used'),
        pytest.param(
            False,
            False,
            marks=pytest.mark.config(**USE_PRICE_FROM_SAAS_CONFIG),
            id='no cached price',
        ),
    ],
)
async def test_cached_price(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        cache_price,
        fts_success,
        handlers_version,
):
    taxi_config.set_values(
        {
            'EATS_FULL_TEXT_SEARCH_NOMENCLATURE_SETTINGS': {
                'products_info_batch_size': 250,
                'place_products_info_batch_size': 250,
                'place_categories_get_parents_batch_size': 50,
                'place_settings': {
                    '__default__': {'handlers_version': handlers_version},
                },
            },
        },
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        saas_doc = utils.gta_to_document(
            ITEM_URL, utils.item_to_gta(ITEM, with_price=cache_price),
        )
        return utils.get_saas_response([saas_doc])

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nmn_place_ass_details(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return mockserver.make_response(status=500)

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=PLACE_SLUG),
        params={'text': 'My Search Text'},
    )

    assert _saas_search_proxy.times_called > 0
    assert response.status_code == (200 if fts_success else 500)
    if fts_success:
        _, fts_items = response.json()['payload']
        [fts_item] = fts_items['items']
        assert fts_item['price'] == ITEM['price']
