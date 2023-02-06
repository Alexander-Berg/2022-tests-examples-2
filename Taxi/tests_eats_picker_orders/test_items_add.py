# pylint: disable=too-many-lines
import pytest

from . import utils


@utils.marking_types_config()
@pytest.mark.parametrize(
    'measure_value, measure_quantum', [[1000, 0.75], [0, 1]],
)
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('request_version', [None, 0])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@pytest.mark.parametrize('require_approval', [None, False, True])
@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize(
    'marking_type, require_marks',
    [(None, False), ('marked_milk', True), ('another_type', False)],
)
@pytest.mark.parametrize(
    'request_body,expected_items_quantity',
    (
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'quantity': 1,
                    },
                ],
            },
            {'item-1': 11, 'item-2': 20},
            id='add_existing',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-3',
                        'vendor_code': '7777',
                        'quantity': 3,
                    },
                ],
            },
            {'item-1': 10, 'item-2': 20, 'item-3': 3},
            id='add_new',
        ),
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'quantity': 10,
                    },
                    {
                        'eats_item_id': 'item-3',
                        'vendor_code': '7777',
                        'quantity': 30,
                    },
                ],
            },
            {'item-1': 20, 'item-2': 20, 'item-3': 30},
            id='add_existing_and_new',
        ),
    ),
)
@utils.send_order_events_config()
async def test_add_items_200(
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        generate_product_info,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        require_approval,
        sold_by_weight,
        request_body,
        expected_items_quantity,
        handle,
        request_version,
        measure_version,
        measure_value: int,
        measure_quantum: float,
        marking_type,
        require_marks,
        mock_processing,
):
    price_for_items = {'item-1': 11, 'item-2': 12, 'item-3': 13}
    initial_quantity = {'item-1': 10, 'item-2': 20}
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=require_approval,
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id,
            eats_item_id=eats_item_id,
            quantity=quantity,
            price=price_for_items[eats_item_id],
            measure_value=measure_value,
            measure_quantum=int(measure_value * measure_quantum),
            quantum_quantity=quantity / measure_quantum,
            absolute_quantity=quantity * measure_value,
            quantum_price=round(
                price_for_items[eats_item_id] * measure_quantum, 2,
            ),
        )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=sold_by_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=price,
                    measure_quantum=measure_quantum,
                    measure_value=measure_value,
                ),
                'barcode': item_id,
                'sku': item_id,
            }
            for item_id, price in price_for_items.items()
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()

    old_origin_ids = list(initial_quantity.keys())
    origin_ids = [
        item['eats_item_id']
        for item in request_body['items']
        if item['eats_item_id'] not in old_origin_ids
    ]
    public_ids = [str(i) for i in range(len(origin_ids))]
    mock_eats_products_public_id(
        [
            {'origin_id': origin_id, 'public_id': public_id}
            for origin_id, public_id in zip(origin_ids, public_ids)
        ],
    )
    mock_nmn_products_info(
        [
            generate_product_info(public_id, public_id, [], marking_type)
            for public_id in public_ids
        ],
    )

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 1
    assert get_order(order_id)['last_version'] == 1
    items = get_order_items(order_id=order_id, version=1)
    items_quantity = {item['eats_item_id']: item['quantity'] for item in items}
    assert items_quantity == expected_items_quantity
    for item in items:
        utils.check_updated_item_measure(
            item,
            measure_value,
            item['quantity'],
            price_for_items[item['eats_item_id']],
            measure_quantum,
        )
        if item['eats_item_id'] in origin_ids:
            assert item['require_marks'] == require_marks
        else:
            assert item['require_marks'] is None

    assert mock_processing.times_called == 1


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('request_version', [None, 0])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@pytest.mark.parametrize('require_approval', [None, False, True])
@pytest.mark.parametrize(
    'request_body,expected_items_quantity',
    (
        pytest.param(
            {
                'items': [
                    {
                        'eats_item_id': 'item-1',
                        'vendor_code': '7777',
                        'weight': 1000,
                    },
                ],
            },
            {'item-1': 11, 'item-2': 20},
            id='add_existing_by_weight',
        ),
    ),
)
@utils.send_order_events_config()
async def test_add_items_weight_200(
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
        require_approval,
        request_body,
        expected_items_quantity,
        handle,
        request_version,
        measure_version,
        mock_processing,
):
    measure_quantum = 0.75
    measure_value = 1000
    price_for_items = {'item-1': 11, 'item-2': 12, 'item-3': 13}
    initial_quantity = {'item-1': 10, 'item-2': 20}
    payment_limit = 1000
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=require_approval,
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id,
            eats_item_id=eats_item_id,
            quantity=quantity,
            price=price_for_items[eats_item_id],
            measure_value=measure_value,
            sold_by_weight=True,
            measure_quantum=0.75 * measure_value,
        )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=True,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=price,
                    measure_quantum=measure_quantum,
                    measure_value=measure_value,
                ),
                'barcode': item_id,
                'sku': item_id,
            }
            for item_id, price in price_for_items.items()
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 1
    assert get_order(order_id)['last_version'] == 1
    items = get_order_items(order_id=order_id, version=1)
    items_quantity = {item['eats_item_id']: item['quantity'] for item in items}
    assert items_quantity == expected_items_quantity
    for item in items:
        utils.check_updated_item_measure(
            item,
            measure_value,
            item['quantity'],
            price_for_items[item['eats_item_id']],
            0.75,
        )

    assert mock_processing.times_called == 1


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_limit_exceeded_change_disabled(
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
):
    price_for_items = {'item-1': 11, 'item-2': 12, 'item-3': 13}
    initial_quantity = {'item-1': 10, 'item-2': 20}
    request_body = {
        'items': [
            {'eats_item_id': 'item-3', 'vendor_code': '7777', 'quantity': 300},
        ],
    }
    initial_value = sum(
        quantity * price_for_items[eats_item_id]
        for eats_item_id, quantity in initial_quantity.items()
    )
    added_value = sum(
        item['quantity'] * price_for_items[item['eats_item_id']]
        for item in request_body['items']
    )
    payment_limit = initial_value + added_value - 1
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=False,
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id,
            eats_item_id=eats_item_id,
            quantity=quantity,
            price=price_for_items[eats_item_id],
        )
    items_before_request = get_order_items(order_id, version=0)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=True,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=price,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            }
            for item_id, price in price_for_items.items()
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    @mockserver.json_handler('/eats-picker-payments/api/v1/limit')
    def mock_eats_picker_payment(request):
        pass

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )

    assert response.status_code == 422
    assert response.json()['code'] == 'payment_limit_exceeded'
    assert response.json()['details']['limit_overrun'] == '1.00'

    order_row = get_order(order_id)
    assert order_row['payment_limit'] == payment_limit
    assert order_row['last_version'] == 0

    items_rows = get_order_items(order_id, version=0)
    assert items_rows == items_before_request

    assert mock_eats_picker_payment.times_called == 0


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_add_items_400_bad_request(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={'items': [{'eats_item_id': 'item-1', 'quantity': 5.5}]},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'empty_addition'


async def test_add_items_400_no_author_type(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    response = await taxi_eats_picker_orders.post(
        '/api/v1/items',
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@pytest.mark.parametrize(
    'is_catch_weight, quantity', [[True, 0], [False, 0], [False, 0.9]],
)
async def test_add_items_400_wrong_quantity(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        create_order,
        generate_integration_item_data,
        handle,
        is_catch_weight,
        quantity,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=is_catch_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': item_id,
                    'vendor_code': item_id,
                    'quantity': quantity,
                },
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
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
async def test_add_items_400_bad_field_set(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        mockserver,
        create_order,
        generate_integration_item_data,
        handle,
        is_catch_weight,
        quantity_fields,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    item_id = 'item-1'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=is_catch_weight,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                dict(
                    {'eats_item_id': item_id, 'vendor_code': item_id},
                    **quantity_fields,
                ),
            ],
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'handle, error_message',
    [
        ['/4.0/eats-picker/api/v1/items', 'order_not_found_for_picker'],
        ['/api/v1/items', 'order_not_found'],
    ],
)
async def test_add_items_404_order_not_found(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        handle,
        error_message,
):
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers('1122'),
        params={'eats_id': '123', 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 404
    assert response.json()['code'] == error_message


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_add_items_412_no_items(
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        return {'matched_items': [], 'not_matched_items': []}

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_add_items_412_not_matched_items(
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='item-1', measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [
                {'barcode': None, 'sku': '7777', 'item': item},
            ],
        }

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'integration_items_not_found'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle, request_picker_id, customer_id, author_type, expected_author_id, '
    'expected_author_type',
    [
        [
            '/4.0/eats-picker/api/v1/items',
            '1122',
            None,
            None,
            '1122',
            'picker',
        ],
        ['/api/v1/items', None, '1122', 'customer', '1122', 'customer'],
        ['/api/v1/items', None, None, 'system', None, 'system'],
    ],
)
@pytest.mark.parametrize('reason', [None, 'Fail', 'Out of stock'])
@utils.send_order_events_config()
async def test_add_items_reason(
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        handle,
        request_picker_id,
        customer_id,
        author_type,
        expected_author_id,
        expected_author_type,
        reason,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=f'item-{i}',
                    is_catch_weight=True,
                    barcodes=[str(i)],
                    vendor_code=str(i),
                    measure_quantum=0.75,
                ),
                'barcode': str(i),
                'sku': str(i),
            }
            for i in range(1, 7)
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=5, price=11,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-2', quantity=5, price=11,
    )
    unknown_picker_id = 'unknown'
    delete_reason = 'out of stock'
    create_order_item(
        order_id=order_id,
        eats_item_id='item-3',
        is_deleted_by=unknown_picker_id,
        reason=delete_reason,
        quantity=5,
        price=11,
    )
    soft_deleted_id = 'soft_deleted'
    create_order_item(
        order_id=order_id,
        eats_item_id=soft_deleted_id,
        is_deleted_by=picker_id,
        reason=delete_reason,
        quantity=5,
        price=11,
    )

    params = {'eats_id': eats_id}
    if author_type is not None:
        params['author_type'] = author_type
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '1',
                    'quantity': 5.5,
                },
                {
                    'eats_item_id': 'item-4',
                    'barcode': None,
                    'vendor_code': '2',
                    'quantity': 5.5,
                },
            ],
            'reason': reason,
            'customer_id': customer_id,
        },
    )
    assert response.status_code == 200

    order_items = get_order_items(order_id=order_id, version=1)
    assert len(order_items) == 5
    for item in order_items:
        if item['eats_item_id'] == soft_deleted_id:
            assert item['reason'] == delete_reason
        else:
            assert item['reason'] == reason
        assert item['author'] == expected_author_id
        assert item['author_type'] == expected_author_type

    assert mock_processing.times_called == 1


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_add_items_412_items_mismatch(
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='wrong_item_id',
            vendor_code='7778',
            measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7778', 'item': item}],
            'not_matched_items': [],
        }

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'item_mismatch'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
async def test_add_items_412_empty_max_overweight(
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        handle,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(state='assigned', eats_id=eats_id, picker_id=picker_id)

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item = generate_integration_item_data(
            origin_id='item-1',
            vendor_code='7777',
            is_catch_weight=True,
            measure_max_overweight=None,
            measure_quantum=0.75,
        )
        return {
            'matched_items': [{'barcode': None, 'sku': '7777', 'item': item}],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    assert response.status_code == 412
    assert response.json()['code'] == 'weight_parameter_is_missing'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
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
        [None, 'another_picker', 'system', 200, 2],
        [0, 'another_picker', 'system', 200, 2],
        [1, 'another_picker', 'system', 409, None],
        [None, 'another_picker', 'picker', 200, 2],
        [0, 'another_picker', 'picker', 200, 2],
        [1, 'another_picker', 'picker', 409, None],
    ],
)
@utils.send_order_events_config()
async def test_add_items_version_author(
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
    eats_item_id = 'item-1'
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
        eats_item_id=eats_item_id,
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
        eats_item_id=eats_item_id,
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
                    origin_id=eats_item_id,
                    barcodes=[eats_item_id],
                    vendor_code=eats_item_id,
                    price=price,
                    is_catch_weight=sold_by_weight,
                    measure_quantum=1,
                    measure_value=measure_value,
                ),
                'barcode': eats_item_id,
                'sku': eats_item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    if request_version is not None:
        params['version'] = request_version
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'eats_item_id': eats_item_id,
                    'vendor_code': eats_item_id,
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()['order_version'] == 2
        assert get_order(order_id)['last_version'] == 2
        items = get_order_items(order_id=order_id, version=2)
        assert len(items) == 1
        assert items[0]['eats_item_id'] == eats_item_id
        assert items[0]['quantity'] == expected_quantity
        assert mock_processing.times_called == 1
    else:
        assert get_order(order_id)['last_version'] == 1
        assert mock_processing.times_called == 0


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle, request_picker_id, customer_id',
    [
        ['/4.0/eats-picker/api/v1/items', 'picker_id', None],
        ['/api/v1/items', None, 'customer_id'],
        ['/api/v1/items', None, None],
    ],
)
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, quantity_expected',
    [
        (None, None, 7),
        ('picker_id', None, 2),
        ('picker_id', 'picker', 2),
        ('system', None, 2),
        ('system', 'system', 2),
        ('customer_id', 'customer', 2),
        ('unknown', None, 7),
        ('unknown', 'picker', 7),
    ],
)
@utils.send_order_events_config()
async def test_add_items_200_soft_deleted(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mockserver,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        generate_integration_item_data,
        get_order_items,
        handle,
        request_picker_id,
        customer_id,
        is_deleted_by,
        deleted_by_type,
        quantity_expected,
        measure_version,
        mock_processing,
):
    picker_id = 'picker_id'
    eats_id = '123'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='0',
        quantity=5,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id='0',
                    is_catch_weight=True,
                    barcodes=['0'],
                    vendor_code='0',
                    price=10,
                    measure_quantum=0.75,
                ),
                'barcode': '0',
                'sku': '0',
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params={'eats_id': eats_id, 'version': 0, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': '0',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 2,
                },
            ],
            'customer_id': customer_id,
        },
    )
    assert response.status_code == 200
    items = get_order_items(order_id=order_id, version=1)
    assert len(items) == 1
    assert items[0]['is_deleted_by'] is None
    assert items[0]['deleted_by_type'] is None
    assert items[0]['quantity'] == quantity_expected

    assert mock_processing.times_called == 1


