from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils

SHIPPING_INFO_TRANSLATIONS = {
    'eats-catalog': {
        'slug.delivery_fee.description': {
            'ru': 'Обычно от %(n_price)s %(s_currency_sign)s',
        },
        'slug.delivery_fee.value.free_of_charge': {'ru': 'Бесплатно'},
        'slug.delivery_fee.value.price': {
            'ru': '%(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_info.name.courier': {'ru': 'Курьером'},
        'slug.shipping_info.name.taxi': {'ru': 'Курьером на автомобиле'},
        'slug.shipping_info.name.marketplace_courier': {
            'ru': 'Курьером ресторана',
        },
        'slug.shipping_info.name.pickup': {'ru': 'С собой'},
        'slug.shipping_info.name.rover': {'ru': 'Ровером'},
        'slug.shipping_info.continuous_thresholds.message': {
            'ru': 'Цена ниже за каждые 100 %(s_currency_sign)s в заказе',
        },
        'slug.shipping_info.continuous_thresholds.low': {
            'ru': 'Заказ от 0 %(s_currency_sign)s',
        },
        'slug.shipping_info.continuous_thresholds.high': {
            'ru': 'Заказ от %(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_info.continuous_thresholds.value': {
            'ru': '%(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_thresholds.name.from': {
            'ru': 'Заказ от %(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_thresholds.name.up_to': {
            'ru': 'Заказ до %(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_thresholds.value': {
            'ru': '%(n_price)s %(s_currency_sign)s',
        },
    },
}

EXPECTED_THRESHOLDS = [
    {'name': 'Заказ до 499 ₽', 'value': '100 ₽'},
    {'name': 'Заказ до 1999 ₽', 'value': '60 ₽'},
    {'name': 'Заказ от 2000 ₽', 'value': '30 ₽'},
]

EXPECTED_DELIVERY_FEE = {
    'icon': 'asset://icon_high_price',
    'name': {
        'color': [{'theme': 'light', 'value': '#ff0000'}],
        'text': '130 ₽',  # min_threshold + surge_delivery_fee
    },
    'description': 'Обычно от 30 ₽',
}

EXPECTED_INFO_PICKUP = {
    'icon': 'asset://icon_pickup',
    'name': 'С собой',
    'deliveryFee': {
        'name': {
            'color': [{'theme': 'light', 'value': '#00ff00'}],
            'text': 'Бесплатно',
        },
    },
}

EXPECTED_INFO_ROVER = {
    'icon': 'asset://icon_rover',
    'name': 'Ровером',
    'deliveryFee': {
        'name': {
            'color': [{'theme': 'light', 'value': '#00ff00'}],
            'text': 'Бесплатно',
        },
    },
}


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@experiments.eats_catalog_surge_radius()
@pytest.mark.translations(**SHIPPING_INFO_TRANSLATIONS)
@pytest.mark.parametrize(
    'surge_info, allow_pickup, expected_shipping_info',
    [
        pytest.param(
            None,
            True,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='no surge, courier+pickup+rover',
        ),
        pytest.param(
            None,
            True,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
            ],
            id='no surge, courier+pickup',
        ),
        pytest.param(
            None,
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='no surge, courier+rover',
        ),
        pytest.param(
            None,
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
            ],
            id='no surge, courier',
        ),
        pytest.param(
            None,
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
            ],
            marks=experiments.currency_sign('ignored'),
            id='no surge, courier, ignore currency sign',
        ),
        pytest.param(
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            True,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
            ],
            id='radius surge, courier+pickup',
        ),
        pytest.param(
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
            ],
            id='radius surge, courier',
        ),
        pytest.param(
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 100},
            True,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'deliveryFee': EXPECTED_DELIVERY_FEE,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='price surge, courier+pickup+rover',
        ),
        pytest.param(
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 100},
            True,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'deliveryFee': EXPECTED_DELIVERY_FEE,
                },
                EXPECTED_INFO_PICKUP,
            ],
            id='price surge, courier+pickup',
        ),
        pytest.param(
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 100},
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'deliveryFee': EXPECTED_DELIVERY_FEE,
                },
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='price surge, courier+rover',
        ),
        pytest.param(
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 100},
            False,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'deliveryFee': EXPECTED_DELIVERY_FEE,
                },
            ],
            id='price surge, courier',
        ),
    ],
)
async def test_shipping_info(
        slug,
        eats_catalog_storage,
        surge_resolver,
        delivery_price,
        surge_info,
        allow_pickup,
        expected_shipping_info,
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
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=100),
                storage.DeliveryCondition(order_cost=500, delivery_cost=60),
                storage.DeliveryCondition(order_cost=2000, delivery_cost=30),
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

    # Стоимость доставки выбрана достаточно маленькая, чтобы не связываться
    # с nativeMaxDeliveryFee.
    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 100.0, 'order_price': 0.0},
            {'delivery_cost': 60.0, 'order_price': 500.0},
            {'delivery_cost': 30.0, 'order_price': 2000.0},
        ],
    )
    if surge_info is not None:
        delivery_price.set_place_surge(
            {'placeId': 1, 'nativeInfo': surge_info},
        )
        show_radius = surge_info.get('show_radius')
        if show_radius:
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
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data['payload']['foundPlace']['locationParams']['shippingInfo']
        == expected_shipping_info
    )


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@pytest.mark.translations(**SHIPPING_INFO_TRANSLATIONS)
@pytest.mark.parametrize(
    'allow_pickup, place_type, couriers_type, expected_shipping_info',
    [
        pytest.param(
            True,
            storage.PlaceType.Native,
            storage.CouriersType.Pedestrian,
            [
                {
                    'icon': 'asset://icon_courier',
                    'name': 'Курьером',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='courier+pickup+rover',
        ),
        pytest.param(
            True,
            storage.PlaceType.Marketplace,
            storage.CouriersType.Vehicle,
            [
                {
                    'icon': 'asset://icon_taxi',
                    'name': 'Курьером на автомобиле',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='taxi+pickup+rover',
        ),
        pytest.param(
            True,
            storage.PlaceType.Marketplace,
            storage.CouriersType.Pedestrian,
            [
                {
                    'icon': 'asset://icon_marketplace_courier',
                    'name': 'Курьером ресторана',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='marketplace courier+pickup+rover',
        ),
        pytest.param(
            True,
            storage.PlaceType.Marketplace,
            storage.CouriersType.YandexTaxi,
            [
                {
                    'icon': 'asset://icon_taxi',
                    'name': 'Курьером на автомобиле',
                    'thresholds': EXPECTED_THRESHOLDS,
                },
                EXPECTED_INFO_PICKUP,
                EXPECTED_INFO_ROVER,
            ],
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='marketplace courier+taxi+pickup+rover',
        ),
    ],
)
async def test_shipping_info_by_courier_type(
        slug,
        eats_catalog_storage,
        allow_pickup,
        place_type,
        couriers_type,
        expected_shipping_info,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_1',
            place_type=place_type,
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=couriers_type,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=100),
                storage.DeliveryCondition(order_cost=500, delivery_cost=60),
                storage.DeliveryCondition(order_cost=2000, delivery_cost=30),
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

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data['payload']['foundPlace']['locationParams']['shippingInfo']
        == expected_shipping_info
    )


@pytest.mark.parametrize(
    [],
    [
        pytest.param(id='pricing calc'),
        pytest.param(
            marks=[
                experiments.ENABLE_CONTINUOUS_THRESHOLDS_CALC,
                experiments.currency_sign('₽'),
            ],
            id='catalog calc',
        ),
    ],
)
@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@pytest.mark.translations(**SHIPPING_INFO_TRANSLATIONS)
async def test_pricing_thresholds(slug, eats_catalog_storage, delivery_price):
    """
    Проверяем, что если прайсинг отвечает с полем
    thresholds_info, то эти данные как есть
    попадают в ответ слага в shippingInfo
    """

    thresholds = [
        {'name': 'Цена ниже за каждые 100 ₽ в заказе', 'value': ' '},
        {'name': 'Заказ от 0 ₽', 'value': '399 ₽'},
        {'name': 'Заказ от 1100 ₽', 'value': '0 ₽'},
    ]
    thresholds_fees = [
        {'delivery_cost': '399', 'order_price': '0'},
        {'delivery_cost': '0', 'order_price': '1100'},
    ]

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
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 100.0, 'order_price': 0.0},
            {'delivery_cost': 60.0, 'order_price': 500.0},
            {'delivery_cost': 30.0, 'order_price': 2000.0},
        ],
    )

    delivery_price.set_place_surge({'placeId': 1})

    # Тут осознано цифры не такие же как в
    # delivery_conditions, чтобы проверить что оно действительно
    # пробрасывается без изменений
    delivery_price.set_thresholds_info(
        {'thresholds': thresholds, 'thresholds_fees': thresholds_fees},
    )

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()

    shipping_info = data['payload']['foundPlace']['locationParams'][
        'shippingInfo'
    ]
    couriers_thresholds = shipping_info[0]['thresholds']

    assert couriers_thresholds == thresholds


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@pytest.mark.translations(**SHIPPING_INFO_TRANSLATIONS)
async def test_non_zero_min_price(slug, eats_catalog_storage, delivery_price):
    """
    Проверяем, что при сурже берется
    минимальный ненулевой трешхолд
    в сообщение "обычно от"
    """

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
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 200, 'order_price': 0.0},
            {'delivery_cost': 100, 'order_price': 500.0},
            {'delivery_cost': 0, 'order_price': 2000.0},
        ],
    )

    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 100,
            },
        },
    )

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()

    shipping_info = data['payload']['foundPlace']['locationParams'][
        'shippingInfo'
    ]
    assert shipping_info[0] == {
        'icon': 'asset://icon_courier',
        'name': 'Курьером',
        'deliveryFee': {
            'icon': 'asset://icon_high_price',
            'name': {
                'color': [{'theme': 'light', 'value': '#ff0000'}],
                'text': '200 ₽',  # min_threshold + surge_delivery_fee
            },
            'description': 'Обычно от 100 ₽',
        },
    }


