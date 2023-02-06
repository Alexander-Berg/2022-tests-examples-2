import pytest

from tests_eats_customer_slots import utils


PLACE_ID = 1
PLACE_ORIGIN_ID = 'place_origin_id1'

SLOT_ASAP_TRUE_FIRST = 'slot-asap-true-first-id'
SLOT_ASAP_TRUE_SECOND = 'slot-asap-true-second-id'
SLOT_ASAP_FALSE_FIRST = 'slot-asap-false-first-id'
SLOT_ASAP_FALSE_SECOND = 'slot-asap-false-second-id'


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@pytest.mark.parametrize(
    'asap, delivery_slot_start, delivery_slot_end',
    [
        (
            False,
            '2021-10-19T16:00:00.000000+00:00',
            '2021-10-19T18:00:00.000000+00:00',
        ),
        (True, None, None),
    ],
)
@pytest.mark.parametrize('delivery_duration', [600, 1200])
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': PLACE_ID,
            'categories': [{'id': 1, 'name': 'category_1'}],
            'revision_id': 1,
            'slug': 'place_1',
            'updated_at': '2021-10-12T20:00:00+03:00',
            'name': 'place 1',
            'origin_id': PLACE_ORIGIN_ID,
        },
    ],
)
@utils.settings_config(asap_disable_threshold=3600)
@utils.partner_picking_slots()
async def test_get_picking_slots_200(
        taxi_eats_customer_slots,
        asap,
        delivery_slot_start,
        delivery_slot_end,
        delivery_duration,
        mockserver,
):
    expected_picking_slots = {
        SLOT_ASAP_TRUE_SECOND: {
            'slot_id': SLOT_ASAP_TRUE_SECOND,
            'duration': 1200,
            'from': '2021-10-19T12:30:00.0+00:00',
            'to': '2021-10-19T13:00:00.0+00:00',
        },
        SLOT_ASAP_TRUE_FIRST: {
            'slot_id': SLOT_ASAP_TRUE_FIRST,
            'duration': 1200,
            'from': '2021-10-19T12:00:00.0+00:00',
            'to': '2021-10-19T13:00:00.0+00:00',
        },
        SLOT_ASAP_FALSE_SECOND: {
            'slot_id': SLOT_ASAP_FALSE_SECOND,
            'duration': 1200,
            'from': '2021-10-19T16:30:00.1+00:00',
            'to': '2021-10-19T17:00:00.12+00:00',
        },
        SLOT_ASAP_FALSE_FIRST: {
            'slot_id': SLOT_ASAP_FALSE_FIRST,
            'duration': 1200,
            'from': '2021-10-19T16:00:00.123+00:00',
            'to': '2021-10-19T16:30:00.123456+00:00',
        },
    }

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def mock_partner_get_picking_slots(request):
        assert request.method == 'POST'
        assert request.json['place_origin_id'] == PLACE_ORIGIN_ID
        return mockserver.make_response(
            status=200,
            json={'picking_slots': list(expected_picking_slots.values())},
        )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'asap': asap,
            'delivery_slot_start': delivery_slot_start,
            'delivery_slot_end': delivery_slot_end,
            'delivery_duration': delivery_duration,
            'items': [
                {'origin_id': 'origin_id_1', 'quantity': 2, 'quantum': 500},
            ],
        },
    )

    assert mock_partner_get_picking_slots.times_called == 1
    assert response.status_code == 200
    assert response.json()['place_id'] == PLACE_ID
    assert response.json()['place_origin_id'] == PLACE_ORIGIN_ID
    assert len(response.json()['picking_slots']) == 2
    picking_slots = response.json()['picking_slots']
    expected_slot_first_id = (
        SLOT_ASAP_TRUE_FIRST if asap else SLOT_ASAP_FALSE_FIRST
    )
    expected_slot_second_id = (
        SLOT_ASAP_TRUE_SECOND if asap else SLOT_ASAP_FALSE_SECOND
    )
    assert picking_slots[0]['picking_slot_id'] == expected_slot_first_id
    assert (
        picking_slots[0]['picking_slot_start']
        == expected_picking_slots[expected_slot_first_id]['from']
    )
    assert (
        picking_slots[0]['picking_slot_end']
        == expected_picking_slots[expected_slot_first_id]['to']
    )
    assert picking_slots[1]['picking_slot_id'] == expected_slot_second_id
    assert (
        picking_slots[1]['picking_slot_start']
        == expected_picking_slots[expected_slot_second_id]['from']
    )
    assert (
        picking_slots[1]['picking_slot_end']
        == expected_picking_slots[expected_slot_second_id]['to']
    )


