# pylint: disable=import-error
from eats_analytics import eats_analytics
# pylint: enable=import-error

from . import catalog
from . import configs
from . import translations
from . import utils


@configs.ENABLE_ANALYTICS
@configs.DISABLE_UMLAAS
@translations.DEFAULT
async def test_catalog_analytics(
        taxi_eats_full_text_search, mockserver, eats_catalog, load_json,
):
    """
    Проверяет формирование аналитического контекста при поиске с главной
    """

    place = catalog.Place()
    eats_catalog.add_block(catalog.Block(id='open', type='open', list=[place]))

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(request):
        return load_json('saas_response.json')

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

    assert response.status == 200

    data = response.json()
    assert len(data['blocks']) == 1

    block = data['blocks'][0]
    utils.assert_has_catalog_place(block['payload'], place)

    expected_request_analytics = eats_analytics.AnalyticsContext(
        search_item_type=eats_analytics.SearchItemType.REQUEST,
        search_query='My Search Text',
        search_request_id=response.headers['x-request-id'],
        search_selector=None,
        search_places_found=1,
        search_places_available=1,
        search_blocks=[
            eats_analytics.SearchBlock(
                type=eats_analytics.SearchBlockType.PLACES,
                title=None,
                items_count=1,
            ),
        ],
    )

    request_analytics = data['analytics']
    assert (
        eats_analytics.decode(request_analytics) == expected_request_analytics
    )

    expected_place_analytics = eats_analytics.AnalyticsContext(
        search_item_type=eats_analytics.SearchItemType.PLACE,
        place_slug='slug_1',
        place_name='Рест',
        place_business=eats_analytics.Business.RESTAURANT,
        place_available=True,
        is_ad=False,
        search_place_position=0,
        search_place_items_count=0,
        search_place_block_title=None,
    )

    place_analytics = block['payload'][0]['analytics']
    assert eats_analytics.decode(place_analytics) == expected_place_analytics
