# pylint: disable=too-many-lines
import pytest

from . import utils


@utils.marking_types_config()
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('request_version', [None, 0])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'barcode_weight_encoding', [None, 'ean13-tail-gram-4'],
)
@pytest.mark.parametrize(
    'marking_type, require_marks',
    [(None, False), ('marked_milk', True), ('another_type', False)],
)
@pytest.mark.parametrize(
    'request_body',
    (
        {
            'items': [
                {
                    'old_item_id': 'item-1',
                    'vendor_code': '7777',
                    'quantity': 5.5,
                },
            ],
        },
        {
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': '4321',
                    'quantity': 5.5,
                    'barcode': '12345',
                },
            ],
        },
    ),
)
@utils.send_order_events_config()
async def test_update_order_200(
        load_json,
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_nmn_products_info,
        generate_product_info,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        barcode_weight_encoding,
        request_body,
        handle,
        request_version,
        measure_version,
        mock_processing,
        marking_type,
        require_marks,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, spent=None,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item_measure_v2.json')
        expected_item['barcode']['weight_encoding'] = barcode_weight_encoding
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()

    old_origin_ids = {'item-1'}
    origin_ids = [
        item['eats_item_id']
        for item in request_body['items']
        if 'eats_item_id' in item
        and item['eats_item_id'] not in old_origin_ids
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
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 1

    assert mock_processing.times_called == 1

    params['version'] = 1
    response = await taxi_eats_picker_orders.get(
        '/api/v1/order', params={'eats_id': eats_id},
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    for item in expected_response['payload']['picker_items']:
        item['weight_barcode_type'] = barcode_weight_encoding
        if item['id'] in origin_ids:
            item['require_marks'] = require_marks
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert (
        abs(float(response_data['payload']['payment_limit']) - 4000.0) < 1e-6
    )
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    held_payment_limit = 138.88
    assert (
        float(response_data['payload']['held_payment_limit'])
        == held_payment_limit
    )
    del response_data['payload']['held_payment_limit']
    for item in response_data['payload']['picker_items']:
        item.pop('measure_v2', None)
        item['measure']['relative_quantum'] = pytest.approx(
            item['measure']['relative_quantum'],
        )
    assert response_data == expected_response


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle, request_picker_id, customer_id, author_type, expected_author_id, '
    'expected_author_type',
    [
        [
            '/4.0/eats-picker/api/v2/order',
            '1122',
            None,
            None,
            '1122',
            'picker',
        ],
        ['/api/v1/order', None, '1122', 'customer', '1122', 'customer'],
        ['/api/v1/order', None, None, 'system', None, 'system'],
    ],
)
@pytest.mark.parametrize('reason', [None, 'Fail', 'Out of stock'])
@utils.send_order_events_config()
async def test_order_update_item_reason(
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
        quantity=5,
        price=11,
        is_deleted_by=unknown_picker_id,
        reason=delete_reason,
    )
    soft_deleted_id = 'soft_deleted'
    create_order_item(
        order_id=order_id,
        eats_item_id=soft_deleted_id,
        quantity=5,
        price=11,
        is_deleted_by=picker_id,
        reason=delete_reason,
    )
    params = {'eats_id': eats_id}
    if author_type is not None:
        params['author_type'] = author_type
    response_put = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params=params,
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-5',
                    'vendor_code': '7777',
                    'quantity': 10,
                },
            ],
            'reason': reason,
            'customer_id': customer_id,
        },
    )

    assert response_put.status_code == 200
    assert mock_processing.times_called == 1

    order_items = get_order_items(order_id=order_id, version=1)
    assert len(order_items) == 4
    for item in order_items:
        if item['eats_item_id'] == soft_deleted_id:
            assert item['reason'] == delete_reason
        else:
            assert item['reason'] == reason
        assert item['author'] == expected_author_id
        assert item['author_type'] == expected_author_type


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'request_body,expected_items_quantity',
    (
        [
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'eats_item_id': '4321',
                        'vendor_code': '7777',
                        'quantity': 5.5,
                    },
                ],
            },
            {'4321': 5.5},
        ],
        [
            {
                'items': [
                    {
                        'old_item_id': 'item-1',
                        'quantity': 5.5,
                        'vendor_code': '7777',
                    },
                ],
            },
            {'4321': 5.5},
        ],
    ),
)
@utils.send_order_events_config()
async def test_update_order_multiple_core_items(
        load_json,
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        request_body,
        expected_items_quantity,
        handle,
        measure_version,
        mock_processing,
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
        item = load_json('expected_item_measure_v2.json')
        wrong_item = item.copy()
        wrong_item['origin_id'] = 'wrong-id'
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': item},
                {'barcode': None, 'sku': '7777', 'item': wrong_item},
            ],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = get_order_items(order_id=order_id, version=1)
    items_quantity = {item['eats_item_id']: item['quantity'] for item in items}
    assert items_quantity == expected_items_quantity


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_self_replacement(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        quantity=10,
        sold_by_weight=False,
        measure_value=500,
        price=25,
    )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-1',
                    'barcode': '1',
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = get_order_items(order_id=order_id, version=1)
    assert len(items) == 1
    assert items[0]['eats_item_id'] == 'item-1'
    utils.check_updated_item_measure(
        items[0], measure_value=500, price=25, quantity=1, quantum=0.75,
    )
    assert get_item_replacement_of(items[0]['id']) == {'item-1'}


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_to_existing_item(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 3):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=500,
            price=25,
            measure_quantum=375,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = get_order_items(order_id=order_id, version=1)
    assert len(items) == 1
    assert items[0]['eats_item_id'] == 'item-2'
    utils.check_updated_item_measure(
        items[0], measure_value=500, price=25, quantity=21, quantum=0.75,
    )
    assert get_item_replacement_of(items[0]['id']) == {'item-1', 'item-2'}


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_1_item_to_self_and_new(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        quantity=10,
        sold_by_weight=False,
        measure_value=500,
        price=25,
    )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-1',
                    'barcode': '1',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 1, {'item-1'}),
            ('item-2', 2, {'item-1'}),
    ):
        assert (
            get_item_replacement_of(items[eats_item_id]['id'])
            == replacement_of_items
        )
        utils.check_updated_item_measure(
            items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize(
    'measure_value, measure_quantum', [[500, 0.75], [0, 1]],
)
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_1_item_to_2_existing(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        measure_value: int,
        measure_quantum: float,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 4):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=measure_value,
            price=25,
            measure_quantum=int(measure_value * measure_quantum),
        )

    mock_edadeal(False, measure_quantum, measure_value)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-3',
                    'barcode': '3',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-2', 21, {'item-1', 'item-2'}),
            ('item-3', 32, {'item-1', 'item-3'}),
    ):
        assert (
            get_item_replacement_of(items[eats_item_id]['id'])
            == replacement_of_items
        )
        utils.check_updated_item_measure(
            items[eats_item_id],
            measure_value=measure_value,
            price=25,
            quantity=quantity,
            quantum=measure_quantum,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_1_new(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 4):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=500,
            price=25,
            measure_quantum=375,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-4',
                    'barcode': '4',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-2',
                    'eats_item_id': 'item-4',
                    'barcode': '4',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-3', 30, set()),
            ('item-4', 3, {'item-1', 'item-2'}),
    ):
        assert (
            get_item_replacement_of(items[eats_item_id]['id'])
            == replacement_of_items
        )
        utils.check_updated_item_measure(
            items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_1_existing(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 4):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=500,
            price=25,
            measure_quantum=375,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-3',
                    'barcode': '3',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-2',
                    'eats_item_id': 'item-3',
                    'barcode': '3',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 1
    utils.check_updated_item_measure(
        items['item-3'],
        measure_value=500,
        price=25,
        quantity=33,
        quantum=0.75,
    )
    assert get_item_replacement_of(items['item-3']['id']) == {
        'item-1',
        'item-2',
        'item-3',
    }


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_one_of_them(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 3):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=500,
            price=25,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-2',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 1
    utils.check_updated_item_measure(
        items['item-2'], measure_value=500, price=25, quantity=3, quantum=0.75,
    )
    assert get_item_replacement_of(items['item-2']['id']) == {
        'item-1',
        'item-2',
    }


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_cross_replacement(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=5000,
    )
    for i in range(1, 3):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=False,
            measure_value=500,
            price=25,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 1,
                },
                {
                    'old_item_id': 'item-2',
                    'eats_item_id': 'item-1',
                    'barcode': '1',
                    'quantity': 2,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 2, {'item-2'}),
            ('item-2', 1, {'item-1'}),
    ):
        assert (
            get_item_replacement_of(items[eats_item_id]['id'])
            == replacement_of_items
        )
        utils.check_updated_item_measure(
            items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize('query_by', ['barcode', 'vendor_code'])
@utils.send_order_events_config()
async def test_update_order_multi_replacements_200(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        sold_by_weight,
        query_by,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in range(1, 6):
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=sold_by_weight,
            measure_value=500,
            price=25,
            measure_quantum=375,
        )

    mock_edadeal(sold_by_weight, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    request_body = {
        # item-1 не участвует в заменах
        'items': [
            {
                # item-2 заменяется, но не заменяет другие товары
                'old_item_id': 'item-2',
                'eats_item_id': 'item-3',
                'quantity': 1,
            },
            {
                # item-3 заменяется сам на себя и на item-4,
                # заменяет item-2 и item-4
                'old_item_id': 'item-3',
                'eats_item_id': 'item-3',
                'quantity': 2,
            },
            {'old_item_id': 'item-3', 'eats_item_id': 'item-4', 'quantity': 4},
            {
                # item-4 заменяет item-3 и заменяется на item-3,
                # item-5 и item-6, но не сам на себя
                'old_item_id': 'item-4',
                'eats_item_id': 'item-3',
                'quantity': 8,
            },
            {
                # item-5 не заменяется, но заменяет item-4
                'old_item_id': 'item-4',
                'eats_item_id': 'item-5',
                'quantity': 16,
            },
            {
                # item-6 отсутствует в оригинальном составе заказа
                'old_item_id': 'item-4',
                'eats_item_id': 'item-6',
                'quantity': 32,
            },
        ],
    }

    for item in request_body['items']:
        item[query_by] = item['eats_item_id'][len('item-') :]

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=1)
    }
    assert len(items) == 5
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 10, set()),
            ('item-3', 11, {'item-2', 'item-3', 'item-4'}),
            ('item-4', 4, {'item-3'}),
            ('item-5', 66, {'item-4', 'item-5'}),
            ('item-6', 32, {'item-4'}),
    ):
        assert (
            get_item_replacement_of(items[eats_item_id]['id'])
            == replacement_of_items
        )
        utils.check_updated_item_measure(
            items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@utils.send_order_events_config()
async def test_update_order_2_replacements(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        get_item_replacement_of,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )

    for i in [1, 2]:
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=1,
            sold_by_weight=False,
        )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    for old_id, new_id in [(1, 3), (2, 4)]:
        response = await taxi_eats_picker_orders.put(
            handle,
            headers=utils.make_headers(picker_id, measure_version),
            params={'eats_id': eats_id, 'author_type': 'customer'},
            json={
                'items': [
                    {
                        'old_item_id': f'item-{old_id}',
                        'eats_item_id': f'item-{new_id}',
                        'barcode': '4',
                        'quantity': 1,
                    },
                ],
            },
        )
        assert response.status_code == 200
    assert mock_processing.times_called == 2

    items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id=order_id, version=2)
    }
    assert get_item_replacement_of(items['item-3']['id']) == {'item-1'}
    assert get_item_replacement_of(items['item-4']['id']) == {'item-2'}


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'new_item_price, limit_exceeded',
    (
        pytest.param(100, False, id='limit_not_exceeded'),
        pytest.param(1000, True, id='limit_exceeded'),
    ),
)
@utils.send_order_events_config()
async def test_change_payment_limit_200(
        load_json,
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_by_eats_id,
        new_item_price,
        limit_exceeded,
        handle,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    request_body = {
        'items': [
            {'old_item_id': 'item-1', 'vendor_code': '7777', 'quantity': 5.5},
        ],
    }
    initial_limit = 1000
    final_limit = max(
        initial_limit,
        sum(
            item['quantity'] * new_item_price for item in request_body['items']
        ),
    )
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        payment_limit=initial_limit,
        spent=None,
    )
    create_order_item(
        order_id=order_id, eats_item_id='item-1', quantity=1.0, price=10,
    )

    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_edadeal(_):
        expected_item = load_json('expected_item_measure_v2.json')
        expected_item['price'] = str(
            new_item_price * expected_item['measure']['quantum'],
        )
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id, 'author_type': 'customer'}
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        handle, headers=headers, params=params, json=request_body,
    )

    if limit_exceeded:
        assert response.status_code == 422
        assert response.json()['details']['limit_overrun'] == '4500.00'
        return

    assert response.status_code == 200
    assert response.json()['order_version'] == 1

    assert mock_processing.times_called == 1

    params['version'] = 1
    response = await taxi_eats_picker_orders.get(
        '/api/v1/order',
        params={'eats_id': eats_id, 'author_type': 'customer'},
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response.json')
    expected_response['payload']['picker_items'][0]['price'] = (
        '%.2f' % new_item_price
    )
    response_data = response.json()
    assert response_data['payload']['is_asap']
    del response_data['payload']['is_asap']
    assert response_data['payload']['status_updated_at']
    del response_data['payload']['status_updated_at']
    assert response_data['payload']['created_at']
    del response_data['payload']['created_at']
    assert response_data['payload']['updated_at']
    del response_data['payload']['updated_at']
    assert response_data['payload']['customer_phone']
    del response_data['payload']['customer_phone']
    assert response_data['payload']['customer_picker_phone_forwarding']
    del response_data['payload']['customer_picker_phone_forwarding']
    assert response_data['payload']['payment_limit']
    del response_data['payload']['payment_limit']
    assert response_data['payload']['payment_limit_coefficient']
    del response_data['payload']['payment_limit_coefficient']
    assert response_data['payload']['held_payment_limit']
    del response_data['payload']['held_payment_limit']
    for item in response_data['payload']['picker_items']:
        item.pop('measure_v2', None)
        item['measure']['relative_quantum'] = pytest.approx(
            item['measure']['relative_quantum'],
        )
    assert response_data == expected_response

    order = get_order_by_eats_id(eats_id)
    assert float(order['payment_limit']) == final_limit


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, expected_quantity',
    [
        (None, None, 21),
        ('1122', None, 1),
        ('1122', 'picker', 1),
        ('system', None, 1),
        ('system', 'system', 1),
        ('customer_id', 'customer', 1),
        ('unknown', None, 21),
        ('unknown', 'picker', 21),
    ],
)
@pytest.mark.parametrize(
    'handle, request_picker_id',
    [['/4.0/eats-picker/api/v2/order', '1122'], ['/api/v1/order', None]],
)
@utils.send_order_events_config()
async def test_update_order_replace_soft_deleted_2_items(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        handle,
        request_picker_id,
        is_deleted_by,
        deleted_by_type,
        expected_quantity,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=f'item-1',
        quantity=10,
        sold_by_weight=False,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=f'item-2',
        quantity=20,
        sold_by_weight=False,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
    )

    mock_edadeal(False, 0.75)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': 'item-2',
                    'barcode': '2',
                    'quantity': 1,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert mock_processing.times_called == 1

    item = get_order_items(order_id, version=1)[0]
    assert item['is_deleted_by'] is None
    assert item['deleted_by_type'] is None
    assert item['quantity'] == expected_quantity


@pytest.mark.parametrize(
    'measure_version, limit_overrun',
    [(None, '100.00'), ('1', '100.00'), ('2', '99.93')],
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
@pytest.mark.parametrize(
    'handle, request_picker_id',
    [['/4.0/eats-picker/api/v2/order', '1122'], ['/api/v1/order', None]],
)
@utils.send_order_events_config()
async def test_update_order_soft_deleted_limit(
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
        handle,
        request_picker_id,
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

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(request_picker_id, measure_version),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={
            'items': [
                {
                    'old_item_id': 'item_0',
                    'eats_item_id': 'item_n',
                    'barcode': 'item_n',
                    'quantity': 1,
                },
            ],
        },
    )

    assert response.status_code == status

    if status == 200:
        assert response.json()['order_version'] == 1
        assert get_order(order_id)['last_version'] == 1
        assert mock_processing.times_called == 1
    elif status == 422:
        assert response.json()['code'] == 'payment_limit_exceeded'
        assert response.json()['details']['limit_overrun'] == limit_overrun
