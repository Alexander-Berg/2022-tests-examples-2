# pylint: disable=too-many-lines
import typing

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils
from eats_catalog import umlaas
from . import layout_utils


EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)
BADGE_DEFAULT_COLOR = 'lightgray'
BADGE_DEFAULT_COLOR_PAIR = [
    {'theme': 'dark', 'value': BADGE_DEFAULT_COLOR},
    {'theme': 'light', 'value': BADGE_DEFAULT_COLOR},
]

ROVER_BADGE_TEXT = 'Бесплатная доставка ровером'
ROVER_BADGE_COLOR = '#bada55'

HEADERS = {
    'x-device-id': 'test_simple',
    'x-request-id': 'hello',
    'x-platform': 'superapp_taxi_web',
    'x-app-version': '1.12.0',
    'X-Eats-Session': 'blablabla',
    'cookie': 'just a cookie',
}

JSON_ANY = {
    'location': {'longitude': 37.591503, 'latitude': 55.802998},
    'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
}

CLOSE_NOTIFICATION = experiments.always_match(
    name='eats_catalog_close_notify',
    is_config=True,
    consumer='eats-catalog-close-notify-badge',
    value={
        'catalog_badge': {
            'enabled': True,
            'notify_interval': 30,
            'text_key': 'test.badge.close_notify',
            'color': BADGE_DEFAULT_COLOR_PAIR,
        },
    },
)


CLOSE_NOTIFICATION_TRANSLATION = pytest.mark.translations(
    **{
        'eats-catalog': {
            'test.badge.close_notify': {
                'ru': [
                    'минута до закрытия',
                    '%(minutes)s минуты до закрытия',
                    '%(minutes)s минут до закрытия',
                    '%(minutes)s минут до закрытия',
                ],
            },
        },
    },
)


def create_themed_color():
    return [
        {'theme': 'light', 'value': '#ffffff'},
        {'theme': 'dark', 'value': '#ffffff'},
    ]


def create_tag_response(tag):
    return {
        'text': {'text': tag, 'color': create_themed_color()},
        'background': create_themed_color(),
    }


def create_tag_meta(tag):
    result = create_tag_response(tag)
    result['text']['text_key'] = f'key.{tag}'
    result['tag'] = tag
    return result


