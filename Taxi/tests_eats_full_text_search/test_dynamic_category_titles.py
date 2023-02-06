import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


DYN_CATEGORY_ID = 44008
DYN_CATEGORY_TITLE = 'Скидки'


@pytest.mark.parametrize(
    'fts_request,fts_status_code,fts_response',
    (
        (
            {
                'latitude': 0.0,
                'longitude': 0.0,
                'text': 'My Search Text',
                'category': DYN_CATEGORY_ID,
            },
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'category',
                        'scopeBoundary': str(DYN_CATEGORY_ID),
                        'itemsType': {
                            'title': DYN_CATEGORY_TITLE,
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'category',
                        'scopeBoundary': str(DYN_CATEGORY_ID),
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Другие категории',
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Совпадения в других категориях',
                            'type': 'item',
                        },
                        'items': [
                            {
                                'adult': True,
                                'ancestors': [
                                    {
                                        'available': True,
                                        'gallery': [],
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': None,
                                        'schedule': None,
                                    },
                                ],
                                'available': True,
                                'description': 'Some item description',
                                'id': 10,
                                'inStock': None,
                                'name': 'My Search Item',
                                'optionGroups': [],
                                'picture': None,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': None,
                                'decimalPromoPrice': None,
                                'promoTypes': [],
                                'shippingType': 'delivery',
                                'weight': None,
                            },
                        ],
                    },
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
@pytest.mark.config(
    EATS_PRODUCTS_DYNAMIC_CATEGORIES={
        'popular': {'id': 0, 'name': 'Популярное'},
        'discount': {'id': DYN_CATEGORY_ID, 'name': DYN_CATEGORY_TITLE},
        'repeat': {'id': 0, 'name': 'Вы уже заказывали'},
    },
)
@translations.DEFAULT
async def test_dynamic_category_titles(
        taxi_eats_full_text_search,
        mockserver,
        fts_request,
        fts_status_code,
        fts_response,
):
    """
    Проверяем что заголовок блока категорий
    можно переопределить в конфиге
    по ID категории
    """

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My Search Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
    }

    item_url = '/{}/items/{}'.format(
        item['place_slug'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    @mockserver.json_handler(
        '/eats-products/api/v1/for-search/place/dynamic_categories',
    )
    def _products(request):
        return mockserver.make_response(status=404)

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{}'.format(place_slug), params=fts_request,
    )

    # assert _saas_search_proxy.times_called == 2
    # assert _nomenclature.times_called == 1
    assert response.status_code == fts_status_code
    assert response.json() == fts_response
