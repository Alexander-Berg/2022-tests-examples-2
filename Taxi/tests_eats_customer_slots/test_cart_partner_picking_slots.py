import pytest

from tests_eats_customer_slots import utils


PLACE_ID = 0
BRAND_ID = 0
USER_ID = 'user_0'


async def invalidate_load_info_cache(
        taxi_eats_customer_slots, mock_calculate_load, mockserver,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-nomenclature/v1/products/info')
    def mock_products_info(request):
        return mockserver.make_response(
            json={
                'products': [
                    {
                        'id': public_id,
                        'origin_id': f'origin_id_{public_id[-1]}',
                        'place_brand_id': f'{BRAND_ID}',
                        'name': 'name',
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

    mock_calculate_load.response['json']['places_load_info'][0].update(
        place_id=PLACE_ID, brand_id=BRAND_ID, shop_picking_type='shop_picking',
    )

    await taxi_eats_customer_slots.invalidate_caches(
        cache_names=['places-load-info-cache'],
    )


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.cart_partner_picking_slots(items_quantity_diff_threshold=0)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': [f'{BRAND_ID}']},
)
@pytest.mark.parametrize(
    'order_kwargs',
    [
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(0, quantity=1),
                utils.make_order_item(1, quantity=1),
            ],
        },
    ],
)
async def test_calculate_slots_cart_picking_slots_skip_cache(
        taxi_eats_customer_slots,
        mock_calculate_load,
        mockserver,
        mock_partner_picking_slots,
        order_kwargs,
):
    await invalidate_load_info_cache(
        taxi_eats_customer_slots, mock_calculate_load, mockserver,
    )
    # pylint: disable=invalid-name
    mock_partner_picking_slots_times_called = (
        mock_partner_picking_slots.times_called
    )

    order = utils.make_order(place_id=PLACE_ID, brand_id=f'{BRAND_ID}')
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 1
    )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 2
    )


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.cart_partner_picking_slots(items_quantity_diff_threshold=1)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': [f'{BRAND_ID}']},
)
@pytest.mark.parametrize(
    'order_kwargs',
    [
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(0, quantity=1),
                utils.make_order_item(1, quantity=1),
            ],
        },
    ],
)
async def test_calculate_slots_cart_picking_slots_store_and_use_cached(
        taxi_eats_customer_slots,
        mock_calculate_load,
        mockserver,
        mock_partner_picking_slots,
        order_kwargs,
):
    await invalidate_load_info_cache(
        taxi_eats_customer_slots, mock_calculate_load, mockserver,
    )
    # pylint: disable=invalid-name
    mock_partner_picking_slots_times_called = (
        mock_partner_picking_slots.times_called
    )

    order = utils.make_order(**order_kwargs)
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 1
    )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 1
    )


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.cart_partner_picking_slots(items_quantity_diff_threshold=3)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': [f'{BRAND_ID}']},
)
@pytest.mark.parametrize(
    'order_kwargs',
    [
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(
                    0, quantum=500, quantity=1, is_catch_weight=True,
                ),
                utils.make_order_item(1, quantity=1),
            ],
        },
    ],
)
@pytest.mark.parametrize(
    'order_2nd_ver_kwargs',
    [
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(
                    0, quantum=500, quantity=1, is_catch_weight=True,
                ),
            ],
        },
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(
                    0, quantum=500, quantity=1, is_catch_weight=True,
                ),
                utils.make_order_item(1, quantity=1),
                utils.make_order_item(2, quantity=1),
            ],
        },
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(
                    0, quantum=500, quantity=1, is_catch_weight=True,
                ),
                utils.make_order_item(1, quantity=4),
            ],
        },
        {
            'place_id': PLACE_ID,
            'brand_id': f'{BRAND_ID}',
            'items': [
                utils.make_order_item(
                    0, quantum=500, quantity=7, is_catch_weight=True,
                ),
                utils.make_order_item(1, quantity=1),
            ],
        },
    ],
)
async def test_calculate_slots_cart_picking_slots_invalidate_cached(
        taxi_eats_customer_slots,
        mock_calculate_load,
        mockserver,
        mock_partner_picking_slots,
        order_kwargs,
        order_2nd_ver_kwargs,
):
    await invalidate_load_info_cache(
        taxi_eats_customer_slots, mock_calculate_load, mockserver,
    )
    # pylint: disable=invalid-name
    mock_partner_picking_slots_times_called = (
        mock_partner_picking_slots.times_called
    )

    order = utils.make_order(**order_kwargs)
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 1
    )

    order_2nd_ver = utils.make_order(**order_2nd_ver_kwargs)
    response = await taxi_eats_customer_slots.post(
        '/api/v1/order/calculate-slots',
        headers={'X-Eats-User': f'user_id={USER_ID}'},
        json=order_2nd_ver,
    )
    assert response.status == 200
    assert response.json()['available_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 2
    )


@pytest.mark.now('2021-10-19T12:00:00.000000+00:00')
@utils.slots_enabled()
@utils.daily_slots_config()
@utils.settings_config()
@utils.cart_partner_picking_slots(items_quantity_diff_threshold=3)
@pytest.mark.eats_catalog_storage_cache(file='catalog_storage_cache.json')
@pytest.mark.config(
    EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': [f'{BRAND_ID}']},
)
@pytest.mark.parametrize(
    'items',
    [[{'public_id': '0', 'quantity': 1}, {'public_id': '1', 'quantity': 1}]],
)
@pytest.mark.parametrize(
    'items_2nd_ver,is_cache_invalidated',
    [
        ([{'public_id': '0', 'quantity': 1}], True),
        (
            [
                {'public_id': '0', 'quantity': 1},
                {'public_id': '1', 'quantity': 1},
                {'public_id': '2', 'quantity': 1},
            ],
            True,
        ),
        (
            [
                {'public_id': '0', 'quantity': 1},
                {'public_id': '1', 'quantity': 4.9},
            ],
            True,
        ),
        (
            [
                {'public_id': '0', 'quantity': 2.05},
                {'public_id': '1', 'quantity': 3.05},
            ],
            True,
        ),
        (
            [
                {'public_id': '0', 'quantity': 2},
                {'public_id': '1', 'quantity': 2.9},
            ],
            False,
        ),
        (
            [
                {'public_id': '0', 'quantity': 1},
                {'public_id': '1', 'quantity': 3.9},
            ],
            False,
        ),
    ],
)
async def test_calculate_slots_partner_picking_slots_redis_cache(
        taxi_eats_customer_slots,
        mock_calculate_load,
        mockserver,
        mock_partner_picking_slots,
        items,
        items_2nd_ver,
        is_cache_invalidated,
):
    await invalidate_load_info_cache(
        taxi_eats_customer_slots, mock_calculate_load, mockserver,
    )
    # pylint: disable=invalid-name
    mock_partner_picking_slots_times_called = (
        mock_partner_picking_slots.times_called
    )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/partner/get-picking-slots',
        json={'place_id': PLACE_ID, 'user_id': USER_ID, 'items': items},
    )
    assert response.status == 200
    assert response.json()['picking_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == 1
    )

    response = await taxi_eats_customer_slots.post(
        '/api/v1/partner/get-picking-slots',
        json={
            'place_id': PLACE_ID,
            'user_id': USER_ID,
            'items': items_2nd_ver,
        },
    )
    assert response.status == 200
    assert response.json()['picking_slots']
    assert (
        mock_partner_picking_slots.times_called
        - mock_partner_picking_slots_times_called
        == (2 if is_cache_invalidated else 1)
    )
