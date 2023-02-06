import pytest

from . import catalog
from . import utils


ELASTIC_INDEX = 'menu_item_testing'
ELASTIC_DOC_TYPE = 'menu_item'

SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_RESTAURANT_MENU_PREFIX = 3
SAAS_MISSPELL = 'try_at_first'

REST_MENU_SAAS_CATALOG_SEARCH_ENABLED = pytest.mark.experiments3(
    name='eats_fts_rest_menu_saas_catalog_search',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)


def cleanup_fts_indexer(pgsql):
    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute('DELETE FROM fts_indexer.place_state')


def fts_item_gen(place_id, place_slug, item_id, category_id):
    return {
        'place_id': place_id,
        'place_slug': place_slug,
        'categories': [category_id],
        'nomenclature_item_id': f'nomenclature_item_id_{item_id}',
        'origin_id': f'N_{item_id}',
        'title': 'My Search Item',
        'price': 100,
        'adult': True,
        'shipping_type': 1,
        'description': 'Some item description',
        'parent_categories': [
            {
                'id': category_id,
                'parent_id': None,
                'title': 'My Search Category',
            },
        ],
        'images': [{'url': 'nomenclature_url_1'}],
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
    }


def fts_category_gen(place_id, place_slug, category_id):
    return {
        'place_id': place_id,
        'place_slug': place_slug,
        'category_id': category_id,
        'title': 'My Search Category',
        'gallery': [{'url': 'URL'}],
        'parent_categories': [
            {
                'id': category_id,
                'parent_id': None,
                'title': 'My Search Category',
            },
        ],
    }


def make_places():
    availability = catalog.Availability(
        available_from='2021-02-18T00:00:00+03:00',
        available_to='2021-10-18T23:00:00+03:00',
    )

    delivery = catalog.Delivery(text='10-20 min')

    shop_one = catalog.Place(
        id=1,
        slug='my_place_slug_1',
        name='Магазин 1',
        business=catalog.Business.Shop,
        brand=catalog.Brand(id=1000),
        availability=availability,
        delivery=delivery,
    )

    shop_two = catalog.Place(
        id=2,
        slug='my_place_slug_2',
        name='Магазин 2',
        business=catalog.Business.Shop,
        brand=catalog.Brand(id=2000),
        availability=availability,
        delivery=delivery,
    )

    rest_one = catalog.Place(
        id=3,
        slug='my_place_slug_3',
        name='Ресторан 1',
        business=catalog.Business.Restaurant,
        brand=catalog.Brand(id=3000),
        availability=availability,
        delivery=delivery,
    )

    rest_two = catalog.Place(
        id=4,
        slug='my_place_slug_4',
        name='Ресторан 2',
        business=catalog.Business.Restaurant,
        brand=catalog.Brand(id=4000),
        availability=availability,
        delivery=delivery,
    )

    return [shop_one, shop_two, rest_one, rest_two]


#
# /eats/v1/full-text-search/v1/search
#


def fts_search_post_request_gen():
    return {
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'text': 'My Search Text',
    }


