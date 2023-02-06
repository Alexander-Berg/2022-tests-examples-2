# pylint: disable=too-many-lines

from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils


FIND_BY_EATER = (
    '/eats-user-reactions/eats-user-reactions/v1/favourites/find-by-eater'
)


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


BURGER_FILTER = [
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


FILTERS_DESCRIPTIONS = {
    'top_rating': 'Это топ',
    'pickup': 'Это самовывоз',
    'plus': 'Это плюс',
    'favorite': 'Это избранное',
}


def count_filters_in_request(filters_v2):
    result = 0
    if not filters_v2:
        return result
    for group in filters_v2['groups']:
        result = len(group['filters'])
    return result


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.experiments3(filename='experiments.json')
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(
    filter_icon='/icons/top',
    filter_name='Топ',
    filter_picture='/images/top',
    tag_name='top_rating',
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_filters(catalog_for_layout, eats_catalog_storage, mockserver):
    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def core_quick_filters(_):
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
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )
    assert core_quick_filters.times_called == 1
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']
    picture_url = (
        '/images/1387779/c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
    )
    assert filters == [
        {
            'slug': 'burger',
            'type': 'quickfilter',
            'payload': {
                'name': 'Бургеры',
                'state': 'enabled',
                'picture_url': picture_url,
            },
        },
    ]


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PICKUP={
        'filter_name': 'Навынос',
        'filter_picture': '/images/pickup_filter',
        'filter_icon': '/icons/pickup_filter',
        'filter_name_v2': 'Навынос',
        'filter_icon_v2': '/icons/pickup_filter2',
    },
)
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(
    filter_icon='/icons/top',
    filter_name='Топ',
    filter_picture='/images/top',
    tag_name='top_rating',
)
@pytest.mark.experiments3(
    name='eats_catalog_pickup',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'rename by device_id',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'pickup_rename_device_id',
                },
            },
            'value': {'name': 'С собой'},
        },
    ],
)
@pytest.mark.parametrize(
    'request_filters, device_id, expected_places_count, response_filters',
    [
        pytest.param(
            {'groups': []},
            'device_id',
            2,
            [
                {
                    'slug': 'pickup',
                    'type': 'pickup',
                    'payload': {
                        'name': 'Навынос',
                        'state': 'enabled',
                        'picture_url': '/images/pickup_filter',
                        'icon_url': '/icons/pickup_filter2',
                    },
                },
            ],
            id='no pickup filter in request',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'slug': 'pickup', 'type': 'pickup'}],
                    },
                ],
            },
            'device_id',
            1,
            [
                {
                    'slug': 'pickup',
                    'type': 'pickup',
                    'payload': {
                        'name': 'Навынос',
                        'state': 'selected',
                        'picture_url': '/images/pickup_filter',
                        'icon_url': '/icons/pickup_filter2',
                    },
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
        device_id,
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
        headers={
            'x-device-id': device_id,
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters_v2=request_filters,
    )
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    block = response.json()['blocks'][0]
    assert len(block['list']) == expected_places_count, block
    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters
    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]
    assert selected_count == count_filters_in_request(request_filters)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.experiments3(filename='experiments.json')
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(
    filter_icon='/icons/top',
    filter_name='Топ',
    filter_icon_v2='/icons/top2',
    filter_picture='/images/top',
    tag_name='top_rating',
)
@pytest.mark.parametrize(
    'request_filters, expected_places_count, response_filters',
    [
        pytest.param(
            {'groups': []},
            2,
            [
                {
                    'slug': 'top_rating',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Топ',
                        'state': 'enabled',
                        'picture_url': '/images/top',
                        'icon_url': '/icons/top2',
                    },
                },
            ],
            id='no top_rating filter in request',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {'slug': 'top_rating', 'type': 'quickfilter'},
                        ],
                    },
                ],
            },
            1,
            [
                {
                    'slug': 'top_rating',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Топ',
                        'state': 'selected',
                        'picture_url': '/images/top',
                        'icon_url': '/icons/top2',
                    },
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
        filters_v2=request_filters,
    )
    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200
    block = response.json()['blocks'][0]
    assert len(block['list']) == expected_places_count, block
    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters
    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]
    assert selected_count == count_filters_in_request(request_filters)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PLUS_FILTER={
        'name': 'Кэшбек',
        'icon_url': '/icons/plus',
        'name_v2': 'Кэшбек 2',
        'icon_url_v2': '/icons/plus2',
        'filter_picture': '/images/plus',
    },
)
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.parametrize(
    'request_filters, expected_places, response_filters',
    [
        pytest.param(
            {'groups': []},
            ['regular', 'with_plus'],
            [
                {
                    'slug': 'plus',
                    'type': 'plus',
                    'payload': {
                        'name': 'Кэшбек',
                        'state': 'enabled',
                        'picture_url': '/images/plus',
                        'icon_url': '/icons/plus2',
                    },
                },
            ],
            id='no plus filter in request',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [{'type': 'plus', 'slug': 'plus'}],
                    },
                ],
            },
            ['with_plus'],
            [
                {
                    'slug': 'plus',
                    'type': 'plus',
                    'payload': {
                        'name': 'Кэшбек',
                        'state': 'selected',
                        'picture_url': '/images/plus',
                        'icon_url': '/icons/plus2',
                    },
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
        filters_v2=request_filters,
    )
    assert eats_plus.times_called == 1
    assert response.status_code == 200
    data = response.json()
    block = layout_utils.find_block('any', data)
    for slug in expected_places:
        layout_utils.find_place_by_slug(slug, block)
    assert data['filters_v2']['list'] == response_filters
    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]
    assert selected_count == count_filters_in_request(request_filters)


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
    assert data['filters_v2']['list'] == [
        {
            'slug': 'plus',
            'type': 'plus',
            'payload': {
                'name': 'Кэшбек',
                'state': 'selected',
                'icon_url': 'asset://yandex-plus',
            },
        },
    ]


