# pylint: disable=C5521
# pylint: disable=C0302
from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage


async def test_internal_place_404(internal_place):
    response = await internal_place('place')
    assert response.status_code == 404


@pytest.mark.parametrize(
    'personal_phone_id, available_pickup',
    [
        pytest.param(
            'special_user',
            True,
            marks=[
                experiments.qsr_pickup_user('special_user'),
                experiments.couriers_pickup(brand_ids=[1]),
            ],
            id='special_user_with_special_brand',
        ),
        pytest.param(
            'special_user',
            True,
            marks=[experiments.qsr_pickup_user('special_user')],
            id='special_user_with_simple_brand',
        ),
        pytest.param(
            'simple_user',
            False,
            marks=[experiments.couriers_pickup(brand_ids=[1])],
            id='simple_user_with_special_brand',
        ),
        pytest.param('simple_user', True, id='simple_user_with_simple_brand'),
    ],
)
@pytest.mark.parametrize(
    'delivery_conditions',
    [
        pytest.param(
            [
                {'order_price': 0, 'delivery_cost': 800},
                {'order_price': 100, 'delivery_cost': 401},
                {'order_price': 1000, 'delivery_cost': 2},
            ],
            id='price_conditions',
        ),
        pytest.param([], id='empty_conditions'),
    ],
)
@pytest.mark.parametrize(
    'surge_value',
    [
        pytest.param(400, id='limit surge'),
        pytest.param(199, id='no limit surge'),
    ],
)
@pytest.mark.now('2021-04-09T13:48:00+03:00')
@pytest.mark.regions_settings(file='regions_settings.json')
async def test_basic(
        internal_place,
        eats_catalog_storage,
        prediction,
        delivery_price,
        mockserver,
        delivery_conditions,
        surge_value,
        personal_phone_id,
        available_pickup,
):

    eats_catalog_storage.add_place(
        storage.Place(
            slug='some_place',
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 500,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=1 * 60),
        ),
    )

    shipping_types = [
        storage.ShippingType.Delivery,
        storage.ShippingType.Pickup,
    ]

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-04-09T10:00:00+03:00'),
            end=parser.parse('2021-04-09T20:00:00+03:00'),
        ),
    ]

    for zone_id, shipping_type in enumerate(shipping_types, start=1):
        eats_catalog_storage.add_zone(
            storage.Zone(
                place_id=1,
                zone_id=zone_id,
                shipping_type=shipping_type,
                working_intervals=schedule,
            ),
        )

    @mockserver.json_handler('/eats-offers/v1/offer/match')
    def eats_offers_match(request):
        assert {
            'session_id': 'blablabla',
            'need_prolong': True,
            'parameters': {'location': [37.591503, 55.802998]},
        } == request.json

        return {
            'session_id': 'blablabla',
            'request_time': '2021-04-09T10:48:00+00:00',
            'expiration_time': '2021-04-09T11:48:00+00:00',
            'prolong_count': 1,
            'parameters': {
                'delivery_time': '2021-04-09T13:45:00+03:00',
                'location': [37.591503, 55.802998],
            },
            'payload': {},
            'status': 'NO_CHANGES',
        }

    prediction.set_place_time(place_id=1, min_minutes=10, max_minutes=20)
    prediction.expected_request = {
        'predicting_at': '2021-04-09T10:45:00+00:00',
        'server_time': '2021-04-09T10:48:00+00:00',
        'user_location': {'lat': 55.802998, 'lon': 37.591503},
        'requested_times': [
            {
                'id': 1,
                'place': {
                    'id': 1,
                    'time_to_delivery': 23,
                    'average_preparation_time': 12.0,
                    'place_increment': 1.0,
                    'region_delivery_time_offset': -10.0,
                    'zone_id': 1.0,
                    'brand_id': 1,
                    'is_fast_food': False,
                    'shown_rating': 4.8002,
                    'average_user_rating': 4.8002,
                    'price_category': 1,
                    'location': {'lon': 37.5916, 'lat': 55.8129},
                    'delivery_type': 'native',
                    'courier_type': 'pedestrian',
                },
                'default_times': {
                    'total_time': 36.0,
                    'cooking_time': 12.0,
                    'delivery_time': 23.0,
                    'boundaries': {'min': 30, 'max': 40},
                },
            },
        ],
    }

    delivery_price.set_delivery_conditions(delivery_conditions)
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'deliveryFee': surge_value,
                'loadLevel': 91,
                'surgeLevel': 2,
            },
        },
    )
    delivery_price.expected_request = {
        'add_surge_inside_pricing': False,
        'due': '2021-04-09T13:45:00+03:00',
        'offer': '2021-04-09T10:48:00+00:00',
        'place_info': {
            'brand_id': 1,
            'place_id': 1,
            'position': [37.5916, 55.8129],
            'region_id': 1,
            'type': 'native',
            'business_type': 'restaurant',
            'currency': {'sign': '₽'},
        },
        'route_info': {'distance_m': 1101.0703634086447, 'time_sec': 960.0},
        'user_info': {
            'user_id': '123',
            'device_id': '',
            'position': [37.591503, 55.802998],
            'personal_phone_id': personal_phone_id,
        },
        'zone_info': {'zone_name': 'Zone Name', 'zone_type': 'pedestrian'},
    }

    response = await internal_place(
        headers={
            'X-Eats-User': 'user_id=123, personal_phone_id={}'.format(
                personal_phone_id,
            ),
            'X-Eats-Session': 'blablabla',
        },
        slug='some_place',
        delivery_time='2021-04-09T13:48:00+03:00',
        position=[37.591503, 55.802998],
    )

    assert response.status_code == 200
    assert eats_offers_match.times_called == 1
    assert prediction.times_called == 1
    assert delivery_price.times_called == 1

    thresholds = []
    if not delivery_conditions:
        thresholds = [
            {'order_price': '0', 'delivery_cost': '139'},
            {'order_price': '500', 'delivery_cost': '89'},
            {'order_price': '2000', 'delivery_cost': '0'},
        ]
    else:
        thresholds = [
            {'order_price': '0', 'delivery_cost': '349'},
            {'order_price': '100', 'delivery_cost': '349'},
            {'order_price': '1000', 'delivery_cost': '2'},
        ]

    min_delivery_fee = 89 if not delivery_conditions else 2
    surge_delivery_fee = min(349, surge_value + min_delivery_fee)

    assert {
        'place': {
            'name': 'Тестовое заведение 1293',
            'brand': {'id': 1, 'slug': 'coffee_boy_euocq'},
            'business': 'restaurant',
            'location': {
                'country': {'id': 35, 'code': 'RU'},
                'address': {'short': 'Новодмитровская улица, 2к6'},
                'position': [37.5916, 55.8129],
                'region_id': 1,
            },
            'currency': {'code': 'RUB', 'sign': '₽'},
            'assembly_cost': '123',
            'delivery': {
                'type': 'native',
                'thresholds': thresholds,
                'estimated_duration': {'min': 10, 'max': 20},
                'courier_type': 'pedestrian',
                'available_courier_types': [
                    {'priority': 1, 'type': 'pedestrian'},
                ],
                'zone_name': 'Zone Name',
            },
            'is_available': True,
            'available_shipping_types': (
                ['pickup', 'delivery'] if available_pickup else ['delivery']
            ),
            'available_payment_methods': ['googlePay', 'applePay', 'payture'],
            'constraints': {
                'maximum_order_price': {'value': '500', 'text': '500 ₽'},
                'maximum_order_weight': {'value': 12.0, 'text': '12 кг'},
            },
            'surge': {
                'title': 'Повышенный спрос',
                'message': (
                    'Заказов сейчас очень много — чтобы еда приехала в срок, '
                    'стоимость доставки временно увеличена'
                ),
                'description': 'Повышенный спрос',
                'delivery_fee': str(surge_delivery_fee),
            },
            'surge_info': {
                'level': 2,
                'delivery_fee': str(surge_delivery_fee),
                'additional_fee': str(surge_value),
            },
            'timings': {
                'avg_preparation': 12,
                'extra_preparation': 1,
                'fixed': 20,
                'preparation': 10,
            },
            'is_marketplace': False,
            'is_ultima': False,
        },
        'timepicker': [
            [
                '2021-04-09T14:30:00+03:00',
                '2021-04-09T15:00:00+03:00',
                '2021-04-09T15:30:00+03:00',
                '2021-04-09T16:00:00+03:00',
                '2021-04-09T16:30:00+03:00',
                '2021-04-09T17:00:00+03:00',
                '2021-04-09T17:30:00+03:00',
                '2021-04-09T18:00:00+03:00',
                '2021-04-09T18:30:00+03:00',
                '2021-04-09T19:00:00+03:00',
                '2021-04-09T19:30:00+03:00',
                '2021-04-09T20:00:00+03:00',
            ],
            [],
        ],
        'offer': {
            'delivery_time': '2021-04-09T10:45:00+00:00',
            'position': [37.591503, 55.802998],
            'request_time': '2021-04-09T10:48:00+00:00',
        },
    } == response.json()