@pytest.mark.parametrize(
    'badge_color',
    [
        pytest.param(
            '#bada55',
            marks=pytest.mark.experiments3(
                is_config=True,
                match={
                    'predicate': {'init': {}, 'type': 'true'},
                    'enabled': True,
                },
                name='eats_catalog_badge',
                consumers=['eats-catalog-layout-badge'],
                clauses=[
                    {
                        'title': 'All',
                        'value': {'text': 'Беееейдж', 'color': '#bada55'},
                        'predicate': {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'place_id',
                                'arg_type': 'int',
                                'value': 1,
                            },
                        },
                    },
                ],
                default_value={},
            ),
        ),
        pytest.param(
            BADGE_DEFAULT_COLOR,
            marks=pytest.mark.experiments3(
                is_config=True,
                match={
                    'predicate': {'init': {}, 'type': 'true'},
                    'enabled': True,
                },
                name='eats_catalog_badge',
                consumers=['eats-catalog-layout-badge'],
                clauses=[
                    {
                        'title': 'All',
                        'value': {'text': 'Беееейдж'},
                        'predicate': {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'place_id',
                                'arg_type': 'int',
                                'value': 1,
                            },
                        },
                    },
                ],
                default_value={},
            ),
        ),
    ],
)
async def test_badge_feature(
        badge_color, catalog_for_layout, eats_catalog_storage,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug='with_badge',
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2, brand=storage.Brand(brand_id=2), slug='without_badge',
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    with_badge_place = layout_utils.find_place_by_slug('with_badge', block)
    assert with_badge_place['payload']['data']['features']['badge'] == {
        'text': 'Беееейдж',
        'color': [
            {'theme': 'dark', 'value': badge_color},
            {'theme': 'light', 'value': badge_color},
        ],
    }

    without_badge_place = layout_utils.find_place_by_slug(
        'without_badge', block,
    )
    assert 'badge' not in without_badge_place['payload']['data']['features']


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_badge',
    consumers=['eats-catalog-layout-badge'],
    clauses=[
        {
            'title': 'All',
            'value': {'text': 'БЕРИ С СОБОЙ!!1!', 'color': '#bada55'},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'has_pickup',
                                'arg_type': 'bool',
                                'value': True,
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'shipping_type',
                                'arg_type': 'string',
                                'value': 'delivery',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'block_shipping_type',
                                'arg_type': 'string',
                                'value': 'delivery',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'application',
                                'arg_type': 'string',
                                'value': 'superapp_taxi_web',
                            },
                        },
                    ],
                },
            },
        },
    ],
    default_value={},
)
@pytest.mark.parametrize(
    'request_pickup,shipping_type,has_badge',
    (
        pytest.param(
            False, storage.ShippingType.Pickup, True, id='has pickup',
        ),
        pytest.param(
            False, storage.ShippingType.Delivery, False, id='has no pickup',
        ),
        pytest.param(
            True,
            storage.ShippingType.Pickup,
            False,
            id='no bagde on pickup filter',
        ),
    ),
)
async def test_pickup_badge(
        taxi_eats_catalog,
        eats_catalog_storage,
        request_pickup,
        shipping_type,
        has_badge,
):
    """
    Проверяем, что для ресторанов с самовывозом отображается
    бейджик самовывоза.
    Что для ресторанов без самовывоза бейджика нет.
    Что при применении фильтра самовывоз бейджик скрывается.
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug=place_slug,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=shipping_type,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    payload = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
    }

    if request_pickup:
        payload.update({'filters': [{'type': 'pickup', 'slug': 'pickup'}]})

    response = await taxi_eats_catalog.post(
        '/internal/v1/catalog-for-layout',
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
        json=payload,
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    place = layout_utils.find_place_by_slug(place_slug, block)

    if has_badge:
        assert place['payload']['data']['features']['badge'] == {
            'text': 'БЕРИ С СОБОЙ!!1!',
            'color': [
                {'theme': 'dark', 'value': '#bada55'},
                {'theme': 'light', 'value': '#bada55'},
            ],
        }
    else:
        assert 'badge' not in place['payload']['data']['features']


async def test_plus_badge_feature(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {
            'cashback': [
                {
                    'place_id': 1,
                    'cashback': 1.1,
                    'badge': {
                        'details_form': {
                            'background': {'styles': {'rainbow': False}},
                            'button': {
                                'deeplink': 'Вау! deeplink',
                                'title': 'Вау! button_title',
                            },
                            'description': 'Вау! description',
                            'image_url': 'Вау! image_url',
                            'title': 'Вау! title',
                        },
                        'styles': {'rainbow': True},
                        'text': 'Вау! Можно потратить до 111 =)',
                    },
                },
                {'place_id': 2, 'cashback': 22.22},
                {
                    'place_id': 3,
                    'cashback': 333,
                    'badge': {
                        'text': 'Покупай подписку и плати баллами за еду',
                        'color': [
                            {'theme': 'dark', 'value': '00000'},
                            {'theme': 'light', 'value': '11111'},
                        ],
                    },
                },
            ],
        }

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='with_plus_badge',
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='without_plus_badge',
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='with_non_plus_badge',
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': True}],
    )

    assert eats_plus.times_called == 1
    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    with_plus_badge_place = layout_utils.find_place_by_slug(
        'with_plus_badge', block,
    )
    assert with_plus_badge_place['payload']['data']['features']['badge'] == {
        'details_form': {
            'background': {'styles': {'rainbow': False}},
            'button': {
                'deeplink': 'Вау! deeplink',
                'title': 'Вау! button_title',
            },
            'description': 'Вау! description',
            'image_url': 'Вау! image_url',
            'title': 'Вау! title',
        },
        'styles': {'rainbow': True},
        'text': 'Вау! Можно потратить до 111 =)',
        'color': BADGE_DEFAULT_COLOR_PAIR,
    }

    without_plus_badge_place = layout_utils.find_place_by_slug(
        'without_plus_badge', block,
    )
    assert (
        'badge' not in without_plus_badge_place['payload']['data']['features']
    )

    with_non_plus_badge_place = layout_utils.find_place_by_slug(
        'with_non_plus_badge', block,
    )
    assert (
        with_non_plus_badge_place['payload']['data']['features']['badge']
        == {
            'text': 'Покупай подписку и плати баллами за еду',
            'color': [
                {'theme': 'dark', 'value': '00000'},
                {'theme': 'light', 'value': '11111'},
            ],
        }
    )


@pytest.mark.now('2021-04-13T12:17:00+03:00')
@experiments.USE_DELIVERY_SLOTS
async def test_delivery_slot(
        catalog_for_layout, eats_catalog_storage, mockserver,
):
    now = parser.parse('2021-04-13T12:17:00+03:00')

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='shop_preorder',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1, place_id=1, working_intervals=storage.opened_at(now),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='restaurant',
            business=storage.Business.Restaurant,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=2, place_id=2, working_intervals=storage.opened_at(now),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='shop_asap',
            business=storage.Business.Restaurant,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=3, place_id=3, working_intervals=storage.opened_at(now),
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=4,
            brand=storage.Brand(brand_id=4),
            slug='native_assembly',
            business=storage.Business.Restaurant,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.ShopPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=4, place_id=4, working_intervals=storage.opened_at(now),
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(request):
        assert request.headers['x-platform'] == 'superapp_taxi_web'
        assert request.headers['x-app-version'] == '1.12.0'
        assert {
            'places': [{'place_id': 1, 'estimated_delivery_duration': 1380}],
            'delivery_point': {'lat': 55.802998, 'lon': 37.591503},
            'delivery_time': {
                'time': '2021-04-13T12:17:00',
                'zone': 'Europe/Moscow',
            },
            'device_id': 'test_simple',
            'user_id': 'bla',
            'phone_id': 'my-phone',
            'personal_phone_id': 'my-phone',
            'source': 'layout',
        } == request.json

        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': False,
                },
                {
                    'place_id': '2',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': True,
                },
            ],
        }

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert eats_customer_slots.times_called == 1
    assert response.status == 200

    block = layout_utils.find_block('open', response.json())

    shop_asap = layout_utils.find_place_by_slug('shop_asap', block)
    assert shop_asap['payload']['data']['features']['delivery'] == {
        'icons': ['asset://native_delivery'],
        'text': '25\u2009–\u200935 мин',
    }

    shop_preorder = layout_utils.find_place_by_slug('shop_preorder', block)
    assert shop_preorder['payload']['data']['features']['delivery'] == {
        'icons': ['asset://native_delivery'],
        'text': 'short_delivery_slot_text',
    }

    restaurant = layout_utils.find_place_by_slug('restaurant', block)
    assert restaurant['payload']['data']['features']['delivery'] == {
        'icons': ['asset://native_delivery'],
        'text': '25\u2009–\u200935 мин',
    }

    shop_asap = layout_utils.find_place_by_slug('native_assembly', block)
    assert shop_asap['payload']['data']['features']['delivery'] == {
        'icons': ['asset://native_delivery'],
        'text': '25\u2009–\u200935 мин',
    }

    assert len(block) == 4


@pytest.mark.now('2021-04-28T00:56:00+03:00')
@pytest.mark.parametrize(
    'response_code, response_data, feature',
    [
        pytest.param(
            200,
            {'is_retail_new_user': True},
            {'icons': ['asset://native_delivery'], 'text': 'free delivery'},
            marks=experiments.free_delivery(True),
            id='free delivery',
        ),
        pytest.param(
            200,
            {'is_retail_new_user': False},
            {
                'icons': ['asset://native_delivery'],
                'text': '25\u2009–\u200935 мин',
            },
            marks=experiments.free_delivery(True),
            id='not new retail',
        ),
        pytest.param(
            500,
            {'is_retail_new_user': True},
            {
                'icons': ['asset://native_delivery'],
                'text': '25\u2009–\u200935 мин',
            },
            marks=experiments.free_delivery(True),
            id='error response',
        ),
        pytest.param(
            200,
            {},
            {
                'icons': ['asset://native_delivery'],
                'text': '25\u2009–\u200935 мин',
            },
            marks=experiments.free_delivery(False),
            id='experiment disabled',
        ),
    ],
)
async def test_shop_free_delivery(
        catalog_for_layout,
        eats_catalog_storage,
        surge,
        response_code,
        response_data,
        feature,
):

    for place_id in range(1, 5):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='shop_{}'.format(place_id),
                business=storage.Business.Shop,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-28T00:00:00+03:00'),
                        end=parser.parse('2021-04-28T08:00:00+03:00'),
                    ),
                ],
            ),
        )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=10,
            brand=storage.Brand(brand_id=10),
            slug='restaurant',
            business=storage.Business.Restaurant,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=10,
            place_id=10,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-28T00:00:00+03:00'),
                    end=parser.parse('2021-04-28T08:00:00+03:00'),
                ),
            ],
        ),
    )

    surge.set_expected(
        expected_user={
            'user_id': 'bla',
            'personal_phone_id': 'my-phone',
            'device_id': 'test_simple',
        },
        expected_location={'region_id': 1, 'position': [37.591503, 55.802998]},
    )
    if response_code == 200:
        surge.set_user_info(user_info=response_data)
    else:
        assert response_code == 500

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1

    block = layout_utils.find_block('open', response.json())

    restaurant = layout_utils.find_place_by_slug('restaurant', block)
    assert restaurant['payload']['data']['features']['delivery'] == {
        'icons': ['asset://native_delivery'],
        'text': '25\u2009–\u200935 мин',
    }

    for place_id in range(1, 5):
        shop = layout_utils.find_place_by_slug(
            'shop_{}'.format(place_id), block,
        )
        assert shop['payload']['data']['features']['delivery'] == feature


@pytest.mark.now('2021-04-28T00:56:00+03:00')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_badge',
    consumers=['eats-catalog-layout-badge'],
    clauses=[
        {
            'title': 'newbie',
            'value': {'text': 'so free delivery', 'color': '#ffffff'},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'is_eda_new_user',
                                'arg_type': 'bool',
                                'value': True,
                            },
                        },
                        {
                            'init': {
                                'predicate': {
                                    'init': {
                                        'arg_name': 'business',
                                        'arg_type': 'string',
                                        'value': 'shop',
                                    },
                                    'type': 'eq',
                                },
                            },
                            'type': 'not',
                        },
                    ],
                },
            },
        },
        {
            'title': 'All',
            'value': {'text': 'Беееейдж'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'business',
                    'arg_type': 'string',
                    'value': 'restaurant',
                },
            },
        },
    ],
    default_value={},
)
@pytest.mark.parametrize(
    'response_code, response_data, feature',
    [
        pytest.param(
            200,
            {'is_eda_new_user': True},
            {
                'text': 'so free delivery',
                'color': [
                    {'theme': 'dark', 'value': '#ffffff'},
                    {'theme': 'light', 'value': '#ffffff'},
                ],
            },
            marks=experiments.free_delivery(True),
            id='free delivery',
        ),
        pytest.param(
            200,
            {'is_eda_new_user': False},
            {'text': 'Беееейдж', 'color': BADGE_DEFAULT_COLOR_PAIR},
            marks=experiments.free_delivery(True),
            id='not new retail',
        ),
        pytest.param(
            500,
            {'is_eda_new_user': True},
            {'text': 'Беееейдж', 'color': BADGE_DEFAULT_COLOR_PAIR},
            marks=experiments.free_delivery(True),
            id='error response',
        ),
        pytest.param(
            200,
            {},
            {'text': 'Беееейдж', 'color': BADGE_DEFAULT_COLOR_PAIR},
            marks=experiments.free_delivery(False),
            id='experiment disabled',
        ),
    ],
)
async def test_restaurant_free_delivery(
        catalog_for_layout,
        eats_catalog_storage,
        surge,
        response_code,
        response_data,
        feature,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='shop',
            business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-28T00:00:00+03:00'),
                    end=parser.parse('2021-04-28T08:00:00+03:00'),
                ),
            ],
        ),
    )

    for place_id in range(3, 10):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug='restaurant_{}'.format(place_id),
                business=storage.Business.Restaurant,
            ),
        )
        eats_catalog_storage.add_zone(
            storage.Zone(
                zone_id=place_id,
                place_id=place_id,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-04-28T00:00:00+03:00'),
                        end=parser.parse('2021-04-28T08:00:00+03:00'),
                    ),
                ],
            ),
        )

    surge.set_expected(
        expected_user={
            'user_id': 'bla',
            'personal_phone_id': 'my-phone',
            'device_id': 'test_simple',
        },
        expected_location={'region_id': 1, 'position': [37.591503, 55.802998]},
    )
    if response_code == 200:
        surge.set_user_info(user_info=response_data)
    else:
        assert response_code == 500

    response = await catalog_for_layout(
        headers={
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'cookie': 'just a cookie',
        },
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1

    block = layout_utils.find_block('open', response.json())

    shop = layout_utils.find_place_by_slug('shop', block)
    assert 'badge' not in shop['payload']['data']['features']

    for place_id in range(3, 10):
        restaurant = layout_utils.find_place_by_slug(
            'restaurant_{}'.format(place_id), block,
        )
        assert 'badge' in restaurant['payload']['data']['features'], place_id
        assert restaurant['payload']['data']['features']['badge'] == feature


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_DELIVERY_FEATURE={
        'surge_icon_url': 'asset://surg',
        'native_delivery_icon_url': 'asset://native_delivery',
        'taxi_delivery_icon_url': 'asset://native_delivery',
        'vehicle_delivery_icon_url': (
            'https://eda.yandex.ru/s3/img/bdu_taxi.png'
        ),
    },
)
async def test_vehicle_delivery_icon(catalog_for_layout, eats_catalog_storage):
    """
    Проверяем, что для автомобильной зоны,
    отображается иконка машинки
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug=place_slug,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            couriers_type=storage.CouriersType.Vehicle,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert found_place['payload']['data']['features']['delivery'] == {
        'icons': ['https://eda.yandex.ru/s3/img/bdu_taxi.png'],
        'text': '25\u2009–\u200935 мин',
    }


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@configs.eats_catalog_delivery_feature(
    pickup_icon='assets://super_pickup_icon',
)
async def test_pickup_block(catalog_for_layout, eats_catalog_storage):
    """
    Проверяем, что для блока самовывоза отображается растояние,
    а не время доставки
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug=place_slug,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    block_id = 'pickup'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'pickup', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert found_place['payload']['data']['features']['delivery'] == {
        'icons': ['assets://super_pickup_icon'],
        'text': '1.1 км',
    }


@experiments.places_with_free_delivery_badge(
    'Бейдж бесплатной доставки из экспа',
)
@pytest.mark.parametrize(
    'plus_priority,exp_priority,close_priority,expected_badge',
    (
        pytest.param(
            10,
            1,
            1,
            'Бейдж плюса',
            marks=pytest.mark.now('2021-03-20T15:00:00+00:00'),
            id='plus badge wins',
        ),
        pytest.param(
            1,
            10,
            20,
            '18 минут до закрытия',
            marks=(
                pytest.mark.now('2021-03-20T21:30:00+00:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='close notification wins',
        ),
    ),
)
async def test_badge_feature_priority(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        experiments3,
        surge,
        plus_priority,
        exp_priority,
        close_priority,
        expected_badge,
):
    """
    Проверяем, что при доступности бейджика плюса и экспериментального
    в выдачу попадает тот у которого выше приоритет
    в конфиге eats_catalog_badge_priority
    """

    experiments3.add_config(
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        name='eats_catalog_badge_priority',
        consumers=['eats-catalog-for-layout'],
        default_value={
            'plus': plus_priority,
            'free_delivery': 0,
            'experiment': exp_priority,
            'close_notify': close_priority,
        },
    )

    schedule = storage.WorkingInterval(
        start=parser.parse('2021-03-20T10:00:00+00:00'),
        end=parser.parse('2021-03-20T22:00:00+00:00'),
    )

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug=place_slug,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(zone_id=1, place_id=1, working_intervals=[schedule]),
    )

    surge.set_place_info(place_id=1, free_delivery={'count': 1})

    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/presentation/cashback/places-list',
    )
    def eats_plus(_):
        return {
            'cashback': [
                {
                    'place_id': 1,
                    'cashback': 1.1,
                    'badge': {'text': 'Бейдж плюса'},
                },
            ],
        }

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert surge.times_called == 1
    assert eats_plus.times_called == 1

    block = layout_utils.find_block('open', response.json())

    place = layout_utils.find_place_by_slug(place_slug, block)
    assert place['payload']['data']['features']['badge'] == {
        'text': expected_badge,
        'color': BADGE_DEFAULT_COLOR_PAIR,
    }


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.USE_DELIVERY_SLOTS
@pytest.mark.parametrize(
    'mode, text',
    (
        pytest.param('default', '25\u2009–\u200935 мин', id='default'),
        pytest.param('min', '~25 мин', id='min'),
        pytest.param('max', '~35 мин', id='max'),
    ),
)
async def test_delivery_feature_mode(
        catalog_for_layout, eats_catalog_storage, mockserver, mode, text,
):
    """
    Проверяем, что параметры блока контролируют формат отображения
    ETA
    """

    place_slugs = []

    businesses = [storage.Business.Shop, storage.Business.Restaurant]
    for idx, business in enumerate(businesses, 1):
        place_slug = f'place_{idx}'
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                brand=storage.Brand(brand_id=idx),
                slug=place_slug,
                business=business,
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=idx,
                zone_id=idx,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-06-30T10:00:00+03:00'),
                        end=parser.parse('2021-06-30T20:00:00+03:00'),
                    ),
                ],
            ),
        )

        place_slugs.append(place_slug)

    eats_customer_slots_path = (
        '/eats-customer-slots/api/v1/places/calculate-delivery-time'
    )

    @mockserver.json_handler(eats_customer_slots_path)
    def eats_customer_slots(request):
        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': True,
                },
            ],
        }

    block_id = 'open'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'delivery_feature_mode': mode,
            },
        ],
    )

    assert eats_customer_slots.times_called == 1
    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    assert place_slugs
    for place_slug in place_slugs:
        found_place = layout_utils.find_place_by_slug(place_slug, block)
        assert (
            found_place['payload']['data']['features']['delivery']['text']
            == text
        )


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.USE_DELIVERY_SLOTS
@pytest.mark.parametrize(
    'asap_availability, business, is_available_now',
    (
        pytest.param(True, storage.Business.Shop, True, id='available shop'),
        pytest.param(
            False, storage.Business.Shop, False, id='unavailable shop',
        ),
        pytest.param(
            False,
            storage.Business.Restaurant,
            True,
            id='ignore slot for non shop place',
        ),
    ),
)
async def test_is_available_now_with_slots(
        catalog_for_layout,
        eats_catalog_storage,
        mockserver,
        asap_availability,
        business,
        is_available_now,
):
    """
    Проверяем, что слоты влияют на поле meta.is_available_now
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug=place_slug,
            business=business,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    eats_customer_slots_path = (
        '/eats-customer-slots/api/v1/places/calculate-delivery-time'
    )

    @mockserver.json_handler(eats_customer_slots_path)
    def eats_customer_slots(request):
        return {
            'places': [
                {
                    'place_id': '1',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 42,
                    'slots_availability': True,
                    'asap_availability': asap_availability,
                },
            ],
        }

    block_id = 'open'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'open', 'disable_filters': False}],
    )

    if business == storage.Business.Shop:
        assert eats_customer_slots.times_called == 1

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert found_place['meta']['is_available_now'] == is_available_now


