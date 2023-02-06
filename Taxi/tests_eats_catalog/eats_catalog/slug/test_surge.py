# pylint: disable=too-many-lines
import dataclasses

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils
from . import utils


@dataclasses.dataclass
class Eta:
    min: int
    max: int


@pytest.mark.now('2021-03-30T12:55:00+00:00')
async def test_surge_thresholds(slug, eats_catalog_storage, mockserver):
    """EDACAT-727: тест проверяет, что к в случае суржа для НД ресторана (не
    лавки) к минимальной ненулевой стоимости доставки будет прибавлено значение
    суржа."""

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T23:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 3,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    response = await slug(
        'place_1',
        query={'latitude': 55.750028, 'longitude': 37.534397},
        headers={
            'x-device-id': 'test',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'X-Eats-Session': 'blablabla',
        },
    )
    assert response.status_code == 200
    assert eda_delivery_price_surge.times_called == 1

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['id'] == 1
    assert found_place['place']['slug'] == 'place_1'
    assert found_place['place']['deliveryThresholds'] == [
        {
            'orderPrice': {
                'min': 0,
                'decimalMin': '0',
                'max': 499,
                'decimalMax': '499',
            },
            'deliveryCost': 189,
            'decimalDeliveryCost': '189',
            'name': 'на заказ до 499 ₽',
        },
        {
            'orderPrice': {
                'min': 500,
                'decimalMin': '500',
                'max': 1999,
                'decimalMax': '1999',
            },
            'deliveryCost': 139,
            'decimalDeliveryCost': '139',
            'name': 'на заказ 500-1999 ₽',
        },
        {
            'orderPrice': {
                'min': 2000,
                'decimalMin': '2000',
                'max': None,
                'decimalMax': None,
            },
            'deliveryCost': 0,
            'decimalDeliveryCost': '0',
            'name': 'на заказ от 2000 ₽',
        },
    ]
    assert found_place['surge']['deliveryFee'] == 99 + 139


@pytest.mark.now('2021-03-30T12:55:00+00:00')
@pytest.mark.parametrize(
    'enabled',
    (
        pytest.param(
            False, marks=experiments.surge_preorder(False), id='false',
        ),
        pytest.param(True, marks=experiments.surge_preorder(True), id='true'),
    ),
)
async def test_surge_preorder(slug, eats_catalog_storage, mockserver, enabled):
    """
    Проверяем что сурж применяется для предзаказа
    по эксперименту
    """

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T23:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 3,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    response = await slug(
        'place_1',
        query={
            'latitude': 55.750028,
            'longitude': 37.534397,
            'deliveryTime': parser.parse(
                '2021-03-30T16:00:00+00:00',
            ).isoformat('T'),
        },
        headers={
            'x-device-id': 'test',
            'x-platform': 'ios_app',
            'x-app-version': '5.10.0',
            'X-Eats-Session': 'blablabla',
        },
    )
    assert response.status_code == 200
    assert eda_delivery_price_surge.times_called == 1

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['id'] == 1
    assert found_place['place']['slug'] == 'place_1'
    assert found_place['place']['deliveryThresholds'] == [
        {
            'orderPrice': {
                'min': 0,
                'decimalMin': '0',
                'max': 499,
                'decimalMax': '499',
            },
            'deliveryCost': 189,
            'decimalDeliveryCost': '189',
            'name': 'на заказ до 499 ₽',
        },
        {
            'orderPrice': {
                'min': 500,
                'decimalMin': '500',
                'max': 1999,
                'decimalMax': '1999',
            },
            'deliveryCost': 139,
            'decimalDeliveryCost': '139',
            'name': 'на заказ 500-1999 ₽',
        },
        {
            'orderPrice': {
                'min': 2000,
                'decimalMin': '2000',
                'max': None,
                'decimalMax': None,
            },
            'deliveryCost': 0,
            'decimalDeliveryCost': '0',
            'name': 'на заказ от 2000 ₽',
        },
    ]

    if enabled:
        assert found_place['surge']
    else:
        assert not found_place['surge']
    assert found_place['locationParams']['available']


