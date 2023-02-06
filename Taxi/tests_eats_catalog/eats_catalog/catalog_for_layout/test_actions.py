# pylint: disable=too-many-lines
from dateutil import parser
import pytest

from testsuite.utils import matching

from eats_catalog import experiments
from eats_catalog import storage
from . import layout_utils

HEADERS = {
    'x-device-id': 'test_simple',
    'x-request-id': 'hello',
    'x-platform': 'superapp_taxi_web',
    'x-app-version': '1.12.0',
    'X-Eats-Session': 'blablabla',
    'cookie': 'just a cookie',
    'X-Eats-User': 'user_id=1',
}

ACTION_FREE_DELIVERY_TRANSLATION = {
    'eats-catalog': {
        'layout.free_delivery_marketplace.description': {
            'ru': 'Бесплатная доставка oт %(price)s%(currency)s',
        },
    },
}


def create_places(eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.matching_discounts_experiments(True, 'one_for_match')
@experiments.matching_discounts_experiments(True, 'two_for_match')
@experiments.matching_discounts_experiments(False, 'three_for_match')
@experiments.EATS_DISCOUNTS_ENABLE
@pytest.mark.parametrize(
    'use_eats_discounts',
    [
        pytest.param(
            True,
            marks=[
                experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG,
                experiments.sort_promo_actions(
                    consumer='eats-catalog-for-layout',
                    limit=3,
                    order={'101': 1, '3': 2, '100': 3},
                ),
            ],
            id='use_eats_discounts_sort',
        ),
        pytest.param(False, id='not_use_eats_discounts_no_sort'),
    ],
)
async def test_promos(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
        use_eats_discounts,
):
    eats_discounts_applicator.mock_eats_discounts_matches_exp = [
        'one_for_match',
        'two_for_match',
    ]
    eats_discounts_applicator.mock_eats_tags = [
        'tag1',
        '2tag',
        '3tag3',
        '1234',
    ]
    create_places(eats_catalog_storage)

    surge.set_place_info(
        place_id=1,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    place_hierarchy = 'place_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=place_hierarchy,
        name='place_free_delivery',
        description='description',
        picture_uri='picture_uri',
        extra={
            'money_value': {
                'menu_value': {
                    'value_type': 'table',
                    'value': [
                        {
                            'from_cost': '100.00000',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '100.00000',
                            },
                        },
                    ],
                },
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='101', hierarchy_name=place_hierarchy,
    )

    yandex_hierarchy = 'yandex_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=yandex_hierarchy,
        name='yandex_free_delivery',
        description='description',
        picture_uri='picture_uri',
        extra={
            'money_value': {
                'menu_value': {
                    'value_type': 'table',
                    'value': [
                        {
                            'from_cost': '50',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '100',
                            },
                        },
                    ],
                },
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='101', hierarchy_name=yandex_hierarchy,
    )

    eats_discounts_applicator.add_discount(
        discount_id='103',
        hierarchy_name='menu_discounts',
        name='name103',
        description='description103',
        picture_uri='picture_uri103',
        extra={
            'money_value': {
                'menu_value': {'value_type': 'absolute', 'value': '1000'},
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='103', hierarchy_name='menu_discounts',
    )

    eats_discounts_applicator.add_discount(
        discount_id='104',
        hierarchy_name='menu_discounts',
        name='name104',
        description='description104',
        picture_uri='picture_uri104',
        extra={
            'money_value': {
                'menu_value': {'value_type': 'absolute', 'value': '1500'},
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='104', hierarchy_name='menu_discounts',
    )

    eats_discounts_applicator.expected_retail_orders_count = 0
    eats_discounts_applicator.expected_restaurant_orders_count = 0

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': 'http://istock/harold/{w}x{h}',
                        'detailed_picture': 'http://istock/pepe/{w}x{h}',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
                {
                    'id': 2,
                    'name': 'Бесплатные тесты 2',
                    'description': 'При написании фичи, тесты в подарок 2',
                    'type': {
                        'id': 2,
                        'name': 'Тесты в подарок 2',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': True}],
                },
                {
                    'id': 3,
                    'name': 'Бесплатные тесты 3',
                    'description': 'При написании фичи, тесты в подарок 3',
                    'type': {
                        'id': 3,
                        'name': 'Тесты в подарок 3',
                        'picture': 'http://istock/harold',
                        'detailed_picture': 'http://istock/pepe',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    actions = layout_utils.find_actions('promo', place)

    exp_actions = [
        {
            'id': matching.UuidString(),
            'type': 'promo',
            'payload': {
                'icon_url': 'http://istock/harold/orig',
                'accent_color': [
                    {'theme': 'dark', 'value': '#5AC31A'},
                    {'theme': 'light', 'value': '#5AC31A'},
                ],
                'title': 'Бесплатные тесты',
                'description': 'При написании фичи, тесты в подарок',
                'promo_type_id': '1',
                'extended': {
                    'title': 'Бесплатные тесты',
                    'content': 'При написании фичи, тесты в подарок',
                    'button': {'title': 'Посмотреть всё', 'url': ''},
                },
            },
        },
    ]

    exp_actions.insert(
        0 if use_eats_discounts else 1,
        {
            'id': matching.UuidString(),
            'type': 'promo',
            'payload': {
                'icon_url': 'http://istock/harold',
                'accent_color': [
                    {'theme': 'dark', 'value': '#5AC31A'},
                    {'theme': 'light', 'value': '#5AC31A'},
                ],
                'title': 'Бесплатные тесты 3',
                'description': 'При написании фичи, тесты в подарок 3',
                'promo_type_id': '3',
                'extended': {
                    'title': 'Бесплатные тесты 3',
                    'content': 'При написании фичи, тесты в подарок 3',
                    'button': {'title': 'Посмотреть всё', 'url': ''},
                },
            },
        },
    )

    if use_eats_discounts:
        exp_actions.insert(
            0,
            {
                'id': matching.UuidString(),
                'payload': {
                    'accent_color': [
                        {'theme': 'dark', 'value': '#5AC31A'},
                        {'theme': 'light', 'value': '#5AC31A'},
                    ],
                    'description': 'description',
                    'extended': {
                        'button': {'title': 'Посмотреть всё', 'url': ''},
                        'content': 'description',
                        'title': 'yandex_free_delivery',
                    },
                    'icon_url': 'picture_uri',
                    'title': 'yandex_free_delivery',
                    'promo_type_id': '101',
                },
                'type': 'promo',
            },
        )
        exp_actions.insert(
            2,
            {
                'id': matching.UuidString(),
                'type': 'promo',
                'payload': {
                    'icon_url': 'picture_uri104',
                    'accent_color': [
                        {'theme': 'dark', 'value': '#5AC31A'},
                        {'theme': 'light', 'value': '#5AC31A'},
                    ],
                    'title': 'name104',
                    'description': 'description104',
                    'promo_type_id': '100',
                    'extended': {
                        'title': 'name104',
                        'content': 'description104',
                        'button': {'title': 'Посмотреть всё', 'url': ''},
                    },
                },
            },
        )

        exp_actions = exp_actions[:3]  # due to the limit

        assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
        assert (
            eats_discounts_applicator.mock_eats_order_stats.times_called == 3
        )
        assert eats_discounts_applicator.mock_shipping_type_array == {
            'delivery',
            'pickup',
        }
    else:
        assert (
            eats_discounts_applicator.mock_eats_order_stats.times_called == 1
        )
        assert eats_discounts_applicator.mock_eats_discounts.times_called == 0

    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )

    assert actions == exp_actions


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@experiments.matching_discounts_experiments(True, 'one_for_match')
@experiments.matching_discounts_experiments(True, 'two_for_match')
@experiments.matching_discounts_experiments(False, 'three_for_match')
async def test_new_promos(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
):
    eats_discounts_applicator.mock_eats_discounts_matches_exp = [
        'one_for_match',
        'two_for_match',
    ]
    eats_discounts_applicator.mock_eats_tags = [
        'tag1',
        '2tag',
        '3tag3',
        '1234',
    ]
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open', place_id=1, brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
            couriers_type=storage.CouriersType.Bicycle,
        ),
    )

    eats_discounts_applicator.mock_delivery_method = 'pedestrian'

    surge.set_place_info(
        place_id=1,
        surge={
            'nativeInfo': {
                'deliveryFee': 199,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )

    eats_discounts_applicator.add_discount(
        discount_id='101',
        name='place_discount',
        description='discount from place',
        picture_uri='place_picture_uri',
    )
    eats_discounts_applicator.bind_discount(place_id='1', discount_id='101')
    eats_discounts_applicator.add_discount(
        discount_id='102',
        name='yandex_discount',
        description='discount from yandex',
        picture_uri='yandex_picture_uri',
    )
    eats_discounts_applicator.bind_discount(place_id='1', discount_id='102')

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    actions = layout_utils.find_actions('promo', place)
    assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
    assert eats_discounts_applicator.mock_shipping_type_array == {
        'pickup',
        'delivery',
    }
    assert eats_discounts_applicator.mock_eats_order_stats.times_called == 3
    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )

    assert actions == [
        {
            'id': matching.UuidString(),
            'type': 'promo',
            'payload': {
                'icon_url': 'place_picture_uri',
                'accent_color': [
                    {'theme': 'dark', 'value': '#5AC31A'},
                    {'theme': 'light', 'value': '#5AC31A'},
                ],
                'title': 'place_discount',
                'promo_type_id': '103',
                'description': 'discount from place',
                'extended': {
                    'title': 'place_discount',
                    'content': 'discount from place',
                    'button': {'title': 'Посмотреть всё', 'url': ''},
                },
            },
        },
        {
            'id': matching.UuidString(),
            'type': 'promo',
            'payload': {
                'icon_url': 'yandex_picture_uri',
                'accent_color': [
                    {'theme': 'dark', 'value': '#5AC31A'},
                    {'theme': 'light', 'value': '#5AC31A'},
                ],
                'title': 'yandex_discount',
                'promo_type_id': '103',
                'description': 'discount from yandex',
                'extended': {
                    'title': 'yandex_discount',
                    'content': 'discount from yandex',
                    'button': {'title': 'Посмотреть всё', 'url': ''},
                },
            },
        },
    ]


@pytest.mark.now('2021-04-04T20:00:00+03:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
async def test_shipping_type_in_discounts_applicator(
        catalog_for_layout, eats_catalog_storage, eats_discounts_applicator,
):
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

    response = await catalog_for_layout(
        headers=HEADERS,
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

    assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
    assert eats_discounts_applicator.mock_shipping_type_array == {
        'pickup',
        'delivery',
    }
    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )
    assert eats_discounts_applicator.mock_eats_order_stats.times_called == 3


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.parametrize(
    'dimensions, promo_picture, expected_picture',
    [
        pytest.param(
            None,
            'http://picture/{w}x{h}',
            'http://picture/orig',
            id='empty setting should render as original',
        ),
        pytest.param(
            None,
            'http://picture/{w}x{h}/{w}x{h}',
            'http://picture/orig/orig',
            id='all templates should be replaced',
        ),
        pytest.param(
            None,
            'http://picture/',
            'http://picture/',
            id='without template should be unchanged',
        ),
        pytest.param(
            {'width': 110, 'height': 121},
            'http://picture/{w}x{h}',
            'http://picture/110x121',
            id='setting should be placed in template',
        ),
        pytest.param(
            {'width': 11, 'height': 12},
            'http://picture/{w}x{h}/{w}x{h}',
            'http://picture/11x12/11x12',
            id='all templates should be replaced',
        ),
        pytest.param(
            {'width': 122, 'height': 12},
            'http://picture/',
            'http://picture/',
            id='without template should be unchanged',
        ),
    ],
)
async def test_promo_image(
        catalog_for_layout,
        taxi_config,
        eats_catalog_storage,
        mockserver,
        dimensions,
        promo_picture,
        expected_picture,
):
    create_places(eats_catalog_storage)

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {
            'cursor': '',
            'promos': [
                {
                    'id': 1,
                    'name': 'Бесплатные тесты',
                    'description': 'При написании фичи, тесты в подарок',
                    'type': {
                        'id': 1,
                        'name': 'Тесты в подарок',
                        'picture': promo_picture,
                        'detailed_picture': 'http://istock/pepe/{w}x{h}',
                    },
                    'places': [{'id': 1, 'disabled_by_surge': False}],
                },
            ],
        }

    taxi_config.set_values(
        {
            'EATS_CATALOG_PROMO_ACTION': {
                'accent_color': [],
                'button_title': '',
                'picture_dimensions': dimensions,
            },
        },
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    actions = layout_utils.find_actions('promo', place)

    assert len(actions) == 1
    assert actions[0]['payload']['icon_url'] == expected_picture


@pytest.mark.now('2021-06-03T12:00:00+00:00')
@pytest.mark.parametrize(
    'features, reviews',
    [
        pytest.param(storage.Features(), None, id='no editorial data'),
        pytest.param(
            storage.Features(editorial_description='hello'),
            None,
            id='no editorial verdict',
        ),
        pytest.param(
            storage.Features(editorial_verdict='hello'),
            None,
            id='no editorial description',
        ),
        pytest.param(
            storage.Features(
                editorial_verdict='hello', editorial_description='',
            ),
            None,
            id='empty editorial description',
        ),
        pytest.param(
            storage.Features(
                editorial_verdict='', editorial_description='hello',
            ),
            None,
            id='empty editorial verdict',
        ),
        pytest.param(
            storage.Features(
                editorial_verdict='title', editorial_description='description',
            ),
            {'title': 'title', 'description': 'description'},
            id='has review',
        ),
        pytest.param(
            storage.Features(
                editorial_verdict='title', editorial_description='description',
            ),
            {'title': 'title', 'description': 'description'},
            id='has review',
        ),
        pytest.param(
            storage.Features(
                editorial_verdict='title', editorial_description='description',
            ),
            None,
            id='has review, disabled',
            marks=experiments.DISABLE_REVIEW_ACTION,
        ),
    ],
)
async def test_review(
        catalog_for_layout, eats_catalog_storage, features, reviews,
):
    """
    EDACAT-1139: тест проверяет, что пустые вердикты игнорируются в сторадже.
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='open', name='place_1', features=features,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-03T10:00:00+00:00'),
                    end=parser.parse('2021-06-03T23:00:00+00:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)

    if reviews is None:
        layout_utils.assert_no_actions('review', place)
    else:
        actions = layout_utils.find_actions('review', place)
        assert len(actions) == 1
        assert actions[0]['payload']['description'] == reviews['title']
        assert (
            actions[0]['payload']['extended']['content']
            == reviews['description']
        )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@experiments.EATS_DISCOUNTS_PROMO_TYPES_INFO
async def test_marketplace_remove_discount(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
):
    """
    EDAJAM-536, EDAJAM-697: тест проверяет, что скидки на доставку в
    МП удаляются
    """
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            place_type=storage.PlaceType.Marketplace,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=99),
                storage.DeliveryCondition(order_cost=999, delivery_cost=0),
            ],
        ),
    )

    yandex_hierarchy = 'yandex_delivery_discounts'
    eats_discounts_applicator.add_discount(
        discount_id='101',
        hierarchy_name=yandex_hierarchy,
        name='yandex_free_delivery',
        description='description',
        picture_uri='picture_uri',
        promo_type='delivery_discount',  # custom
        extra={
            'money_value': {
                'menu_value': {
                    'value_type': 'table',
                    'value': [
                        {
                            'from_cost': '50',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '100',
                            },
                        },
                    ],
                },
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='101', hierarchy_name=yandex_hierarchy,
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    layout_utils.assert_no_actions('promo', place)
    assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
    assert eats_discounts_applicator.mock_shipping_type_array == {
        'pickup',
        'delivery',
    }
    assert eats_discounts_applicator.mock_eats_order_stats.times_called == 3
    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.translations(**ACTION_FREE_DELIVERY_TRANSLATION)
@experiments.eats_discounts_for_marketplaces(
    {
        'id': 101,
        'name': 'Бесплатная доставка',
        'type': {
            'id': 101,
            'name': 'Бесплатная доставка',
            'picture': 'url',
            'detailed_picture': 'url',
        },
        'excluded_tag': 'not',
        'description': 'layout.free_delivery_marketplace.description',
    },
)
async def test_marketplace_discount(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
):
    """
    EDAJAM-491: тест проверяет, что на маркетплейсы, подходящие под условия,
    навесился промик по бесплатной доставке.
    """
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            place_type=storage.PlaceType.Marketplace,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=99),
                storage.DeliveryCondition(order_cost=999, delivery_cost=0),
            ],
        ),
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    actions = layout_utils.find_actions('promo', place)
    assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
    assert eats_discounts_applicator.mock_shipping_type_array == {
        'pickup',
        'delivery',
    }
    assert eats_discounts_applicator.mock_eats_order_stats.times_called == 3
    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )
    assert {
        'id': matching.UuidString(),
        'type': 'promo',
        'payload': {
            'icon_url': 'url',
            'accent_color': [
                {'theme': 'dark', 'value': '#5AC31A'},
                {'theme': 'light', 'value': '#5AC31A'},
            ],
            'title': 'Бесплатная доставка',
            'description': 'Бесплатная доставка oт 999₽',
            'extended': {
                'title': 'Бесплатная доставка',
                'content': 'Бесплатная доставка oт 999₽',
                'button': {'title': 'Посмотреть всё', 'url': ''},
            },
            'promo_type_id': '101',
        },
    } in actions


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.translations(**ACTION_FREE_DELIVERY_TRANSLATION)
@experiments.eats_discounts_for_marketplaces(
    {
        'id': 101,
        'name': 'Бесплатная доставка',
        'type': {
            'id': 101,
            'name': 'Бесплатная доставка',
            'picture': 'url',
            'detailed_picture': 'url',
        },
        'excluded_tag': 'not',
        'description': 'layout.free_delivery_marketplace.description',
    },
)
async def test_marketplace_discount_corner_case(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
):
    """
    EDAJAM-571: тест проверяет невыставление бейджика бесплатной
    доставки маркетплейсам, когда их последний трешхолд ненулевой.
    """
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            place_type=storage.PlaceType.Marketplace,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
                storage.DeliveryCondition(order_cost=999, delivery_cost=1000),
            ],
        ),
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)
    assert not place['payload']['data']['actions']
    assert eats_discounts_applicator.mock_eats_discounts.times_called == 2
    assert eats_discounts_applicator.mock_shipping_type_array == {
        'pickup',
        'delivery',
    }
    assert eats_discounts_applicator.mock_eats_order_stats.times_called == 3
    assert (
        eats_discounts_applicator.mock_eats_catalog_storage.times_called == 0
    )


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.translations(**ACTION_FREE_DELIVERY_TRANSLATION)
@experiments.eats_discounts_for_marketplaces(
    {
        'id': 101,
        'name': 'Бесплатная доставка',
        'type': {
            'id': 101,
            'name': 'Бесплатная доставка',
            'picture': 'url',
            'detailed_picture': 'url',
        },
        'excluded_tag': 'not',
        'description': 'layout.free_delivery_marketplace.description',
    },
)
async def test_marketplace_with_tag_discount(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        surge,
        eats_discounts_applicator,
):
    """
    EDAJAM-491: тест проверяет, что на маркетплейсы, подходящие под условия,
    но с исключающим тегом, не навесился промик по бесплатной доставке.
    """
    eats_catalog_storage.add_place(
        storage.Place(
            slug='open',
            place_id=1,
            brand=storage.Brand(brand_id=1),
            place_type=storage.PlaceType.Marketplace,
            tags=['not', 'sa'],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T14:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=99),
                storage.DeliveryCondition(order_cost=999, delivery_cost=0),
            ],
        ),
    )

    @mockserver.json_handler('/eats-core-promo/server/api/v1/promo/active')
    def _active(_):
        return {'cursor': '', 'promos': []}

    response = await catalog_for_layout(
        headers=HEADERS,
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert response.status_code == 200

    data = response.json()

    block = layout_utils.find_block('open', data)
    place = layout_utils.find_place_by_slug('open', block)

    assert not place['payload']['data']['actions']