@utils.settings_config(asap_disable_threshold=600)
@pytest.mark.parametrize(
    'asap, delivery_slot_start, delivery_slot_end',
    [
        (
            True,
            '2021-10-19T12:00:00.000000+00:00',
            '2021-10-19T12:00:00.000000+00:00',
        ),
        (True, '2021-10-19T12:00:00.000000+00:00', None),
        (True, None, '2021-10-19T12:00:00.000000+00:00'),
        (False, None, None),
        (False, '2021-10-19T12:00:00.000000+00:00', None),
        (False, None, '2021-10-19T12:00:00.000000+00:00'),
    ],
)
async def test_get_picking_slots_400(
        taxi_eats_customer_slots, asap, delivery_slot_start, delivery_slot_end,
):
    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'asap': asap,
            'delivery_slot_start': delivery_slot_start,
            'delivery_slot_end': delivery_slot_end,
            'delivery_duration': 1200,
            'items': [{'origin_id': 'origin_id_1', 'quantity': 2.0}],
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == 'INVALID_PARAMS'


@utils.settings_config(asap_disable_threshold=600)
@utils.partner_picking_slots()
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': PLACE_ID,
            'categories': [{'id': 1, 'name': 'category_1'}],
            'revision_id': 1,
            'slug': 'place_1',
            'updated_at': '2021-10-12T20:00:00+03:00',
            'name': 'place 1',
            'origin_id': PLACE_ORIGIN_ID,
        },
    ],
)
async def test_get_picking_slots_no_picking_slots_for_place(
        taxi_eats_customer_slots, mockserver,
):
    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def mock_partner_get_picking_slots(request):
        assert request.method == 'POST'
        actual_place_origin_id = request.json['place_origin_id']
        assert actual_place_origin_id == PLACE_ORIGIN_ID
        return mockserver.make_response(
            status=404,
            json={
                'code': 'NOT_FOUND',
                'message': (
                    f'There is no picking'
                    ' slots for place {actual_place_origin_id}'
                ),
            },
        )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'asap': True,
            'delivery_duration': 1200,
            'items': [{'origin_id': 'origin_id_1', 'quantity': 2.0}],
        },
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'NO_PICKING_SLOTS'
    assert mock_partner_get_picking_slots.times_called == 1


@utils.settings_config(asap_disable_threshold=600)
@utils.partner_picking_slots()
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': PLACE_ID,
            'categories': [{'id': 1, 'name': 'category_1'}],
            'revision_id': 1,
            'slug': 'place_1',
            'updated_at': '2021-10-12T20:00:00+03:00',
            'name': 'place 1',
            'origin_id': PLACE_ORIGIN_ID,
        },
    ],
)
async def test_get_picking_slots_partner_unavailable(
        taxi_eats_customer_slots, mockserver,
):
    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def _(request):
        assert request.method == 'POST'
        actual_place_origin_id = request.json['place_origin_id']
        assert actual_place_origin_id == PLACE_ORIGIN_ID
        raise mockserver.NetworkError()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'asap': True,
            'delivery_duration': 1200,
            'items': [{'origin_id': 'origin_id_1', 'quantity': 2.0}],
        },
    )

    assert response.status_code == 500


