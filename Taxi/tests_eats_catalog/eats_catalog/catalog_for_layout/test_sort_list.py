import copy

from dateutil import parser
import pytest

from eats_catalog import storage
from eats_catalog import translations
from . import layout_utils


TRANSLATIONS = {
    'sorts.default': 'Доверюсь вам',
    'sorts.high_rating': 'С высоким рейтингом',
    'sorts.fast_delivery': 'Быстрые',
    'sorts.cheap_first': 'Недорогие',
    'sorts.expensive_first': 'Дорогие',
    'sorts.v2.default': 'По умолчанию',
    'sorts.v2.high_rating': 'По популярности',
    'sorts.v2.fast_delivery': 'По времени',
    'sorts.v2.cheap_first': 'По стоимости',
}

DELIVERY_SORT_LIST = [
    {
        'slug': 'default',
        'description': '_',
        'description_key': 'sorts.default',
    },
    {
        'slug': 'high_rating',
        'description': '_',
        'description_key': 'sorts.high_rating',
    },
    {
        'slug': 'fast_delivery',
        'description': '_',
        'description_key': 'sorts.fast_delivery',
    },
    {
        'slug': 'cheap_first',
        'description': '_',
        'description_key': 'sorts.cheap_first',
    },
    {
        'slug': 'expensive_first',
        'description': '_',
        'description_key': 'sorts.expensive_first',
    },
]

PICKUP_SORT_LIST = [
    {
        'slug': 'default',
        'description': '_',
        'description_key': 'sorts.default',
    },
    {
        'slug': 'high_rating',
        'description': '_',
        'description_key': 'sorts.high_rating',
    },
    {
        'slug': 'cheap_first',
        'description': '_',
        'description_key': 'sorts.cheap_first',
    },
    {
        'slug': 'expensive_first',
        'description': '_',
        'description_key': 'sorts.expensive_first',
    },
]

FILTERS_V2_LIST = [
    {
        'slug': 'default',
        'description': '_',
        'description_key': 'sorts.v2.default',
    },
    {
        'slug': 'high_rating',
        'description': '_',
        'description_key': 'sorts.v2.high_rating',
    },
    {
        'slug': 'fast_delivery',
        'description': '_',
        'description_key': 'sorts.v2.fast_delivery',
    },
    {
        'slug': 'cheap_first',
        'description': '_',
        'description_key': 'sorts.v2.cheap_first',
    },
]


DEFAULT_SORT_CONFIG = pytest.mark.config(
    EATS_CATALOG_SORTS={
        'delivery': {'default': 'default', 'list': DELIVERY_SORT_LIST},
        'pickup': {'default': 'default', 'list': PICKUP_SORT_LIST},
        'filters_v2': {'default': 'default', 'list': FILTERS_V2_LIST},
    },
)


def response_sort_list(sort_list: list):
    result = []
    for entry in sort_list:
        new_entry = copy.deepcopy(entry)
        new_entry['description'] = TRANSLATIONS[
            new_entry.pop('description_key')
        ]
        result.append(new_entry)
    return result


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@DEFAULT_SORT_CONFIG
@translations.eats_catalog_ru(TRANSLATIONS)
@pytest.mark.parametrize(
    'request_filters,request_filters_v2,expected_sort',
    [
        pytest.param(
            None,
            None,
            {
                'current': 'default',
                'default': 'default',
                'list': response_sort_list(DELIVERY_SORT_LIST),
            },
            id='delivery sorts',
        ),
        pytest.param(
            [{'type': 'pickup', 'slug': 'pickup'}],
            None,
            {
                'current': 'default',
                'default': 'default',
                'list': response_sort_list(PICKUP_SORT_LIST),
            },
            id='pickup sorts',
        ),
        pytest.param(
            None,
            {'groups': []},
            {
                'current': 'default',
                'default': 'default',
                'list': response_sort_list(FILTERS_V2_LIST),
            },
            id='filters v2 sorts',
        ),
    ],
)
async def test_sort_list(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        request_filters_v2,
        expected_sort,
):
    """
    Проверяем, что список сортировок корретно заполняется
    в зависимости от переданных фильтров
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug=place_slug,
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
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters=request_filters,
        filters_v2=request_filters_v2,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    sort = response.json()['sort']
    assert sort == expected_sort

    block = layout_utils.find_block('any', response.json())
    layout_utils.find_place_by_slug(place_slug, block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@DEFAULT_SORT_CONFIG
@translations.eats_catalog_ru(TRANSLATIONS)
@pytest.mark.parametrize(
    'request_sort,expected_selected_count',
    [
        pytest.param('default', 0, id='default'),
        pytest.param('high_rating', 1, id='non default'),
    ],
)
async def test_count_sort_list(
        catalog_for_layout,
        eats_catalog_storage,
        request_sort,
        expected_selected_count,
):
    """
    Проверяем, что не дефолтная сортировка
    учитывается в счетчике фильтров
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug=place_slug,
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
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        sort=request_sort,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]

    assert selected_count == expected_selected_count

    block = layout_utils.find_block('any', response.json())
    layout_utils.find_place_by_slug(place_slug, block)


