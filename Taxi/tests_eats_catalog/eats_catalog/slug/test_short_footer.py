# flake8: noqa IS001
from typing import List

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils


SLUG_FOOTER_ENABLED = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_catalog_reward_banner_enabled',
    consumers=['eats-catalog-slug'],
    clauses=[],
    default_value={'enabled': True},
)

COLOR = [
    {'theme': 'light', 'value': '#000000'},
    {'theme': 'dark', 'value': '#FFFFFF'},
]


def get_composers_list(composers: List[str]):
    return pytest.mark.experiments3(
        is_config=True,
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='eats_short_footer_composers',
        consumers=['eats_cart/reward_composer'],
        clauses=[],
        default_value={'composers': composers},
    )


DELIVERY_RANGE_COMPOSER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_reward_delivery_range_composer',
    consumers=['eats_cart/reward_composer'],
    clauses=[
        {
            'title': 'Pickup',
            'value': {
                'reward_banner': {
                    'icon': 'pickup',
                    'text': {
                        'text': 'С собой . Готовят {delivery_time_range} мин',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': '{place_address}',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {'type': 'bool', 'init': {'arg_name': 'is_pickup'}},
        },
        {
            'title': 'Pickup',
            'value': {
                'reward_banner': {
                    'icon': 'pickup',
                    'text': {
                        'text': 'ROVER',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': 'rover',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'is_rover_available'},
            },
        },
    ],
    default_value={
        'reward_banner': {
            'icon': 'icon',
            'text': {
                'text': (
                    'Доставка {delivery_range}{currency_sign} '
                    '. {delivery_time_range} мин.'
                ),
                'color': COLOR,
                'styles': {'rainbow': False},
            },
        },
    },
)


DELIVERY_AND_DISTANCE_COMPOSER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_reward_threshold_delivery_and_distance_composer',
    consumers=['eats_cart/reward_composer'],
    clauses=[
        {
            'title': 'any-title',
            'value': {
                'reward_banner': {
                    'icon': 'icon',
                    'title': {
                        'text': (
                            '{delivery_time_range} мин . '
                            'Доставка {delivery_range} {sign}'
                        ),
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': 'Курьер на авто {distance_km}',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {'type': 'true', 'init': {}},
        },
    ],
    default_value=None,
)

PREORDER_FOOTER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_reward_order_availability_composer',
    consumers=['eats_cart/reward_composer'],
    clauses=[
        {
            'title': 'any-title',
            'value': {
                'reward_banner': {
                    'icon': 'icon',
                    'text': {
                        'text': 'Test preorder in {minutes_to_preorder} mins. Delivery {delivery_time_range} min.',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': 'Test preorder at {preorder_time}. Min cart {min_cart} {currency_sign}.',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {'type': 'true', 'init': {}},
        },
    ],
    default_value=None,
)

DELIVERY_AND_DISTANCE_COMPOSER_TO_TRANSLATE = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_reward_threshold_delivery_and_distance_composer',
    consumers=['eats_cart/reward_composer'],
    clauses=[
        {
            'title': 'any-title',
            'value': {
                'reward_banner': {
                    'icon': 'icon',
                    'title': {
                        'text': 'Меня не видно',
                        'tanker_key': 'text',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': 'Меня не видно',
                        'tanker_key': 'description',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {'type': 'true', 'init': {}},
        },
    ],
    default_value=None,
)

PROMO_FOOTER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_reward_short_promo_composer',
    consumers=['eats_cart/reward_composer'],
    clauses=[
        {
            'title': 'any-title',
            'value': {
                'reward_banner': {
                    'icon': 'icon',
                    'title': {
                        'text': 'Amount need {amount_need}, promo range{promo_delivery_range}, value {promo_value} {sign}',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                    'description': {
                        'text': '{delivery_range} {currency_sign}',
                        'color': COLOR,
                        'styles': {'rainbow': False},
                    },
                },
            },
            'predicate': {'type': 'true', 'init': {}},
        },
    ],
    default_value=None,
)


TRANSLATIONS = {
    'eats-reward-composer': {
        'description': {'ru': 'Курьер на авто %(distance_km)s'},
        'text': {
            'ru': (
                '%(delivery_time_range)s мин . '
                'Доставка %(delivery_range)s %(sign)s'
            ),
        },
    },
}


def get_enable_translation(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_reward_enable_translation',
        consumers=['eats_cart/reward_composer'],
        is_config=False,
        default_value={'enabled': enabled},
    )


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@get_composers_list(['delivery_range'])
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@SLUG_FOOTER_ENABLED
@DELIVERY_RANGE_COMPOSER
@pytest.mark.parametrize(
    'shipping_type, surge_info, allow_delivery, allow_pickup, '
    'expected_banner_response',
    [
        pytest.param(
            'delivery',
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 10,
                'show_radius': 1000.0,
            },
            True,
            False,
            {
                'icon': 'icon',
                'name': {'color': COLOR, 'text': 'Доставка 210₽ . 35–45 мин.'},
                'description': {'color': [], 'text': ''},
            },
            id='footer_delivery_surge',
        ),
        pytest.param(
            'pickup',
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            True,
            True,
            {
                'icon': 'pickup',
                'name': {'color': COLOR, 'text': 'С собой . Готовят 10 мин'},
                'description': {
                    'color': COLOR,
                    'text': 'Новодмитровская улица, 2к6',
                },
            },
            id='footer_pickup',
        ),
        pytest.param(
            'delivery',
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            True,
            True,
            {
                'icon': 'pickup',
                'name': {'color': COLOR, 'text': 'ROVER'},
                'description': {'color': COLOR, 'text': 'rover'},
            },
            id='rover_footer',
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
        ),
    ],
)
async def test_short_footer(
        slug,
        eats_catalog_storage,
        surge_resolver,
        delivery_price,
        shipping_type,
        surge_info,
        allow_delivery,
        allow_pickup,
        expected_banner_response,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_1',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )
    if allow_delivery:
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=1,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-07-25T10:00:00+03:00'),
                        end=parser.parse('2021-07-25T20:00:00+03:00'),
                    ),
                ],
            ),
        )
    if allow_pickup:
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=2,
                shipping_type=storage.ShippingType.Pickup,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-07-25T10:00:00+03:00'),
                        end=parser.parse('2021-07-25T20:00:00+03:00'),
                    ),
                ],
            ),
        )

    if allow_delivery:
        delivery_price.set_delivery_conditions(
            [
                {'delivery_cost': 529.0, 'order_price': 0.0},
                {'delivery_cost': 329.0, 'order_price': 500.0},
                {'delivery_cost': 200.0, 'order_price': 2000.0},
            ],
        )
        delivery_price.set_place_surge(
            {'placeId': 1, 'nativeInfo': surge_info},
        )
        show_radius = surge_info.get('show_radius')
        surge_resolver.place_radius = {
            1: surge_utils.SurgeRadius(pedestrian=show_radius),
        }

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': shipping_type,
        },
    )

    assert response.status_code == 200

    data = response.json()

    if expected_banner_response is None:
        assert 'bottomBanner' not in data['payload']['foundPlace']
    else:
        assert (
            data['payload']['foundPlace']['bottomBanner']
            == expected_banner_response
        )


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@get_composers_list(['threshold_delivery_and_distance'])
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@SLUG_FOOTER_ENABLED
@DELIVERY_AND_DISTANCE_COMPOSER
@pytest.mark.parametrize(
    'courier_type, surge_info, expected_banner_response',
    [
        pytest.param(
            storage.CouriersType.Pedestrian,
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            {
                'icon': 'icon',
                'name': {
                    'color': COLOR,
                    'text': '35–45 мин . Доставка 50–140 ₽',
                },
                'description': {'color': [], 'text': ''},
            },
            id='pedestrian',
        ),
        pytest.param(
            storage.CouriersType.YandexTaxi,
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            {
                'icon': 'icon',
                'name': {
                    'color': COLOR,
                    'text': '35–45 мин . Доставка 50–140 ₽',
                },
                'description': {
                    'color': COLOR,
                    'text': 'Курьер на авто 1,5 км',
                },
            },
            id='yandex_taxi',
        ),
        pytest.param(
            storage.CouriersType.Vehicle,
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            {
                'icon': 'icon',
                'name': {
                    'color': COLOR,
                    'text': '35–45 мин . Доставка 50–140 ₽',
                },
                'description': {
                    'color': COLOR,
                    'text': 'Курьер на авто 1,5 км',
                },
            },
            id='vehicle',
        ),
    ],
)
async def test_delivery_and_distance(
        slug,
        eats_catalog_storage,
        surge_resolver,
        delivery_price,
        courier_type,
        surge_info,
        expected_banner_response,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_1',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=courier_type,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
    )
    # Стоимость доставки выбрана достаточно маленькая, чтобы не связываться
    # с nativeMaxDeliveryFee.
    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 140.0, 'order_price': 0.0},
            {'delivery_cost': 120.0, 'order_price': 500.0},
            {'delivery_cost': 50.0, 'order_price': 2000.0},
        ],
    )
    delivery_price.set_place_surge({'placeId': 1, 'nativeInfo': surge_info})
    show_radius = surge_info.get('show_radius')
    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(pedestrian=show_radius),
    }

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
    )
    assert response.status_code == 200

    bottom_banner = response.json()['payload']['foundPlace']['bottomBanner']
    assert bottom_banner == expected_banner_response


