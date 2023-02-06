import pytest

from . import catalog
from . import utils


ELASTIC_INDEX = 'menu_items'
REQUEST_ID = 'MY COOL REQUEST ID'


@pytest.mark.now('2021-02-26T12:00:00+03:00')
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
async def test_catalog_search_ranking(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        load_json,
        check_headers,
):
    """
    Проверяем что выдача ранжируется с учетом umlaas
    В тестовых данных
    каталог возвращает 3 плейса (1 магазин и 2 реста)
    saas возвращает те же 3 плейса + 2 айтема в магазин
    es возвращает 1 айтема в один из рестов
    ранжирование возвращает
    плейс без айтемов (id = 3)
    магазин (id = 1)
     - item_id = 2
     - item_id = 1
    рест (id = 2)
     - item_id = 3
    """

    one_place = catalog.Place(
        id=1,
        slug='slug_1',
        name='Рест 1',
        brand=catalog.Brand(id=1),
        business=catalog.Business.Shop,
        tags=[],
    )

    two_place = catalog.Place(
        id=2,
        slug='slug_2',
        name='Рест 2',
        brand=catalog.Brand(id=2),
        business=catalog.Business.Restaurant,
        tags=[],
    )

    three_place = catalog.Place(
        id=3,
        slug='slug_3',
        name='Рест 3',
        brand=catalog.Brand(id=3),
        business=catalog.Business.Restaurant,
        tags=[],
    )

    eats_catalog.add_block(
        catalog.Block(
            id='open', type='open', list=[one_place, two_place, three_place],
        ),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
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

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        assert request.query['request_id'] == REQUEST_ID
        assert request.json == load_json('expected_umlaas_request.json')
        return load_json('umlaas_response.json')

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers={'x-request-id': REQUEST_ID, **utils.get_headers()},
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0
    assert nomenclature.times_called > 0
    assert umlaas_eats.times_called > 0

    assert response.status == 200

    data = response.json()
    places = data['blocks'][0]['payload']
    assert places

    places_order = ('slug_3', 'slug_1', 'slug_2')
    items_order = ('2', '1')

    for place, slug in zip(places, places_order):
        assert place['slug'] == slug
        if place['slug'] == 'slug_1':
            for item, item_id in zip(place['items'], items_order):
                assert item['id'] == item_id
