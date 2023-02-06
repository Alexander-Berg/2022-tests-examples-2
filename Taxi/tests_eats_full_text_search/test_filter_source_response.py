import pytest

from . import catalog
from . import configs
from . import experiments
from . import utils


ELASTIC_INDEX = 'menu_items'
MATCH_DEVICE_ID = 'match_device_id'
NO_MATCH_DEVICE_ID = 'no_match_device_id'


def filter_source_response(place_id=None, brand_id=None):
    value = {}
    if place_id:
        value.update({'place_ids': [place_id]})
    if brand_id:
        value.update({'brand_ids': [brand_id]})
    return pytest.mark.experiments3(
        name='filter_source_response',
        consumers=['eats-full-text-search/catalog-search'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': MATCH_DEVICE_ID,
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'device_id',
                        'arg_type': 'string',
                        'value': MATCH_DEVICE_ID,
                    },
                },
                'value': value,
            },
        ],
    )


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_ELASTIC_SEARCH_SETTINGS={
        'enable': True,
        'index': ELASTIC_INDEX,
        'size': 1000,
    },
)
@configs.DISABLE_UMLAAS
@pytest.mark.parametrize(
    'device_id, place_id, brand_id, filtered',
    (
        pytest.param(
            MATCH_DEVICE_ID,
            1,
            2,
            True,
            marks=filter_source_response(place_id=1),
            id='filter by place id',
        ),
        pytest.param(
            MATCH_DEVICE_ID,
            1,
            2,
            True,
            marks=filter_source_response(brand_id=2),
            id='filter by brand id',
        ),
        pytest.param(
            MATCH_DEVICE_ID,
            1,
            2,
            False,
            marks=filter_source_response(place_id=10),
            id='no filter by place id',
        ),
        pytest.param(
            MATCH_DEVICE_ID,
            1,
            2,
            False,
            marks=filter_source_response(brand_id=10),
            id='no filter by brand id',
        ),
        pytest.param(
            NO_MATCH_DEVICE_ID,
            1,
            2,
            False,
            marks=filter_source_response(place_id=1),
            id='no match device_id',
        ),
    ),
)
async def test_filter_source_response(
        taxi_eats_full_text_search,
        eats_catalog,
        mockserver,
        device_id,
        place_id,
        brand_id,
        filtered,
):
    """
    Проверяет фильтрацию плейсов по эксперименту
    filter_source_response
    """

    request_params = {
        'text': 'My Search Text',
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    place = catalog.Place(
        brand=catalog.Brand(id=brand_id),
        business=catalog.Business.Restaurant,
        id=place_id,
        name='Рест',
        slug='slug_1',
        tags=[catalog.Tag(name='Завтраки')],
    )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [utils.catalog_place_to_saas_doc(place)],
        )

    @mockserver.json_handler(
        'eats-fts-elastic-search/{}/_search'.format(ELASTIC_INDEX),
    )
    def _elastic_search(_):
        return {}

    @mockserver.json_handler('/eats-nomenclature/v2/place/assortment/details')
    def _nomenclature(_):
        return {}

    headers = utils.get_headers()
    headers['x-device-id'] = device_id

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert eats_catalog.times_called > 0
    assert saas.times_called > 0

    assert response.status == 200
    data = response.json()
    assert len(data['blocks']) == 1
    block = data['blocks'][0]
    payload = block['payload']
    if filtered:
        assert not payload
    else:
        utils.assert_has_catalog_place(payload, place)


@configs.DISABLE_UMLAAS
@filter_source_response(place_id=1)
@experiments.catalog_zero_suggest(
    blocks=[
        experiments.CatalogZeroSuggestBlock(
            title_key='testsuite', brand_ids=[1], limit=10,
        ),
    ],
)
async def test_filter_source_response_zero_suggest(
        taxi_eats_full_text_search, eats_catalog,
):
    """
    Проверяет фильтрацию плейсов по эксперименту
    filter_source_response
    """

    request_params = {
        'location': {'latitude': 55.752338, 'longitude': 37.541323},
    }

    place = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug='slug_1',
        tags=[catalog.Tag(name='Завтраки')],
    )

    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    headers = utils.get_headers()

    response = await taxi_eats_full_text_search.post(
        '/eats/v1/full-text-search/v1/search',
        json=request_params,
        headers=headers,
    )

    assert eats_catalog.times_called > 0

    assert response.status == 200
    data = response.json()
    assert not data['blocks']
