from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils

SURGE_TRANSLATIONS = {
    'eats-catalog': {
        'slug.bottom_banner.title.surge.rover': {'ru': 'Доставка ровером'},
        'slug.bottom_banner.description.surge.rover': {'ru': 'бесплатно'},
        'slug.bottom_banner.title.surge.pickup': {'ru': 'Заберите с собой'},
        'slug.bottom_banner.description.surge.pickup': {
            'ru': 'Не платите за доставку',
        },
        'slug.bottom_banner.description.radius_surge.pickup': {
            'ru': '15 минут пешком',
        },
        'slug.bottom_banner.title.surge.preorder': {'ru': 'Только предзаказы'},
        'slug.bottom_banner.description.radius_surge.preorder': {
            'ru': 'Ресторан пока закрыт',
        },
    },
}

SLUG_BOTTOM_BANNER = pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='eats_catalog_slug_bottom_banner',
    consumers=['eats-catalog-slug'],
    clauses=[
        {
            'title': 'Surge banners',
            'value': {
                'price_surge_rover': {
                    'title': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': 'slug.bottom_banner.title.surge.rover',
                    },
                    'description': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': (
                            'slug.bottom_banner.description.surge.rover'
                        ),
                    },
                },
                'price_surge_pickup': {
                    'title': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': 'slug.bottom_banner.title.surge.pickup',
                    },
                    'description': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': (
                            'slug.bottom_banner.description.surge.pickup'
                        ),
                    },
                },
                'radius_surge_pickup': {
                    'title': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': 'slug.bottom_banner.title.surge.pickup',
                    },
                    'description': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': (
                            'slug.bottom_banner.description.radius_surge.'
                            + 'pickup'
                        ),
                    },
                },
                'radius_surge_preorder': {
                    'title': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': 'slug.bottom_banner.title.surge.preorder',
                    },
                    'description': {
                        'color': [{'theme': 'light', 'value': '#000000'}],
                        'text_key': (
                            'slug.bottom_banner.description.radius_surge.'
                            + 'preorder'
                        ),
                    },
                },
            },
            'predicate': {'type': 'true'},
        },
    ],
)


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=60)
@experiments.SLUG_SHIPPING_ICONS
@SLUG_BOTTOM_BANNER
@experiments.eats_catalog_surge_radius()
@pytest.mark.translations(**SURGE_TRANSLATIONS)
@pytest.mark.parametrize(
    'shipping_type, surge_info, allow_delivery, allow_pickup, '
    + 'expected_banner_response',
    [
        pytest.param(
            'delivery',
            {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
            True,
            False,
            {
                'icon': 'asset://icon_preorder',
                'name': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Только предзаказы',
                },
                'description': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Ресторан пока закрыт',
                },
            },
            id='radius surge without pickup',
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
                'icon': 'asset://icon_pickup',
                'name': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Заберите с собой',
                },
                'description': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': '15 минут пешком',
                },
            },
            id='radius surge with pickup and requested delivery',
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
            None,
            id='radius surge with pickup and requested pickup',
        ),
        pytest.param(
            'delivery',
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            True,
            False,
            None,
            id='price surge without pickup',
        ),
        pytest.param(
            'delivery',
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            True,
            True,
            {
                'icon': 'asset://icon_pickup',
                'name': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Заберите с собой',
                },
                'description': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Не платите за доставку',
                },
            },
            id='price surge with pickup and requested delivery',
        ),
        pytest.param(
            'pickup',
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            True,
            True,
            None,
            id='price surge with pickup and requested pickup',
        ),
        pytest.param(
            'delivery',
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            True,
            False,
            {
                'icon': 'asset://icon_rover',
                'name': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Доставка ровером',
                },
                'description': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'бесплатно',
                },
            },
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='price surge with rover',
        ),
        pytest.param(
            'delivery',
            {'surgeLevel': 1, 'loadLevel': 1, 'deliveryFee': 200},
            True,
            True,
            {
                'icon': 'asset://icon_rover',
                'name': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'Доставка ровером',
                },
                'description': {
                    'color': [{'theme': 'light', 'value': '#000000'}],
                    'text': 'бесплатно',
                },
            },
            marks=(experiments.eda_yandex_rover_courier(place_ids=[1])),
            id='price surge with rover and pickup',
        ),
        pytest.param(
            'delivery',
            None,
            False,
            True,
            None,
            id='no surge, w/o delivery, w pickup, requested delivery',
        ),
        pytest.param(
            'pickup',
            None,
            False,
            True,
            None,
            id='no surge, w/o delivery, w pickup, requested pickup',
        ),
    ],
)
async def test_surge_banner(
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
