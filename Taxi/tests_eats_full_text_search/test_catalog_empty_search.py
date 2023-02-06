import pytest

from . import catalog
from . import translations
from . import utils


ELASTIC_INDEX = 'menu_items'


def make_places():
    availability = catalog.Availability(
        available_from=None, available_to=None, is_available=True,
    )

    shop = catalog.Place(
        id=1,
        slug='slug_1',
        name='Магазин',
        business=catalog.Business.Shop,
        availability=availability,
        tags=[],
    )

    rest = catalog.Place(
        id=2,
        slug='slug_2',
        name='Ресторан',
        business=catalog.Business.Restaurant,
        price_category=catalog.PriceCategory(name='₽₽₽'),
        availability=availability,
        tags=[],
    )

    return [shop, rest]


def match_by_text(arg_name: str, text: str):
    return pytest.mark.experiments3(
        name='eats_fts_catalog_suggest',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': arg_name,
                        'arg_type': 'string',
                        'value': text,
                    },
                },
                'value': {
                    'suggest': {
                        'header': 'Совпадений нет, но есть: ',
                        'header_key': 'header_key',
                        'title': 'Популярное',
                        'title_key': 'title_key',
                        'brand_ids': [1, 2],
                    },
                },
            },
        ],
        is_config=True,
    )


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
@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=(match_by_text(arg_name='text', text='My Search Text'),),
            id='match by original text',
        ),
        pytest.param(
            marks=(
                match_by_text(
                    arg_name='normalized_text', text='my search text',
                ),
            ),
            id='match by normalized text',
        ),
    ),
)
@translations.eats_full_test_search_ru(
    {'header_key': 'Совпадений нет, но есть: ', 'title_key': 'Популярное'},
)
async def test_catalog_empty_search(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json,
):
    """
    Проверяем, что отображается список рекомендаций из эксперимента
    если мы ничего не нашли по запросу
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=list(make_places())),
    )

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return {}

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eats-search-ranking')
    def umlaas_eats(request):
        return load_json('umlaas_response.json')

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(request):
        return {}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(request):
        return {}

    @mockserver.json_handler('/yabs/page/1')
    def yabs(request):
        assert False, 'Should be unreacheble'

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=utils.get_headers(),
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0
    assert umlaas_eats.times_called > 0
    assert yabs.times_called == 0

    assert response.status == 200
    assert response.json() == load_json('search_response.json')
