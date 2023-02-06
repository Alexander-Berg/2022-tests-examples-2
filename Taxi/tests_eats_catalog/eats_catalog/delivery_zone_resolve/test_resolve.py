# pylint: disable=C0302
import logging

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage
from eats_catalog import surge_utils

logger = logging.getLogger(__name__)

RESOLVE_CONFIG = pytest.mark.config(
    EATS_CATALOG_RESOLVER={
        'is_pricing_enabled': False,
        'return_not_found_error': True,
    },
)


@pytest.mark.parametrize(
    [
        'schedule',
        'place_type',
        'delivery_time',
        'availability_strategy',
        'expected_status',
        'preorder_disabled',
        'shipping_type',
    ],
    [
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T12:00:00+00:00')),
            id='ASAP available',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T12:00:00+00:00'),
                experiments.DISABLE_PREORDER,
            ),
            id='ASAP available with prorder disabled',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            200,
            True,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T12:00:00+00:00')),
            id='ASAP available with prorder disabled on place',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T9:00:00+00:00')),
            id='ASAP available (interval start)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T3:00:00+00:00')),
            id='ASAP uavailable',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T21:45:00+00:00')),
            id='ASAP uavailable (too early)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            None,
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T12:00:00+00:00')),
            id='ASAP marketplace available',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            None,
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T23:00:00+00:00')),
            id='ASAP marketplace unavailable',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            None,
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T21:40:00+00:00')),
            id='ASAP marketplace unavailable (too late)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            '2021-04-18T12:00:00+00:00',
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T10:00:00+00:00')),
            id='Preorder marketplace available',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            '2021-04-18T12:00:00+00:00',
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T10:00:00+00:00'),
                experiments.DISABLE_PREORDER,
            ),
            id='Preorder marketplace available but disabled',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            '2021-04-18T23:00:00+00:00',
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T10:00:00+00:00')),
            id='Preorder marketplace unavailable',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Marketplace,
            '2021-04-18T10:20:00+00:00',
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T10:00:00+00:00')),
            id='Preorder marketplace unavailable (too early)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            None,
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T20:00:00+00:00'),
                experiments.DISABLE_PREORDER_FOR_BK,
            ),
            id='Preorder available',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            'burger_king',
            200,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T20:00:00+00:00'),
                experiments.DISABLE_PREORDER_FOR_RESTAURANTS,
            ),
            id='Preorder available (burger king)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            'burger_king',
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T20:00:00+00:00'),
                experiments.DISABLE_PREORDER_FOR_BK,
            ),
            id='Preorder unvailable (burger king)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(
                pytest.mark.now('2021-04-18T20:00:00+00:00'),
                experiments.DISABLE_PREORDER,
            ),
            id='Preorder available but disabled',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            None,
            204,
            True,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T20:00:00+00:00')),
            id='Preorder available but disabled on place',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T20:17:00+00:00',
            None,
            204,
            False,
            storage.ShippingType.Delivery,
            marks=(pytest.mark.now('2021-04-18T20:00:00+00:00')),
            id='Preorder available (could not prepare)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            None,
            None,
            200,
            False,
            storage.ShippingType.Pickup,
            marks=(pytest.mark.now('2021-04-18T20:00:00+00:00')),
            id='ASAP available (pickup)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            None,
            200,
            False,
            storage.ShippingType.Pickup,
            marks=(pytest.mark.now('2021-04-18T20:00:00+00:00')),
            id='Preorder available (pickup)',
        ),
        pytest.param(
            storage.WorkingInterval(
                start=parser.parse('2021-04-18T9:00:00+00:00'),
                end=parser.parse('2021-04-18T22:00:00+00:00'),
            ),
            storage.PlaceType.Native,
            '2021-04-18T21:00:00+00:00',
            None,
            200,
            True,
            storage.ShippingType.Pickup,
            marks=(pytest.mark.now('2021-04-18T20:00:00+00:00')),
            id='Preorder available and disabled on place (pickup)',
        ),
    ],
)
@pytest.mark.regions_settings(file='regions_settings.json')
async def test_resolve(
        delivery_zones_resolve,
        v2_delivery_zones_resolve,
        eats_catalog_storage,
        schedule,
        place_type,
        delivery_time,
        availability_strategy,
        expected_status,
        preorder_disabled,
        shipping_type,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            place_type=place_type,
            timing=storage.PlaceTiming(average_preparation=20 * 60),
            features=storage.Features(
                availability_strategy=availability_strategy,
                supports_preordering=not preorder_disabled,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            zone_id=1,
            place_id=1,
            working_intervals=[schedule],
            timing=storage.ZoneTimings(market_avg_time=30 * 60),
            shipping_type=shipping_type,
            source_info=storage.SourceInfo(
                source='eats_core', external_id='abc',
            ),
        ),
    )

    response = await delivery_zones_resolve(
        place_id=1,
        delivery_time=delivery_time,
        shipping_type=str(shipping_type),
    )

    assert expected_status == response.status_code

    if expected_status == 200:
        expected_thresholds = [
            {
                'decimal_delivery_cost': '139',
                'decimal_min_order_price': '0',
                'delivery_cost': 139,
                'min_order_price': 0,
            },
            {
                'decimal_delivery_cost': '89',
                'decimal_min_order_price': '500',
                'delivery_cost': 89,
                'min_order_price': 500,
            },
            {
                'decimal_delivery_cost': '0',
                'decimal_min_order_price': '2000',
                'delivery_cost': 0,
                'min_order_price': 2000,
            },
        ]
        if shipping_type == storage.ShippingType.Pickup:
            expected_thresholds = [
                {
                    'decimal_delivery_cost': '0',
                    'decimal_min_order_price': '0',
                    'delivery_cost': 0,
                    'min_order_price': 0,
                },
            ]

        expected_response = {
            'available_shipping_types': [str(shipping_type)],
            'couriers_type': 'pedestrian',
            'delivery_condition': {'thresholds': expected_thresholds},
            'id': 1,
            'eats_core_id': 'abc',
            'name': 'Zone Name',
            'place_id': 1,
        }

        if place_type == storage.PlaceType.Marketplace:
            expected_response['marketplace_avg_time'] = 30
        else:
            expected_response['marketplace_avg_time'] = None

        assert expected_response == response.json()

    # Сейчас V2 просто повторяет то, что делает V1
    response_v2 = await v2_delivery_zones_resolve(
        place_id=1,
        delivery_time=delivery_time,
        shipping_type=str(shipping_type),
    )

    expected_status_v2 = {200: 200, 204: 404}[expected_status]
    assert response_v2.status_code == expected_status_v2
    if expected_status == 200:
        assert response_v2.json() == {
            'place_delivery_zone': response.json(),
            'courier_delivery_zones': [],
        }


