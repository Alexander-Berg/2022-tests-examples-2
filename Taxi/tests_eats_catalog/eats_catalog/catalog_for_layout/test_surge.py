from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils
from . import layout_utils


@pytest.mark.parametrize(
    'is_open, is_pickup, has_surge',
    [
        pytest.param(True, False, True, id='open'),
        pytest.param(False, False, False, id='closed'),
        pytest.param(
            True,
            True,
            False,
            marks=experiments.free_delivery(True),
            id='pickup',
        ),
    ],
)
@pytest.mark.now('2021-10-11T14:00:00+03:00')
async def test_surge(
        catalog_for_layout,
        eats_catalog_storage,
        surge,
        is_open,
        is_pickup,
        has_surge,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='slug-1', brand=storage.Brand(brand_id=1),
        ),
    )
    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-11T10:00:00+03:00'),
            end=parser.parse('2021-10-11T18:00:00+03:00'),
        )
        if is_open
        else storage.WorkingInterval(
            start=parser.parse('1999-10-11T10:00:00+03:00'),
            end=parser.parse('1999-10-11T18:00:00+03:00'),
        ),
    ]
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1, zone_id=1, working_intervals=working_intervals,
        ),
    )
    if is_pickup:
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=2,
                shipping_type=storage.ShippingType.Pickup,
                working_intervals=working_intervals,
            ),
        )
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

    filters = None
    if is_pickup:
        filters = [{'type': 'pickup', 'slug': 'pickup'}]

    response = await catalog_for_layout(
        blocks=[{'id': 'any', 'type': 'any', 'disable_filters': False}],
        filters=filters,
    )
    assert response.status_code == 200
    assert surge.times_called == 1

    block = layout_utils.find_block('any', response.json())
    [place] = block
    features = place['payload']['data']['features']
    surge_level = place['meta']['surge_level']
    if has_surge:
        assert 'surge' in features
        assert surge_level == 2
    else:
        assert 'surge' not in features
        assert surge_level == 0


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@experiments.eats_surge_planned(interval=120)
@configs.eats_catalog_delivery_feature(
    taxi_delivery_icon_url='test://taxi_delivery',
    disable_by_surge_for_minutes=180,  # 3 часа
    radius_surge_can_keep_automobile_zones=True,
)
@pytest.mark.parametrize(
    'show_radius, expect_delivery_disabled, expect_taxi_delivery, preorder',
    [
        pytest.param(
            1000.0,
            True,
            False,
            False,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied',
        ),
        pytest.param(
            1000.0,
            True,
            False,
            True,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied preorder',
        ),
        pytest.param(
            1000.0,
            True,
            False,
            'can-not-deliver',
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied preorder can not deliver',
        ),
        pytest.param(
            1000.0,
            False,
            True,
            False,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=True,
            ),
            id='radius surge applied keep taxi',
        ),
        pytest.param(
            2000.0,
            False,
            False,
            False,
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius too big',
        ),
        pytest.param(1000.0, False, False, False, id='no experiment'),
    ],
)
async def test_delivery_disabled_by_radius_surge(
        catalog_for_layout,
        eats_catalog_storage,
        surge_resolver,
        show_radius,
        expect_delivery_disabled,
        expect_taxi_delivery,
        preorder,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_slug',
            location=storage.Location(lon=37.5916, lat=55.8129),
        ),
    )

    working_intervals = [
        storage.WorkingInterval(
            start=parser.parse('2021-07-25T10:00:00+03:00'),
            end=parser.parse('2021-07-25T20:00:00+03:00'),
        ),
    ]
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=working_intervals,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            couriers_type=storage.CouriersType.YandexTaxi,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=working_intervals,
        ),
    )

    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(pedestrian=show_radius),
    }

    delivery_time = None
    if preorder:
        if preorder == 'can-not-deliver':
            delivery_time = {
                'time': '2021-07-25T15:30:00+03:00',
                'zone': 10800,
            }
        else:
            delivery_time = {
                'time': '2021-07-25T16:00:00+03:00',
                'zone': 10800,
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
        location={'longitude': 37.6, 'latitude': 55.8},
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
        delivery_time=delivery_time,
    )

    if expect_delivery_disabled:
        layout_utils.assert_no_block_or_empty('open', response.json())
        block = layout_utils.find_block('closed', response.json())
        expect_delivery_text = 'Сегодня 19:00'
    else:
        layout_utils.assert_no_block_or_empty('closed', response.json())
        block = layout_utils.find_block('open', response.json())
        expect_delivery_text = '35\u2009–\u200945 мин'
    place = layout_utils.find_place_by_slug('place_slug', block)
    delivery_features = place['payload']['data']['features']['delivery']
    assert delivery_features['text'] == expect_delivery_text
    expect_delivery_icon = (
        'test://taxi_delivery'
        if expect_taxi_delivery
        else 'asset://native_delivery'
    )
    assert delivery_features['icons'] == [expect_delivery_icon]


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@experiments.eats_catalog_surge_radius(enabled=True, place_batch_size=1)
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
async def test_eats_catalog_surge_radius_batch(
        catalog_for_layout, eats_catalog_storage, surge_resolver,
):
    """
    Проверяем, что в surge_resolver
    идет несколько параллельных запросов
    """

    place_id = 1

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    polygon = storage.Polygon(
        [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]],
    )

    for idx in range(10):
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=idx,
                slug=f'place_{idx}',
                brand=storage.Brand(brand_id=idx),
                location=storage.Location(lon=0.0, lat=0.0),
            ),
        )

        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=idx,
                zone_id=idx,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=schedule,
                polygon=polygon,
                couriers_type=storage.CouriersType.Pedestrian,
            ),
        )

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=1000),
    }

    @surge_resolver.request_assertion
    def _surge_request_assertion(request):
        req = request.json
        assert len(req['placeIds']) == 1

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
        location={'longitude': 0.01, 'latitude': 0.01},
        blocks=[
            {'id': 'open', 'type': 'open', 'disable_filters': False},
            {'id': 'closed', 'type': 'closed', 'disable_filters': False},
        ],
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == 10

    data = response.json()
    open_block = layout_utils.find_block('open', data)
    closed_block = layout_utils.find_block('closed', data)

    # проверяем что сурж радиусом отключил один рест
    assert len(open_block) == 9
    assert len(closed_block) == 1


