import pytest

from . import catalog
from . import translations
from . import utils


ELASTIC_INDEX = 'menu_items'

TRANSTALTIONS = {
    'selector.all': 'Все',
    'selector.restaurant': 'Рестораны',
    'selector.shop': 'Магазины',
}

EATS_FTS_SELECTOR = pytest.mark.experiments3(
    name='eats_fts_selector',
    consumers=['eats-full-text-search/catalog-search'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always true',
            'predicate': {'type': 'true'},
            'value': {
                'default': 'all',
                'selectors': [
                    {
                        'slug': 'all',
                        'text': 'selector.all',
                        'businesses': ['restaurant', 'shop', 'store'],
                    },
                    {
                        'slug': 'restaurant',
                        'text': 'selector.restaurant',
                        'businesses': ['restaurant', 'store'],
                    },
                    {
                        'slug': 'shop',
                        'text': 'selector.shop',
                        'businesses': ['shop', 'store'],
                    },
                ],
            },
        },
    ],
    is_config=True,
)


def make_places():
    shop = catalog.Place(
        id=1, slug='slug_1', name='Магаз', business=catalog.Business.Shop,
    )

    rest = catalog.Place(
        id=2, slug='slug_2', name='Рест', business=catalog.Business.Restaurant,
    )

    lavka = catalog.Place(
        id=3, slug='slug_3', name='Лавка', business=catalog.Business.Store,
    )

    return [shop, rest, lavka]


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
@EATS_FTS_SELECTOR
@pytest.mark.parametrize(
    'request_selector,response_selector,expected_slugs',
    (
        pytest.param(
            None,
            'all',
            ('slug_1', 'slug_2', 'slug_3'),  # 1 - shop, 2 - rest, 3 - store
            id='default',
        ),
        pytest.param(
            '',
            'all',
            ('slug_1', 'slug_2', 'slug_3'),  # 1 - shop, 2 - rest, 3 - store
            id='empty string',
        ),
        pytest.param('all', 'all', ('slug_1', 'slug_2', 'slug_3'), id='all'),
        pytest.param(
            'restaurant', 'restaurant', ('slug_2', 'slug_3'), id='restaurant',
        ),
        pytest.param('shop', 'shop', ('slug_1', 'slug_3'), id='shop'),
    ),
)
@translations.eats_full_test_search_ru(TRANSTALTIONS)
async def test_selector(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        load_json,
        taxi_config,
        request_selector,
        response_selector,
        expected_slugs,
):
    """
    Проверяет логику работы поиска по каталогу
    (с главной страницы еды)
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': request_selector,
    }

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=list(make_places())),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return {'hits': {'total': 0, 'hits': []}}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0

    assert response.status == 200
    blocks = response.json()['blocks']
    assert len(blocks) == 2  # блок селектора + блок заведений
    selector_block = blocks[0]
    assert selector_block['type'] == 'selector'
    selectors = selector_block['payload']
    assert selectors['current'] == response_selector
    assert selectors['list'] == [
        {'slug': 'all', 'text': 'Все'},
        {'slug': 'restaurant', 'text': 'Рестораны'},
        {'slug': 'shop', 'text': 'Магазины'},
    ]

    place_block = blocks[1]
    assert place_block['type'] == 'places'
    response_slugs = set(place['slug'] for place in place_block['payload'])
    assert response_slugs == set(expected_slugs)


@EATS_FTS_SELECTOR
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
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SELECTOR={
        'min_versions': [{'platform': 'ios_app', 'version': '5.15.0'}],
    },
)
@pytest.mark.parametrize(
    'version,has_selector',
    (
        pytest.param('5.11.0', False, id='disabled by version'),
        pytest.param('5.15.0', True, id='allowed by equal version'),
        pytest.param('6.0.0', True, id='allowed by greater version'),
    ),
)
@translations.eats_full_test_search_ru(TRANSTALTIONS)
async def test_selector_disabled_by_version(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        load_json,
        version,
        has_selector,
):
    """
    Проверяем, что конфиг ограничивает версию приложения,
    для которой приходит селектор
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'all',
    }

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=make_places()),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return {'hits': {'total': 0, 'hits': []}}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    headers = utils.get_headers()
    headers.update({'x-platform': 'ios_app', 'x-app-version': version})

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0

    assert response.status == 200
    blocks = response.json()['blocks']

    if has_selector:
        assert len(blocks) == 2  # блок селектора + блок заведений
        selector_block = blocks[0]
        assert selector_block['type'] == 'selector'
    else:
        assert len(blocks) == 1  # блок заведений
        selector_block = blocks[0]
        assert selector_block['type'] != 'selector'


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
@EATS_FTS_SELECTOR
@pytest.mark.parametrize(
    'catalog_businesses, was_found',
    (
        pytest.param(
            frozenset(['shop']),
            True,
            id='only restaurant selected, but only shops found',
        ),
        pytest.param(
            frozenset([]),
            False,
            id='only restaurant selected, but nothing found',
        ),
    ),
)
@translations.eats_full_test_search_ru(TRANSTALTIONS)
async def test_selector_on_empty_response(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        load_json,
        taxi_config,
        catalog_businesses,
        was_found,
):
    """
    Проверяет логику работы поиска по каталогу
    (с главной страницы еды)
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
        'selector': 'restaurant',
    }

    places = (
        place
        for place in make_places()
        if place.business in catalog_businesses
    )
    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=list(places)),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {'hits': {'total': 0, 'hits': []}}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0

    assert response.status == 200
    data = response.json()
    blocks = data['blocks']
    assert data['header']['text']
    if was_found:
        assert saas.times_called > 0
    else:
        assert saas.times_called == 0
    assert len(blocks) == 2  # блок селектора + блок заведений
    selector_block = blocks[0]
    assert selector_block['type'] == 'selector'