@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name='eats_catalog_badge',
    consumers=['eats-catalog-layout-badge'],
    clauses=[
        {
            'title': 'All',
            'value': {'text': ROVER_BADGE_TEXT, 'color': ROVER_BADGE_COLOR},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'is_rover_delivery_available',
                    'arg_type': 'bool',
                    'value': True,
                },
            },
        },
    ],
    default_value={},
)
@experiments.eda_yandex_rover_courier(place_ids=[1], weekday=1, hour=12)
@pytest.mark.now('2021-09-20T12:30:00+03:00')
@pytest.mark.parametrize(
    'place_id,shipping_type,has_badge',
    (
        pytest.param(
            2,
            storage.ShippingType.Delivery,
            False,
            id='place without rover no badge',
        ),
        pytest.param(1, storage.ShippingType.Delivery, True, id='with badge'),
    ),
)
async def test_rover_badge(
        catalog_for_layout,
        eats_catalog_storage,
        place_id,
        shipping_type,
        has_badge,
):
    """
    Проверяем, что для ресторанов с доступной доставкой ровером отображается
    бейджик доставки роверов. Доступность доставки ровером регулируется
    экспериментом eda_yandex_rover_courier и зависит от ресторана, зоны
    доставки и времени работы ровера. Так же должна быть выбрана доставка
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            brand=storage.Brand(brand_id=1),
            slug=place_slug,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=shipping_type,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    payload = {
        'location': {'longitude': 37.591503, 'latitude': 55.802998},
        'blocks': [{'id': 'any', 'type': 'any', 'disable_filters': False}],
    }

    response = await catalog_for_layout(**payload)

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())
    place = layout_utils.find_place_by_slug(place_slug, block)

    if has_badge:
        assert place['payload']['data']['features']['badge'] == {
            'text': ROVER_BADGE_TEXT,
            'color': [
                {'theme': 'dark', 'value': ROVER_BADGE_COLOR},
                {'theme': 'light', 'value': ROVER_BADGE_COLOR},
            ],
        }
    else:
        assert 'badge' not in place['payload']['data']['features']


@pytest.mark.config(
    EATS_CATALOG_LAYOUT_PLACES_TAGS_META={
        'data': [create_tag_meta('new'), create_tag_meta('percent')],
    },
)
@experiments.known_tags(['new', 'percent'])
@pytest.mark.translations(
    **{
        'eats-catalog': {
            'key.new': {'ru': 'new'},
            'key.percent': {'ru': 'percent'},
        },
    },
)
async def test_place_tags_feature(catalog_for_layout, eats_catalog_storage):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug='no_tags',
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='one_tag',
            tags=['new'],
        ),
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='two_tags',
            tags=['percent', 'new'],
        ),
    )

    response = await catalog_for_layout(**JSON_ANY)

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    no_tags_place = layout_utils.find_place_by_slug('no_tags', block)
    assert 'tags' not in no_tags_place['payload']['data']['features']

    one_tag_place = layout_utils.find_place_by_slug('one_tag', block)
    assert 'tags' in one_tag_place['payload']['data']['features']
    tags = one_tag_place['payload']['data']['features']['tags']
    assert len(tags) == 1
    assert tags == [create_tag_response('new')]

    two_tags_place = layout_utils.find_place_by_slug('two_tags', block)
    assert 'tags' in two_tags_place['payload']['data']['features']
    tags = two_tags_place['payload']['data']['features']['tags']
    assert len(tags) == 2
    assert tags == [create_tag_response('new'), create_tag_response('percent')]


@pytest.mark.now('2021-06-30T19:00:00+03:00')
@experiments.eta_text(
    default_tpl=r'От %(min)s до %(max)s м',
    equal_tpl=r'Примерно %(max)s м',
    min_tpl=r'От %(min)s м',
    max_tpl=r'До %(max)s м',
    avg_tpl='Над %(avg)s под %(max)s м',
    default_hours_tpl=r'Где %(min)s там и %(max)sч',
    equal_hours_tpl=r'В районе %(max)sч',
    min_hours_tpl=r'Не меньше %(min)sч',
    max_hours_tpl=r'Хорошо если %(max)sч',
    avg_hours_tpl='Где-то %(avg)sч',
)
@pytest.mark.parametrize(
    'eta_min,eta_max,mode,expected,as_hours',
    (
        pytest.param(10, 20, 'default', 'От 10 до 20 м', False),
        pytest.param(10, 10, 'default', 'Примерно 10 м', False),
        pytest.param(10, 20, 'min', 'От 10 м', False),
        pytest.param(10, 20, 'max', 'До 20 м', False),
        pytest.param(10, 20, 'avg', 'Над 15 под 20 м', False),
        pytest.param(10, 15, 'avg', 'Примерно 15 м', False),
        pytest.param(10, 45, 'avg', 'Над 30 под 45 м', False),
        pytest.param(10, 10, 'avg', 'Примерно 10 м', False),
        pytest.param(60, 95, 'default', 'Где 1 там и 1.5ч', True),
        pytest.param(3 * 60, 3 * 60, 'default', 'В районе 3ч', True),
        pytest.param(12 * 60, 13 * 60, 'min', 'Не меньше 12ч', True),
        pytest.param(120, 150, 'max', 'Хорошо если 2.5ч', True),
        pytest.param(150, 450, 'avg', 'Где-то 5ч', True),
        pytest.param(60, 0, 'avg', 'Над 30 под 0 м', True),
    ),
)
async def test_eta_text(
        catalog_for_layout,
        eats_catalog_storage,
        umlaas_eta,
        eta_min,
        eta_max,
        mode,
        expected,
        as_hours,
):
    """
    Проверяем, что эксперимент переопределяет формат
    отображения ETA
    """

    idx = 1
    place_slug = f'place_{idx}'
    eats_catalog_storage.add_place(
        storage.Place(place_id=idx, slug=place_slug),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=idx,
            zone_id=idx,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    umlaas_eta.set_eta(
        umlaas.UmlaasEta(place_id=idx, eta_min=eta_min, eta_max=eta_max),
    )

    block_id = 'open'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'delivery_feature_mode': mode,
                'round_eta_to_hours': as_hours,
            },
        ],
    )

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert (
        found_place['payload']['data']['features']['delivery']['text']
        == expected
    )


@pytest.mark.now('2021-06-30T19:00:00+03:00')
@pytest.mark.parametrize(
    'eta_min,eta_max,expected_format,as_hours,',
    [
        pytest.param(
            10,
            20,
            '10 TO 20',
            False,
            marks=experiments.always_match(
                name='eats_catalog_eta',
                consumer='eats-catalog-eta',
                is_config=True,
                value={
                    'l10n': [
                        {
                            'default': '{min} TO {max}',
                            'key': 'default',
                            'tanker': {
                                'key': 'invalid_tanker_key',
                                'keyset': 'eats-catalog',
                            },
                        },
                    ],
                },
            ),
            id='format from experiment',
        ),
        pytest.param(
            60,
            90,
            '1-1.5h',
            True,
            marks=experiments.always_match(
                name='eats_catalog_eta',
                consumer='eats-catalog-eta',
                is_config=True,
                value={
                    'l10n': [
                        {
                            'default': '{min}-{max}h',
                            'key': 'default.hours',
                            'tanker': {
                                'key': 'invalid_tanker_key',
                                'keyset': 'eats-catalog',
                            },
                        },
                    ],
                },
            ),
            id='format from experiment hours',
        ),
        pytest.param(
            10,
            20,
            '10\u2009–\u200920 мин',
            False,
            marks=experiments.always_match(
                name='eats_catalog_eta',
                consumer='eats-catalog-eta',
                is_config=True,
                value={
                    'l10n': [
                        {
                            'default': '{min} TO {max} {unknown}',
                            'key': 'default',
                            'tanker': {
                                'key': 'invalid_tanker_key',
                                'keyset': 'eats-catalog',
                            },
                        },
                    ],
                },
            ),
            id='invalid from experiment',
        ),
        pytest.param(
            60,
            90,
            '1\u2009–\u20091.5 ч',
            True,
            marks=experiments.always_match(
                name='eats_catalog_eta',
                consumer='eats-catalog-eta',
                is_config=True,
                value={
                    'l10n': [
                        {
                            'default': '{min}-{max} {hello}h',
                            'key': 'default.hours',
                            'tanker': {
                                'key': 'invalid_tanker_key',
                                'keyset': 'eats-catalog',
                            },
                        },
                    ],
                },
            ),
            id='format from experiment hours',
        ),
    ],
)
async def test_eta_text_exp_default(
        catalog_for_layout,
        eats_catalog_storage,
        umlaas_eta,
        eta_min,
        eta_max,
        expected_format,
        as_hours,
):
    """
    Проверяем, что если эксп ссылается
    на невалидный ключ танкера,
    возвращается default из эксперимента
    и значения min/max корректно подставляются
    """

    idx = 1
    place_slug = f'place_{idx}'
    eats_catalog_storage.add_place(
        storage.Place(place_id=idx, slug=place_slug),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=idx,
            zone_id=idx,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
            timing=storage.ZoneTimings(market_avg_time=30 * 60),
        ),
    )

    umlaas_eta.set_eta(
        umlaas.UmlaasEta(place_id=idx, eta_min=eta_min, eta_max=eta_max),
    )

    block_id = 'open'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': as_hours,
            },
        ],
    )

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert (
        found_place['payload']['data']['features']['delivery']['text']
        == expected_format
    )


@experiments.brand_link([{'brand_id': 1, 'link': 'http://yandex.ru'}])
@pytest.mark.now('2021-12-07T00:27:00+03:00')
async def test_link_override(catalog_for_layout, eats_catalog_storage):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='test_place', brand=storage.Brand(brand_id=1),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-12-07T00:00:00+03:00'),
                    end=parser.parse('2021-12-07T20:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200
    block = layout_utils.find_block('open', response.json())

    found_place = layout_utils.find_place_by_slug('test_place', block)
    assert found_place['payload']['link'] == {'deeplink': 'http://yandex.ru'}


@pytest.mark.parametrize(
    'text,place_type',
    [
        pytest.param(
            None,
            storage.PlaceType.Native,
            id='no badge',
            marks=pytest.mark.now('2022-02-07T22:32:00+03:00'),
        ),
        pytest.param(
            None,
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T22:32:00+03:00'),
                CLOSE_NOTIFICATION,
            ),
            id='no translation',
        ),
        pytest.param(
            '18 минут до закрытия',
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T22:32:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge 18 minutes',
        ),
        pytest.param(
            '8 минут до закрытия',
            storage.PlaceType.Marketplace,
            marks=(
                pytest.mark.now('2022-02-07T22:32:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge marketplace',
        ),
        pytest.param(
            'минута до закрытия',
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T22:49:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge 1 minute',
        ),
        pytest.param(
            '0 минут до закрытия',
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T22:49:10+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='badge 0 minutes',
        ),
        pytest.param(
            None,
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T23:32:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='after close',
        ),
        pytest.param(
            None,
            storage.PlaceType.Native,
            marks=(
                pytest.mark.now('2022-02-07T20:00:00+03:00'),
                CLOSE_NOTIFICATION,
                CLOSE_NOTIFICATION_TRANSLATION,
            ),
            id='long before close',
        ),
    ],
)
async def test_close_notification(
        catalog_for_layout, eats_catalog_storage, text, place_type,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            place_type=place_type,
            slug='test_place',
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(average_preparation=10 * 60),
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            timing=storage.ZoneTimings(market_avg_time=20 * 60),
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-02-07T00:00:00+03:00'),
                    end=parser.parse('2022-02-07T20:10:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            timing=storage.ZoneTimings(market_avg_time=20 * 60),
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-02-07T20:10:00+03:00'),
                    end=parser.parse('2022-02-07T23:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await catalog_for_layout(
        [{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200
    block = layout_utils.find_block('any', response.json())

    place = layout_utils.find_place_by_slug('test_place', block)
    if text is None:
        assert 'badge' not in place['payload']['data']['features']
    else:
        badge = place['payload']['data']['features']['badge']

        assert badge == {'color': BADGE_DEFAULT_COLOR_PAIR, 'text': text}


@CLOSE_NOTIFICATION
@CLOSE_NOTIFICATION_TRANSLATION
@pytest.mark.parametrize(
    'expecting_place',
    [
        pytest.param(
            True,
            marks=pytest.mark.now('2022-02-12T21:40:00+03:00'),
            id='open 10 before closing',
        ),
        pytest.param(
            False,
            marks=pytest.mark.now('2022-02-12T21:51:00+03:00'),
            id='closed 1 after closing',
        ),
    ],
)
async def test_not_round_schedule(
        catalog_for_layout, eats_catalog_storage, expecting_place,
):
    """
    Проверяет, что для расписания, у которого время оканчния интервала
    не округляется до самого себя, время до закрытия вычисляется на основании
    окончания интервала, а не на основе округленного значения
    """

    schedule: typing.List[storage.WorkingInterval] = [
        storage.WorkingInterval(
            start=parser.parse('2022-02-12T11:00:00+03:00'),
            end=parser.parse('2022-02-12T22:12:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='test_place',
            brand=storage.Brand(brand_id=1),
            timing=storage.PlaceTiming(average_preparation=22 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, zone_id=1, working_intervals=schedule),
    )

    response = await catalog_for_layout(
        [{'id': 'open', 'type': 'open', 'disable_filters': False}],
    )

    assert response.status_code == 200
    if expecting_place:
        block = layout_utils.find_block('open', response.json())
        place = layout_utils.find_place_by_slug('test_place', block)

        badge = place['payload']['data']['features']['badge']
        assert badge == {
            'color': BADGE_DEFAULT_COLOR_PAIR,
            'text': '10 минут до закрытия',
        }
    else:
        layout_utils.assert_no_block_or_empty('open', response.json())


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.SHOW_SURGE_RADIUS_ON_CATALOG
@experiments.eats_catalog_surge_radius()
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
async def test_surge_radius_icon(
        catalog_for_layout, eats_catalog_storage, surge_resolver,
):
    """
    Проверяем, что иконка суржа отображатеся если заведение под суржом радиусом
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, brand=storage.Brand(brand_id=1), slug=place_slug,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    surge_resolver.place_radius = {1: surge_utils.SurgeRadius(pedestrian=0)}

    block_id = 'closed'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'closed', 'disable_filters': False}],
    )

    assert surge_resolver.times_called == 1

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())

    found_place = layout_utils.find_place_by_slug(place_slug, block)
    assert not found_place['payload']['availability']['is_available']
    delivery = found_place['payload']['data']['features']['delivery']
    assert delivery['icons'][0] == 'asset://surg'


