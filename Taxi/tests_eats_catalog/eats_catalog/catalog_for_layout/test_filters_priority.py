from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(EATS_CATALOG_PICKUP={'filter_name': 'Навынос'})
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(filter_name='Топ', tag_name='top_rating')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_catalog_filters_priority',
    consumers=['eats-catalog-for-layout'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always match',
            'predicate': {'type': 'true'},
            'value': {
                'pickup': 100,
                'favorite': 90,
                'top': 80,
                'cashback': 70,
            },
        },
    ],
)
@translations.eats_catalog_ru({'c4l.filters.burger.name': 'Бургеры'})
async def test_filters_priority(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    Проверяем что фильтры в выдаче
    приходят согласно приоритетам из конфигов
    """

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def _core_quick_filters(_):
        return {
            'payload': [
                {
                    'categoryId': 569,
                    'genitive': 'бургеров',
                    'id': 1,
                    'isEnabled': True,
                    'isWizardEnabled': True,
                    'name': 'Бургеры',
                    'photoURI': (
                        '/images/1387779/'
                        'c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
                    ),
                    'pictureURI': (
                        '/images/1370147/'
                        '3c05d89f3fa0d94395f3c9e1f66c5295.png'
                    ),
                    'promoPhotoURI': (
                        '/images/1380157/'
                        'b24d89df4288aaabff0168510ead6675-{w}x{h}.png'
                    ),
                    'slug': 'burger',
                    'sort': 1,
                },
            ],
        }

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='slug',
            quick_filters=storage.QuickFilters(
                general=[storage.QuickFilter(quick_filter_id=1)],
            ),
            tags=['top_rating'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']
    assert filters == [
        {
            'slug': 'pickup',
            'type': 'pickup',
            'payload': {'name': 'Навынос', 'state': 'enabled'},
        },
        {
            'slug': 'top_rating',
            'type': 'quickfilter',
            'payload': {'name': 'Топ', 'state': 'enabled'},
        },
        {
            'slug': 'burger',
            'type': 'quickfilter',
            'payload': {
                'name': 'Бургеры',
                'state': 'enabled',
                'picture_url': (
                    '/images/1387779/'
                    'c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
                ),
            },
        },
    ]
