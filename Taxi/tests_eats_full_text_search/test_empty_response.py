import pytest

from . import experiments
from . import translations
from . import utils


EMPTY_RESPONSE_HEADER = 'Увы, ничего не найдено'


@pytest.mark.parametrize(
    'fts_request',
    (
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
            },
            id='Catalog Search',
        ),
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            id='Menu Search',
        ),
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
                'category': '100',
            },
            id='Category Search',
        ),
    ),
)
@translations.DEFAULT
async def test_items_availability(
        taxi_eats_full_text_search, mockserver, fts_request,
):
    """
    Проверяем, что при пустой выдачи приходит
    надпись "Увы, ничего не найдено"
    в разных режимах поиска
    """

    @mockserver.json_handler(
        '/catalog/v1/internal/catalog-for-full-text-search',
    )
    def _catalog(request):
        return {'payload': {'places': []}}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def _umlaas_eats(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response([])

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {'categories': [], 'products': []}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == 200

    header = response.json().get('header')
    assert header, 'No header in response'

    text = header.get('text')
    assert text, 'No text in response'

    assert text == EMPTY_RESPONSE_HEADER


@pytest.mark.parametrize(
    'fts_request',
    (
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
            },
            id='Catalog Search',
        ),
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
            },
            id='Menu Search',
        ),
        pytest.param(
            {
                'location': {'latitude': 0.0, 'longitude': 0.0},
                'text': 'My Search Text',
                'place_slug': 'my_place_slug',
                'category': '100',
            },
            id='Category Search',
        ),
    ),
)
@experiments.BANNER_MARKET
@translations.DEFAULT
async def test_banner_market(
        taxi_eats_full_text_search, mockserver, fts_request,
):
    """
    Проверяем, что при пустой выдачи приходит
    надпись "Увы, ничего не найдено" и баннер Маркета
    в разных режимах поиска
    """

    @mockserver.json_handler('/saas-search-proxy/')
    def _saas_search_proxy(request):
        return utils.get_saas_response([])

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=fts_request,
        headers=utils.get_headers(),
    )

    assert response.status_code == 200

    header = response.json().get('header')
    assert header, 'No header in response'

    text = header.get('text')
    assert text, 'No text in response'

    assert text == EMPTY_RESPONSE_HEADER

    blocks = response.json().get('blocks')
    blocks_size = len(blocks)
    assert blocks_size > 1

    separator_block = blocks[blocks_size - 2]
    assert separator_block.get('type') == 'separator'

    banners_block = blocks[blocks_size - 1]
    assert banners_block.get('type') == 'banners'