@pytest.mark.now('2021-03-30T12:55:00+00:00')
async def test_surge_taxi(slug, eats_catalog_storage, mockserver):
    """
    Проверяем что сурж не применяется для доставки такси
    """

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            couriers_type=storage.CouriersType.YandexTaxi,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T23:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 3,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    response = await slug(
        'place_1',
        query={'latitude': 55.750028, 'longitude': 37.534397},
        headers={'X-Eats-Session': 'blablabla'},
    )
    assert response.status_code == 200
    assert eda_delivery_price_surge.times_called == 1

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['id'] == 1
    assert found_place['place']['slug'] == 'place_1'
    assert found_place['place']['deliveryThresholds'] == [
        {
            'orderPrice': {
                'min': 0,
                'decimalMin': '0',
                'max': 499,
                'decimalMax': '499',
            },
            'deliveryCost': 189,
            'decimalDeliveryCost': '189',
            'name': 'на заказ до 499 ₽',
        },
        {
            'orderPrice': {
                'min': 500,
                'decimalMin': '500',
                'max': 1999,
                'decimalMax': '1999',
            },
            'deliveryCost': 139,
            'decimalDeliveryCost': '139',
            'name': 'на заказ 500-1999 ₽',
        },
        {
            'orderPrice': {
                'min': 2000,
                'decimalMin': '2000',
                'max': None,
                'decimalMax': None,
            },
            'deliveryCost': 0,
            'decimalDeliveryCost': '0',
            'name': 'на заказ от 2000 ₽',
        },
    ]
    assert found_place['surge'] is None
    assert found_place['locationParams']['available']


