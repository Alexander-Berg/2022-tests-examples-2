from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils


TRANSLATIONS = {
    'c4l.filters.burger.name': 'Бургеры',
    'c4l.filters.sushi.name': 'Суши',
    'c4l.filters.pizza.name': 'Пицца',
}

CORE_QUICK_FILTERS_RESPONSE = {
    'payload': [
        {
            'categoryId': 569,
            'genitive': 'бургеров',
            'id': 1,
            'isEnabled': True,
            'isWizardEnabled': True,
            'name': 'Бургеры',
            'photoURI': (
                '/images/1387779/c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
            ),
            'pictureURI': (
                '/images/1370147/3c05d89f3fa0d94395f3c9e1f66c5295.png'
            ),
            'promoPhotoURI': (
                '/images/1380157/b24d89df4288aaabff0168510ead6675-{w}x{h}.png'
            ),
            'slug': 'burger',
            'sort': 190,
        },
        {
            'id': 2,
            'categoryId': 52,
            'genitive': 'суши и роллов',
            'isEnabled': True,
            'isWizardEnabled': True,
            'name': 'Суши',
            'photoURI': (
                '/images/1387779/f89baa2592e8e3c0687825ce631dcf91-{w}x{h}.jpg'
            ),
            'pictureURI': (
                '/images/1368744/22b13338eb57ea4cc1bb73c8e117ca21.png'
            ),
            'promoPhotoURI': (
                '/images/1387779/532c23e0b5f1bfe861eccfa84aada89f-{w}x{h}.png'
            ),
            'slug': 'sushi',
            'sort': 200,
        },
        {
            'id': 3,
            'categoryId': 34,
            'genitive': 'пиццы',
            'isEnabled': True,
            'isWizardEnabled': True,
            'name': 'Пицца',
            'photoURI': (
                '/images/1380157/4529d57df6bc970d11c1f3496296d99b-{w}x{h}.jpg'
            ),
            'pictureURI': (
                '/images/1370147/41d38ec3605ce8392adf409e9b37765b.png'
            ),
            'promoPhotoURI': (
                '/images/1387779/08d575249e2e378679090c7007cc53e9-{w}x{h}.png'
            ),
            'slug': 'pizza',
            'sort': 180,
        },
    ],
}


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_filters(catalog_for_layout, eats_catalog_storage, mockserver):
    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def core_quick_filters(request):
        return CORE_QUICK_FILTERS_RESPONSE

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            quick_filters=storage.QuickFilters(
                general=[storage.QuickFilter(quick_filter_id=1)],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        location={'longitude': 37.591503, 'latitude': 55.802998},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert core_quick_filters.times_called == 1
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    filters: slice = response.json()['filters']['list']
    assert filters == [
        {
            'active': False,
            'name': 'Бургеры',
            'slug': 'burger',
            'type': 'quickfilter',
            'group': 'quick',
        },
    ]


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.parametrize(
    'request_filters, expected_places_count, response_filters',
    [
        pytest.param(
            [],
            2,
            [
                {
                    'active': False,
                    'name': 'Навынос',
                    'slug': 'pickup',
                    'type': 'pickup',
                    'group': 'shipping',
                },
            ],
            id='no pickup filter in request',
        ),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            1,
            [
                {
                    'active': True,
                    'name': 'Навынос',
                    'slug': 'pickup',
                    'type': 'pickup',
                    'group': 'shipping',
                },
            ],
            id='pickup filter in request',
        ),
    ],
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_filters_pickup(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        expected_places_count,
        response_filters,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='first',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='second',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=2,
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
        filters=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    block = response.json()['blocks'][0]
    assert len(block['list']) == expected_places_count, block

    filters: slice = response.json()['filters']['list']
    assert filters == response_filters


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(tag_name='top_rating', filter_name='Топ')
@pytest.mark.parametrize(
    'request_filters, expected_places_count, response_filters',
    [
        pytest.param(
            [],
            2,
            [
                {
                    'active': False,
                    'name': 'Топ',
                    'slug': 'top_rating',
                    'type': 'quickfilter',
                    'group': 'quick',
                },
            ],
            id='no top_rating filter in request',
        ),
        pytest.param(
            [{'type': 'quickfilter', 'slug': 'top_rating'}],
            1,
            [
                {
                    'active': True,
                    'name': 'Топ',
                    'slug': 'top_rating',
                    'type': 'quickfilter',
                    'group': 'quick',
                },
            ],
            id='top_filter filter in request',
        ),
    ],
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_top_rating_filter(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        request_filters,
        expected_places_count,
        response_filters,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='first',
            quick_filters=storage.QuickFilters(general=[]),
            tags=['top_rating'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='second',
            quick_filters=storage.QuickFilters(general=[]),
            tags=['unknwon_tag'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Delivery,
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
        filters=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    block = response.json()['blocks'][0]
    assert len(block['list']) == expected_places_count, block

    filters: slice = response.json()['filters']['list']
    assert filters == response_filters


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.parametrize(
    'request_filters, expected_places, response_filters',
    [
        pytest.param(
            [],
            ['regular', 'with_plus'],
            [
                {
                    'active': False,
                    'name': 'Кэшбек',
                    'icon_url': 'asset://yandex-plus',
                    'slug': 'plus',
                    'type': 'plus',
                    'group': 'quick',
                },
            ],
            id='no plus filter in request',
        ),
        pytest.param(
            [{'type': 'plus', 'slug': 'plus'}],
            ['with_plus'],
            [
                {
                    'active': True,
                    'name': 'Кэшбек',
                    'icon_url': 'asset://yandex-plus',
                    'slug': 'plus',
                    'type': 'plus',
                    'group': 'quick',
                },
            ],
            id='plus filter in request',
        ),
    ],
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_plus_filter(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        request_filters,
        expected_places,
        response_filters,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='regular',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='with_plus',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {'cashback': [{'place_id': 2, 'cashback': 7.8210}]}

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters=request_filters,
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('any', data)

    for slug in expected_places:
        layout_utils.find_place_by_slug(slug, block)

    assert data['filters']['list'] == response_filters


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.TOP_RATING_TAG
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_plus_filter_empty(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='regular',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {'cashback': []}

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters=[{'type': 'plus', 'slug': 'plus'}],
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    data = response.json()

    layout_utils.assert_no_block_or_empty('any', data)
    assert data['filters']['list'] == [
        {
            'active': True,
            'name': 'Кэшбек',
            'icon_url': 'asset://yandex-plus',
            'slug': 'plus',
            'type': 'plus',
            'group': 'quick',
        },
    ]


@pytest.mark.now('2021-04-04T13:32:00+03:00')
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_pickup_render(catalog_for_layout, eats_catalog_storage):
    """
    Проверяет, что при активном фильтре самовывоза в фиче доставки
    отрисовывается расстояние, а не время доставки
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug='first',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-04T10:00:00+03:00'),
                    end=parser.parse('2021-04-04T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='second',
            location=storage.Location(
                lon=37.59963990515195, lat=55.80887037715973,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-04T10:00:00+03:00'),
                    end=parser.parse('2021-04-04T22:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3, brand=storage.Brand(brand_id=3), slug='preorder',
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3,
            place_id=3,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-04T15:00:00+03:00'),
                    end=parser.parse('2021-04-04T22:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters=[
            {
                'active': True,
                'name': 'Навынос',
                'slug': 'pickup',
                'type': 'pickup',
                'group': 'shipping',
            },
        ],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    assert len(block) == 3

    first_place = layout_utils.find_place_by_slug('first', block)
    assert {'icons': [], 'text': '1.1 км'} == first_place['payload']['data'][
        'features'
    ]['delivery']

    second_place = layout_utils.find_place_by_slug('second', block)
    assert {'icons': [], 'text': '820 м'} == second_place['payload']['data'][
        'features'
    ]['delivery']

    preoreder_place = layout_utils.find_place_by_slug('preorder', block)
    assert {'icons': [], 'text': 'Сегодня 15:00'} == preoreder_place[
        'payload'
    ]['data']['features']['delivery']


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_tags_view',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'Invalid schema',
            'value': {'top_rating': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@experiments.TOP_RATING_TAG
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_config_fail(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    EDACAT-924: проверяет, что в случае если в конфиге отображения фильтра
    тегов содержится значение не совпадающее со схемой конфига ручка все равно
    ответит без ошибки
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='first',
            quick_filters=storage.QuickFilters(general=[]),
            tags=['top_rating'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='second',
            quick_filters=storage.QuickFilters(general=[]),
            tags=['unknwon_tag'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2,
            place_id=2,
            shipping_type=storage.ShippingType.Delivery,
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
        filters=[{'type': 'quickfilter', 'slug': 'top_rating'}],
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())
    # TODO: кажется все таки должно быть 2 так как такого фильтра нет
    assert len(block) == 1

    filters: slice = response.json()['filters']['list']
    assert filters == []


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.parametrize(
    'block_type,disable_filters,expected_filters',
    (
        pytest.param(
            'open',
            False,
            [
                {
                    'active': False,
                    'name': 'Бургеры',
                    'slug': 'burger',
                    'type': 'quickfilter',
                    'group': 'quick',
                },
            ],
            id='open block',
        ),
        pytest.param('open', True, [], id='open block disabled filters'),
        pytest.param('closed', False, [], id='closed block'),
    ),
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_blocks_with_filters(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        block_type,
        disable_filters,
        expected_filters,
):
    """
    Проверяем, что фильтры формируются только по запрошенному блоку
    """

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def core_quick_filters(request):
        return CORE_QUICK_FILTERS_RESPONSE

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            quick_filters=storage.QuickFilters(
                general=[storage.QuickFilter(quick_filter_id=1)],
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+03:00'),
                    end=parser.parse('2021-03-15T22:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[
            {
                'id': 'any',
                'type': block_type,
                'disable_filters': disable_filters,
            },
        ],
    )

    assert core_quick_filters.times_called == 1
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    filters: slice = response.json()['filters']['list']
    assert filters == expected_filters

    if block_type == 'open':
        block = layout_utils.find_block('any', response.json())
        assert len(block) == 1
