import pytest

from . import catalog
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
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': True},
)
@pytest.mark.parametrize('umlaas_eats_status_code', (400, 500))
async def test_catalog_search_umlaas_fail(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        load_json,
        taxi_config,
        umlaas_eats_status_code,
):
    """
    Проверяем, что ошибки из umlaas не виляют на
    код ответа ручки поиска
    """

    place = catalog.Place()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return mockserver.make_response(status=umlaas_eats_status_code)

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json={
            'text': 'My Search Text',
            'location': {'latitude': 55.750449, 'longitude': 37.534576},
        },
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert umlaas_eats.times_called > 0

    assert response.status == 200
    data = response.json()
    block = data['blocks'][0]
    utils.assert_has_catalog_place(block['payload'], place)