@get_enable_translation(True)
@get_composers_list(['availability_and_preorder'])
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@SLUG_FOOTER_ENABLED
@PREORDER_FOOTER
@pytest.mark.now('2021-05-12T13:11:00+03:00')
async def test_short_footer_preorder(slug, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='not_open_yet',
            timing=storage.PlaceTiming(average_preparation=20 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-05-12T18:00:00+03:00'),
                    end=parser.parse('2021-05-12T23:00:00+03:00'),
                ),
            ],
        ),
    )

    # Запрашиваем слаг для того чтобы определить ближайшее возможное
    # время, на которое можно оформить предзаказ.
    response = await slug(
        'not_open_yet', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200
    assert response.json()['payload']['foundPlace']['bottomBanner'] == {
        'icon': 'icon',
        'name': {
            'color': COLOR,
            'text': 'Test preorder in 439 mins. Delivery 115–125 min.',
        },
        'description': {
            'color': COLOR,
            'text': 'Test preorder at 20:30. Min cart 0 ₽.',
        },
    }


@get_enable_translation(True)
@pytest.mark.translations(**TRANSLATIONS)
@get_composers_list(['threshold_delivery_and_distance'])
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@pytest.mark.config(EATS_REWARD_COMPOSER_CURRENCY_ROUNDING={'USD': 1})
@SLUG_FOOTER_ENABLED
@DELIVERY_AND_DISTANCE_COMPOSER_TO_TRANSLATE
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.now('2021-05-12T18:11:00+03:00')
async def test_footer_localiser(
        slug,
        eats_catalog_storage,
        eats_discounts_applicator,
        delivery_price,
        surge_resolver,
):

    surge_info = {
        'surgeLevel': 1,
        'loadLevel': 1,
        'deliveryFee': 200,
        'show_radius': 1000.0,
    }

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_1',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=storage.CouriersType.Vehicle,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
    )
    # Стоимость доставки выбрана достаточно маленькая, чтобы не связываться
    # с nativeMaxDeliveryFee.
    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 140.0, 'order_price': 0.0},
            {'delivery_cost': 120.0, 'order_price': 500.0},
            {'delivery_cost': 50.0, 'order_price': 2000.0},
        ],
    )
    delivery_price.set_place_surge({'placeId': 1, 'nativeInfo': surge_info})
    show_radius = surge_info.get('show_radius')
    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(pedestrian=show_radius),
    }

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
    )
    assert response.status_code == 200

    bottom_banner = response.json()['payload']['foundPlace']['bottomBanner']
    assert bottom_banner == {
        'icon': 'icon',
        'name': {'color': COLOR, 'text': '35–45 мин . Доставка 50–140 ₽'},
        'description': {'color': COLOR, 'text': 'Курьер на авто 1,5 км'},
    }


