from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils


def delivery_time_filter_config(values: list, min_items: int = 3):
    return experiments.always_match(
        is_config=True,
        name='eats_catalog_delivery_time_filter',
        consumer='eats-catalog-for-layout',
        value={'min_items': min_items, 'values': values},
    )


DELIVERY_TIME_FILTER = delivery_time_filter_config(
    min_items=3,
    values=[
        {'slug': 'zero', 'text': '0', 'value': 0, 'forced': True},
        {'slug': 'thirty', 'text': '30', 'value': 30},
        {'slug': 'forty_five', 'text': '45', 'value': 45},
        {'slug': 'sixty', 'text': '60', 'value': 60},
        {'slug': 'sixty_plus', 'text': '60+', 'value': 'unlimited'},
    ],
)


@DELIVERY_TIME_FILTER
@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.parametrize(
    'request_filters, places, response_filters',
    [
        pytest.param(
            None,
            [
                {'slug': 'first', 'min': 10, 'max': 15, 'in_response': True},
                {'slug': 'second', 'min': 30, 'max': 35, 'in_response': True},
                {'slug': 'third', 'min': 50, 'max': 60, 'in_response': True},
                {'slug': 'fourth', 'min': 60, 'max': 120, 'in_response': True},
            ],
            [
                {
                    'slug': 'delivery_time',
                    'type': 'delivery_time',
                    'payload': {
                        'default': 'sixty_plus',
                        'values': [
                            {'slug': 'zero', 'text': '0', 'state': 'enabled'},
                            {
                                'slug': 'thirty',
                                'text': '30',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'forty_five',
                                'text': '45',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty',
                                'text': '60',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty_plus',
                                'text': '60+',
                                'state': 'selected',
                            },
                        ],
                    },
                },
            ],
            id='All delivery time values',
        ),
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {
                                'slug': 'delivery_time',
                                'type': 'delivery_time',
                                'payload': {'value': {'slug': 'thirty'}},
                            },
                        ],
                    },
                ],
            },
            [
                {'slug': 'first', 'min': 10, 'max': 15, 'in_response': True},
                {'slug': 'second', 'min': 30, 'max': 35, 'in_response': False},
                {'slug': 'third', 'min': 50, 'max': 60, 'in_response': False},
                {
                    'slug': 'fourth',
                    'min': 60,
                    'max': 120,
                    'in_response': False,
                },
            ],
            [
                {
                    'slug': 'delivery_time',
                    'type': 'delivery_time',
                    'payload': {
                        'default': 'sixty_plus',
                        'values': [
                            {'slug': 'zero', 'text': '0', 'state': 'enabled'},
                            {
                                'slug': 'thirty',
                                'text': '30',
                                'state': 'selected',
                            },
                            {
                                'slug': 'forty_five',
                                'text': '45',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty',
                                'text': '60',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty_plus',
                                'text': '60+',
                                'state': 'enabled',
                            },
                        ],
                    },
                },
            ],
            id='less then thirty',
        ),
        pytest.param(
            None,
            [
                {'slug': 'first', 'min': 10, 'max': 15, 'in_response': True},
                {'slug': 'second', 'min': 40, 'max': 40, 'in_response': True},
            ],
            [
                {
                    'slug': 'delivery_time',
                    'type': 'delivery_time',
                    'payload': {
                        'default': 'forty_five',
                        'values': [
                            {'slug': 'zero', 'text': '0', 'state': 'enabled'},
                            {
                                'slug': 'thirty',
                                'text': '30',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'forty_five',
                                'text': '45',
                                'state': 'selected',
                            },
                        ],
                    },
                },
            ],
            id='no places after 45 min',
        ),
    ],
)
async def test_filters_delivery_time(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        places,
        response_filters,
        mockserver,
):
    """
    Проверяем фильтр времени доставки
    При запросе без фильтра проверяем что
    возвращаются доступные и обязательные фильтры
    При запросе с фильтром проверяем, что возвращается тот же набор
    фильтров, но возвращается только один плейс (который подходит под условие)
    маркеры seleсted проставляются на нужные позиции
    """

    for idx, place in enumerate(places):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=idx),
                slug=place['slug'],
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

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        result: list = []
        for idx, place in enumerate(places):
            result.append(
                dict(
                    id=idx,
                    relevance=float(idx),
                    type='ranking',
                    predicted_times=dict(min=place['min'], max=place['max']),
                    blocks=[],
                ),
            )
        return dict(
            exp_list=[],
            request_id='',
            provider='',
            available_blocks=[],
            result=result,
        )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters_v2=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200

    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters

    block = layout_utils.find_block('any', response.json())
    for place in places:
        if place['in_response']:
            layout_utils.find_place_by_slug(place['slug'], block)
        else:
            layout_utils.assert_no_slug(place['slug'], block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_delivery_time_filter',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'All',
            'value': {
                'min_items': 3,
                'values': [
                    {'slug': 'zero', 'text': '0', 'value': 0, 'force': True},
                    {'slug': 'thirty', 'text': '30', 'value': 30},
                    {'slug': 'forty_five', 'text': '45', 'value': 45},
                    {'slug': 'sixty', 'text': '60', 'value': 60},
                    {
                        'slug': 'sixty_plus',
                        'text': '60+',
                        'value': 'unlimited',
                    },
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'request_filters, places, response_filters',
    [
        pytest.param(
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {'type': 'pickup', 'slug': 'pickup'},
                            {
                                'type': 'delivery_time',
                                'slug': 'delivery_time',
                                'payload': {'value': {'slug': 'thirty'}},
                            },
                        ],
                    },
                ],
            },
            [
                {
                    'slug': 'first',
                    'average_preparation': 15,
                    'in_response': True,
                },
                {
                    'slug': 'second',
                    'average_preparation': 35,
                    'in_response': True,
                },
                {
                    'slug': 'third',
                    'average_preparation': 60,
                    'in_response': True,
                },
                {
                    'slug': 'fourth',
                    'average_preparation': 120,
                    'in_response': True,
                },
            ],
            [
                {
                    'slug': 'pickup',
                    'type': 'pickup',
                    'payload': {'name': 'Навынос', 'state': 'selected'},
                },
                {
                    'slug': 'delivery_time',
                    'type': 'delivery_time',
                    'payload': {
                        'default': 'sixty_plus',
                        'values': [
                            {'slug': 'zero', 'text': '0', 'state': 'enabled'},
                            {
                                'slug': 'thirty',
                                'text': '30',
                                'state': 'selected',
                            },
                            {
                                'slug': 'forty_five',
                                'text': '45',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty_plus',
                                'text': '60+',
                                'state': 'enabled',
                            },
                        ],
                    },
                },
            ],
            id='delivery time and pickup',
        ),
    ],
)
async def test_filters_delivery_time_and_pickup(
        catalog_for_layout,
        eats_catalog_storage,
        request_filters,
        places,
        response_filters,
        mockserver,
):
    """
    Проверяем, что фильтр времени доставки
    продолжает приходить если выбран самовывоз,
    но не учитывается для фильтрации рестов
    """

    for idx, place in enumerate(places):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                place_type=storage.PlaceType.Native,
                timing=storage.PlaceTiming(
                    preparation=0,
                    average_preparation=place['average_preparation'] * 60,
                ),
                brand=storage.Brand(brand_id=idx),
                slug=place['slug'],
                quick_filters=storage.QuickFilters(general=[]),
            ),
        )
        zone = storage.Zone(
            zone_id=idx,
            place_id=idx,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        )
        eats_catalog_storage.add_zone(zone)

    response = await catalog_for_layout(
        location={'longitude': 37.5916, 'latitude': 55.8129},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters_v2=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters

    selected_count: int = response.json()['filters_v2']['meta'][
        'selected_count'
    ]
    assert selected_count == 2  # delivery_time + pickup

    block = layout_utils.find_block('any', response.json())
    for place in places:
        if place['in_response']:
            layout_utils.find_place_by_slug(place['slug'], block)
        else:
            layout_utils.assert_no_slug(place['slug'], block)


@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_delivery_time_filter',
    consumers=['eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'All',
            'value': {
                'min_items': 3,
                'values': [
                    {'slug': 'zero', 'text': '0', 'value': 0, 'force': True},
                    {'slug': 'thirty', 'text': '30', 'value': 30},
                    {'slug': 'forty_five', 'text': '45', 'value': 45},
                    {'slug': 'sixty', 'text': '60', 'value': 60},
                    {
                        'slug': 'sixty_plus',
                        'text': '60+',
                        'value': 'unlimited',
                    },
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.parametrize(
    'request_delivery_time, request_filters, places, response_filters',
    [
        pytest.param(
            None,
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {
                                'type': 'delivery_time',
                                'slug': 'delivery_time',
                                'payload': {'value': {'slug': 'thirty'}},
                            },
                        ],
                    },
                ],
            },
            [
                {
                    'slug': 'first',
                    'average_preparation': 15,
                    'in_response': True,
                },
                {
                    'slug': 'second',
                    'average_preparation': 35,
                    'in_response': False,
                },
                {
                    'slug': 'third',
                    'average_preparation': 60,
                    'in_response': False,
                },
                {
                    'slug': 'fourth',
                    'average_preparation': 120,
                    'in_response': False,
                },
            ],
            [
                {
                    'slug': 'delivery_time',
                    'type': 'delivery_time',
                    'payload': {
                        'default': 'sixty_plus',
                        'values': [
                            {'slug': 'zero', 'text': '0', 'state': 'enabled'},
                            {
                                'slug': 'thirty',
                                'text': '30',
                                'state': 'selected',
                            },
                            {
                                'slug': 'forty_five',
                                'text': '45',
                                'state': 'enabled',
                            },
                            {
                                'slug': 'sixty_plus',
                                'text': '60+',
                                'state': 'enabled',
                            },
                        ],
                    },
                },
            ],
            id='delivery time and asap',
        ),
        pytest.param(
            {'time': '2021-03-15T17:00:00+00:00', 'zone': 10800},
            None,
            [
                {
                    'slug': 'first',
                    'average_preparation': 15,
                    'in_response': True,
                },
                {
                    'slug': 'second',
                    'average_preparation': 35,
                    'in_response': True,
                },
                {
                    'slug': 'third',
                    'average_preparation': 60,
                    'in_response': True,
                },
                {
                    'slug': 'fourth',
                    'average_preparation': 120,
                    'in_response': True,
                },
            ],
            [],
            id='delivery time and preorder',
        ),
        pytest.param(
            {'time': '2021-03-15T17:00:00+00:00', 'zone': 10800},
            {
                'groups': [
                    {
                        'type': 'and',
                        'filters': [
                            {
                                'type': 'delivery_time',
                                'slug': 'delivery_time',
                                'payload': {'value': {'slug': 'thirty'}},
                            },
                        ],
                    },
                ],
            },
            [
                {
                    'slug': 'first',
                    'average_preparation': 15,
                    'in_response': True,
                },
                {
                    'slug': 'second',
                    'average_preparation': 35,
                    'in_response': True,
                },
                {
                    'slug': 'third',
                    'average_preparation': 60,
                    'in_response': True,
                },
                {
                    'slug': 'fourth',
                    'average_preparation': 120,
                    'in_response': True,
                },
            ],
            [],
            id='delivery time in request and preorder',
        ),
    ],
)
async def test_filters_delivery_time_and_preorder(
        catalog_for_layout,
        eats_catalog_storage,
        request_delivery_time,
        request_filters,
        places,
        response_filters,
):
    """
    Проверяем, что фильтр времени доставки
    не фильтрует выдачу и не приходит в ответе,
    если выбран предзаказ
    """

    for idx, place in enumerate(places):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                place_type=storage.PlaceType.Native,
                timing=storage.PlaceTiming(
                    preparation=0,
                    average_preparation=place['average_preparation'] * 60,
                ),
                brand=storage.Brand(brand_id=idx),
                slug=place['slug'],
                quick_filters=storage.QuickFilters(general=[]),
            ),
        )
        zone = storage.Zone(
            zone_id=idx,
            place_id=idx,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-15T10:00:00+00:00'),
                    end=parser.parse('2021-03-15T22:00:00+00:00'),
                ),
            ],
        )
        eats_catalog_storage.add_zone(zone)

    response = await catalog_for_layout(
        location={'longitude': 37.5916, 'latitude': 55.8129},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        delivery_time=request_delivery_time,
        filters_v2=request_filters,
    )

    assert eats_catalog_storage.search_times_called == 1
    assert response.status_code == 200

    filters: slice = response.json()['filters_v2']['list']
    assert filters == response_filters

    block = layout_utils.find_block('any', response.json())
    for place in places:
        if place['in_response']:
            layout_utils.find_place_by_slug(place['slug'], block)
        else:
            layout_utils.assert_no_slug(place['slug'], block)


