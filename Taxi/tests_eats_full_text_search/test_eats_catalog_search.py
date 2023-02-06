import pytest

from . import catalog
from . import colors
from . import experiments
from . import utils


ELASTIC_INDEX = 'menu_items'


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@experiments.CATALOG_PLACE_META
async def test_eats_catalog_search(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        load_json,
        check_headers,
):
    """
    Проверяет работу поиска с сервисом eats_catalog вместо catalog
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'delivery',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
    }

    usd = catalog.Currency(code='USD', sign='$')

    place_rating_with_color = catalog.Rating(
        icon=colors.ColoredIconV2(
            color=colors.ThemedColorV2(dark='#FFFFFF', light='#AAAAAA'),
            uri='icon_uri',
        ),
        text='4.7 (100)',
    )

    place_rating_without_color = catalog.Rating(
        icon=colors.ColoredIconV2(uri='icon_uri'), text='4.7 (100)',
    )

    shop_wo_items = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Shop,
        currency=usd,
        id=1,
        name='Рест без айтемов',
        slug='slug_1',
        tags=[catalog.Tag(name='Завтраки')],
    )

    shop_w_items = catalog.Place(
        brand=catalog.Brand(id=2),
        business=catalog.Business.Shop,
        id=2,
        name='Рест с айтемами',
        slug='slug_2',
        tags=[catalog.Tag(name='Завтраки')],
    )
    shop_items_from_saas = catalog.Place(
        brand=catalog.Brand(id=3),
        business=catalog.Business.Shop,
        id=3,
        name='Рест которого нет в SAAS, но там есть его айтем',
        slug='slug_3',
        tags=[catalog.Tag(name='Завтраки')],
    )
    shop_no_saas_items = catalog.Place(
        brand=catalog.Brand(id=4),
        business=catalog.Business.Shop,
        id=4,
        name='Рест которого нет в SAAS, и айтемов для него там тоже нет',
        slug='slug_4',
    )
    shop_saas_category = catalog.Place(
        brand=catalog.Brand(id=5),
        business=catalog.Business.Shop,
        id=5,
        name='Рест которого нет в SAAS, но есть только его категория',
        slug='slug_5',
    )
    shop_disabled = catalog.Place(
        availability=catalog.Availability(
            available_from='2021-02-18T23:00:00+03:00',
            available_to=None,
            is_available=False,
        ),
        brand=catalog.Brand(id=6),
        business=catalog.Business.Shop,
        currency=usd,
        id=6,
        name='Задизейбленный плейс с айтемом',
        slug='slug_6',
        tags=[],
    )
    rest_es_items = catalog.Place(
        availability=catalog.Availability(
            available_from='2021-02-18T23:00:00+03:00', available_to=None,
        ),
        brand=catalog.Brand(id=7),
        business=catalog.Business.Restaurant,
        currency=usd,
        id=7,
        name='Ресторан с айтемами из эластика',
        rating=place_rating_with_color,
        price_category=catalog.PriceCategory(name='₽₽₽'),
        slug='slug_7',
        tags=[],
    )
    rest_other_es = catalog.Place(
        availability=catalog.Availability(
            available_from='2021-02-18T23:00:00+03:00', available_to=None,
        ),
        brand=catalog.Brand(id=8),
        business=catalog.Business.Pharmacy,
        currency=usd,
        delivery=catalog.Delivery(text='~ 15 min'),
        id=8,
        name='Друой рест с айтемами из эластика',
        rating=place_rating_without_color,
        price_category=catalog.PriceCategory(name='₽₽₽'),
        slug='slug_8',
        tags=[],
    )

    eats_catalog.add_block(
        catalog.Block(
            id='open',
            type='open',
            list=[
                shop_wo_items,
                shop_w_items,
                shop_items_from_saas,
                shop_no_saas_items,
                shop_saas_category,
                rest_es_items,
                rest_other_es,
            ],
        ),
    )

    eats_catalog.add_block(
        catalog.Block(id='closed', type='closed', list=[shop_disabled]),
    )

    def catalog_assert(request):
        params = request.json
        for field in ('latitude', 'longitude'):
            assert params[field] == request_params['location'][field]
        for field in ('region_id', 'shipping_type'):
            assert params[field] == request_params[field]
        blocks = params['blocks']
        assert len(blocks) == 2

        blocks.sort(key=lambda x: x['id'])
        for idx, block_type in enumerate(['closed', 'open']):
            assert blocks[idx] == {
                'id': block_type,
                'type': block_type,
                'low': 0,
                'min_count': 0,
                'no_data': False,
            }

    eats_catalog.assert_callback = catalog_assert

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        # проверяем что в saas передаются ВСЕ id плейсов
        # из каталога
        places = ('i_pid:{}'.format(i) for i in range(1, 9))
        for place in places:
            assert place in request.query['template']
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        menu_item = request.json['query']['bool']['must'][0]['match'][
            'menu_item'
        ]
        assert menu_item == 'My Search Text'

        terms = request.json['query']['bool']['must'][1]['bool']['should']
        requested_place_ids = set()
        for term in terms:
            requested_place_ids.add(term['term']['place_id'])
        assert requested_place_ids == set([7, 8])

        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        check_headers(request.headers, utils.get_headers())
        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0

    assert response.status == 200
    assert response.json() == load_json('search_response.json')


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
async def test_eats_catalog_search_no_closed(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        load_json,
        taxi_config,
):
    """
    Проверяет работу поиска с сервисом eats_catalog вместо catalog
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    shop_items_from_saas = catalog.Place(
        brand=catalog.Brand(id=3),
        business=catalog.Business.Shop,
        id=3,
        name='Рест которого нет в SAAS, но там есть его айтем',
        slug='slug_3',
        tags=[catalog.Tag(name='Завтраки')],
    )

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=[shop_items_from_saas]),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return load_json('nomenclature_response.json')

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0

    assert response.status == 200
    data = response.json()
    assert len(data['blocks']) == 1

    block = data['blocks'][0]
    utils.assert_has_catalog_place(block['payload'], shop_items_from_saas)