@pytest.mark.now('2021-04-21T18:07:00+03:00')
async def test_invalid_resolve(delivery_zones_resolve, eats_catalog_storage):
    eats_catalog_storage.add_place(storage.Place(place_id=1))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            name='Хамовники с Плющихой',
            couriers_type=storage.CouriersType.Pedestrian,
            shipping_type=storage.ShippingType.Delivery,
            timing=storage.ZoneTimings(arrival_time=0),
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-21T07:00:00+03:00'),
                    end=parser.parse('2021-04-21T23:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-04-22T07:00:00+03:00'),
                    end=parser.parse('2021-04-22T23:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=100, delivery_cost=0),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1000,
            name='Default',
            couriers_type=storage.CouriersType.Pedestrian,
            shipping_type=storage.ShippingType.Delivery,
            timing=storage.ZoneTimings(arrival_time=0),
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-21T00:00:00+03:00'),
                    end=parser.parse('2021-04-22T00:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-04-22T00:00:00+03:00'),
                    end=parser.parse('2021-04-23T00:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    response = await delivery_zones_resolve(place_id=1)

    assert response.status_code == 200

    data = response.json()

    assert data['name'] == 'Default'


@pytest.mark.now('2021-04-21T18:07:00+03:00')
@pytest.mark.parametrize(
    'response_code',
    [
        pytest.param(200, id='regular'),
        pytest.param(
            204,
            id='courier pickup place',
            marks=(experiments.couriers_pickup(place_ids=[1]),),
        ),
        pytest.param(
            200,
            id='courier pickup place as courier',
            marks=(
                experiments.couriers_pickup(place_ids=[1]),
                experiments.qsr_pickup_user(),
            ),
        ),
    ],
)
async def test_pickup_resolve(
        delivery_zones_resolve, eats_catalog_storage, response_code,
):
    eats_catalog_storage.add_place(storage.Place(place_id=1))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            name='pickup',
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-21T07:00:00+03:00'),
                    end=parser.parse('2021-04-21T23:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-04-22T07:00:00+03:00'),
                    end=parser.parse('2021-04-22T23:00:00+03:00'),
                ),
            ],
            delivery_conditions=[],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=2,
            name='delivery',
            shipping_type=storage.ShippingType.Delivery,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-04-21T07:00:00+03:00'),
                    end=parser.parse('2021-04-21T23:00:00+03:00'),
                ),
                storage.WorkingInterval(
                    start=parser.parse('2021-04-22T07:00:00+03:00'),
                    end=parser.parse('2021-04-22T23:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    response = await delivery_zones_resolve(place_id=1, shipping_type='pickup')

    assert response.status_code == response_code
    if response_code == 200:
        data = response.json()

        assert data['delivery_condition'] == {
            'thresholds': [
                {
                    'min_order_price': 0,
                    'decimal_min_order_price': '0',
                    'delivery_cost': 0,
                    'decimal_delivery_cost': '0',
                },
            ],
        }
        assert data['name'] == 'pickup'
        assert data['id'] == 1


@pytest.mark.now('2021-05-12T13:11:00+03:00')
async def test_earliest_available_delivery_timepicker(
        slug, delivery_zones_resolve, eats_catalog_storage,
):
    """
    EDACAT-949: проверяет, что если ресторан еще закрыт, то можно сделать
    предзаказ к ближайшему доступному времени. При этом предполагается, что
    ближайшее время будет получено из таймпикера слага, а успешность
    предзаказа зависит от того вернул ли резолвер код ответа 200.
    """

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
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    # Запрашиваем слаг для того чтобы определить ближайшее возможное
    # время, на которое можно оформить предзаказ.
    response = await slug(
        'not_open_yet', query={'latitude': 55.73442, 'longitude': 37.583948},
    )
    assert response.status_code == 200, 'unavailable to find place by slug'

    slug_data = response.json()['payload']

    timepicker = slug_data['availableTimePicker']
    assert timepicker == [
        [
            '2021-05-12T20:30:00+03:00',
            '2021-05-12T21:00:00+03:00',
            '2021-05-12T21:30:00+03:00',
            '2021-05-12T22:00:00+03:00',
            '2021-05-12T22:30:00+03:00',
            '2021-05-12T23:00:00+03:00',
            '2021-05-12T23:30:00+03:00',
            '2021-05-13T00:00:00+03:00',
        ],
        ['2021-05-13T00:30:00+03:00'],
    ]
    delivery_time = timepicker[0][0]

    assert delivery_time != '2021-05-12T18:00:00+03:00'

    for day in timepicker:
        for delivery_time in day:

            response = await delivery_zones_resolve(
                place_id=1,
                delivery_time=delivery_time,
                location=[37.583948, 55.73442],
            )

            assert response.status_code == 200, (
                'invalid response for ' + delivery_time
            )


@pytest.mark.now('2021-05-12T13:11:00+03:00')
async def test_earliest_available_delivery_available_to(
        slug, delivery_zones_resolve, eats_catalog_storage,
):
    """
    EDACAT-949: проверяет, что если ресторан еще закрыт, то можно сделать
    предзаказ к ближайшему доступному времени. При этом предполагается, что
    ближайшее время будет получено из locationParams слага, а успешность
    предзаказа зависит от того вернул ли резолвер код ответа 200.
    """

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
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    # Запрашиваем слаг для того чтобы определить ближайшее возможное
    # время, на которое можно оформить предзаказ.
    response = await slug(
        'not_open_yet', query={'latitude': 55.73442, 'longitude': 37.583948},
    )

    assert response.status_code == 200, 'unavailable to find place by slug'

    slug_data = response.json()['payload']

    assert slug_data['foundPlace']['locationParams']
    assert 'availableFrom' in slug_data['foundPlace']['locationParams']
    assert slug_data['foundPlace']['locationParams']['availableFrom']

    delivery_time = slug_data['foundPlace']['locationParams']['availableFrom']

    assert delivery_time != '2021-05-12T18:00:00+03:00'

    logger.info('Using delivery time %s', delivery_time)

    response = await delivery_zones_resolve(
        place_id=1,
        delivery_time=delivery_time,
        location=[37.591503, 55.802998],
    )

    assert response.status_code == 200


@pytest.mark.now('2021-05-18T04:21:00+03:00')
@pytest.mark.config(
    EATS_CATALOG_PLACE_STORAGE_SETTINGS={
        'min_delivery_minutes': 5,
        'min_preparation_minutes': 5,
        'consider_new_for': 7,
        'schedule_end_offset': 30,
    },
)
async def test_schedule_end_offset(
        slug, delivery_zones_resolve, eats_catalog_storage,
):
    """
    Проверят функционал оффсета времени доступности заказа
    """

    async def resolve(delivery_time):
        response = await delivery_zones_resolve(
            place_id=1, delivery_time=delivery_time,
        )

        return response.status_code == 200

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
                    start=parser.parse('2021-05-18T03:00:00+03:00'),
                    end=parser.parse('2021-05-18T10:00:00+03:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    # Запрашиваем слаг для того чтобы определить ближайшее возможное
    # время, на которое можно оформить предзаказ.
    response = await slug(
        'not_open_yet', query={'longitude': 37.591503, 'latitude': 55.802998},
    )
    assert response.status_code == 200, 'unavailable to find place by slug'

    slug_data = response.json()['payload']

    timepicker = slug_data['availableTimePicker']

    assert timepicker == [
        [
            '2021-05-18T05:30:00+03:00',
            '2021-05-18T06:00:00+03:00',
            '2021-05-18T06:30:00+03:00',
            '2021-05-18T07:00:00+03:00',
            '2021-05-18T07:30:00+03:00',
            '2021-05-18T08:00:00+03:00',
            '2021-05-18T08:30:00+03:00',
            '2021-05-18T09:00:00+03:00',
            '2021-05-18T09:30:00+03:00',
            #  '2021-05-18T10:00:00+03:00', <- offset
        ],
        [],
    ]

    for day in timepicker:
        for delivery_time in day:
            assert await resolve(delivery_time), (
                'invalid response for ' + delivery_time
            )

    # Проверяем, что предзаказ недоступен на последний интервал
    # так как он должен был быть удален офсетом
    assert not await resolve('2021-05-18T10:00:00+03:00')


@pytest.mark.now('2021-05-31T14:16:00+03:00')
async def test_brute_force_pickup_resolve(
        slug, delivery_zones_resolve, eats_catalog_storage,
):
    """
    EDACAT-1087: Проверяет, что все времена из таймпикера самовывоза
    резолвятся без ошибок
    """

    async def resolve(delivery_time):
        response = await delivery_zones_resolve(
            place_id=85303,
            location=[37.645708, 55.759157],
            delivery_time=delivery_time,
            shipping_type='pickup',
        )

        return response.status_code == 200

    eats_catalog_storage.add_place_from_file('85303_place.json')
    eats_catalog_storage.add_zones_from_file('85303_zones.json')

    response = await slug(
        'eatpoint_nosovixinskoe_shosse_14a',
        query={
            'longitude': 37.645708,
            'latitude': 55.759157,
            'shippingType': 'pickup',
        },
    )
    assert response.status_code == 200, 'unable to find place by slug'

    slug_data = response.json()['payload']

    timepicker = slug_data['availableTimePicker']

    assert timepicker == [
        [
            '2021-05-31T15:00:00+03:00',
            '2021-05-31T15:30:00+03:00',
            '2021-05-31T16:00:00+03:00',
            '2021-05-31T16:30:00+03:00',
            '2021-05-31T17:00:00+03:00',
        ],
        [],
    ]

    for day in timepicker:
        for delivery_time in day:
            assert await resolve(delivery_time), (
                'invalid response for ' + delivery_time
            )


@pytest.mark.now('2021-06-21T21:13:29+03:00')
async def test_pickup_closing_early(
        delivery_zones_resolve, eats_catalog_storage,
):
    """
    EDACAT-1227: проверяет, что ASAP заказ самовывоза можно оформить за
    45 минут до закрытия заведения
    """

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=399669,
            timing=storage.PlaceTiming(average_preparation=15 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=399669,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-21T07:00:00+00:00'),
                    end=parser.parse('2021-06-21T19:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    response = await delivery_zones_resolve(
        place_id=399669,
        location=[37.591503, 55.802998],
        delivery_time='2021-06-21T21:13:29+03:00',
        shipping_type='pickup',
    )

    assert response.status_code == 200


@pytest.mark.now('2021-06-30T21:46:00+03:00')
@RESOLVE_CONFIG
async def test_unresolved_error(delivery_zones_resolve, eats_catalog_storage):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=399669,
            timing=storage.PlaceTiming(average_preparation=15 * 60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=399669,
            zone_id=1,
            shipping_type=storage.ShippingType.Pickup,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-06-21T07:00:00+00:00'),
                    end=parser.parse('2021-06-21T19:00:00+00:00'),
                ),
            ],
            delivery_conditions=[
                storage.DeliveryCondition(order_cost=0, delivery_cost=0),
            ],
        ),
    )

    response = await delivery_zones_resolve(
        place_id=399669,
        location=[37.591503, 55.802998],
        delivery_time='2021-06-21T21:13:29+03:00',
        shipping_type='pickup',
    )

    assert response.status_code == 404

    data = response.json()
    assert data['code'] == 'PLACE_UNAVAILABLE_FOR_TIME'


@RESOLVE_CONFIG
@pytest.mark.parametrize(
    'response_code',
    [
        pytest.param(
            200,
            marks=(pytest.mark.now('2021-09-07T08:30:00+03:00')),
            id='no filter',
        ),
        pytest.param(
            404,
            marks=(
                pytest.mark.now('2021-09-07T08:30:00+03:00'),
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                ),
            ),
            id='filter active',
        ),
        pytest.param(
            200,
            marks=(
                pytest.mark.now('2021-09-07T10:30:00+03:00'),
                configs.places_storage_settings(
                    enable_place_schedule_filter=True,
                ),
            ),
            id='filter active available time',
        ),
    ],
)
async def test_place_schedule_filter(
        delivery_zones_resolve, eats_catalog_storage, response_code,
):

    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-09-07T09:00:00+03:00'),
                    end=parser.parse('2021-09-07T19:00:00+03:00'),
                ),
            ],
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-09-07T07:00:00+03:00'),
                    end=parser.parse('2021-09-07T19:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await delivery_zones_resolve(place_id=1)

    assert response.status_code == response_code


@RESOLVE_CONFIG
@pytest.mark.now('2021-07-25T15:00:00+03:00')
@configs.eats_catalog_delivery_feature(
    taxi_delivery_icon_url='test://taxi_delivery',
    disable_by_surge_for_minutes=180,  # 3 часа
    radius_surge_can_keep_automobile_zones=True,
)
@pytest.mark.parametrize(
    'show_radius, expect_delivery_disabled, expected_zone_couriers_type',
    [
        pytest.param(
            1000.0,
            True,
            'pedestrian',
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius surge applied',
        ),
        pytest.param(
            1000.0,
            False,
            'yandex_taxi',
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=True,
            ),
            id='radius surge applied keep taxi',
        ),
        pytest.param(
            2000.0,
            False,
            'pedestrian',
            marks=experiments.eats_catalog_surge_radius(
                enable_taxi_flowing=False,
            ),
            id='radius too big',
        ),
        pytest.param(1000.0, False, 'pedestrian', id='no experiment'),
    ],
)
async def test_resolve_delivery_disabled_by_radius_surge(
        v2_delivery_zones_resolve,
        eats_catalog_storage,
        surge_resolver,
        show_radius,
        expect_delivery_disabled,
        expected_zone_couriers_type,
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

    response = await v2_delivery_zones_resolve(
        place_id=1, location=[37.6, 55.8],
    )

    if expect_delivery_disabled:
        assert response.status_code == 404
        return

    assert response.status_code == 200

    expected_zone_id = 1 if expected_zone_couriers_type == 'pedestrian' else 2
    place_delivery_zone = response.json()['place_delivery_zone']
    assert place_delivery_zone['id'] == expected_zone_id
    assert place_delivery_zone['couriers_type'] == expected_zone_couriers_type
    assert place_delivery_zone['available_shipping_types'] == ['delivery']


@pytest.mark.now('2021-12-23T12:48:00+03:00')
@RESOLVE_CONFIG
@pytest.mark.parametrize(
    'enabled,response_code',
    [
        pytest.param(True, 200, id='enabled'),
        pytest.param(False, 404, id='disabled'),
    ],
)
async def test_delivery_zone_disable(
        delivery_zones_resolve, eats_catalog_storage, enabled, response_code,
):

    eats_catalog_storage.add_place(storage.Place(place_id=1))
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            enabled=enabled,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-12-23T10:00:00+03:00'),
                    end=parser.parse('2021-12-23T19:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await delivery_zones_resolve(
        place_id=1, location=[37.591503, 55.802998],
    )

    assert response.status_code == response_code


@pytest.mark.now('2021-12-23T10:00:00+00:00')
@RESOLVE_CONFIG
@configs.eats_catalog_offer(empty_delivery_time_interval=30)
@pytest.mark.parametrize(
    'delivery_time, offer_match_time',
    (
        pytest.param('2021-12-23T10:29:00+00:00', None, id='asap'),
        pytest.param(
            '2021-12-23T10:30:00+00:00',
            '2021-12-23T10:30:00+00:00',
            id='preorder',
        ),
    ),
)
async def test_get_offer(
        delivery_zones_resolve,
        eats_catalog_storage,
        offers,
        delivery_time,
        offer_match_time,
):
    """
    Проверяем что с включенным экспом eats_catalog_get_offer
    резолв вызывает матч офера, но никогда
    не создает новый офер
    """
    eats_catalog_storage.add_place(
        storage.Place(
            place_id=1, timing=storage.PlaceTiming(average_preparation=60),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-12-23T09:00:00+00:00'),
                    end=parser.parse('2021-12-23T19:00:00+00:00'),
                ),
            ],
        ),
    )

    expected_request = {
        'need_prolong': False,
        'parameters': {'location': [37.591503, 55.802998]},
        'session_id': 'blablabla',
    }

    if offer_match_time:
        expected_request['parameters'].update(
            {'delivery_time': offer_match_time},
        )

    offers.match_request(expected_request)

    offers.match_response(
        status=404, body={'code': 'NOT_FOUND', 'message': 'not_found'},
    )

    response = await delivery_zones_resolve(
        place_id=1,
        location=[37.591503, 55.802998],
        delivery_time=delivery_time,
        headers={
            'x-device-id': 'test_simple',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=123',
            'X-Eats-Session': 'blablabla',
        },
    )

    assert response.status_code == 200
    assert offers.match_times_called == 1
    assert offers.set_times_called == 1