@pytest.mark.now('2021-07-25T15:00:00+03:00')
@configs.eats_catalog_delivery_feature(
    taxi_delivery_icon_url='test://taxi_delivery',
    disable_by_surge_for_minutes=180,  # 3 часа
    radius_surge_can_keep_automobile_zones=True,
)
@experiments.eats_catalog_surge_radius()
async def test_delivery_disabled_by_radius_surge_stats(
        catalog_for_layout, eats_catalog_storage, mockserver, surge_resolver,
):
    for place_id in [1, 2, 3]:
        eats_catalog_storage.add_place(
            storage.Place(
                place_id=place_id,
                brand=storage.Brand(brand_id=place_id),
                slug=f'place_{place_id}',
                location=storage.Location(lon=37.5916, lat=55.8129),
            ),
        )

        working_intervals = [
            storage.WorkingInterval(
                start=parser.parse('2021-07-25T10:00:00+03:00'),
                end=parser.parse('2021-07-25T20:00:00+03:00'),
            ),
        ]
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=place_id,
                zone_id=place_id,
                shipping_type=storage.ShippingType.Delivery,
                working_intervals=working_intervals,
            ),
        )

    surge_resolver.place_radius = {3: surge_utils.SurgeRadius(pedestrian=1000)}

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def _order_stats(request):
        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': 'bla'},
                    'counters': [
                        {
                            'properties': [{'name': 'place_id', 'value': '1'}],
                            'value': 100,
                            'first_order_at': '2021-08-19T13:04:05+0000',
                            'last_order_at': '2021-09-19T13:04:05+0000',
                        },
                        {
                            'properties': [{'name': 'place_id', 'value': '3'}],
                            'value': 3,
                            'first_order_at': '2021-08-19T13:04:05+0000',
                            'last_order_at': '2021-09-19T13:04:05+0000',
                        },
                    ],
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
        location={'longitude': 37.6, 'latitude': 55.8},
        blocks=[
            {
                'id': 'any',
                'type': 'any',
                'disable_filters': False,
                'no_data': True,
            },
        ],
    )

    [block] = response.json()['blocks']
    assert block['stats'] == {
        'places_count': 3,
        'native_surge_places_count': 0,
        'market_surge_places_count': 0,
        'orders_count': 103,
        'radius_surge_orders_count': 3,
    }


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.SHOW_SURGE_RADIUS_ON_CATALOG
@experiments.eats_catalog_surge_radius()
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@pytest.mark.parametrize(
    'has_pickup',
    (pytest.param(False, id='no_pickup'), pytest.param(True, id='has_pickup')),
)
async def test_surge_radius_change_shipping_type(
        catalog_for_layout, eats_catalog_storage, surge_resolver, has_pickup,
):
    """
    Проверяем, отображение заведение на каталоге при сурже радиусом
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

    if has_pickup:
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=2,
                shipping_type=storage.ShippingType.Pickup,
                working_intervals=[
                    storage.WorkingInterval(
                        start=parser.parse('2021-06-30T10:00:00+03:00'),
                        end=parser.parse('2021-06-30T20:00:00+03:00'),
                    ),
                ],
            ),
        )

    surge_resolver.place_radius = {1: surge_utils.SurgeRadius(pedestrian=0)}

    block_id = 'any'

    response = await catalog_for_layout(
        blocks=[
            {
                'id': block_id,
                'type': 'any',
                'disable_filters': False,
                'allow_surge_radius_shipping_type_flowing': True,
            },
        ],
    )

    assert surge_resolver.times_called == 1

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())
    found_place = layout_utils.find_place_by_slug(place_slug, block)
    is_available = found_place['payload']['availability']['is_available']
    delivery = found_place['payload']['data']['features']['delivery']
    if has_pickup:
        assert is_available
        assert delivery['text'] == '1.1 км'
    else:
        assert not is_available
        assert delivery['icons'][0] == 'asset://surg'
        assert delivery['text'] == 'Сегодня 17:00'


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.DISABLE_CALC_SURGE_BULK
@experiments.eats_catalog_surge_radius()
@experiments.eats_surge_planned(interval=120)
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@pytest.mark.parametrize(
    'native_surge_level,lavka_surge_level,delivery_type,'
    'business,delivery_time,has_surge',
    (
        pytest.param(
            0,
            0,
            storage.PlaceType.Native,
            storage.Business.Restaurant,
            None,
            False,
            id='no_surge',
        ),
        pytest.param(
            1,
            0,
            storage.PlaceType.Native,
            storage.Business.Restaurant,
            None,
            True,
            id='native_surge',
        ),
        pytest.param(
            0,
            1,
            storage.PlaceType.Native,
            storage.Business.Store,
            None,
            True,
            id='lavka_surge',
        ),
        pytest.param(
            1,
            1,
            storage.PlaceType.Marketplace,
            storage.Business.Restaurant,
            None,
            False,
            id='marketplace_no_surge',
        ),
        pytest.param(
            1,
            1,
            storage.PlaceType.Native,
            storage.Business.Restaurant,
            '2021-06-30T13:00:00+03:00',
            True,
            id='preorder_has_surge',
        ),
        pytest.param(
            1,
            1,
            storage.PlaceType.Native,
            storage.Business.Restaurant,
            '2021-06-30T14:30:00+03:00',
            False,
            id='preorder_has_no_surge',
        ),
    ),
)
async def test_money_surge_via_surge_resolver(
        catalog_for_layout,
        eats_catalog_storage,
        surge_resolver,
        native_surge_level,
        lavka_surge_level,
        delivery_type,
        business,
        delivery_time,
        has_surge,
):
    """
    Проверяем получение суржа на каталоге из
    eats_surge_resolver
    """

    place_slug = 'place_slug'

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug=place_slug,
            place_type=delivery_type,
            business=business,
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

    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(
            native_surge_level=native_surge_level,
            lavka_surge_level=lavka_surge_level,
        ),
    }

    block_id = 'any'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'any', 'disable_filters': False}],
        time=delivery_time,
    )

    assert response.status_code == 200

    block = layout_utils.find_block(block_id, response.json())
    found_place = layout_utils.find_place_by_slug(place_slug, block)
    delivery = found_place['payload']['data']['features']['delivery']
    if has_surge:
        assert delivery['icons'][0] == 'asset://surg'
    else:
        assert not delivery['icons'] or delivery['icons'][0] != 'asset://surg'


@pytest.mark.now('2021-06-30T12:00:00+03:00')
@experiments.DISABLE_CALC_SURGE_BULK
@experiments.eats_catalog_surge_radius()
@experiments.eats_surge_planned(interval=120)
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@configs.eda_delivery_price_promo()
@pytest.mark.experiments3(
    name='eats_new_user_promotion',
    consumers=['eda-delivery-price/is-new-user'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'free_surge': True, 'retail_free_delivery': False},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'native_orders',
                    'arg_type': 'int',
                    'value': 3,
                },
            },
        },
    ],
    enable_debug=True,
)
async def test_null_surge_for_newbie(
        catalog_for_layout, eats_catalog_storage, surge_resolver, mockserver,
):
    """
    Проверяем зануление суржа для новичков
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

    surge_resolver.place_radius = {
        1: surge_utils.SurgeRadius(native_surge_level=1, lavka_surge_level=1),
    }

    eater_id = 'eats_id_1'
    phone_id = 'phone_id_1'

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def stats(request):
        assert request.json == {
            'identities': [
                {'type': 'eater_id', 'value': eater_id},
                {'type': 'phone_id', 'value': phone_id},
            ],
            'group_by': [
                'business_type',
                'delivery_type',
                'brand_id',
                'place_id',
            ],
        }
        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': '176999844'},
                    'counters': [
                        {
                            'first_order_at': '2021-05-27T15:32:00+0000',
                            'last_order_at': '2021-05-31T15:32:00+0000',
                            'properties': [
                                {'name': 'brand_id', 'value': '1'},
                                {
                                    'name': 'business_type',
                                    'value': 'restaurant',
                                },
                                {'name': 'delivery_type', 'value': 'native'},
                                {'name': 'place_id', 'value': '1'},
                            ],
                            'value': 3,
                        },
                        {
                            'first_order_at': '2021-05-27T15:32:00+0000',
                            'last_order_at': '2021-05-31T15:32:00+0000',
                            'properties': [
                                {'name': 'brand_id', 'value': '2'},
                                {'name': 'business_type', 'value': 'shop'},
                                {
                                    'name': 'delivery_type',
                                    'value': 'marketplace',
                                },
                                {'name': 'place_id', 'value': '2'},
                            ],
                            'value': 3,
                        },
                    ],
                },
            ],
        }

    block_id = 'any'

    response = await catalog_for_layout(
        blocks=[{'id': block_id, 'type': 'any', 'disable_filters': False}],
        headers={
            'X-Eats-User': f'user_id={eater_id},personal_phone_id={phone_id}',
            'x-device-id': 'test_simple',
            'x-request-id': 'hello',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-Session': 'blablabla',
            'cookie': 'just a cookie',
        },
    )

    assert response.status_code == 200

    assert stats.times_called == 1

    block = layout_utils.find_block(block_id, response.json())
    found_place = layout_utils.find_place_by_slug(place_slug, block)
    delivery = found_place['payload']['data']['features']['delivery']
    assert not delivery['icons'] or delivery['icons'][0] != 'asset://surg'


@pytest.mark.now('2021-10-20T06:00:00+03:00')
@experiments.eats_catalog_surge_radius(enabled=True)
@experiments.SHOW_SURGE_RADIUS_ON_CATALOG
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=120)
async def test_surge_radius_closed_place(
        catalog_for_layout, eats_catalog_storage, surge_resolver,
):
    """
    Проверяем что если плейс уже закрыт и без суржа,
    к нему не добавляются признаки суржа радиусом.
    """

    place_id = 1

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-20T18:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=0),
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
        blocks=[{'id': 'closed', 'type': 'closed', 'disable_filters': False}],
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == 1

    data = response.json()
    block = layout_utils.find_block('closed', data)
    place = layout_utils.find_place_by_slug('place_1', block)
    delivery_features = place['payload']['data']['features']['delivery']
    assert not place['payload']['availability']['is_available']
    assert 'asset://surg' not in delivery_features['icons']
