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
    EATS_FULL_TEXT_SEARCH_RANKING_SETTINGS={'enable_umlaas_eats': False},
)
@pytest.mark.parametrize(
    'use_grocery_api,response_file,es_times_called,grocery_api_times_called',
    (
        pytest.param(
            False, 'search_response_es.json', 1, 0, id='use elastic search',
        ),
        pytest.param(
            True, 'search_response_grocery.json', 0, 1, id='use grocery api',
        ),
    ),
)
async def test_grocery_search(
        taxi_eats_full_text_search,
        mockserver,
        eats_catalog,
        load_json,
        experiments3,
        use_grocery_api,
        response_file,
        es_times_called,
        grocery_api_times_called,
):
    """
    Проверяет поиск по лавке
    """

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_fts_grocery',
        consumers=['eats-full-text-search/catalog-search'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'enabled': use_grocery_api},
                'predicate': {'type': 'true'},
            },
        ],
    )

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    place = catalog.Place(
        slug='lavka_1', name='Лавка', business=catalog.Business.Store, tags=[],
    )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return {}

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
        assert requested_place_ids == set([1])

        return load_json('elastic_search_response.json')

    @mockserver.json_handler('/grocery-api/lavka/v1/api/v1/search')
    def grocery_api(request):
        assert request.json['position']['location'] == [37.541323, 55.752338]
        assert request.json['text'] == 'My Search Text'
        return load_json('grocery_api_reponse.json')

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def nomenclature(request):
        return {}

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert nomenclature.times_called == 0

    assert elastic_search.times_called == es_times_called
    assert grocery_api.times_called == grocery_api_times_called

    assert response.status == 200
    assert response.json() == load_json(response_file)