@pytest.mark.now('2022-05-26T13:50:22+03:00')
@RESOLVE_CONFIG
@pytest.mark.parametrize(
    'slots_times_called, business, shipping_type, response_code',
    [
        pytest.param(
            1,
            storage.Business.Shop,
            storage.ShippingType.Delivery,
            200,
            marks=experiments.ENABLE_SHOP_RESOLVE,
            id='shop and slot enabled',
        ),
        pytest.param(
            0,
            storage.Business.Shop,
            storage.ShippingType.Pickup,
            404,
            marks=experiments.ENABLE_SHOP_RESOLVE,
            id='shop pickup and slot enabled',
        ),
        pytest.param(
            0,
            storage.Business.Restaurant,
            storage.ShippingType.Delivery,
            404,
            marks=experiments.ENABLE_SHOP_RESOLVE,
            id='restaurant and slot enabled',
        ),
        pytest.param(
            0,
            storage.Business.Shop,
            storage.ShippingType.Delivery,
            404,
            id='shop and slot disabled',
        ),
        pytest.param(
            0,
            storage.Business.Restaurant,
            storage.ShippingType.Delivery,
            404,
            id='restaurant and slot disabled',
        ),
    ],
)
async def test_slot_resolve(
        mockserver,
        delivery_zones_resolve,
        eats_catalog_storage,
        slots_times_called,
        business,
        shipping_type,
        response_code,
):
    """
    Проверяет, что обращение к сервису слотов за доступностью магазина
    происходит только при включенном конфиге и только для магазинов
    """

    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/places/validate-delivery-time',
    )
    def validate_places(request):
        places = request.json['places']
        assert len(places) == 1
        assert places[0]['place_id'] == 1

        return {
            'places': [
                {
                    'place_id': '1',
                    'delivery_availability': True,
                    'is_asap': True,
                },
            ],
        }

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, business=business),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            enabled=True,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    # Long time ago
                    start=parser.parse('2021-12-23T10:00:00+03:00'),
                    end=parser.parse('2021-12-23T19:00:00+03:00'),
                ),
            ],
        ),
    )

    response = await delivery_zones_resolve(
        place_id=1,
        shipping_type=shipping_type,
        location=[37.591503, 55.802998],
    )

    assert response.status_code == response_code
    assert validate_places.times_called == slots_times_called


