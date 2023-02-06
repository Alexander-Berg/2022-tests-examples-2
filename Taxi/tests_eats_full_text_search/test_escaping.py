import pytest

from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'


@pytest.mark.parametrize(
    'request_text,fts_status_code,fts_response',
    (
        (
            'My Search Text',
            200,
            {
                'meta': {},
                'payload': [
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {
                            'title': 'Категории',
                            'type': 'category',
                        },
                        'items': [],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My "Search" Item',
                                'description': 'Some "item" description',
                                'available': True,
                                'inStock': 2,
                                'price': 100,
                                'decimalPrice': '100',
                                'promoPrice': None,
                                'decimalPromoPrice': None,
                                'promoTypes': [],
                                'adult': False,
                                'weight': '100 г',
                                'picture': {
                                    'url': 'URL',
                                    'scale': 'aspect_fit',
                                },
                                'optionGroups': [],
                                'ancestors': [],
                                'shippingType': 'all',
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
@translations.DEFAULT
async def test_escaping(
        taxi_eats_full_text_search,
        mockserver,
        request_text,
        fts_status_code,
        fts_response,
):
    """
    Проверяем, разэскейпливание в title и description
    """

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': 'N_10',
        'title': 'My \\"Search\\" Item',
        'in_stock': 2,
        'price': 100,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some \\"item\\" description',
        'parent_categories': [],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_SERVICE
        assert int(args['kps']) == SAAS_PREFIX
        assert request_text in args['text']
        x = utils.get_saas_response(
            [utils.gta_to_document(item_url, utils.item_to_gta(item))],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        assert request.query['slug'] == place_slug
        json = request.json
        products = json['products']
        assert len(products) == 1
        assert products[0] == item['nomenclature_item_id']
        return {
            'categories': [
                {'category_id': str(category_id)}
                for category_id in request.json['categories']
            ],
            'products': [utils.to_nomenclature_product(item)],
        }

    params = {'text': request_text}

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response
