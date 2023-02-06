import pytest

from . import catalog
from . import experiments
from . import utils


ELASTIC_INDEX = 'menu_items'

ITEMS_LIMIT = 1
SEARCH_TYPE = 'category'
SHOW_MORE_TEXT = 'Show More'


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
@experiments.place_block_settings(
    place_items_limit=ITEMS_LIMIT,
    search_type=SEARCH_TYPE,
    show_more='on_limit',
    show_more_text=SHOW_MORE_TEXT,
)
async def test_catalog_search_place_items_limit(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        load_json,
        taxi_config,
        check_headers,
):
    """
    Проверяем, что эксперимент ограничивает
    количество товаров под рестом
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
    }

    place = catalog.Place(slug='slug_1', business=catalog.Business.Shop)

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    headers = utils.get_headers()
    headers['x-platform'] = 'ios_app'

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        check_headers(request.headers, headers)

        response = load_json('nomenclature_response.json')
        response['categories'] = [
            {'category_id': str(category_id)}
            for category_id in request.json['categories']
        ]
        return response

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0

    assert response.status == 200
    response_place = response.json()['blocks'][0]['payload'][0]

    assert response_place['slug'] == place.slug
    assert response_place['show_more']['title'] == SHOW_MORE_TEXT

    assert len(response_place['items']) == ITEMS_LIMIT
    item = response_place['items'][0]
    assert item['search_type'] == SEARCH_TYPE