@pytest.mark.parametrize(
    'badge_for_marketplace',
    [
        pytest.param(
            BADGE_DEFAULT_COLOR,
            marks=pytest.mark.experiments3(
                is_config=True,
                match={
                    'predicate': {'init': {}, 'type': 'true'},
                    'enabled': True,
                },
                name='eats_catalog_badge',
                consumers=['eats-catalog-layout-badge'],
                clauses=[
                    {
                        'title': 'All',
                        'value': {
                            'text': 'Доставка {max_delivery_fee}{currency}',
                        },
                        'predicate': {
                            'type': 'all_of',
                            'init': {
                                'predicates': [
                                    {
                                        'type': 'eq',
                                        'init': {
                                            'arg_name': 'delivery_type',
                                            'arg_type': 'string',
                                            'value': 'marketplace',
                                        },
                                    },
                                    {
                                        'type': 'lt',
                                        'init': {
                                            'arg_name': 'max_delivery_fee',
                                            'arg_type': 'double',
                                            'value': 100,
                                        },
                                    },
                                    {
                                        'type': 'gt',
                                        'init': {
                                            'arg_name': 'max_delivery_fee',
                                            'arg_type': 'double',
                                            'value': 0,
                                        },
                                    },
                                    {
                                        'type': 'eq',
                                        'init': {
                                            'arg_name': (
                                                'max_delivery_fee_threshold'
                                            ),
                                            'arg_type': 'double',
                                            'value': 0,
                                        },
                                    },
                                ],
                            },
                        },
                    },
                ],
                default_value={},
            ),
        ),
    ],
)
async def test_badge_feature_for_marketplace(
        badge_for_marketplace, catalog_for_layout, eats_catalog_storage,
):
    """
    EDAJAM-567: проверяем, что на маркетплейсы навешивается
    бейджик маленькой стоимости доставки
    """
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='with_badge',
            place_type=storage.PlaceType.Marketplace,
            country=storage.Country(
                currency=storage.Currency(sign='₽', code='RUB'),
            ),
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=2,
            brand=storage.Brand(brand_id=2),
            slug='without_badge_marketplace',
            place_type=storage.PlaceType.Marketplace,
            country=storage.Country(
                currency=storage.Currency(sign='₽', code='RUB'),
            ),
        ),
    )
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=3,
            brand=storage.Brand(brand_id=3),
            slug='without_badge_native',
            place_type=storage.PlaceType.Native,
            country=storage.Country(
                currency=storage.Currency(sign='₽', code='RUB'),
            ),
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
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=12,
            place_id=3,
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
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=11,
            place_id=2,
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
                storage.DeliveryCondition(order_cost=0, delivery_cost=111),
            ],
        ),
    )

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
    )

    assert response.status_code == 200

    block = layout_utils.find_block('any', response.json())

    with_badge_place = layout_utils.find_place_by_slug('with_badge', block)
    assert with_badge_place['payload']['data']['features']['badge'] == {
        'text': 'Доставка 99₽',
        'color': [
            {'theme': 'dark', 'value': badge_for_marketplace},
            {'theme': 'light', 'value': badge_for_marketplace},
        ],
    }

    without_badge_place = layout_utils.find_place_by_slug(
        'without_badge_marketplace', block,
    )
    assert 'badge' not in without_badge_place['payload']['data']['features']

    without_badge_place = layout_utils.find_place_by_slug(
        'without_badge_native', block,
    )
    assert 'badge' not in without_badge_place['payload']['data']['features']
