import pytest

from . import catalog
from . import utils


ELASTIC_INDEX = 'menu_items'


def make_places():
    one = catalog.Place(
        id=1,
        slug='slug_1',
        name='Рест без айтемов',
        business=catalog.Business.Shop,
    )

    two = catalog.Place(
        id=7,
        slug='slug_7',
        name='Ресторан с айтемами из эластика',
        business=catalog.Business.Restaurant,
    )

    return [one, two]


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
async def test_elastic_search_unavailable(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json,
):
    """
    Проверяем что поиск по каталогу работает
    Если Elastic Search 500-тит
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
        'region_id': 1,
        'shipping_type': 'all',
        'delivery_time': {'time': '2021-03-12T21:00:00+00:00', 'zone': 3},
    }

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=list(make_places())),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        '/eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {'categories': [], 'items': {}}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert elastic_search.times_called > 0

    assert response.status == 200
    assert response.json() == load_json('search_response.json')