@DELIVERY_TIME_FILTER
@pytest.mark.now('2021-03-15T15:00:00+00:00')
@pytest.mark.parametrize(
    'delivery_time_value,has_places',
    (
        pytest.param('thirty', False, id='hide close on thirty'),
        pytest.param('sixty_plus', True, id='do not hide close on infinity'),
    ),
)
async def test_filters_delivery_time_and_disabled_places(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        delivery_time_value,
        has_places,
):
    """
    Проверяет, что фильтр времени доставки отфильтровывает ресты
    не доступные к заказу в выбранный момент времени
    """

    place_slug = 'slug'

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
                    end=parser.parse('2021-03-15T12:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(request):
        data = dict(
            id=1,
            relevance=float(1),
            type='ranking',
            predicted_times=dict(min=10, max=15),
            blocks=[],
        )
        return dict(
            exp_list=[],
            request_id='',
            provider='',
            available_blocks=[],
            result=[data],
        )

    response = await catalog_for_layout(
        location={'longitude': 37.591503, 'latitude': 55.802998},
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters_v2={
            'groups': [
                {
                    'type': 'and',
                    'filters': [
                        {
                            'type': 'delivery_time',
                            'slug': 'delivery_time',
                            'payload': {
                                'value': {'slug': delivery_time_value},
                            },
                        },
                    ],
                },
            ],
        },
    )

    assert eats_catalog_storage.search_times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200
    data = response.json()

    if has_places:
        block = layout_utils.find_block('any', data)
        assert block
    else:
        layout_utils.assert_no_block_or_empty('any', data)


@pytest.mark.now('2022-01-14T12:33:00+03:00')
@pytest.mark.parametrize(
    'place_etas, response_filters',
    [
        pytest.param(
            [
                {'id': 1, 'eta': {'min': 10, 'max': 20}},
                {'id': 2, 'eta': {'min': 40, 'max': 50}},
                {'id': 3, 'eta': {'min': 5, 'max': 5}},
            ],
            [
                {'slug': 'fifteen', 'state': 'enabled', 'text': '<15'},
                {'slug': 'thirty', 'state': 'enabled', 'text': '30'},
                {'slug': 'sixty', 'state': 'selected', 'text': '60'},
            ],
            marks=delivery_time_filter_config(
                values=[
                    {'slug': 'fifteen', 'text': '<15', 'value': 10},
                    {'slug': 'thirty', 'text': '30', 'value': 30},
                    {'slug': 'forty_five', 'text': '45', 'value': 45},
                    {'slug': 'sixty', 'text': '60', 'value': 60},
                ],
            ),
        ),
        pytest.param(
            [
                {'id': 1, 'eta': {'min': 10, 'max': 20}},
                {'id': 2, 'eta': {'min': 40, 'max': 50}},
            ],
            [
                {'slug': 'thirty', 'state': 'enabled', 'text': '30'},
                {'slug': 'sixty', 'state': 'selected', 'text': '60'},
            ],
            marks=delivery_time_filter_config(
                min_items=2,
                values=[
                    {'slug': 'fifteen', 'text': '<15', 'value': 10},
                    {'slug': 'thirty', 'text': '30', 'value': 30},
                    {'slug': 'forty_five', 'text': '45', 'value': 45},
                    {'slug': 'sixty', 'text': '60', 'value': 60},
                ],
            ),
        ),
    ],
)
async def test_delivery_time_filter_config(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        place_etas,
        response_filters,
):
    for place in place_etas:
        place_id = place['id']

        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug=f'place_{place_id}',
                quick_filters=storage.QuickFilters(general=[]),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2022-01-14T10:00:00+03:00'),
                        end=parser.parse('2022-01-14T18:00:00+03:00'),
                    ),
                ],
            ),
        )

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/catalog')
    def umlaas_eats(_):
        result = []
        for place in place_etas:
            result.append(
                {
                    'id': place['id'],
                    'relevance': 0.0,
                    'type': 'ranking',
                    'predicted_times': place['eta'],
                    'blocks': [],
                },
            )
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'available_blocks': [],
            'result': result,
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert eats_catalog_storage.search_times_called == 1
    assert umlaas_eats.times_called == 1
    assert response.status_code == 200

    data = response.json()
    assert data['filters_v2']['list']

    assert (
        response_filters == data['filters_v2']['list'][0]['payload']['values']
    )