@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@pytest.mark.translations(**SHIPPING_INFO_TRANSLATIONS)
@experiments.EATS_DISCOUNTS_ENABLE
@experiments.EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG
@pytest.mark.parametrize(
    'courier_info, is_continuous',
    [
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'thresholds': [
                    {'name': 'Заказ до 499 ₽', 'value': '200 ₽'},
                    {'name': 'Заказ до 1999 ₽', 'value': '100 ₽'},
                    {'name': 'Заказ от 2000 ₽', 'value': '0 ₽'},
                ],
            },
            False,
            id='no promo',
        ),
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'thresholds': [
                    {'name': 'Заказ до 499 ₽', 'value': '100 ₽'},
                    {'name': 'Заказ до 1999 ₽', 'value': '50 ₽'},
                    {'name': 'Заказ от 2000 ₽', 'value': '0 ₽'},
                ],
            },
            False,
            marks=[experiments.ENABLE_SHIPPING_FEE_WITH_PROMO_CALC],
            id='promo',
        ),
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'deliveryFee': {
                    'icon': 'asset://icon_high_price',
                    'name': {
                        'color': [{'theme': 'light', 'value': '#ff0000'}],
                        'text': '200 ₽',
                    },
                    'description': 'Обычно от 100 ₽',
                },
            },
            False,
            marks=pytest.mark.now('2021-07-25T15:00:00+03:00'),
            id='surge no promo',
        ),
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'deliveryFee': {
                    'icon': 'asset://icon_high_price',
                    'name': {
                        'color': [{'theme': 'light', 'value': '#ff0000'}],
                        'text': '100 ₽',
                    },
                    'description': 'Обычно от 100 ₽',
                },
            },
            False,
            marks=[
                pytest.mark.now('2021-07-25T15:00:00+03:00'),
                experiments.ENABLE_SHIPPING_FEE_WITH_PROMO_CALC,
            ],
            id='surge promo',
        ),
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'thresholds': [
                    {
                        'name': 'Цена ниже за каждые 100 ₽ в заказе',
                        'value': ' ',
                    },
                    {'name': 'Заказ от 0 ₽', 'value': '400 ₽'},
                    {'name': 'Заказ от 1100 ₽', 'value': '0 ₽'},
                ],
            },
            True,
            id='continuous no promo',
        ),
        pytest.param(
            {
                'icon': 'asset://icon_courier',
                'name': 'Курьером',
                'thresholds': [
                    {
                        'name': 'Цена ниже за каждые 100 ₽ в заказе',
                        'value': ' ',
                    },
                    {'name': 'Заказ от 0 ₽', 'value': '200 ₽'},
                    {'name': 'Заказ от 1100 ₽', 'value': '0 ₽'},
                ],
            },
            True,
            marks=[
                experiments.ENABLE_SHIPPING_FEE_WITH_PROMO_CALC,
                experiments.ENABLE_CONTINUOUS_THRESHOLDS_CALC,
                experiments.currency_sign('₽'),
            ],
            id='continuous promo',
        ),
    ],
)
async def test_shipping_info_promo(
        slug,
        eats_catalog_storage,
        eats_discounts_applicator,
        delivery_price,
        courier_info,
        is_continuous,
):
    """
    Проверяем, что применяется скидка к стоимости доставки курьером
    """

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
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-07-25T10:00:00+03:00'),
                    end=parser.parse('2021-07-25T20:00:00+03:00'),
                ),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 200, 'order_price': 0.0},
            {'delivery_cost': 100, 'order_price': 500.0},
            {'delivery_cost': 0, 'order_price': 2000.0},
        ],
    )

    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 100,
            },
        },
    )

    if is_continuous:
        thresholds = [
            {'name': 'Цена ниже за каждые 100 ₽ в заказе', 'value': ' '},
            {'name': 'Заказ от 0 ₽', 'value': '400 ₽'},
            {'name': 'Заказ от 1100 ₽', 'value': '0 ₽'},
        ]
        thresholds_fees = [
            {'delivery_cost': '400', 'order_price': '0'},
            {'delivery_cost': '0', 'order_price': '1100'},
        ]
        delivery_price.set_thresholds_info(
            {'thresholds': thresholds, 'thresholds_fees': thresholds_fees},
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

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
        },
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200

    data = response.json()

    shipping_info = data['payload']['foundPlace']['locationParams'][
        'shippingInfo'
    ]
    assert shipping_info[0] == courier_info