@pytest.mark.now('2021-06-30T18:04:00+03:00')
async def test_empty_timepicker(internal_place, eats_catalog_storage):
    """
    Проверяет, что в случаях, когда у заведения нет доступных времен,
    на которые можно оформить предзаказ, то ручка все равно вернет массив из
    двух элементов, по спеке
    """

    eats_catalog_storage.add_place(
        storage.Place(
            slug='some_place',
            features=storage.Features(supports_preordering=False),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-30T10:00:00+03:00'),
                    end=parser.parse('2021-06-30T20:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='some_place',
        delivery_time='2021-04-09T13:48:00+03:00',
        position=[37.591503, 55.802998],
    )

    assert response.status_code == 200

    data = response.json()
    assert data['timepicker'] == [[], []]


@pytest.mark.now('2021-05-19T18:55:00+03:00')
async def test_internal_place_without_position(
        internal_place, eats_catalog_storage,
):
    """
    EDACAT-1012: проверяет, что в случае запроса к доступному, по времени,
    заведению без указания геопозиции не будет попытки запросить время
    доставки из cart_eta, а следоватьно не будет исключния, которое
    возникает в следствии того что была попытка сделать запрос к cart_eta
    без точки
    """

    eats_catalog_storage.add_place_from_file('EDACAT-1012_place.json')
    eats_catalog_storage.add_zones_from_file('EDACAT-1012_zones.json')

    response = await internal_place(slug='makdonalds_kerchenskaya_13a')

    assert response.status_code == 200
    assert response.json()['place']['is_marketplace'] is False


@pytest.mark.now('2021-08-02T21:48:00+03:00')
@pytest.mark.parametrize(
    'platform, has_taxi_payment',
    [
        pytest.param('desktop_web', False, id='desktop'),
        pytest.param('unknown', False, id='unknown'),
        pytest.param('superapp_web', True, id='superapp_web'),
        pytest.param('superapp_pp_web', True, id='superapp_bro_web'),
        pytest.param(None, False, id='none'),
        pytest.param('', False, id='empty'),
        pytest.param('ios_app', False, id='ios_app'),
        pytest.param('android_app', False, id='android_app'),
    ],
)
async def test_taxi_payment_method(
        internal_place, eats_catalog_storage, platform, has_taxi_payment,
):

    eats_catalog_storage.add_place(storage.Place(slug='some_place'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-08-02T20:00:00+03:00'),
                    end=parser.parse('2021-08-03T00:00:00+03:00'),
                ),
            ],
        ),
    )

    headers = {}
    if platform:
        headers['x-platform'] = platform

    response = await internal_place(
        headers=headers, slug='some_place', position=[37.591503, 55.802998],
    )

    assert response.status_code == 200

    data = response.json()

    payment_methods = data['place']['available_payment_methods']

    assert has_taxi_payment == ('taxi' in payment_methods)

    if platform == 'ios_app':
        assert 'applePay' in payment_methods
        assert 'googlePay' not in payment_methods

    if platform == 'android_app':
        assert 'googlePay' in payment_methods
        assert 'applePay' not in payment_methods


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@pytest.mark.parametrize(
    'use_surge_final_cost',
    (
        pytest.param(False, id='false'),
        pytest.param(True, marks=experiments.USE_SURGE_FINAL_PRICE, id='true'),
    ),
)
async def test_surge_final_cost(
        internal_place,
        eats_catalog_storage,
        delivery_price,
        use_surge_final_cost,
):
    """
    Проверяет, что если активен эксп eats_catalog_use_surge_final_price
    цена доставки при сурже берется из прайсинга,
    а не высчитывается из трешхолдов
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=1),
            slug='place_1',
            location=storage.Location(lon=37.5916, lat=55.8129),
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
        ),
    )

    delivery_cost = 10.0
    surge_fee = 20.0
    surge_final_cost = 50.0

    delivery_price.set_delivery_conditions(
        [{'delivery_cost': delivery_cost, 'order_price': 0.0}],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': surge_fee,
            },
        },
    )
    delivery_price.set_surge_final_cost(surge_final_cost)

    response = await internal_place(
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'desktop_web',
            'x-app-version': '1.12.0',
            'x-eats-session': 'blablabla',
            'x-request-language': 'ru',
        },
        slug='place_1',
        position=[37.6, 55.8],
    )

    assert response.status_code == 200
    data = response.json()

    delivery_fee = delivery_cost + surge_fee
    if use_surge_final_cost:
        delivery_fee = surge_final_cost
    assert data['place']['surge_info']['delivery_fee'] == str(
        int(delivery_fee),
    )


@pytest.mark.now('2021-04-09T13:48:00+03:00')
async def test_disable_pricing(
        internal_place,
        eats_catalog_storage,
        delivery_price,
        surge,
        prediction,
):
    """
    Проверяем, что если передан флаг
    disable_pricing, то каталог не ходит
    в /v1/calc-delivery-price-surge за ценами
    и /unlaas-eats/v1/eta
    но взамен ходит в /v2/calc-surge-bulk
    """
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-04-09T10:00:00+03:00'),
            end=parser.parse('2021-04-09T20:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='some_place', working_intervals=schedule,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=schedule,
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=30),
                storage.DeliveryCondition(order_cost=500, delivery_cost=20),
                storage.DeliveryCondition(order_cost=1000, delivery_cost=0),
            ],
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

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='some_place',
        position=[37.591503, 55.802998],
        disable_pricing=True,
    )

    assert prediction.times_called == 0
    assert delivery_price.times_called == 0
    assert surge.times_called == 1

    assert response.status_code == 200
    data = response.json()

    # проверяем что трешлоды все еще заполняются
    # данными из кэша
    assert data['place']['delivery']['thresholds'] == [
        {'order_price': '0', 'delivery_cost': '30'},
        {'order_price': '500', 'delivery_cost': '20'},
        {'order_price': '1000', 'delivery_cost': '0'},
    ]
    # проверяем что сурж применился
    assert data['place']['surge_info']['level'] == 2


@pytest.mark.now('2021-11-17T18:27:00+03:00')
async def test_regions_setting_fallback(
        internal_place, mockserver, eats_catalog_storage,
):
    """
    Проверяет что в случае если кеш настроек регона не будет заполнен
    ручка вренет валидный ответ
    """

    # NOTE(nk2ge5k): на деле это ничего не делает так как в conftest autouse
    # фикстура, которая заполняет кеш до того как успевает дернуться этот
    # мок. Оставляю его тут больше для понятности и на случай если каким-то
    # образом autouse пропадет.
    @mockserver.handler('/eats-core/v1/export/settings/regions-settings')
    def _eats_core(_):
        return mockserver.make_response(status=500)

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-11-17T10:00:00+03:00'),
            end=parser.parse('2021-11-17T20:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='some_place', working_intervals=schedule,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, zone_id=1, working_intervals=schedule),
    )

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='some_place',
        position=[37.591503, 55.802998],
    )

    assert response.status_code == 200

    data = response.json()
    assert data['place']['name'] == 'Тестовое заведение 1293'


ENABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'internal_place': True}},
)

DISABLE_PROLONGATION = pytest.mark.config(
    EATS_CATALOG_OFFER={'prolongation': {'internal_place': False}},
)


@pytest.mark.parametrize(
    'expected_prolong',
    [
        pytest.param(True, id='offer prolong expected, default config'),
        pytest.param(
            True,
            id='offer prolong expected by config',
            marks=ENABLE_PROLONGATION,
        ),
        pytest.param(
            False,
            id='no offer prolong expected by config',
            marks=DISABLE_PROLONGATION,
        ),
    ],
)
async def test_offer_prolongation_config(
        internal_place, offers, expected_prolong,
):
    offers.match_request(
        {
            'need_prolong': expected_prolong,
            'parameters': {'location': [37.591503, 55.802998]},
            'session_id': 'blablabla',
        },
    )

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='some_place',
        position=[37.591503, 55.802998],
    )

    assert response.status_code == 404
    assert offers.match_times_called == 1


@pytest.mark.now('2021-11-19T16:09:00+03:00')
@experiments.USE_CUSTOMER_SLOTS_SHARED
@configs.disable_brand_preorder(brand_ids=['1'])
@pytest.mark.parametrize(
    ['brand_id', 'timepicker'],
    [
        pytest.param(1, [[], []], id='disabled timepicker'),
        pytest.param(
            2,
            [
                [
                    '2021-11-19T18:30:00+03:00',
                    '2021-11-19T19:00:00+03:00',
                    '2021-11-19T19:30:00+03:00',
                    '2021-11-19T20:00:00+03:00',
                    '2021-11-19T20:30:00+03:00',
                    '2021-11-19T21:00:00+03:00',
                    '2021-11-19T21:30:00+03:00',
                ],
                [],
            ],
            id='enabled timepicker',
        ),
    ],
)
async def test_disable_timpicker(
        internal_place, eats_catalog_storage, brand_id, timepicker,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-11-19T12:00:00+03:00'),
            end=parser.parse('2021-11-19T20:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            brand=storage.Brand(brand_id=brand_id),
            slug='test_shop',
            business=storage.Business.Shop,
            working_intervals=schedule,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, working_intervals=schedule),
    )

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='test_shop',
        position=[37.583948, 55.73442],
    )

    assert response.status_code == 200

    data = response.json()
    assert data['timepicker'] == timepicker


@pytest.mark.now('2021-12-23T16:09:00+03:00')
@pytest.mark.parametrize(
    'delivery_time,timepicker,is_available,business,disable_on_place',
    [
        pytest.param(
            None,
            [
                [
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                    '2021-12-23T19:30:00+03:00',
                    '2021-12-23T20:00:00+03:00',
                    '2021-12-23T20:30:00+03:00',
                    '2021-12-23T21:00:00+03:00',
                    '2021-12-23T21:30:00+03:00',
                ],
                [],
            ],
            True,
            storage.Business.Restaurant,
            False,
            id='ASAP, preorder enabled',
        ),
        pytest.param(
            None,
            [
                [
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                    '2021-12-23T19:30:00+03:00',
                    '2021-12-23T20:00:00+03:00',
                    '2021-12-23T20:30:00+03:00',
                    '2021-12-23T21:00:00+03:00',
                    '2021-12-23T21:30:00+03:00',
                ],
                [],
            ],
            True,
            storage.Business.Shop,
            False,
            marks=(experiments.DISABLE_PREORDER_FOR_RESTAURANTS),
            id='ASAP, preorder disable for restaraunts',
        ),
        pytest.param(
            None,
            [[], []],
            True,
            storage.Business.Shop,
            False,
            marks=(experiments.DISABLE_PREORDER_FOR_SHOPS_ONLY),
            id='ASAP, preorder disable for shops',
        ),
        pytest.param(
            None,
            [[], []],
            True,
            storage.Business.Restaurant,
            False,
            marks=(experiments.DISABLE_PREORDER),
            id='ASAP, preorder disabled',
        ),
        pytest.param(
            '2021-12-23T18:09:00+03:00',
            [
                [
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                    '2021-12-23T19:30:00+03:00',
                    '2021-12-23T20:00:00+03:00',
                    '2021-12-23T20:30:00+03:00',
                    '2021-12-23T21:00:00+03:00',
                    '2021-12-23T21:30:00+03:00',
                ],
                [],
            ],
            True,
            storage.Business.Restaurant,
            False,
            id='Preorder, preorder enabled',
        ),
        pytest.param(
            '2021-12-23T18:09:00+03:00',
            [[], []],
            False,
            storage.Business.Restaurant,
            False,
            marks=(experiments.DISABLE_PREORDER),
            id='Preorder, preorder disabled',
        ),
        pytest.param(
            '2021-12-23T18:09:00+03:00',
            [
                [
                    '2021-12-23T18:30:00+03:00',
                    '2021-12-23T19:00:00+03:00',
                    '2021-12-23T19:30:00+03:00',
                    '2021-12-23T20:00:00+03:00',
                    '2021-12-23T20:30:00+03:00',
                    '2021-12-23T21:00:00+03:00',
                    '2021-12-23T21:30:00+03:00',
                ],
                [],
            ],
            True,
            storage.Business.Restaurant,
            False,
            marks=(experiments.DISABLE_PREORDER_FOR_SHOPS_ONLY),
            id='Preorder, preorder disabled for shop + restaurant',
        ),
        pytest.param(
            '2021-12-23T18:09:00+03:00',
            [[], []],
            False,
            storage.Business.Restaurant,
            True,
            id='Preorder, preorder disabled on place',
        ),
        pytest.param(
            None,
            [[], []],
            True,
            storage.Business.Restaurant,
            True,
            id='ASAP, preorder disabled on place',
        ),
    ],
)
async def test_disable_preorder(
        internal_place,
        eats_catalog_storage,
        delivery_time,
        timepicker,
        is_available,
        business,
        disable_on_place,
):
    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-12-23T12:00:00+03:00'),
            end=parser.parse('2021-12-23T20:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            slug='test_place',
            business=business,
            features=storage.Features(
                supports_preordering=not disable_on_place,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(place_id=1, working_intervals=schedule),
    )

    response = await internal_place(
        headers={'X-Eats-User': 'user_id=123', 'X-Eats-Session': 'blablabla'},
        slug='test_place',
        position=[37.583948, 55.73442],
        delivery_time=delivery_time,
    )

    assert response.status_code == 200

    data = response.json()
    assert data['timepicker'] == timepicker
    assert data['place']['is_available'] == is_available


EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)


@pytest.mark.now('2022-02-17T21:43:00+03:00')
@experiments.USE_DELIVERY_SLOTS
@pytest.mark.parametrize(
    'slot_available',
    [
        pytest.param(True, id='slot available'),
        pytest.param(False, id='slot unavailable'),
    ],
)
@pytest.mark.parametrize(
    'asap_available',
    [
        pytest.param(True, id='asap available'),
        pytest.param(False, id='asap unavailable'),
    ],
)
async def test_place_delivery_slot(
        internal_place,
        eats_catalog_storage,
        mockserver,
        slot_available,
        asap_available,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=100, slug='test_place', business=storage.Business.Shop,
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=100,
            working_intervals=[
                storage.WorkingInterval(
                    # Расписание на следующий день для того чтобы без
                    # слота всегда получалось бы недоступная доставка
                    start=parser.parse('2022-02-18T12:00:00+03:00'),
                    end=parser.parse('2022-02-18T20:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(_):
        return {
            'places': [
                {
                    'place_id': '100',
                    'short_text': 'short_delivery_slot_text',
                    'full_text': 'full_delivery_slot_text',
                    'delivery_eta': 2,
                    'slots_availability': slot_available,
                    'asap_availability': asap_available,
                },
            ],
        }

    response = await internal_place(
        slug='test_place', position=[37.583948, 55.73442],
    )

    assert response.status_code == 200
    assert eats_customer_slots.times_called == 1

    data = response.json()
    assert data['place']['is_available'] == (slot_available or asap_available)


@pytest.mark.now('2022-03-23T19:02:00+03:00')
@pytest.mark.parametrize(
    'business, expected_constraint',
    [
        pytest.param(
            storage.Business.Shop,
            {'value': 11.0, 'text': '11 кг'},
            marks=configs.max_order_weight({}, 11),
            id='shop not in config',
        ),
        pytest.param(
            storage.Business.Shop,
            {'value': 40.0, 'text': '40 кг'},
            marks=configs.max_order_weight({'test_brand': 40}, 11),
            id='shop in config',
        ),
        pytest.param(
            storage.Business.Restaurant,
            None,
            marks=configs.max_order_weight({}, 11),
            id='restaurant not in config',
        ),
        pytest.param(
            storage.Business.Restaurant,
            None,
            marks=configs.max_order_weight({'test_brand': 40}, 11),
            id='restaurant with config',
        ),
    ],
)
async def test_max_order_weight_config(
        eats_catalog_storage, internal_place, business, expected_constraint,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=100,
            slug='test_place',
            business=business,
            brand=storage.Brand(slug='test_brand'),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=100,
            working_intervals=[
                storage.WorkingInterval(
                    # Расписание на следующий день для того чтобы без
                    # слота всегда получалось бы недоступная доставка
                    start=parser.parse('2022-03-23T00:00:00+03:00'),
                    end=parser.parse('2022-03-23T23:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await internal_place(
        slug='test_place', position=[37.583948, 55.73442],
    )

    assert response.status_code == 200

    data = response.json()

    constraints = data['place']['constraints']
    assert constraints.get('maximum_order_weight', None) == expected_constraint


@pytest.mark.now('2022-03-23T19:02:00+03:00')
@pytest.mark.parametrize(
    ('brand_id', 'is_cash_only'),
    [pytest.param(1, True), pytest.param(2, False)],
)
@pytest.mark.config(
    EATS_RETAIL_ALCOHOL_SHOPS={
        '1': {
            'rules': 'text.alcohol_shops.rules',
            'licenses': 'text.alcohol_shops.licenses',
            'rules_with_storage_info': {'full': {}},
            'storage_time': 48,
        },
    },
)
async def test_is_cash_only_place(
        eats_catalog_storage, internal_place, brand_id, is_cash_only,
):
    """
    Тест проверяет что ограничение is_cash_only проставляется для алкомаркета
    и не проставляется для других заведений.
    """
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='slug', brand=storage.Brand(brand_id=brand_id),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-03-23T00:00:00+03:00'),
                    end=parser.parse('2022-03-23T23:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await internal_place(
        slug='slug', position=[37.583948, 55.73442],
    )

    assert response.status_code == 200

    data = response.json()
    constraints = data['place']['constraints']

    if is_cash_only:
        assert constraints['is_cash_only']
    else:
        assert 'is_cash_only' not in constraints


@pytest.mark.now('2022-06-28T15:07:39+03:00')
@pytest.mark.parametrize(
    'is_ultima', [pytest.param(True), pytest.param(False)],
)
async def test_ultima(eats_catalog_storage, internal_place, is_ultima):
    """
    Тест проверят, что для заведений с Ультима зоной приходит флаг
    is_ultima=True
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='test_place', brand=storage.Brand(brand_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-06-28T10:00:00+03:00'),
                    end=parser.parse('2022-06-28T18:00:00+03:00'),
                ),
            ],
            features=storage.ZoneFeatures(is_ultima=is_ultima),
        ),
    )

    response = await internal_place(slug='test_place')

    assert response.status_code == 200

    data = response.json()
    assert data['place']['is_ultima'] == is_ultima
