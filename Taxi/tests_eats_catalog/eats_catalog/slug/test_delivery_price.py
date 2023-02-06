from dateutil import parser
import pytest

from eats_catalog import experiments
from eats_catalog import storage

INTERNAL_EATS_CATALOG_PLACES_ZONES = (
    'eats-catalog-storage'
    '/internal/eats-catalog-storage/v1/search/places-zones'
)


@pytest.mark.parametrize(
    'thresholds,surge_info,expected_surge',
    [
        pytest.param(
            [
                {
                    'name': 'на заказ до 499 ₽',
                    'orderPrice': {
                        'min': 0,
                        'decimalMin': '0',
                        'max': 499,
                        'decimalMax': '499',
                    },
                    'deliveryCost': 129,
                    'decimalDeliveryCost': '129',
                },
                {
                    'name': 'на заказ 500-1999 ₽',
                    'orderPrice': {
                        'min': 500,
                        'decimalMin': '500',
                        'max': 1999,
                        'decimalMax': '1999',
                    },
                    'deliveryCost': 29,
                    'decimalDeliveryCost': '29',
                },
                {
                    'name': 'на заказ от 2000 ₽',
                    'orderPrice': {
                        'min': 2000,
                        'decimalMin': '2000',
                        'max': None,
                        'decimalMax': None,
                    },
                    'deliveryCost': 19,
                    'decimalDeliveryCost': '19',
                },
            ],
            {'deliveryFee': 0, 'loadLevel': 0, 'surgeLevel': 0},
            None,
            marks=(experiments.currency_sign('sign')),
            id='get thresholds from eda-delivery-price service',
        ),
        pytest.param(
            [
                {
                    'name': 'на заказ до 499 ₽',
                    'orderPrice': {
                        'min': 0,
                        'decimalMin': '0',
                        'max': 499,
                        'decimalMax': '499',
                    },
                    'deliveryCost': 129,
                    'decimalDeliveryCost': '129',
                },
                {
                    'name': 'на заказ 500-1999 ₽',
                    'orderPrice': {
                        'min': 500,
                        'decimalMin': '500',
                        'max': 1999,
                        'decimalMax': '1999',
                    },
                    'deliveryCost': 29,
                    'decimalDeliveryCost': '29',
                },
                {
                    'name': 'на заказ от 2000 ₽',
                    'orderPrice': {
                        'min': 2000,
                        'decimalMin': '2000',
                        'max': None,
                        'decimalMax': None,
                    },
                    'deliveryCost': 19,
                    'decimalDeliveryCost': '19',
                },
            ],
            {'deliveryFee': 201, 'loadLevel': 0, 'surgeLevel': 3},
            {
                'title': 'Повышенный спрос',
                'message': (
                    'Заказов сейчас очень много — чтобы еда '
                    'приехала в срок, стоимость доставки '
                    'временно увеличена'
                ),
                'description': 'Повышенный спрос',
                'deliveryFee': (201 + 19),
            },
            marks=(experiments.currency_sign('sign')),
            id='get thresholds from eda-delivery-price service, with surge',
        ),
    ],
)
@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_slug_delivery_thresholds(
        slug,
        surge,
        delivery_price,
        thresholds,
        surge_info,
        expected_surge,
        eats_catalog_storage,
):
    eats_catalog_storage.add_place(
        storage.Place(
            features=storage.Features(
                constraints=[
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderPrice, 50000,
                    ),
                    storage.Constraint(
                        storage.ConstraintCode.MaxOrderWeight, 12,
                    ),
                ],
            ),
            timing=storage.PlaceTiming(extra_preparation=60.0),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=30),
                storage.DeliveryCondition(order_cost=1699, delivery_cost=20),
                storage.DeliveryCondition(order_cost=2000, delivery_cost=0),
            ],
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

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 129.0, 'order_price': 0.0},
            {'delivery_cost': 29.0, 'order_price': 500.0},
            {'delivery_cost': 19.0, 'order_price': 2000.0},
        ],
    )

    delivery_price.set_place_surge({'placeId': 1, 'nativeInfo': surge_info})

    response = await slug('coffee_boy_novodmitrovskaya_2k6')

    assert response.status == 200

    assert surge.times_called == 0
    assert delivery_price.times_called == 1

    found_place: dict = response.json()['payload']['foundPlace']

    assert found_place['place']['deliveryThresholds'] == thresholds
    assert found_place['surge'] == expected_surge


