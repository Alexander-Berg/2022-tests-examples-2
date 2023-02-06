import pytest

from . import utils


async def test_update_order_400_no_author_type(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.put(
        '/api/v1/order',
        params={'eats_id': '123'},
        json={
            'items': [
                {
                    'old_item_id': 'old_item_id',
                    'eats_item_id': 'eats_item_id',
                    'vendor_code': '7777',
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
@pytest.mark.parametrize(
    'request_version, author, author_type, expected_status, expected_quantity',
    [
        [None, 'someone', None, 200, 3],
        [0, 'someone', None, 204, None],
        [1, 'someone', None, 200, 3],
        [None, 'customer', 'customer', 200, 3],
        [0, 'customer', 'customer', 204, None],
        [1, 'customer', 'customer', 200, 3],
        [None, None, 'system', 200, 3],
        [0, None, 'system', 204, None],
        [1, None, 'system', 200, 3],
        [None, '1122', 'system', 200, 3],
        [0, '1122', 'system', 204, None],
        [1, '1122', 'system', 200, 3],
        [None, '1122', 'picker', 200, 3],
        [0, '1122', 'picker', 204, None],
        [1, '1122', 'picker', 200, 3],
        [None, 'another_picker', 'system', 200, 1],
        [0, 'another_picker', 'system', 200, 1],
        [1, 'another_picker', 'system', 409, None],
        [None, 'another_picker', 'picker', 200, 1],
        [0, 'another_picker', 'picker', 200, 1],
        [1, 'another_picker', 'picker', 409, None],
    ],
)
@utils.send_order_events_config()
async def test_update_order_version_author(
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        handle,
        measure_version,
        request_version,
        author,
        author_type,
        expected_status,
        expected_quantity,
        mock_processing,
):
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    old_item_id = 'item-1'
    new_item_id = 'item-2'
    sold_by_weight = False
    measure_value = 1000
    price = 25
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        last_version=1,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=old_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=1,
        version=0,
        author=None,
        author_type=None,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=old_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=2,
        version=1,
        author=author,
        author_type=author_type,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=new_item_id,
        sold_by_weight=sold_by_weight,
        price=price,
        measure_value=measure_value,
        quantity=2,
        version=1,
        author=author,
        author_type=author_type,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=new_item_id,
                    barcodes=[new_item_id],
                    vendor_code=new_item_id,
                    price=price,
                    is_catch_weight=sold_by_weight,
                    measure_quantum=1,
                    measure_value=measure_value,
                ),
                'barcode': new_item_id,
                'sku': new_item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'old_item_id': old_item_id,
                    'eats_item_id': new_item_id,
                    'vendor_code': new_item_id,
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert get_order(order_id)['last_version'] == 2
        items = get_order_items(order_id=order_id, version=2)
        assert len(items) == 1
        assert items[0]['eats_item_id'] == new_item_id
        assert items[0]['quantity'] == expected_quantity

        assert mock_processing.times_called == 1
    else:
        assert get_order(order_id)['last_version'] == 1


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
async def test_update_order_412_no_items(
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        return {'matched_items': [], 'not_matched_items': []}

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
async def test_update_order_412_not_matched_items(
        load_json,
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = load_json('expected_item.json')
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [
                {'barcode': None, 'sku': '7777', 'item': item},
            ],
        }

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
async def test_update_order_412_items_mismatch(
        load_json,
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = load_json('expected_item.json')
        return {
            'matched_items': [
                {'barcode': None, 'sku': 'different-sku', 'item': item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7778',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'item_mismatch'


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
@pytest.mark.parametrize('measure_value, quantum', [[500, 0], [0, 0.75]])
async def test_update_order_412_incorrect_measure(
        mock_edadeal,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        handle,
        measure_value,
        quantum,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    mock_edadeal(False, quantum, measure_value)

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, '2'),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '1',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_item_incorrect_measure'


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
async def test_update_order_404_order_item_not_found(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mock_eats_products_public_id,
        create_order,
        create_order_item,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'wrong-id',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_item_not_found'


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
async def test_limit_exceeded_change_disabled(
        load_json,
        mockserver,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_by_eats_id,
        get_order_items,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    request_body = {
        'items': [
            {'old_item_id': 'item-1', 'vendor_code': '7777', 'quantity': 5.5},
        ],
    }
    new_item_price = 250
    initial_limit = 1000
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=initial_limit,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )
    items_before_request = get_order_items(order_id, version=0)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item.json')
        expected_item['price'] = str(new_item_price)
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eats_picker_item_categories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == 1
        return mockserver.make_response(
            status=200, json={'items_categories': []},
        )

    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.da_headers(picker_id)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )

    assert response.status_code == 422
    assert response.json()['code'] == 'payment_limit_exceeded'

    order_row = get_order_by_eats_id(eats_id)
    assert order_row['payment_limit'] == initial_limit
    assert order_row['last_version'] == 0

    items_rows = get_order_items(order_id, version=0)
    assert items_rows == items_before_request


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
@pytest.mark.parametrize(
    'is_catch_weight, quantity', [[True, 0], [False, 0], [False, 0.9]],
)
async def test_update_order_400_bad_quantity(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        load_json,
        create_order,
        create_order_item,
        handle,
        is_catch_weight,
        quantity,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item.json')
        expected_item['is_catch_weight'] = is_catch_weight
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': item_id,
                    'vendor_code': '7777',
                    'quantity': quantity,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
@pytest.mark.parametrize(
    'is_catch_weight, quantity_fields',
    [
        [True, {}],
        [True, {'quantity': 1, 'weight': 100}],
        [False, {}],
        [False, {'weight': 100}],
        [False, {'quantity': 1, 'weight': 100}],
    ],
)
async def test_update_order_400_bad_field_set(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        load_json,
        create_order,
        create_order_item,
        handle,
        is_catch_weight,
        quantity_fields: dict,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item.json')
        expected_item['is_catch_weight'] = is_catch_weight
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                dict(
                    {'old_item_id': item_id, 'vendor_code': '7777'},
                    **quantity_fields,
                ),
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'state, expected_status',
    [
        ['new', 200],
        ['waiting_dispatch', 409],
        ['dispatching', 200],
        ['dispatch_failed', 409],
        ['assigned', 200],
        ['picking', 200],
        ['waiting_confirmation', [409, 200]],
        ['picked_up', 409],
        ['paid', 409],
        ['cancelled', 409],
        ['complete', 409],
    ],
)
@pytest.mark.parametrize(
    'handle',
    [
        '/4.0/eats-picker/api/v1/order',
        '/4.0/eats-picker/api/v2/order',
        '/api/v1/order',
    ],
)
@utils.send_order_events_config()
async def test_order_update_order_state(
        taxi_eats_picker_orders,
        mockserver,
        mock_eats_products_public_id,
        load_json,
        init_measure_units,
        create_order,
        create_order_item,
        handle,
        state,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state=state, eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item.json')
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    @mockserver.json_handler(
        f'/eats-picker-item-categories/api/v1/items/categories',
    )
    def _mock_eats_picker_item_categories(request):
        assert request.method == 'POST'
        assert int(request.json['place_id']) == 1
        return mockserver.make_response(
            status=200, json={'items_categories': []},
        )

    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.da_headers(picker_id),
        params={'eats_id': eats_id, 'version': 0, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    if isinstance(expected_status, list):
        expected_status = expected_status[
            1 if handle == '/api/v1/order' else 0
        ]
    assert response.status_code == expected_status
    if expected_status == 409:
        assert response.json().get('code') == 'ORDER_WRONG_STATE'
    else:
        assert mock_processing.times_called == 1
