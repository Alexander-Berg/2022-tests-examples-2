import json

from dateutil import parser
import pytest

from eats_catalog import configs
from eats_catalog import experiments
from eats_catalog import storage

EATS_CUSTOMER_SLOTS = (
    '/eats-customer-slots/api/v1/places/calculate-delivery-time'
)


@pytest.mark.now('2021-03-29T0:51:00+03:00')
@experiments.USE_DELIVERY_SLOTS
@pytest.mark.parametrize(
    'delivery_time, slot_response_code, slot_response, location_pramas',
    [
        pytest.param(
            None,
            200,
            {
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
            },
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': True,
                'availableByTime': True,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': None,
                'eatDay': None,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': True,
                'deliverySlot': {
                    'description': '105\u2009–\u2009115 мин',
                    'shortDescription': '105\u2009–\u2009115 мин',
                },
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='asap available',
        ),
        pytest.param(
            None,
            200,
            {
                'places': [
                    {
                        'place_id': '1',
                        'short_text': 'short_delivery_slot_text',
                        'full_text': 'full_delivery_slot_text',
                        'delivery_eta': 42,
                        'slots_availability': False,
                        'asap_availability': True,
                    },
                ],
            },
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': True,
                'availableByTime': True,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': None,
                'eatDay': None,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': True,
                'deliverySlot': {
                    'description': '105\u2009–\u2009115 мин',
                    'shortDescription': '105\u2009–\u2009115 мин',
                },
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='asap available but no slots',
        ),
        pytest.param(
            None,
            200,
            {
                'places': [
                    {
                        'place_id': '1',
                        'short_text': 'short_delivery_slot_text',
                        'full_text': 'full_delivery_slot_text',
                        'delivery_eta': 42,
                        'slots_availability': True,
                        'asap_availability': False,
                    },
                ],
            },
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': True,
                'availableByTime': True,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': None,
                'eatDay': None,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': False,
                'deliverySlot': {
                    'description': 'full_delivery_slot_text',
                    'shortDescription': 'short_delivery_slot_text',
                },
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='asap unavailable',
        ),
        pytest.param(
            None,
            200,
            {
                'places': [
                    {
                        'place_id': '1',
                        'short_text': 'short_delivery_slot_text',
                        'full_text': 'full_delivery_slot_text',
                        'delivery_eta': 42,
                        'slots_availability': False,
                        'asap_availability': False,
                    },
                ],
            },
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': False,
                'availableByTime': False,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': None,
                'eatDay': None,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': False,
                'deliverySlot': {
                    'description': 'full_delivery_slot_text',
                    'shortDescription': 'short_delivery_slot_text',
                },
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='none available',
        ),
        pytest.param(
            '2021-03-29T08:00:00+03:00',
            200,
            {
                'places': [
                    {
                        'place_id': '1',
                        'short_text': 'short_delivery_slot_text',
                        'full_text': 'full_delivery_slot_text',
                        'delivery_eta': 42,
                        'slots_availability': False,
                        'asap_availability': True,
                    },
                ],
            },
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': True,
                'availableByTime': True,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': None,
                'eatDay': None,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': True,
                'deliverySlot': {
                    'description': 'full_delivery_slot_text',
                    'shortDescription': 'short_delivery_slot_text',
                },
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='preorder with asap available',
        ),
        pytest.param(
            None,
            500,
            {'message': 'fatal error'},
            {
                'deliveryTime': {'min': 105, 'max': 115},
                'available': True,
                'availableByTime': True,
                'availableByLocation': True,
                'distance': 8.739703054214749,
                'availableFrom': None,
                'availableTo': '2021-03-29T08:00:00+03:00',
                'eatDay': 0,
                'availableSlug': None,
                'availableShippingTypes': [{'type': 'delivery'}],
                'prepareTime': {'minutes': 0.0, 'readyAt': None},
                'availableNow': True,
                'shippingInfoAction': {
                    'deliveryFee': {'name': '0 - 139 ₽'},
                    'message': 'Доставка',
                },
            },
            id='error',
        ),
    ],
)
async def test_delivery_slots(
        slug,
        eats_catalog_storage,
        mockserver,
        delivery_time,
        slot_response_code,
        slot_response,
        location_pramas,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug='shop',
            business=storage.Business.Shop,
            features=storage.Features(
                shop_picking_type=storage.ShopPickingType.OurPicking,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-29T0:00:00+03:00'),
                    end=parser.parse('2021-03-29T8:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(request):

        expected_time = '2021-03-29T00:51:00'
        if delivery_time:
            expected_time = delivery_time[:-6]

        assert request.headers['x-platform'] == 'superapp_taxi_web'
        assert request.headers['x-app-version'] == '1.12.0'
        assert {
            'places': [{'place_id': 1, 'estimated_delivery_duration': 6180}],
            'delivery_point': {'lat': 55.73442, 'lon': 37.583948},
            'delivery_time': {'time': expected_time, 'zone': 'Europe/Moscow'},
            'device_id': 'testsuite',
            'user_id': 'bla',
            'phone_id': 'my-phone',
            'personal_phone_id': 'my-phone',
            'source': 'slug',
        } == request.json

        return mockserver.make_response(
            status=slot_response_code, response=json.dumps(slot_response),
        )

    response = await slug(
        'shop',
        query={
            'latitude': 55.73442,
            'longitude': 37.583948,
            'deliveryTime': delivery_time,
        },
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'X-Eats-Session': 'bla',
        },
    )

    assert eats_customer_slots.times_called == 1
    assert response.status_code == 200

    data = response.json()

    assert data['payload']['foundPlace']['place']['slug'] == 'shop'
    assert location_pramas == data['payload']['foundPlace']['locationParams']


@pytest.mark.now('2021-03-29T0:51:00+03:00')
@pytest.mark.parametrize(
    'request_slug, business, piking_type, availability_strategy, user_agent',
    [
        pytest.param(
            'restaurant',
            storage.Business.Restaurant,
            storage.ShopPickingType.OurPicking,
            None,
            'testsuite',
            id='restaurant',
        ),
        pytest.param(
            'native_assembly',
            storage.Business.Shop,
            storage.ShopPickingType.ShopPicking,
            None,
            'testsuite',
            id='native_assembly',
        ),
    ],
)
async def test_delivery_slots_no_slot(
        slug,
        eats_catalog_storage,
        mockserver,
        request_slug,
        business,
        piking_type,
        availability_strategy,
        user_agent,
):
    eats_catalog_storage.add_place(
        storage.Place(
            slug=request_slug,
            business=business,
            features=storage.Features(
                availability_strategy=availability_strategy,
                shop_picking_type=piking_type,
            ),
        ),
    )
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-29T0:00:00+03:00'),
                    end=parser.parse('2021-03-29T8:00:00+03:00'),
                ),
            ],
        ),
    )

    @mockserver.json_handler(EATS_CUSTOMER_SLOTS)
    def eats_customer_slots(_):
        return {}

    response = await slug(
        request_slug,
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'X-Eats-Session': 'bla',
            'user-agent': user_agent,
        },
    )

    assert eats_customer_slots.times_called == 0
    assert response.status_code == 200


@pytest.mark.now('2021-11-19T16:09:00+03:00')
@configs.disable_brand_preorder(brand_ids=['1'])
@experiments.USE_CUSTOMER_SLOTS_SHARED
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
        slug, eats_catalog_storage, brand_id, timepicker,
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

    response = await slug(
        'test_shop',
        query={'latitude': 55.73442, 'longitude': 37.583948},
        headers={
            'x-device-id': 'testsuite',
            'x-platform': 'superapp_taxi_web',
            'x-app-version': '1.12.0',
            'X-Eats-User': 'user_id=bla, personal_phone_id=my-phone',
            'X-Eats-Session': 'bla',
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data['payload']['availableTimePicker'] == timepicker