@pytest.mark.now('2021-01-01T12:00:00+00:00')
async def test_slug_limit_delivery_fee(
        slug, mockserver, eats_catalog_storage, delivery_price,
):
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, slug='testsuite', region=storage.Region(region_id=1),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T22:00:00+00:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-01-02T10:00:00+00:00'),
                    end=parser.parse('2021-01-02T14:00:00+00:00'),
                ),
            ],
        ),
    )

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 529.0, 'order_price': 0.0},
            {'delivery_cost': 329.0, 'order_price': 500.0},
            {'delivery_cost': 200.0, 'order_price': 2000.0},
        ],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {
                'surgeLevel': 1,
                'loadLevel': 1,
                'deliveryFee': 200,
            },
        },
    )

    @mockserver.json_handler('/eats-core/v1/export/settings/regions-settings')
    def _regions_settings(request):
        return {
            'payload': {
                'defaultMarketPlaceOffset': 0,
                'defaultNativeOffset': -10,
                'regionsOptions': [
                    {
                        'nativeMaxDeliveryFee': 399,
                        'offset': -10,
                        'regionId': 1,
                        'yandexTaxiMaxDeliveryFee': None,
                    },
                ],
                'storeOptions': {'minTime': 10, 'offset': 10},
            },
        }

    response = await slug('testsuite')
    assert response.status == 200

    found_place: dict = response.json()['payload']['foundPlace']
    assert found_place['place']['deliveryThresholds'] == [
        {
            'name': 'на заказ до 499 ₽',
            'orderPrice': {
                'min': 0,
                'decimalMin': '0',
                'max': 499,
                'decimalMax': '499',
            },
            'deliveryCost': 399,
            'decimalDeliveryCost': '399',
        },
        {
            'name': 'на заказ 500-1999 ₽',
            'orderPrice': {
                'min': 500,
                'decimalMin': '500',
                'max': 1999,
                'decimalMax': '1999',
            },
            'deliveryCost': 329,
            'decimalDeliveryCost': '329',
        },
        {
            'name': 'на заказ от 2000 ₽',
            'orderPrice': {
                'min': 2000,
                'decimalMin': '2000',
                'max': None,
                'decimalMax': None,
            },
            'deliveryCost': 200,
            'decimalDeliveryCost': '200',
        },
    ]
    assert found_place['surge'] == {
        'title': 'Повышенный спрос',
        'message': (
            'Заказов сейчас очень много — чтобы еда '
            'приехала в срок, стоимость доставки '
            'временно увеличена'
        ),
        'description': 'Повышенный спрос',
        'deliveryFee': 399,
    }


@pytest.mark.now('2021-01-01T12:00:00+00:00')
@pytest.mark.parametrize(
    'should_fail,place_type,courier_type',
    (
        pytest.param(
            False,
            storage.PlaceType.Native,
            storage.CouriersType.Pedestrian,
            id='ok',
        ),
        pytest.param(
            True,
            storage.PlaceType.Native,
            storage.CouriersType.Pedestrian,
            id='fallback',
        ),
        pytest.param(
            False,
            storage.PlaceType.Native,
            storage.CouriersType.YandexTaxi,
            id='taxi_ok',
        ),
        pytest.param(
            True,
            storage.PlaceType.Native,
            storage.CouriersType.YandexTaxi,
            id='taxi_fallback',
        ),
        pytest.param(
            False,
            storage.PlaceType.Marketplace,
            storage.CouriersType.Pedestrian,
            id='marketplace',
        ),
    ),
)
async def test_pricing_metrics(
        slug,
        taxi_eats_catalog,
        taxi_eats_catalog_monitor,
        eats_catalog_storage,
        delivery_price,
        should_fail,
        place_type,
        courier_type,
):
    """
    Проверяет метрики фолбека цены доставки
    """

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, slug='testsuite', place_type=place_type),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-01-01T10:00:00+00:00'),
                    end=parser.parse('2021-01-01T22:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=100),
                storage.DeliveryCondition(order_cost=500, delivery_cost=60),
                storage.DeliveryCondition(order_cost=2000, delivery_cost=30),
            ],
            couriers_type=courier_type,
        ),
    )

    delivery_price.set_delivery_conditions(
        [
            {'delivery_cost': 300.0, 'order_price': 0.0},
            {'delivery_cost': 200.0, 'order_price': 500.0},
            {'delivery_cost': 100.0, 'order_price': 2000.0},
        ],
    )
    delivery_price.set_place_surge(
        {
            'placeId': 1,
            'nativeInfo': {'surgeLevel': 0, 'loadLevel': 0, 'deliveryFee': 0},
        },
    )

    delivery_price.should_fail = should_fail

    await taxi_eats_catalog.tests_control(reset_metrics=True)

    response = await slug(
        'testsuite', query={'latitude': 55.8, 'longitude': 37.6},
    )
    assert response.status == 200

    metric = await taxi_eats_catalog_monitor.get_metric('delivery-price')

    if place_type == storage.PlaceType.Marketplace:
        # МП не должен влиять на метрики фолбека прайсинга
        assert not metric['total-shows']
        assert not metric['fallback-shows']
        assert not metric['pricing-shows']
        return

    def fallback_assert(metric_value):
        assert metric_value['total-shows'] == 1
        assert metric_value['fallback-shows'] == 1
        assert not metric_value['pricing-shows']

    def ok_assert(metric_value):
        assert metric_value['total-shows'] == 1
        assert metric_value['pricing-shows'] == 1
        assert not metric_value['fallback-shows']

    if should_fail:
        fallback_assert(metric)
    else:
        ok_assert(metric)

    if courier_type == storage.CouriersType.YandexTaxi:
        taxi_metric = await taxi_eats_catalog_monitor.get_metric(
            'delivery-price-taxi',
        )
        if should_fail:
            fallback_assert(taxi_metric)
        else:
            ok_assert(taxi_metric)