@pytest.mark.parametrize(
    'measure_version, limit_overrun',
    [(None, '200.00'), ('1', '200.00'), ('2', '199.93')],
)
@pytest.mark.parametrize(
    'handle, request_picker_id, customer_id',
    [
        ['/4.0/eats-picker/api/v1/items', '1122', None],
        ['/api/v1/items', None, 'customer_id'],
        ['/api/v1/items', None, None],
    ],
)
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, status',
    [
        (None, None, 422),
        ('1122', None, 200),
        ('1122', 'picker', 200),
        ('system', None, 200),
        ('system', 'system', 200),
        ('customer_id', 'customer', 200),
        ('unknown', None, 422),
        ('unknown', 'picker', 422),
    ],
)
@utils.send_order_events_config()
async def test_add_items_soft_deleted_limit(
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mockserver,
        taxi_eats_picker_orders,
        generate_integration_item_data,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        handle,
        request_picker_id,
        customer_id,
        is_deleted_by,
        deleted_by_type,
        status,
        measure_version,
        mock_processing,
        limit_overrun,
):
    payment_limit = 1100
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=payment_limit,
        require_approval=False,
    )
    for i, (quantity, price, soft_deleted) in enumerate(
            [(1, 100, False), (2, 200, False), (1, 500, True)],
    ):
        create_order_item(
            order_id=order_id,
            eats_item_id='item_' + str(i),
            quantity=quantity,
            price=price,
            is_deleted_by=(is_deleted_by if soft_deleted else None),
            deleted_by_type=(deleted_by_type if soft_deleted else None),
        )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        item_id = 'item_n'
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id=item_id,
                    is_catch_weight=False,
                    barcodes=[item_id],
                    vendor_code=item_id,
                    price=300,
                    measure_quantum=0.75,
                ),
                'barcode': item_id,
                'sku': item_id,
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {
        'eats_id': eats_id,
        'customer_id': customer_id,
        'author_type': 'customer',
    }
    request_body = {
        'items': [
            {'eats_item_id': 'item_n', 'vendor_code': 'item_n', 'quantity': 1},
        ],
    }
    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params=params,
        json=request_body,
    )

    assert response.status_code == status

    if status == 200:
        assert response.json()['order_version'] == 1
        assert get_order(order_id)['last_version'] == 1
        assert mock_processing.times_called == 1
    elif status == 422:
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == limit_overrun
        assert mock_processing.times_called == 0


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
    'handle', ['/4.0/eats-picker/api/v1/items', '/api/v1/items'],
)
@utils.send_order_events_config()
async def test_add_items_order_state(
        taxi_eats_picker_orders,
        mockserver,
        generate_integration_item_data,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        create_order,
        handle,
        state,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(
        state=state, eats_id=eats_id, picker_id=picker_id, last_version=0,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        matched_items = [
            {
                'item': generate_integration_item_data(
                    origin_id='item-1', measure_quantum=0.75,
                ),
                'barcode': 'item-1',
                'sku': 'item-1',
            },
        ]
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.post(
        handle,
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id, 'version': 0, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'eats_item_id': 'item-1',
                    'barcode': None,
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
    )
    if isinstance(expected_status, list):
        expected_status = expected_status[
            1 if handle == '/api/v1/items' else 0
        ]
    assert response.status_code == expected_status
    if expected_status == 409:
        assert response.json().get('code') == 'ORDER_WRONG_STATE'
        assert mock_processing.times_called == 0
    else:
        assert mock_processing.times_called == 1
