import pytest

from . import catalog
from . import experiments
from . import rest_menu_storage
from . import utils


SET_SAAS_SETTINGS = pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_SAAS_SETTINGS={
        'service': 'eats_fts',
        'prefix': 1,
        'misspell': 'try_at_first',
        'prefix_erms_menu': 4,
    },
)


@experiments.USE_ERMS_IN_CATALOG_SEARCH
@SET_SAAS_SETTINGS
async def test_metrics(
        taxi_eats_full_text_search,
        mockserver,
        statistics,
        eats_catalog,
        rest_menu_storage_items_preview,
):
    """
    Проверяем метрики поиска с каталога
    """

    rest = catalog.Place(
        brand=catalog.Brand(id=1),
        business=catalog.Business.Restaurant,
        id=1,
        name='Рест',
        slug='slug_1',
    )
    shop = catalog.Place(
        brand=catalog.Brand(id=2),
        business=catalog.Business.Shop,
        id=2,
        name='Магаз',
        slug='slug_2',
    )
    eats_catalog.add_block(
        catalog.Block(id='open', type='open', list=[rest, shop]),
    )

    item = rest_menu_storage.ItemPreview(
        id='item_id',
        legacy_id=10,
        adult=False,
        available=True,
        name='Какой-то айтем',
        price='123.45',
        weight_value='999.999',
        weight_unit='l',
    )

    rest_menu_storage_items_preview.places = [
        rest_menu_storage.Place(place_id='1', items=[item]),
    ]

    @mockserver.json_handler('/saas-search-proxy/')
    def saas(_):
        return utils.get_saas_response(
            [
                utils.item_preview_to_saas_doc(
                    place_id='1', place_slug='slug_1', item_preview=item,
                ),
                utils.catalog_place_to_saas_doc(shop),
            ],
        )

    async with statistics.capture(taxi_eats_full_text_search) as capture:
        response = await taxi_eats_full_text_search.post(
            '/eats/v1/full-text-search/v1/search',
            json={
                'text': 'My Search Text',
                'location': {'latitude': 55.752338, 'longitude': 37.541323},
            },
            headers=utils.get_headers(),
        )

    assert saas.times_called > 0
    assert response.status == 200

    assert capture.statistics['response.catalog.searches.total'] == 1
    assert capture.statistics['response.catalog.searches.empty'] == 0

    assert capture.statistics['response.catalog.retail-places'] == 1
    assert capture.statistics['response.catalog.retail-items'] == 0

    assert capture.statistics['response.catalog.restaurant-places'] == 1
    assert capture.statistics['response.catalog.restaurant-items'] == 1