@pytest.mark.now('2022-05-26T14:08:14+03:00')
@RESOLVE_CONFIG
@experiments.ENABLE_SHOP_RESOLVE
@pytest.mark.parametrize(
    'delivery_time, delivery_available, is_asap, response_code',
    [
        pytest.param(None, True, True, 200),
        pytest.param(None, True, False, 404),
        pytest.param(None, False, True, 200),
        pytest.param(None, False, False, 404),
        pytest.param('2022-05-26T14:49:40+03:00', True, True, 200),
        pytest.param('2022-05-26T14:49:40+03:00', True, False, 200),
        pytest.param('2022-05-26T14:49:40+03:00', False, True, 404),
        pytest.param('2022-05-26T14:49:40+03:00', False, False, 404),
    ],
)
async def test_shop_resolve(
        mockserver,
        delivery_zones_resolve,
        eats_catalog_storage,
        delivery_time,
        delivery_available,
        is_asap,
        response_code,
):
    @mockserver.json_handler(
        '/eats-customer-slots/api/v1/places/validate-delivery-time',
    )
    def validate_places(request):
        places = request.json['places']
        assert len(places) == 1
        assert places[0]['place_id'] == 1

        return {
            'places': [
                {
                    'place_id': '1',
                    'delivery_availability': delivery_available,
                    'is_asap': is_asap,
                },
            ],
        }

    eats_catalog_storage.add_place(
        storage.Place(place_id=1, business=storage.Business.Shop),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            place_id=1,
            enabled=True,
            zone_id=1,
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2022-05-26T13:00:30+03:00'),
                    end=parser.parse('2022-05-26T17:00:43+03:00'),
                ),
            ],
        ),
    )

    response = await delivery_zones_resolve(
        place_id=1,
        delivery_time=delivery_time,
        location=[37.591503, 55.802998],
    )

    assert validate_places.times_called == 1
    assert response.status_code == response_code
