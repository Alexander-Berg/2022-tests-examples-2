import pytest

from tests_eats_customer_slots import utils


def make_delivery_slot(
        start: str,
        end: str,
        estimated_delivery_timepoint: str,
        select_by_default: bool,
):
    slot = {
        'start': start,
        'end': end,
        'estimated_delivery_timepoint': estimated_delivery_timepoint,
    }
    if select_by_default:
        slot['select_by_default'] = select_by_default  # type: ignore
    return slot


def make_param(
        expected_slots,
        expected_asap,
        time_zone='Europe/Moscow',
        delivery_time=None,
        validate_expiration=False,
        slot_max_end_threshold=None,
):
    return [
        time_zone,
        delivery_time,
        expected_slots,
        expected_asap,
        validate_expiration,
        slot_max_end_threshold,
    ]


@utils.slots_enabled()
@utils.settings_config(
    asap_disable_threshold=1800, approximate_picking_time=10,
)
@pytest.mark.now('2022-06-25T12:00:00+03:00')
@pytest.mark.parametrize(
    'time_zone, delivery_time, expected_slots, expected_asap, '
    'validate_expiration, slot_max_end_threshold',
    [
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T14:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T14:00:00+03:00',
                    True,
                ),
                make_delivery_slot(
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T16:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    False,
                ),
            ],
            False,
        ),
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T16:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    True,
                ),
            ],
            False,
            delivery_time='2022-06-25T15:10:00+03:00',
        ),
        make_param([], False, delivery_time='2022-06-25T16:10:00+03:00'),
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T11:00:00+00:00',
                    '2022-06-25T12:00:00+00:00',
                    '2022-06-25T11:00:00+00:00',
                    True,
                ),
                make_delivery_slot(
                    '2022-06-25T12:00:00+00:00',
                    '2022-06-25T13:00:00+00:00',
                    '2022-06-25T12:00:00+00:00',
                    False,
                ),
            ],
            False,
            time_zone='Etc/UTC',
        ),
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T12:00:00+00:00',
                    '2022-06-25T13:00:00+00:00',
                    '2022-06-25T12:00:00+00:00',
                    True,
                ),
            ],
            False,
            time_zone='Etc/UTC',
            delivery_time='2022-06-25T12:10:00+00:00',
        ),
        make_param(
            [],
            False,
            time_zone='Etc/UTC',
            delivery_time='2022-06-25T13:10:00+00:00',
        ),
        make_param(
            [],
            False,
            delivery_time='2022-06-25T15:10:00+03:00',
            validate_expiration=True,
        ),
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T14:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T14:00:00+03:00',
                    True,
                ),
                make_delivery_slot(
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T16:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    False,
                ),
            ],
            False,
            slot_max_end_threshold=4 * 3600,
        ),
        make_param(
            [
                make_delivery_slot(
                    '2022-06-25T14:00:00+03:00',
                    '2022-06-25T15:00:00+03:00',
                    '2022-06-25T14:00:00+03:00',
                    True,
                ),
            ],
            False,
            slot_max_end_threshold=3 * 3600,
        ),
        make_param([], False, slot_max_end_threshold=2 * 3600),
    ],
)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
async def test_calculate_slots_shop_delivery(
        taxi_eats_customer_slots,
        mockserver,
        experiments3,
        mock_calculate_load,
        time_zone,
        delivery_time,
        expected_slots,
        expected_asap,
        validate_expiration,
        slot_max_end_threshold,
        now,
):
    experiments3.add_experiment3_from_marker(
        utils.partner_delivery_slots_config3(
            True,
            validate_expiration=validate_expiration,
            slot_max_end_threshold=slot_max_end_threshold,
        ),
        None,
    )

    place_id = 0
    brand_id = 0
    now = utils.localize(now, time_zone)

    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=place_id,
        brand_id=brand_id,
        time_zone=time_zone,
        working_intervals=[],
        shop_picking_type='shop_picking',
    )

    order = utils.make_order(
        place_id=place_id, brand_id=str(brand_id), delivery_time=delivery_time,
    )

    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def _mock_products_info(request):
        products_info = {
            'public_id_0': {
                'id': 'public_id_0',
                'origin_id': utils.generate_place_origin_id(place_id),
                'place_brand_id': str(brand_id),
                'name': 'name_0',
                'description': {},
                'is_choosable': True,
                'is_catch_weight': False,
                'adult': False,
                'shipping_type': 'pickup',
                'barcodes': [],
                'images': [],
                'is_sku': True,
            },
        }
        return mockserver.make_response(
            json={
                'products': [
                    products_info[public_id]
                    for public_id in request.json['product_ids']
                ],
            },
        )

    await taxi_eats_customer_slots.invalidate_caches()

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots', json=order,
    )
    assert response.status == 200
    response_body = response.json()

    assert response_body['available_asap'] == expected_asap
    assert response_body['available_slots'] == expected_slots