@pytest.mark.parametrize(
    'fts_request, fts_status_code, fts_response',
    [
        pytest.param(
            fts_search_post_request_gen(),
            200,
            'search_response.json',
            id='search',
        ),
    ],
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': SAAS_SERVICE,
        'prefix': SAAS_PREFIX,
        'prefix_restaurant_menu': SAAS_RESTAURANT_MENU_PREFIX,
        'misspell': SAAS_MISSPELL,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RESTAURANT_AVAILABILITY_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@pytest.mark.pgsql(
    'eats_full_text_search_indexer',
    files=['pg_eats_full_text_search_indexer.sql'],
)
@pytest.mark.parametrize(
    'dynamic_price',
    [
        pytest.param(
            True,
            marks=[
                utils.dynamic_prices(10),
                pytest.mark.smart_prices_cache({'3': 100, '4': 100}),
            ],
            id='dynamic_prices_10_100',
        ),
        pytest.param(
            True,
            marks=[
                utils.dynamic_prices(100),
                pytest.mark.smart_prices_cache({'3': 10, '4': 10}),
            ],
            id='dynamic_prices_100_10',
        ),
        pytest.param(
            False,
            marks=pytest.mark.smart_prices_cache({'3': 100, '4': 100}),
            id='dynamic_prices_off_by_exp',
        ),
        pytest.param(
            False,
            marks=utils.dynamic_prices(100),
            id='dynamic_prices_off_by_service',
        ),
    ],
)
@REST_MENU_SAAS_CATALOG_SEARCH_ENABLED
async def test_rest_menu_saas_catalog_search(
        taxi_eats_full_text_search,
        mockserver,
        pgsql,
        load_json,
        eats_catalog,
        fts_request,
        fts_status_code,
        fts_response,
        dynamic_price,
):
    """
    Тест проверяет, что товар находится в SaaS и попадает в правильный блок.
    Из eats-catalog-storage возвращается 2 магазина и 2 ресторана.
    Из SaaS возвращается:
    - 2 магазина с 1 товаром в каждом
    - 2 ресторана с 2 товарами в одном из них
    - не существующий магазин
    - не существующий ресторан
    - не существующий идентификатор товара в номенклатуре (магазин 2)
    - не существующий идентификатор товара в маппинге (магазин 2)
    - не существующий идентификатор товара в ES (ресторан 4)
    Из eats-nomenclature возвращается 2 товара, по 1 в каждом магазине.
    Из elasticsearch возвращается 2 блюда в одном ресторане.
    Наличие dynamic_price включает наценку айтемов (10%)
    Порядок в ответе ручки поиска, должен быть такой:
    - my_place_slug_3
    - my_place_slug_1
      * 10
    - my_place_slug_2
      * 20
    - my_place_slug_4
      * 111
      * 222
    """

    place_id = 1
    place_slug = 'my_place_slug_1'
    core_item_id = 10
    core_category_id = 100
    item_1 = fts_item_gen(place_id, place_slug, core_item_id, core_category_id)
    category_1 = fts_category_gen(place_id, place_slug, core_category_id)
    place_id = 2
    place_slug = 'my_place_slug_2'
    core_item_id = 20
    core_category_id = 300
    item_2 = fts_item_gen(place_id, place_slug, core_item_id, core_category_id)
    category_2 = fts_category_gen(place_id, place_slug, core_category_id)

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=list(make_places())),
    )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/{}/{}/_search'.format(
            ELASTIC_INDEX, ELASTIC_DOC_TYPE,
        ),
    )
    def _elastic_search(request):
        requested_item_ids = set(request.json['query']['terms']['_id'])
        assert requested_item_ids == set([333, 222, 111])
        assert len(requested_item_ids) == request.json['size']
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {
            'categories': [
                utils.to_nomenclature_category(category_1),
                utils.to_nomenclature_category(category_2),
            ],
            'products': [
                utils.to_nomenclature_product(item_1),
                utils.to_nomenclature_product(item_2),
            ],
        }

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas(request):
        args = request.query
        assert args['service'] == SAAS_SERVICE
        assert args['kps'] == str(SAAS_PREFIX) + ',' + str(
            SAAS_RESTAURANT_MENU_PREFIX,
        )
        assert args['msp'] == SAAS_MISSPELL
        assert (
            args['template']
            == '%request% && (i_pid:4 | i_pid:3 | i_pid:2 | i_pid:1)'
        )
        return load_json('saas_response.json')

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return load_json('umlaas_response.json')

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    cleanup_fts_indexer(pgsql)

    assert eats_catalog.times_called == 1
    assert _saas.times_called == 2
    assert _nomenclature.times_called == 2
    assert _elastic_search.times_called == 1
    assert _umlaas_eats.times_called == 1
    assert response.status_code == fts_status_code
    resp = load_json(fts_response)
    if dynamic_price:
        for payload in resp['blocks'][0]['payload']:
            if payload['business'] != 'restaurant':
                continue
            for item in payload['items']:
                item['decimal_price'] = '{:g}'.format(
                    float(item['decimal_price']) * 1.1,
                )
                item['price'] = '{:s} ₽'.format(item['decimal_price'])
    assert response.json() == resp