@pytest.mark.now('2021-03-30T12:55:00+00:00')
async def test_surge_unavailable_place(slug, eats_catalog_storage, mockserver):
    """
    Проверяем что сурж не применяется для закрытых ресторанов
    """

    eats_catalog_storage.add_place(storage.Place(place_id=1, slug='place_1'))
    eats_catalog_storage.add_zone(
        storage.Zone(
            couriers_type=storage.CouriersType.Pedestrian,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T10:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': 3,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    response = await slug(
        'place_1',
        query={'latitude': 55.750028, 'longitude': 37.534397},
        headers={'X-Eats-Session': 'blablabla'},
    )
    assert response.status_code == 200
    assert eda_delivery_price_surge.times_called == 1

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['id'] == 1
    assert found_place['place']['slug'] == 'place_1'
    assert not found_place['locationParams']['available']
    assert found_place['surge'] is None


@pytest.mark.parametrize(
    [
        'header',
        'surge_level',
        'coroutine_times_called',
        'business_type',
        'surge_notify_times_called',
    ],
    [
        pytest.param(
            'user_id=1000',
            3,
            1,
            storage.Business.Restaurant,
            1,
            id='matched exp, non zero surge level',
        ),
        pytest.param(
            'user_id=1000',
            3,
            1,
            storage.Business.Store,
            0,
            id='matched exp, non zero surge level',
        ),
        pytest.param(
            'user_id=1000',
            0,
            0,
            storage.Business.Restaurant,
            0,
            id='matched exp, zero surge level',
        ),
        pytest.param(
            'user_id=1005',
            3,
            0,
            storage.Business.Restaurant,
            0,
            id='non matched exp',
        ),
    ],
)
@pytest.mark.experiments3(
    name='eats_catalog_need_to_surge_notify',
    consumers=['eats-catalog-need-to-surge-notify'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['1000'],
                    'arg_name': 'eats_user_id',
                    'set_elem_type': 'string',
                },
            },
            'value': {'enabled': True},
        },
    ],
    default_value={'enabled': False},
)
@pytest.mark.now('2021-03-30T12:55:00+00:00')
async def test_surge_notify(
        # ---- fixtures ----
        slug,
        eats_catalog_storage,
        mockserver,
        testpoint,
        # ---- parameters ----
        header,
        surge_level,
        coroutine_times_called,
        business_type,
        surge_notify_times_called,
):
    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='place_1', business=business_type),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-30T8:00:00+00:00'),
                    end=parser.parse('2021-03-30T23:00:00+00:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(
        '/eda-delivery-price/v1/calc-delivery-price-surge',
    )
    def eda_delivery_price_surge(request):
        if business_type == storage.Business.Store:
            return {
                'calculation_result': {
                    'calculation_name': 'testsuite',
                    'result': {
                        'fees': [
                            {'delivery_cost': 0, 'order_price': 2000},
                            {'delivery_cost': 139, 'order_price': 500},
                            {'delivery_cost': 189, 'order_price': 0},
                        ],
                        'is_fallback': False,
                        'extra': {},
                    },
                },
                'surge_extra': {},
                'surge_result': {
                    'placeId': 1,
                    'lavkaInfo': {
                        'minimumOrder': 0,
                        'surgeLevel': surge_level,
                        'loadLevel': 97,
                        'deliveryFee': 99,
                    },
                },
                'experiment_results': [],
                'experiment_errors': [],
                'meta': {},
            }
        return {
            'calculation_result': {
                'calculation_name': 'testsuite',
                'result': {
                    'fees': [
                        {'delivery_cost': 0, 'order_price': 2000},
                        {'delivery_cost': 139, 'order_price': 500},
                        {'delivery_cost': 189, 'order_price': 0},
                    ],
                    'is_fallback': False,
                    'extra': {},
                },
            },
            'surge_extra': {},
            'surge_result': {
                'placeId': 1,
                'nativeInfo': {
                    'surgeLevel': surge_level,
                    'loadLevel': 97,
                    'deliveryFee': 99,
                },
            },
            'experiment_results': [],
            'experiment_errors': [],
            'meta': {},
        }

    eta_eta = Eta(min=40, max=50)

    @mockserver.json_handler('/umlaas-eats/umlaas-eats/v1/eta')
    def umlaas_eats_eta(request):
        return {
            'exp_list': [],
            'request_id': '',
            'provider': '',
            'predicted_times': [
                {
                    'id': 1,
                    'times': {
                        'total_time': 53.0,
                        'cooking_time': 41.0,
                        'delivery_time': 12.0,
                        'boundaries': dataclasses.asdict(eta_eta),
                    },
                },
            ],
        }

    @mockserver.json_handler(
        '/eats-surge-notify/internal/eats-surge-notify/v1/surge-subscribe',
    )
    def eda_eats_surge_notify(request):
        return mockserver.make_response(status=200)

    @testpoint('send_to_surge_subscribe')
    def send_to_surge_subscribe(data):
        return data

    response = await slug(
        'place_1',
        query={'latitude': 55.750028, 'longitude': 37.534397},
        headers={'X-Eats-Session': 'blablabla', 'X-Eats-User': header},
    )

    if coroutine_times_called:
        await send_to_surge_subscribe.wait_call()

    assert response.status_code == 200
    assert eda_delivery_price_surge.times_called == 1
    assert umlaas_eats_eta.times_called == 1
    assert eda_eats_surge_notify.times_called == surge_notify_times_called

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['id'] == 1
    assert found_place['place']['slug'] == 'place_1'
    if surge_level and business_type != storage.Business.Store:
        assert found_place['surge']['deliveryFee'] == 99 + 139


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@experiments.eats_surge_planned(interval=120)
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@experiments.eats_catalog_surge_radius()
@pytest.mark.parametrize(
    'preorder',
    [
        pytest.param(False, id='radius surge applied'),
        pytest.param(True, id='radius surge applied preorder'),
        pytest.param(
            'can-not-deliver',
            id='radius surge applied preorder can not deliver',
        ),
    ],
)
async def test_surge_radius_schedule(
        slug, eats_catalog_storage, surge_resolver, delivery_price, preorder,
):
    """
    EDACAT-1764: проверяет, что при срабатывании суржа радиусом, отображаемое
    расписание заведения не обрезается суржом, а обрезается только таймпикер
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
        storage.WorkingInterval(
            start=parser.parse('2021-10-21T00:00:00+03:00'),
            end=parser.parse('2021-10-21T02:00:00+03:00'),
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

    delivery_price.set_delivery_conditions(
        [{'delivery_cost': 100.0, 'order_price': 0.0}],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
        },
    )
    surge_resolver.place_radius = {1: surge_utils.SurgeRadius(pedestrian=1000)}

    response = await slug(
        'place_1',
        query={
            'latitude': 55.8,
            'longitude': 37.6,
            'shippingType': 'delivery',
            **(
                {
                    'deliveryTime': (
                        '2021-10-20T21:00:00+03:00'
                        if preorder == 'can-not-deliver'
                        else '2021-10-20T21:30:00+03:00'
                    ),
                }
                if preorder
                else {}
            ),
        },
        headers={'x-eats-session': 'blablabla', 'x-request-language': 'ru'},
    )

    assert response.status_code == 200
    data = response.json()

    footer = data['payload']['foundPlace']['place']['footerDescription']
    timepicker = data['payload']['availableTimePicker']

    # Проверяем, что расписание в футере отображается без учета суржа,
    # а только с учетом расписания заведения
    assert footer == (
        'Исполнитель (продавец): ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
        '"КОФЕ БОЙ", 127015, Москва, ул Вятская, д 27, стр 11, '
        'ИНН 7714457772, рег.номер 1207700043759.'
        '<br>Режим работы: с 10:00 до 24:00'
    )

    # Проверям, что пикер учитывает сурж
    assert timepicker == [
        [],
        ['2021-10-21T01:30:00+03:00', '2021-10-21T02:00:00+03:00'],
    ]


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@pytest.mark.parametrize(
    'use_surge_final_cost',
    (
        pytest.param(False, id='false'),
        pytest.param(True, marks=experiments.USE_SURGE_FINAL_PRICE, id='true'),
    ),
)
async def test_surge_final_cost(
        slug, eats_catalog_storage, delivery_price, use_surge_final_cost,
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

    delivery_fee = delivery_cost + surge_fee
    if use_surge_final_cost:
        delivery_fee = surge_final_cost
    assert (
        data['payload']['foundPlace']['surge']['deliveryFee'] == delivery_fee
    )


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
async def test_surge_radius_delivery_conditions(
        slug, eats_catalog_storage, surge_resolver, delivery_price,
):
    """
    Проверяет, что при сурже радиусом, цена остается из прайсинга
    """

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-21T00:00:00+03:00'),
            end=parser.parse('2021-10-21T02:00:00+03:00'),
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
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=2000, delivery_cost=30),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [{'delivery_cost': 100.0, 'order_price': 0.0}],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
                'show_radius': 1000.0,
            },
        },
    )
    surge_resolver.place_radius = {1: surge_utils.SurgeRadius(pedestrian=1000)}

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
    found_place = data['payload']['foundPlace']

    assert found_place['place']['deliveryThresholds'] == [
        {
            'orderPrice': {
                'min': 0,
                'decimalMin': '0',
                'max': None,
                'decimalMax': None,
            },
            'deliveryCost': 100,
            'decimalDeliveryCost': '100',
            'name': 'на заказ от 0 ₽',
        },
    ]


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@pytest.mark.parametrize(
    'place_type,expected_zone,expected_availability,radius,surge_times_called',
    (
        pytest.param('native', 'pedestrian', True, 5000, 0, id='exp_disabled'),
        pytest.param(
            'marketplace',
            'pedestrian',
            True,
            5000,
            0,
            marks=experiments.eats_catalog_surge_radius(),
            id='marketplace',
        ),
        pytest.param(
            'native',
            'pedestrian',
            True,
            5000,
            1,
            marks=experiments.eats_catalog_surge_radius(),
            id='native_in_radius',
        ),
        pytest.param(
            'native',
            'taxi',
            True,
            1000,
            1,
            marks=experiments.eats_catalog_surge_radius(),
            id='native_out_radius',
        ),
    ),
)
async def test_eats_catalog_surge_radius(
        slug,
        eats_catalog_storage,
        offers,
        surge_resolver,
        place_type,
        expected_zone,
        expected_availability,
        radius,
        surge_times_called,
):
    """
    Проверяем сурж радиусом реализованный через поход
    в eats-surge-resolver до резолва зон
    """

    place_id = 1
    offer_time = '2021-10-20T17:42:00+00:00'
    user_id = '12345'
    # растояние от 0,0 до 0.01,0.01 примерно 1600 метров
    position = [0.01, 0.01]

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    polygon = storage.Polygon(
        [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]],
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            slug='place_1',
            location=storage.Location(lon=0.0, lat=0.0),
            place_type=place_type,
        ),
    )

    pedestrian_zone_id = 1
    taxi_zone_id = 2
    pickup_zone_id = 3

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=pedestrian_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=polygon,
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=taxi_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=polygon,
            couriers_type=storage.CouriersType.YandexTaxi,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=pickup_zone_id,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=schedule,
            polygon=polygon,
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    offers.match_response(
        status=200,
        body={
            'session_id': 'hello',
            'request_time': offer_time,
            'expiration_time': '2021-10-20T17:50:00+00:00',
            'prolong_count': 1,
            'parameters': {'location': position},
            'payload': {},
            'status': 'NO_CHANGES',
        },
    )

    @surge_resolver.request_assertion
    def _surge_request_assertion(request):
        req = request.json
        assert req['placeIds'] == [place_id]
        assert req['ts'] == offer_time
        assert req['user_info'] == {
            'user_id': user_id,
            'region_id': 1,
            'position': position,
        }

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=radius),
    }

    response = await slug(
        'place_1',
        query={'latitude': 0.01, 'longitude': 0.01},
        headers={
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': f'user_id={user_id}',
        },
    )

    assert response.status_code == 200
    assert surge_resolver.times_called == surge_times_called

    data = response.json()

    assert utils.is_pickup_available(data)
    assert utils.is_available(data) == expected_availability

    if expected_availability:
        if expected_zone == 'taxi':
            assert utils.is_taxi_delivery(data)
        if expected_zone == 'pedestrian':
            assert utils.is_pedestrian_delivery(data)


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@experiments.eats_catalog_surge_radius(enable_taxi_flowing=False)
@pytest.mark.parametrize(
    'expected_zone,expected_availability,params',
    (
        pytest.param(
            'pedestrian',
            False,
            {'latitude': 0.02, 'longitude': 0.02},
            id='between_radius_and_pedestian_border',
        ),
        pytest.param(
            'taxi',
            True,
            {'latitude': 1.01, 'longitude': 1.01},
            id='after_pedestian_border',
        ),
    ),
)
async def test_eats_catalog_surge_radius_taxi_flowing_off(
        slug,
        eats_catalog_storage,
        surge_resolver,
        expected_zone,
        expected_availability,
        params,
):
    """
    Проверяем, что при выключенном перетоке в такси
    сурж радиус образует бублик с выключенной доставкой
    между радиусом и границей пешей зоны
    """

    place_id = 1
    user_id = '12345'

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            slug='place_1',
            location=storage.Location(lon=0.0, lat=0.0),
            place_type=storage.PlaceType.Native,
        ),
    )

    pedestrian_zone_id = 1
    taxi_zone_id = 2

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=pedestrian_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=storage.Polygon(
                [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]],
            ),
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=taxi_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=storage.Polygon(
                [[0.0, 0.0], [0.0, 2.0], [2.0, 2.0], [2.0, 0.0], [0.0, 0.0]],
            ),
            couriers_type=storage.CouriersType.YandexTaxi,
        ),
    )

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=1000),
    }

    response = await slug(
        'place_1',
        query=params,
        headers={
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': f'user_id={user_id}',
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert utils.is_available(data) == expected_availability

    if expected_availability:
        if expected_zone == 'taxi':
            assert utils.is_taxi_delivery(data)
        if expected_zone == 'pedestrian':
            assert utils.is_pedestrian_delivery(data)


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=experiments.eats_catalog_surge_radius(
                enabled=True,
                enable_taxi_flowing=False,
                enable_taxi_radius=True,
            ),
            id='taxi_flowing_false',
        ),
        pytest.param(
            marks=experiments.eats_catalog_surge_radius(
                enabled=True,
                enable_taxi_flowing=True,
                enable_taxi_radius=True,
            ),
            id='taxi_flowing_true',
        ),
    ),
)
@pytest.mark.parametrize(
    'radius,taxi_radius,params,expected_zone,expected_availability',
    (
        pytest.param(
            1000,
            2000,
            {'latitude': 0.005, 'longitude': 0.005},
            'pedestrian',
            True,
            id='in_pedestrian_radius',
        ),
        pytest.param(
            1000,
            2000,
            {'latitude': 0.009, 'longitude': 0.009},
            'taxi',
            True,
            id='between_pedestrian_radius_and_pedestrian_border',
        ),
        pytest.param(
            1000,
            2000,
            {'latitude': 0.011, 'longitude': 0.011},
            'taxi',
            True,
            id='between_pedestrian_border_and_taxi_radius',
        ),
        pytest.param(
            1000,
            2000,
            {'latitude': 0.019, 'longitude': 0.019},
            None,
            False,
            id='between_taxi_radius_and_taxi_border',
        ),
    ),
)
async def test_eats_catalog_surge_radius_for_taxi(
        slug,
        eats_catalog_storage,
        surge_resolver,
        radius,
        taxi_radius,
        params,
        expected_zone,
        expected_availability,
):
    """
    Проверяем сурж радиусом для такси зон
    Незвисимо от параметра taxi_flowing поведение должно
    быть одно и то же
    """

    place_id = 1
    user_id = '12345'

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            slug='place_1',
            location=storage.Location(lon=0.0, lat=0.0),
            place_type=storage.PlaceType.Native,
        ),
    )

    pedestrian_zone_id = 1
    taxi_zone_id = 2

    # до границы зоны по диагонали 1572 m
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=pedestrian_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=storage.Polygon(
                [
                    [0.0, 0.0],
                    [0.0, 0.01],
                    [0.01, 0.01],
                    [0.01, 0.0],
                    [0.0, 0.0],
                ],
            ),
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    # до границы зоны по диагонали 3145 m
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=taxi_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=storage.Polygon(
                [
                    [0.0, 0.0],
                    [0.0, 0.02],
                    [0.02, 0.02],
                    [0.02, 0.0],
                    [0.0, 0.0],
                ],
            ),
            couriers_type=storage.CouriersType.YandexTaxi,
        ),
    )

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=radius, taxi=taxi_radius),
    }

    response = await slug(
        'place_1',
        query=params,
        headers={
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': f'user_id={user_id}',
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert utils.is_available(data) == expected_availability

    if expected_availability:
        if expected_zone == 'taxi':
            assert utils.is_taxi_delivery(data)
        if expected_zone == 'pedestrian':
            assert utils.is_pedestrian_delivery(data)


@pytest.mark.now('2021-10-20T20:42:00+03:00')
@configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
@experiments.eats_catalog_surge_radius(use_lru_cache=True)
@experiments.surge_resolver_pipeline(pipeline_name='eats_surge_pipeline')
@pytest.mark.parametrize(
    'has_surge_radius',
    (pytest.param(False, id='no_radius'), pytest.param(True, id='has_radius')),
)
async def test_eats_catalog_surge_radius_cache(
        slug, offers, eats_catalog_storage, surge_resolver, has_surge_radius,
):
    """
    Проверяет, что сурж радиусом кэшируется
    """

    place_id = 1
    user_id = '12345'
    offer_time = '2021-10-20T17:42:00+00:00'
    # растояние от 0,0 до 0.01,0.01 примерно 1600 метров
    position = [0.01, 0.01]

    schedule = [
        storage.WorkingInterval(
            start=parser.parse('2021-10-20T10:00:00+03:00'),
            end=parser.parse('2021-10-21T00:00:00+03:00'),
        ),
    ]

    polygon = storage.Polygon(
        [[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]],
    )

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=place_id,
            slug='place_1',
            location=storage.Location(lon=0.0, lat=0.0),
        ),
    )

    pedestrian_zone_id = 1

    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=place_id,
            zone_id=pedestrian_zone_id,
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=schedule,
            polygon=polygon,
            couriers_type=storage.CouriersType.Pedestrian,
        ),
    )

    radius = None
    if has_surge_radius:
        radius = 1000

    surge_resolver.place_radius = {
        place_id: surge_utils.SurgeRadius(pedestrian=radius),
    }

    @surge_resolver.request_assertion
    def _surge_request_assertion(request):
        req = request.json
        assert req['calculator_name'] == 'eats_surge_pipeline'

    offers.match_response(
        status=200,
        body={
            'session_id': 'hello',
            'request_time': offer_time,
            'expiration_time': '2021-10-20T17:50:00+00:00',
            'prolong_count': 1,
            'parameters': {'location': position},
            'payload': {},
            'status': 'NO_CHANGES',
        },
    )

    response = await slug(
        'place_1',
        query={'latitude': 0.01, 'longitude': 0.01},
        headers={
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': f'user_id={user_id}',
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert utils.is_available(data) != has_surge_radius
    assert surge_resolver.times_called == 1

    response = await slug(
        'place_1',
        query={'latitude': 0.01, 'longitude': 0.01},
        headers={
            'X-Eats-Session': 'blablabla',
            'X-Eats-User': f'user_id={user_id}',
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert utils.is_available(data) != has_surge_radius
    # не изменилось так как взяли результат из кэша
    assert surge_resolver.times_called == 1