@pytest.mark.now('2021-04-04T13:32:00+03:00')
@pytest.mark.experiments3(filename='experiments.json')
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(
    filter_icon='/icons/top',
    filter_name='Топ',
    filter_picture='/images/top',
    tag_name='top_rating',
)
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
        filters_v2={
            'groups': [
                {
                    'type': 'and',
                    'filters': [{'slug': 'pickup', 'type': 'pickup'}],
                },
            ],
        },
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
@pytest.mark.experiments3(filename='experiments.json')
@experiments.TOP_RATING_TAG
@experiments.top_rating_view(
    filter_icon='/icons/top',
    filter_name='Топ',
    filter_picture='/images/top',
    tag_name='top_rating',
)
@pytest.mark.parametrize(
    'request_filters, expected_place_slugs, response_filters',
    [
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {'slug': 'burger', 'type': 'quickfilter'},
                            {'slug': 'sushi', 'type': 'quickfilter'},
                        ],
                    },
                ],
            },
            ['first'],
            [
                {
                    'slug': 'sushi',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Суши',
                        'state': 'selected',
                        'picture_url': (
                            '/images/1387779/'
                            'f89baa2592e8e3c0687825ce631dcf91-{w}x{h}.jpg'
                        ),
                    },
                },
                {
                    'slug': 'burger',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Бургеры',
                        'state': 'selected',
                        'picture_url': (
                            '/images/1387779/'
                            'c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
                        ),
                    },
                },
                {
                    'slug': 'pizza',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Пицца',
                        'state': 'enabled',
                        'picture_url': (
                            '/images/1380157/'
                            '4529d57df6bc970d11c1f3496296d99b-{w}x{h}.jpg'
                        ),
                    },
                },
            ],
            id='burger and sushi',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'or',
                        'filters': [
                            {'slug': 'burger', 'type': 'quickfilter'},
                            {'slug': 'pizza', 'type': 'quickfilter'},
                        ],
                    },
                ],
            },
            ['first', 'second'],
            [
                {
                    'slug': 'sushi',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Суши',
                        'state': 'enabled',
                        'picture_url': (
                            '/images/1387779/'
                            'f89baa2592e8e3c0687825ce631dcf91-{w}x{h}.jpg'
                        ),
                    },
                },
                {
                    'slug': 'burger',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Бургеры',
                        'state': 'selected',
                        'picture_url': (
                            '/images/1387779/'
                            'c0b1283f22c4c21383c5f8819bd72e9e-{w}x{h}.jpg'
                        ),
                    },
                },
                {
                    'slug': 'pizza',
                    'type': 'quickfilter',
                    'payload': {
                        'name': 'Пицца',
                        'state': 'selected',
                        'picture_url': (
                            '/images/1380157/'
                            '4529d57df6bc970d11c1f3496296d99b-{w}x{h}.jpg'
                        ),
                    },
                },
            ],
            id='burger or pizza',
        ),
    ],
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_filters_groups(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        expected_place_slugs,
        response_filters,
        mockserver,
):
    """
    Проверяем, что фильтры объединяются через И/ИЛИ
    """

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def core_quick_filters(_):
        return CORE_QUICK_FILTERS_RESPONSE

    # плейс в категориях бургер, суши
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='first',
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=1),
                    storage.QuickFilter(quick_filter_id=2),
                ],
            ),
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

    # плейс в категориях суши, пицца
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='second',
            quick_filters=storage.QuickFilters(
                general=[
                    storage.QuickFilter(quick_filter_id=2),
                    storage.QuickFilter(quick_filter_id=3),
                ],
            ),
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
        filters_v2=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert core_quick_filters.times_called == 1
    assert response.status_code == 200
    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters
    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]
    assert selected_count == count_filters_in_request(request_filters)
    block = layout_utils.find_block('any', response.json())
    for place_slug in expected_place_slugs:
        layout_utils.find_place_by_slug(place_slug, block)


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@pytest.mark.parametrize(
    'block_type,disable_filters,expected_filters',
    (
        pytest.param('open', False, BURGER_FILTER, id='open block'),
        pytest.param(
            'open', True, BURGER_FILTER, id='open block disabled filters',
        ),
        pytest.param('closed', False, BURGER_FILTER, id='closed block'),
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
    Проверяем, что фильтры 2.0 формируются независимо от блоков
    """

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def core_quick_filters(_):
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
        filters_v2={'groups': []},
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
    filters: slice = response.json()['filters_v2']['list']
    assert filters == expected_filters


@pytest.mark.now('2021-03-15T15:00:00+03:00')
@experiments.ENABLE_FAVORITES
@experiments.TOP_RATING_TAG
@experiments.top_rating_view()
@pytest.mark.translations(
    **{
        'eats-catalog': {
            'c4l.filters.favorite.description': {
                'ru': FILTERS_DESCRIPTIONS['favorite'],
            },
            'c4l.filters.pickup.description': {
                'ru': FILTERS_DESCRIPTIONS['pickup'],
            },
            'c4l.filters.plus.description': {
                'ru': FILTERS_DESCRIPTIONS['plus'],
            },
            'c4l.filters.top_rating.description': {
                'ru': FILTERS_DESCRIPTIONS['top_rating'],
            },
        },
    },
)
@translations.eats_catalog_ru(TRANSLATIONS)
async def test_filters_description(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    """
    Проверяем, что описание фильтров
    топ, самовывоз, избранное, плюс протягиваются из танкера
    """

    @mockserver.json_handler('/eats-core/v1/export/quick-filters')
    def _core_quick_filters(_):
        return {'payload': []}

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {'cashback': [{'place_id': 1, 'cashback': 7.8210}]}

    @mockserver.json_handler(FIND_BY_EATER)
    def eats_user_reactions(_):
        return {
            'reactions': [
                {
                    'subject': {'namespace': 'catalog_brand', 'id': '1'},
                    'created_at': '2020-12-01T12:00:00+00:00',
                },
            ],
            'pagination': {'cursor': 'cursor', 'has_more': False},
        }

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), tags=['top_rating'],
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
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'cookie': 'some cookie',
            'x-yandex-uid': 'testsuite',
            'X-Eats-Session': 'qweetestsuit',
            'X-Eats-User': 'user_id=1',
        },
        filters_v2={'groups': []},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert eats_plus.times_called == 1
    assert eats_user_reactions.times_called == 1

    assert response.status_code == 200
    filters: list = response.json()['filters_v2']['list']
    assert len(filters) == len(FILTERS_DESCRIPTIONS)

    for flter in filters:
        slug = flter['slug']
        assert flter['payload']['description'] == FILTERS_DESCRIPTIONS[slug]