@get_composers_list(['promo'])
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@pytest.mark.config(EATS_REWARD_COMPOSER_CURRENCY_ROUNDING={'RUB': 1})
@pytest.mark.config(EATS_CATALOG_PROMO_FOOTER_PRIORITY={'delivery': 100})
@SLUG_FOOTER_ENABLED
@PROMO_FOOTER
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.now('2021-05-12T18:11:00+03:00')
async def test_promo_footer(
        slug,
        eats_catalog_storage,
        eats_discounts_applicator,
        delivery_price,
        surge_resolver,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='with_promo',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
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
                            'from_cost': '10.00000',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '71',
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

    eats_discounts_applicator.add_discount(
        discount_id='102',
        hierarchy_name=place_hierarchy,
        name='yandex_free_delivery',
        description='description',
        picture_uri='picture_uri',
        extra={
            'money_value': {
                'menu_value': {
                    'value_type': 'table',
                    'value': [
                        {
                            'from_cost': '0',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '50',
                            },
                        },
                    ],
                },
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='102', hierarchy_name=place_hierarchy,
    )

    eats_discounts_applicator.add_discount(
        discount_id='103',
        hierarchy_name='menu_discounts',
        name='name103',
        description='description103',
        picture_uri='picture_uri103',
        extra={
            'money_value': {
                'menu_value': {
                    'value_type': 'table',
                    'value': [
                        {
                            'from_cost': '0',
                            'discount': {
                                'value_type': 'fraction',
                                'value': '70',
                            },
                        },
                    ],
                },
            },
        },
    )
    eats_discounts_applicator.bind_discount(
        place_id='1', discount_id='103', hierarchy_name='menu_discounts',
    )

    surge_info = {
        'surgeLevel': 1,
        'loadLevel': 1,
        'deliveryFee': 200,
        'show_radius': 1000.0,
    }

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 140.0, 'order_price': 0.0},
            {'delivery_cost': 120.0, 'order_price': 500.0},
            {'delivery_cost': 54.12, 'order_price': 2000.0},
        ],
    )
    delivery_price.set_place_surge({'placeId': 1, 'nativeInfo': surge_info})
    show_radius = surge_info.get('show_radius')
    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(pedestrian=show_radius),
    }

    response = await slug(
        'with_promo',
        query={
            'latitude': 55.73442,
            'longitude': 37.583948,
            'shippingType': 'delivery',
        },
    )

    assert response.json()['payload']['foundPlace']['bottomBanner'] == {
        'icon': 'icon',
        'name': {
            'color': COLOR,
            'text': 'Amount need 0, promo range15,6–70, value 50 %',
        },
        'description': {'color': COLOR, 'text': '54,1–140 ₽'},
    }
