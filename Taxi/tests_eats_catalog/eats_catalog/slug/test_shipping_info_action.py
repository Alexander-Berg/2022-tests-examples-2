from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils


GENERIC_MESSAGE = 'Доставка Яндекс.Еда'
SURGE_MESSAGE = 'Спрос временно вырос'
CONTINUOUS_SURGE_RANGE = 'Доставка'
PRICE_RANGE = '%(min)s - %(max)s %(s_currency_sign)s'

SHIPPING_INFO_ACTION_TRANSLATIONS = {
    'eats-catalog': {
        'slug.delivery_fee.description': {
            'ru': 'Обычно от %(n_price)s %(s_currency_sign)s',
        },
        'slug.delivery_fee.value.free_of_charge': {'ru': 'Бесплатно'},
        'slug.delivery_fee.value.price': {
            'ru': '%(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_info.name.courier': {'ru': 'Курьером'},
        'slug.shipping_info.name.pickup': {'ru': 'С собой'},
        'slug.shipping_info.name.rover': {'ru': 'Ровером'},
        'slug.shipping_thresholds.name.from': {
            'ru': 'Заказ от %(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_thresholds.name.up_to': {
            'ru': 'Заказ до %(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_thresholds.value': {
            'ru': '%(n_price)s %(s_currency_sign)s',
        },
        'slug.shipping_info_action.message': {'ru': GENERIC_MESSAGE},
        'slug.shipping_info_action.message.surge': {'ru': SURGE_MESSAGE},
        'slug.shipping_info_action.message.coninuous_surge_range': {
            'ru': CONTINUOUS_SURGE_RANGE,
        },
        'slug.delivery_fee.value.range': {'ru': PRICE_RANGE},
    },
}


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@experiments.eats_catalog_surge_radius()
@pytest.mark.translations(**SHIPPING_INFO_ACTION_TRANSLATIONS)
@pytest.mark.parametrize(
    'surge_info, expected_shipping_info_action',
    (
        pytest.param(
            None,
            {
                'deliveryFee': {'name': '30 - 100 ₽'},
                'message': GENERIC_MESSAGE,
            },
            id='no surge, delivery_price',
        ),
        pytest.param(
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            {
                'deliveryFee': {
                    'name': '230 ₽',
                    'icon': 'asset://icon_high_price',
                },
                'color': [{'theme': 'light', 'value': '#0000ff'}],
                'message': SURGE_MESSAGE,
            },
            id='surge',
        ),
        pytest.param(
            {
                'surgeLevel': 0,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 500,
            },
            {
                'deliveryFee': {'name': '30 - 100 ₽'},
                'message': GENERIC_MESSAGE,
            },
            id='surge radius',
        ),
    ),
)
async def test_shipping_info_action(
        slug,
        eats_catalog_storage,
        surge_resolver,
        delivery_price,
        surge_info,
        expected_shipping_info_action,
):
    """
    Проверяем формирование элемента shippingInfoAction
    Если нет суржа, там должен быть диапазон цен
    от минимальной до максимальной
    При денежном сурже - цена доставки и цвет
    При сурже радиусом то же самое, что и без суржа
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
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=100),
                storage.DeliveryCondition(order_cost=500, delivery_cost=60),
                storage.DeliveryCondition(order_cost=2000, delivery_cost=30),
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
        data['payload']['foundPlace']['locationParams']['shippingInfoAction']
        == expected_shipping_info_action
    )


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.SLUG_SHIPPING_ICONS
@experiments.SLUG_SHIPPING_FEE_COLORS
@pytest.mark.translations(**SHIPPING_INFO_ACTION_TRANSLATIONS)
@pytest.mark.parametrize(
    'min_value,max_value,expected_name',
    (
        pytest.param(0, 399, '0 - 399 ₽', id='do_not_use_final_cost'),
        pytest.param(
            0,
            399,
            '0 - 399 ₽',
            marks=experiments.USE_SURGE_FINAL_PRICE,
            id='use_final_cost',
        ),
        pytest.param(
            399,
            399,
            '399 ₽',
            marks=experiments.USE_SURGE_FINAL_PRICE,
            id='equal_range',
        ),
    ),
)
async def test_continuous_surge(
        slug,
        eats_catalog_storage,
        delivery_price,
        min_value,
        max_value,
        expected_name,
):
    """
    Проверяем, если приходит continuous_surge_range
    в ответе прайсинга, то в shippingInfoAction и шторке
    отображается его диапазон.
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

    # Стоимость доставки выбрана достаточно маленькая, чтобы не связываться
    # с nativeMaxDeliveryFee.
    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 100.0, 'order_price': 0.0},
            {'delivery_cost': 60.0, 'order_price': 500.0},
        ],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'loadLevel': 100,
                'surgeLevel': 100,
                'deliveryFee': 100,
            },
        },
    )

    delivery_price.set_continuous_surge_range(min_value, max_value)

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

    location_params = data['payload']['foundPlace']['locationParams']

    assert location_params['shippingInfoAction'] == {
        'deliveryFee': {
            'name': expected_name,
            'icon': 'asset://icon_high_price',
        },
        'color': [{'theme': 'light', 'value': '#0000ff'}],
        'message': CONTINUOUS_SURGE_RANGE,
    }

    assert location_params['shippingInfo'][0] == {
        'icon': 'asset://icon_courier',
        'name': 'Курьером',
        'deliveryFee': {
            'icon': 'asset://icon_high_price',
            'name': {
                'color': [{'theme': 'light', 'value': '#ff0000'}],
                'text': expected_name,
            },
        },
    }
