import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


@pytest.mark.parametrize('handlers_version', ['v1', 'v2'])
@pytest.mark.parametrize(
    'fts_request,fts_status_code,available,fts_response',
    (
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            200,
            True,
            {
                'blocks': [
                    {
                        'title': 'Категории',
                        'type': 'categories',
                        'payload': [],
                    },
                    {
                        'title': 'Товары',
                        'type': 'items',
                        'payload': [
                            {
                                'id': '10',
                                'public_id': 'N_10',
                                'title': 'My Search Item',
                                'description': 'Some item description',
                                'price': 100,
                                'decimal_price': '100',
                                'promo_price': 50,
                                'decimal_promo_price': '50',
                                'price_discount_value': 50,
                                'in_stock': 2,
                                'option_groups': [],
                                'adult': True,
                                'shipping_type': 'pickup',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            200,
            False,
            {
                'header': {'text': 'Увы, ничего не найдено'},
                'blocks': [
                    {
                        'title': 'Категории',
                        'type': 'categories',
                        'payload': [],
                    },
                    {'title': 'Товары', 'type': 'items', 'payload': []},
                ],
            },
        ),
    ),
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@translations.DEFAULT
async def test_items_availability(
        taxi_eats_full_text_search,
        mockserver,
        taxi_config,
        fts_request,
        fts_status_code,
        available,
        fts_response,
        handlers_version,
):
    """
    Проверяем что айтем не показывается, если он не
    доступен в номенклатуре
    """

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

    item = {
        'place_id': 1,
        'place_slug': 'my_place_slug',
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100,
        'promo_price': 50,
        'adult': True,
        'shipping_type': 2,  # pickup
        'description': 'Some item description',
        'parent_categories': [],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert fts_request['text'] in args['text']
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nmn_place_ass_details(request):
        if available:
            return {
                'categories': [
                    {'category_id': str(category_id)}
                    for category_id in request.json['categories']
                ],
                'products': [utils.to_nomenclature_product(item)],
            }
        return {'categories': [], 'products': []}

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nmn_places_cat(request):
        if available:
            return {
                'places_categories': [
                    {
                        'categories': [
                            str(category_id)
                            for category_id in request.json[
                                'places_categories'
                            ][0]['categories']
                        ],
                        'place_id': request.json['places_categories'][0][
                            'place_id'
                        ],
                    },
                ],
            }
        return {'places_categories': [{'categories': [], 'place_id': 1}]}

    @mockserver.json_handler('/eats-nomenclature/v1/place/products/info')
    def _nmn_place_prod_info(request):
        return {
            'products': [
                {
                    'id': item['nomenclature_item_id'],
                    'in_stock': item['in_stock'],
                    'is_available': available,
                    'origin_id': item['origin_id'],
                    'parent_category_ids': ['1'],
                    'price': item['promo_price'],
                    'old_price': item['price'],
                },
            ],
        }

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _nmn_prod_info(request):
        return {
            'products': [
                {
                    'adult': True,
                    'barcodes': [],
                    'description': {'general': item['description']},
                    'id': item['nomenclature_item_id'],
                    'images': [],
                    'is_catch_weight': True,
                    'is_choosable': True,
                    'is_sku': False,
                    'name': item['title'],
                    'origin_id': item['origin_id'],
                    'place_brand_id': '1',
                    'shipping_type': 'pickup',
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-nomenclature/v1/place/categories/get_parent',
    )
    def _nmn_place_cat_get_parent(request):
        return {
            'categories': [
                {
                    'id': '1',
                    'child_ids': [],
                    'name': 'category_1',
                    'sort_order': 0,
                    'type': 'partner',
                    'images': [],
                    'products': [],
                },
            ],
        }

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