@utils.settings_config(asap_disable_threshold=600)
@utils.partner_picking_slots()
async def test_get_picking_slots_no_place_origin_id(taxi_eats_customer_slots):
    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'asap': True,
            'delivery_duration': 1200,
            'items': [{'origin_id': 'origin_id_1', 'quantity': 2.0}],
        },
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'NO_PLACE_ORIGIN_ID'


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': PLACE_ID,
            'categories': [{'id': 1, 'name': 'category_1'}],
            'revision_id': 1,
            'slug': 'place_1',
            'updated_at': '2021-10-12T20:00:00+03:00',
            'name': 'place 1',
            'origin_id': PLACE_ORIGIN_ID,
        },
    ],
)
@utils.settings_config(asap_disable_threshold=3600)
@utils.partner_picking_slots()
async def test_get_checkout_picking_slots(
        taxi_eats_customer_slots, mockserver,
):
    expected_picking_slots = [
        {
            'slot_id': SLOT_ASAP_FALSE_FIRST,
            'duration': 1200,
            'from': '2021-10-19T16:00:00.123+00:00',
            'to': '2021-10-19T16:30:00.123456+00:00',
        },
    ]

    @mockserver.json_handler('/eats-products/internal/v2/products/public_id')
    def mock_products_public_id(request):
        return mockserver.make_response(
            json={
                'products_ids': [
                    {'core_id': core_id, 'public_id': f'public_id{core_id}'}
                    for core_id in request.json['core_ids']
                ],
            },
        )

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def mock_products_info(request):
        return mockserver.make_response(
            json={
                'products': [
                    {
                        'id': public_id,
                        'origin_id': f'origin_id{public_id[-1]}',
                        'place_brand_id': str('brand_id'),
                        'name': 'name1',
                        'description': {},
                        'is_choosable': True,
                        'is_catch_weight': False,
                        'adult': False,
                        'shipping_type': 'pickup',
                        'barcodes': [],
                        'images': [],
                        'is_sku': True,
                    }
                    for public_id in request.json['product_ids']
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def mock_partner_get_picking_slots(request):
        assert request.method == 'POST'
        assert request.json['place_origin_id'] == PLACE_ORIGIN_ID
        assert (
            sorted(request.json['items'], key=lambda item: item['origin_id'])
            == [
                {'origin_id': 'origin_id1', 'quantity': 1.0},
                {'origin_id': 'origin_id2', 'quantity': 2.0},
            ]
        )
        return mockserver.make_response(
            status=200, json={'picking_slots': expected_picking_slots},
        )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/partner/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': '2',
            'items': [
                {'core_id': '1', 'quantity': 1},
                {'public_id': 'public_id2', 'quantity': 2},
            ],
        },
    )

    assert mock_products_public_id.times_called == 1
    assert mock_products_info.times_called == 1
    assert mock_partner_get_picking_slots.times_called == 1

    assert response.status_code == 200
    assert response.json() == {
        'picking_slots': [
            {
                'picking_duration': 1200,
                'picking_slot_end': '2021-10-19T16:30:00.123456+00:00',
                'picking_slot_id': 'slot-asap-false-first-id',
                'picking_slot_start': '2021-10-19T16:00:00.123+00:00',
            },
        ],
        'place_id': 1,
        'place_origin_id': 'place_origin_id1',
    }


@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': i,
            'categories': [],
            'revision_id': 1,
            'slug': f'place_{i}',
            'brand': {
                'id': 0,
                'name': 'brand_0',
                'picture_scale_type': 'aspect_fit',
                'slug': 'brand_0',
            },
            'updated_at': '2021-10-12T20:00:00+03:00',
            'name': f'place {i}',
            'origin_id': f'place_origin_id_{i}',
            'enabled': True,
        }
        for i in range(1, 3)
    ],
)
@utils.partner_picking_slots()
async def test_get_catalog_picking_slots(taxi_eats_customer_slots, mockserver):
    expected_picking_slots = {
        'place_origin_id_1': [
            {
                'slot_id': 'slot_id_1',
                'duration': 1200,
                'from': '2021-10-19T11:00:00.123+00:00',
                'to': '2021-10-19T11:30:00.123456+00:00',
            },
            {
                'slot_id': 'slot_id_2',
                'duration': 1200,
                'from': '2021-10-19T16:00:00.123+00:00',
                'to': '2021-10-19T16:30:00.123456+00:00',
            },
        ],
        'place_origin_id_2': [],
    }

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def _mock_partner_get_picking_slots(request):
        assert request.method == 'POST'
        assert request.json['place_origin_id'] in expected_picking_slots
        return mockserver.make_response(
            status=200,
            json={
                'picking_slots': expected_picking_slots[
                    request.json['place_origin_id']
                ],
            },
        )

    await taxi_eats_customer_slots.invalidate_caches(
        cache_names=['partner-picking-slots-cache'],
    )
    response = await taxi_eats_customer_slots.post(
        '/api/v1/partner/get-average-picking-slots',
        json={
            'places': [{'place_id': i, 'brand_id': '0'} for i in range(1, 4)],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'places_picking_slots': [
            {
                'place_id': 1,
                'place_origin_id': 'place_origin_id_1',
                'picking_slots': [
                    {
                        'picking_slot_end': '2021-10-19T16:30:00.123456+00:00',
                        'picking_slot_id': 'slot_id_2',
                        'picking_slot_start': '2021-10-19T16:00:00.123+00:00',
                    },
                ],
            },
            {'place_id': 2, 'place_origin_id': 'place_origin_id_2'},
            {'place_id': 3},
        ],
    }


@pytest.mark.now('2022-06-08T12:00:00.000000+00:00')
@pytest.mark.config(EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': ['0']})
@utils.settings_config()
@pytest.mark.eats_catalog_storage_cache(
    [
        {
            'id': 0,
            'categories': [],
            'revision_id': 1,
            'slug': f'place_0',
            'brand': {
                'id': 0,
                'name': 'brand_0',
                'picture_scale_type': 'aspect_fit',
                'slug': 'brand_0',
            },
            'updated_at': '2022-06-07T20:00:00+03:00',
            'name': f'place 0',
            'origin_id': f'place_origin_id_0',
            'enabled': True,
        },
    ],
)
@pytest.mark.parametrize(
    'delivery_slot_start, delivery_slot_end, '
    'picking_slots_validation_right_offset, expected_picking_slots',
    [
        (
            '2022-06-08T13:00:00+00:00',
            '2022-06-08T14:00:00+00:00',
            None,
            [
                {
                    'picking_slot_id': 'slot_id_1',
                    'picking_slot_start': '2022-06-08T13:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T13:30:00.0+00:00',
                    'picking_duration': 1200,
                },
            ],
        ),
        (
            '2022-06-08T13:00:00+00:00',
            '2022-06-08T14:00:00+00:00',
            600,
            [
                {
                    'picking_slot_id': 'slot_id_1',
                    'picking_slot_start': '2022-06-08T13:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T13:30:00.0+00:00',
                    'picking_duration': 1200,
                },
            ],
        ),
        (
            '2022-06-08T13:00:00+00:00',
            '2022-06-08T14:00:00+00:00',
            3600 * 4,
            [
                {
                    'picking_slot_id': 'slot_id_1',
                    'picking_slot_start': '2022-06-08T13:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T13:30:00.0+00:00',
                    'picking_duration': 1200,
                },
                {
                    'picking_slot_id': 'slot_id_2',
                    'picking_slot_start': '2022-06-08T16:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T16:30:00.0+00:00',
                    'picking_duration': 1200,
                },
            ],
        ),
        (
            '2022-06-08T11:00:00+00:00',
            '2022-06-08T12:00:00+00:00',
            3600 * 3,
            [
                {
                    'picking_slot_id': 'slot_id_1',
                    'picking_slot_start': '2022-06-08T13:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T13:30:00.0+00:00',
                    'picking_duration': 1200,
                },
            ],
        ),
        (
            '2022-06-08T11:00:00+00:00',
            '2022-06-08T12:00:00+00:00',
            3600 * 6,
            [
                {
                    'picking_slot_id': 'slot_id_1',
                    'picking_slot_start': '2022-06-08T13:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T13:30:00.0+00:00',
                    'picking_duration': 1200,
                },
                {
                    'picking_slot_id': 'slot_id_2',
                    'picking_slot_start': '2022-06-08T16:00:00.0+00:00',
                    'picking_slot_end': '2022-06-08T16:30:00.0+00:00',
                    'picking_duration': 1200,
                },
            ],
        ),
    ],
)
async def test_get_picking_slots_delivery_end_offset(
        taxi_eats_customer_slots,
        mockserver,
        experiments3,
        delivery_slot_start,
        delivery_slot_end,
        picking_slots_validation_right_offset,
        expected_picking_slots,
):
    experiments3.add_experiment3_from_marker(
        utils.partner_picking_slots(
            None, picking_slots_validation_right_offset,
        ),
        None,
    )
    picking_slots = {
        'place_origin_id_0': [
            {
                'slot_id': 'slot_id_1',
                'duration': 1200,
                'from': '2022-06-08T13:00:00+00:00',
                'to': '2022-06-08T13:30:00+00:00',
            },
            {
                'slot_id': 'slot_id_2',
                'duration': 1200,
                'from': '2022-06-08T16:00:00+00:00',
                'to': '2022-06-08T16:30:00+00:00',
            },
        ],
    }

    @mockserver.json_handler(
        '/eats-retail-retail-parser/api/v1/partner/get-picking-slots',
    )
    async def _mock_partner_get_picking_slots(request):
        assert request.method == 'POST'
        assert request.json['place_origin_id'] in picking_slots
        return mockserver.make_response(
            status=200,
            json={
                'picking_slots': picking_slots[
                    request.json['place_origin_id']
                ],
            },
        )

    await taxi_eats_customer_slots.invalidate_caches(
        cache_names=['partner-picking-slots-cache'],
    )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/place/get-picking-slots',
        json={
            'place_id': 0,
            'user_id': '2',
            'asap': False,
            'delivery_slot_start': delivery_slot_start,
            'delivery_slot_end': delivery_slot_end,
            'delivery_duration': 600,
            'items': [
                {'origin_id': 'origin_id_1', 'quantity': 2, 'quantum': 500},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'place_id': 0,
        'place_origin_id': 'place_origin_id_0',
        'picking_slots': expected_picking_slots,
    }
