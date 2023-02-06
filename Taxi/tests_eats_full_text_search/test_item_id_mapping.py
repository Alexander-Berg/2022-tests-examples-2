import pytest

from . import catalog
from . import translations
from . import utils


SAAS_SERVICE = 'eats_fts_testsute'
SAAS_PREFIX = 1
SAAS_MISSPELL = 'try_at_first'

ELASTIC_INDEX = 'menu_items'


@pytest.mark.parametrize(
    'request_text,item_origin_id,fts_status_code,fts_response',
    (
        (
            'My Search Text',
            'N_10',
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
                        'items': [
                            {
                                'id': 100,
                                'name': 'My Search Category',
                                'parentId': None,
                                'schedule': None,
                                'gallery': [{'url': 'URL'}],
                                'available': True,
                                'ancestors': [],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [
                            {
                                'id': 10,
                                'name': 'My Search Item',
                                'description': 'Some item description',
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
                                'ancestors': [
                                    {
                                        'id': 100,
                                        'name': 'My Search Category',
                                        'parentId': None,
                                        'available': True,
                                        'schedule': None,
                                        'gallery': [],
                                    },
                                ],
                                'shippingType': 'all',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            'My Search Text',
            'N_9999',
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
                        'items': [
                            {
                                'id': 100,
                                'name': 'My Search Category',
                                'parentId': None,
                                'schedule': None,
                                'gallery': [{'url': 'URL'}],
                                'available': True,
                                'ancestors': [],
                            },
                        ],
                    },
                    {
                        'scopeType': 'catalog',
                        'scopeBoundary': None,
                        'itemsType': {'title': 'Товары', 'type': 'item'},
                        'items': [],
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
async def test_item_id_mapping(
        taxi_eats_full_text_search,
        mockserver,
        request_text,
        item_origin_id,
        fts_status_code,
        fts_response,
):
    """
    Проверяем что id товаров мамятся из локального кэша
    1й кейс saas складываем core_item_id=9999 + origin_id = N_10
    в базу core_item_id=10, на выдачи ожидаем 10
    1й кейс в saas складываем core_item_id=9999 + origin_id = N_9999
    в базе core_item_id=10, ожидаем выдачу без товара,
    так как в кэшах нет маппинга
    """

    place_slug = 'my_place_slug'

    item = {
        'place_id': 1,
        'place_slug': place_slug,
        'categories': [100],
        'nomenclature_item_id': 'N_10',
        'origin_id': item_origin_id,
        'title': 'My Search Item',
        'in_stock': 2,
        'price': 100,
        'weight': '100 g',
        'adult': False,
        'shipping_type': 0,
        'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
        'description': 'Some item description',
        'parent_categories': [
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
    }

    item_url = '/{}/items/{}'.format(
        item['place_id'], item['nomenclature_item_id'],
    )

    category = {
        'place_id': 1,
        'place_slug': place_slug,
        'category_id': 100,
        'title': 'My Search Category',
        'gallery': [{'url': 'URL'}],
        'parent_categories': [
            {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
        ],
    }

    category_url = '/{}/categories/{}'.format(
        category['place_id'], category['category_id'],
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        args = request.query
        assert args['service'] == SAAS_SERVICE
        assert int(args['kps']) == SAAS_PREFIX
        assert args['msp'] == SAAS_MISSPELL
        assert args['gta'] == '_AllDocInfos'
        assert args['ms'] == 'proto'
        assert args['hr'] == 'json'
        assert request_text in args['text']
        x = utils.get_saas_response(
            [
                utils.gta_to_document(item_url, utils.item_to_gta(item)),
                utils.gta_to_document(
                    category_url, utils.category_to_gta(category),
                ),
            ],
        )
        return x

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        assert request.query['slug'] == place_slug
        json = request.json
        products = json['products']
        return {
            'categories': [utils.to_nomenclature_category(category)],
            'products': (
                [utils.to_nomenclature_product(item)] if products else []
            ),
        }

    params = {'text': request_text}

    response = await taxi_eats_full_text_search.get(
        '/api/v2/menu/goods/search/{slug}'.format(slug=place_slug),
        params=params,
    )

    assert response.status_code == fts_status_code
    assert response.json() == fts_response


@pytest.mark.pgsql('eats_full_text_search_indexer', files=[])
@pytest.mark.experiments3(
    name='eats_fts_use_eats_catalog',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_MAP_ID_SETTINGS={'select_pool_size': 4},
)
async def test_item_id_mapping_fail(
        taxi_eats_full_text_search, eats_catalog, mockserver, pgsql,
):
    """
    Проверяет, что из-за ошибки БД
    сервис не коркается
    https://st.yandex-team.ru/EDACAT-1506

    Без испавление этот тест падает
    из-за азерта здесь
    https://a.yandex-team.ru/arc/trunk/arcadia/taxi/uservices/userver/core/src/engine/semaphore.cpp?rev=r8522787#L60
    в дебажной сборке
    и зависает в релизной
    """

    cursor = pgsql['eats_full_text_search_indexer'].cursor()

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    shops = []
    items = []
    item_urls = []
    # Так как корка возникает
    # из-за того что параллельные корутины обращаются к уже разрушенному
    # семафору, создаем 20 плейсов с 1 товаром в каждом, чтобы
    # вызвать параллельные обращения к базе
    for idx in range(20):
        slug = f'slug_{idx}'
        cursor.execute(
            """
                INSERT INTO
                    fts.place(
                        place_id,
                        brand_id,
                        place_slug,
                        enabled
                    )
                VALUES (
                    %s,
                    %s,
                    %s,
                    true
                );
            """,
            (idx, idx * 1000, slug),
        )
        shop = catalog.Place(
            brand=catalog.Brand(id=idx),
            business=catalog.Business.Shop,
            id=idx,
            name=f'Рест {idx}',
            slug=slug,
        )
        shops.append(shop)

        item = {
            'place_id': idx,
            'place_slug': slug,
            'categories': [100],
            'nomenclature_item_id': f'N_{idx}0',
            'origin_id': f'N_{idx}0',
            'title': 'My Search Item',
            'in_stock': 2,
            'price': 100,
            'weight': '100 g',
            'adult': False,
            'shipping_type': 0,
            'gallery': [{'url': 'URL', 'scale': 'aspect_fit'}],
            'description': 'Some item description',
            'parent_categories': [
                {'id': 100, 'parent_id': None, 'title': 'My Search Category'},
            ],
        }
        items.append(item)

        item_url = '/{}/items/{}'.format(
            item['place_id'], item['nomenclature_item_id'],
        )
        item_urls.append(item_url)

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=shops))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return utils.get_saas_response(
            list(
                [
                    utils.gta_to_document(item_url, utils.item_to_gta(item))
                    for item_url, item in zip(item_urls, items)
                ],
            ),
        )

    @mockserver.json_handler(
        '/eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    # Дропаем таблицу к которой обращаемся,
    # чтобы сэмулировать ошибку БД
    with utils.drop_table(cursor, 'fts', 'items_mapping'):
        response = await taxi_eats_full_text_search.post(
            '/eats/v1/full-text-search/v1/search',
            json=request_params,
            headers=utils.get_headers(),
        )

        assert eats_catalog.times_called > 0
        assert saas.times_called > 0
        assert response.status == 500