FILTERS_V2_LIST_CHEAP_DELVERY = response_sort_list(FILTERS_V2_LIST)
FILTERS_V2_LIST_CHEAP_DELVERY.append(
    {'slug': 'cheap_delivery', 'description': 'По стоимости'},
)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.config(
    EATS_CATALOG_SORTS={
        'delivery': {'default': 'default', 'list': DELIVERY_SORT_LIST},
        'pickup': {'default': 'default', 'list': PICKUP_SORT_LIST},
        'filters_v2': {
            'default': 'default',
            'list': FILTERS_V2_LIST_CHEAP_DELVERY,
        },
    },
)
@translations.eats_catalog_ru(TRANSLATIONS)
@pytest.mark.experiments3(
    name='eats_catalog_delivery_price_sort',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': '',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'enabled_delivery_sort',
                },
            },
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.parametrize(
    'delivery_price_sort_enabled,device_id',
    (
        pytest.param(
            False, 'disable_delivery_sort', id='delivery_sort_disabled',
        ),
        pytest.param(
            True, 'enabled_delivery_sort', id='enabled_delivery_sort',
        ),
    ),
)
async def test_delivery_price_sort(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        delivery_price_sort_enabled,
        device_id,
):

    """
    Проверяем сортировку по стоимости доставки
    В сторадже имеем 3 плейса
    1) Маркеплейс с трешхолдом 400
    2) Натив с ценой 100 из прайсинга
    3) Натив без цены из прайсинга
    В результате ожидаем порядок
    2 1 3
    """

    expected_places_order = [2, 1, 3]

    for idx in range(1, 4):
        place_type = storage.PlaceType.Native
        if idx == 1:
            place_type = storage.PlaceType.Marketplace
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=idx),
                place_type=place_type,
                slug=f'slug_{idx}',
                quick_filters=storage.QuickFilters(general=[]),
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=idx,
                place_id=idx,
                shipping_type=storage.ShippingType.Delivery,
                delivery_conditions=[storage.DeliveryCondition(0, 400)],
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-03-15T10:00:00+00:00'),
                        end=parser.parse('2021-03-15T22:00:00+00:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/eda-delivery-price/v2/calc-surge-bulk')
    def calc_surge_bulk(request):
        if delivery_price_sort_enabled:
            assert request.json['calculatate_price']

        user_info = {
            'is_eda_new_user': False,
            'is_retail_new_user': False,
            'tags': [],
            'any_free_delivery': False,
        }

        places_info = [{'surge': {'placeId': 2}}, {'surge': {'placeId': 3}}]

        if delivery_price_sort_enabled:
            places_info[0]['delivery_price'] = 100.0

        return {'user_info': user_info, 'places_info': places_info}

    response = await catalog_for_layout(
        headers={
            'x-device-id': device_id,
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
        sort='cheap_delivery',
        filters_v2={'groups': []},
    )

    assert calc_surge_bulk.times_called == 1

    assert response.status_code == 200
    data = response.json()

    if delivery_price_sort_enabled:
        assert data['sort']['current'] == 'cheap_delivery'
        assert data['sort']['list'] == FILTERS_V2_LIST_CHEAP_DELVERY

        block = layout_utils.find_block('open', data)
        place_ids = list(place['meta']['place_id'] for place in block)
        assert place_ids == expected_places_order
    else:
        assert data['sort']['current'] == 'default'
        assert data['sort']['list'] == response_sort_list(FILTERS_V2_LIST)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.config(
    EATS_CATALOG_SORTS={
        'delivery': {'default': 'default', 'list': DELIVERY_SORT_LIST},
        'pickup': {'default': 'default', 'list': PICKUP_SORT_LIST},
        'filters_v2': {
            'default': 'default',
            'list': FILTERS_V2_LIST_CHEAP_DELVERY,
        },
    },
)
@translations.eats_catalog_ru(TRANSLATIONS)
@pytest.mark.experiments3(
    name='eats_catalog_delivery_price_sort',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': '',
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'enabled_delivery_sort',
                },
            },
            'value': {'enabled': True},
        },
    ],
)
async def test_reset_sort_on_pricing_error(
        catalog_for_layout, eats_catalog_storage, mockserver,
):

    """
    Проверяет, что если в запросе пришла сортировка
    по стоимости доставки, но прайсинг ответил 500,
    сортировка сбросится
    """

    idx = 1
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=idx,
            brand=storage.Brand(brand_id=idx),
            slug=f'slug_{idx}',
            quick_filters=storage.QuickFilters(general=[]),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=idx,
            place_id=idx,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/eda-delivery-price/v2/calc-surge-bulk')
    def calc_surge_bulk(request):
        assert request.json['calculatate_price']
        return mockserver.make_response('Error', status=500)

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'enabled_delivery_sort',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
        sort='cheap_delivery',
        filters_v2={'groups': []},
    )

    assert calc_surge_bulk.times_called == 1

    assert response.status_code == 200
    data = response.json()

    assert data['sort']['current'] == 'default'
    assert data['sort']['list'] == FILTERS_V2_LIST_CHEAP_DELVERY
