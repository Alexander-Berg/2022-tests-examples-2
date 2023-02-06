import pytest

from . import catalog
from . import utils


ELASTIC_INDEX = 'menu_items'


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
        'places_batch_size': 2,
        'es_request_pool': 2,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': 'eats_fts',
        'prefix': 1,
        'misspell': 'no',
        'disjunction_batch_size': 2,
        'saas_request_pool': 2,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
async def test_catalog_search(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json,
):
    """
    Проверяет, что запросы в SAAS и ES разбиваются на батчи
    в зависимости от параметров конфигов
    """

    text = 'My Search Text'
    request_params = {
        'text': text,
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    places = []
    for idx in range(1, 7):
        places.append(
            catalog.Place(
                id=idx, slug=f'slug_{idx}', brand=catalog.Brand(id=idx),
            ),
        )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=places))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        first_request = list('i_pid:{}'.format(i) for i in range(1, 3))
        second_request = list('i_pid:{}'.format(i) for i in range(3, 5))
        third_request = list('i_pid:{}'.format(i) for i in range(5, 7))
        assert any(
            [
                all(
                    token in request.query['template']
                    for token in first_request
                ),
                all(
                    token in request.query['template']
                    for token in second_request
                ),
                all(
                    token in request.query['template']
                    for token in third_request
                ),
            ],
        )
        assert text in request.query['text']
        return load_json('saas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def elastic_search(request):
        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called == 1
    assert saas.times_called > 0
    assert elastic_search.times_called > 0

    assert response.status == 200
