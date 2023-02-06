# pylint: disable=too-many-lines
import pytest

from . import utils


@utils.marking_types_config()
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('request_version', [None, 0])
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
        {
            'items': [
                {
                    'old_item_id': 'item-1',
                    'eats_item_id': '4321',
                    'weight': 5500,
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
        get_order_by_eats_id,
        get_order_items,
        barcode_weight_encoding,
        request_body,
        request_version,
        measure_version,
        mock_processing,
        marking_type,
        require_marks,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        quantity=1,
        price=10,
        quantum_price=5,
        measure_value=1000,
        measure_quantum=500,
        quantum_quantity=2,
        absolute_quantity=1000,
    )

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

    params = {'eats_id': eats_id}
    if request_version is not None:
        params['version'] = request_version
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=headers,
        params=params,
        json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    new_items = load_json('expected_response_items.json')
    for item in new_items['items']:
        item['weight_barcode_type'] = barcode_weight_encoding
        if item['id'] in origin_ids:
            item['require_marks'] = require_marks
    response_data = response.json()
    for item in response_data['items']:
        item.pop('measure_v2', None)
        item['measure']['relative_quantum'] = pytest.approx(
            item['measure']['relative_quantum'],
        )
    assert response_data == new_items

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id},
        headers=headers,
    )
    order = response.json()
    assert (
        order['payload']['picker_items'][0]['id']
        == new_items['items'][0]['id']
    )

    # check version
    order_row = get_order_by_eats_id(eats_id)
    assert order_row['last_version'] == 1
    items_row = get_order_items(order_id, version=1)
    assert len(items_row) == 1
    item = items_row[0]
    assert item['eats_item_id'] == new_items['items'][0]['id']
    utils.check_updated_item_measure(
        item, measure_value=1000, quantity=5.5, price=25.25, quantum=0.8,
    )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
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
        for item in matched_items:
            item['item']['price'] = str(item['item']['price'])
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
    response_put = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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
        assert item['author'] == picker_id
        assert item['author_type'] == 'picker'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
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
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mockserver,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        request_body,
        expected_items_quantity,
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
    def _mock_get_item_by_code(_):
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

    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items_quantity = {
        item['id']: _get_item_quantity(item)
        for item in response.json()['items']
    }
    assert items_quantity == expected_items_quantity


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_self_replacement(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        measure_version,
        mock_processing,
):
    quantum = 0.75
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

    mock_edadeal(False, quantum)
    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 1
    assert items['item-1']['replacement_of_items'] == ['item-1']
    assert _get_item_quantity(items['item-1']) == 1
    items_row = get_order_items(order_id, version=1)
    assert len(items_row) == 1
    item = items_row[0]
    assert item['eats_item_id'] == 'item-1'
    utils.check_updated_item_measure(
        item, measure_value=500, price=25, quantity=1, quantum=0.75,
    )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_to_existing_item(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 1
    assert set(items['item-2']['replacement_of_items']) == {'item-1', 'item-2'}
    assert _get_item_quantity(items['item-2']) == 21
    items_row = get_order_items(order_id, version=1)
    assert len(items_row) == 1
    item = items_row[0]
    assert item['eats_item_id'] == 'item-2'
    utils.check_updated_item_measure(
        item, measure_value=500, price=25, quantity=21, quantum=0.75,
    )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_1_item_to_self_and_new(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    db_items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id, version=1)
    }
    assert len(db_items) == len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 1, ['item-1']),
            ('item-2', 2, ['item-1']),
    ):
        assert (
            items[eats_item_id]['replacement_of_items'] == replacement_of_items
        )
        assert _get_item_quantity(items[eats_item_id]) == quantity
        utils.check_updated_item_measure(
            db_items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize(
    'measure_value, measure_quantum', [[500, 0.75], [0, 1]],
)
@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_1_item_to_2_existing(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    db_items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id, version=1)
    }
    assert len(db_items) == len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-2', 21, {'item-1', 'item-2'}),
            ('item-3', 32, {'item-1', 'item-3'}),
    ):
        assert (
            set(items[eats_item_id]['replacement_of_items'])
            == replacement_of_items
        )
        assert _get_item_quantity(items[eats_item_id]) == quantity
        utils.check_updated_item_measure(
            db_items[eats_item_id],
            measure_value=measure_value,
            price=25,
            quantity=quantity,
            quantum=measure_quantum,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_1_new(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    db_items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id, version=1)
    }
    assert len(db_items) == len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-3', 30, set()),
            ('item-4', 3, {'item-1', 'item-2'}),
    ):
        assert (
            set(items[eats_item_id]['replacement_of_items'])
            == replacement_of_items
        )
        assert _get_item_quantity(items[eats_item_id]) == quantity
        utils.check_updated_item_measure(
            db_items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_1_existing(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 1
    assert set(items['item-3']['replacement_of_items']) == {
        'item-1',
        'item-2',
        'item-3',
    }
    assert _get_item_quantity(items['item-3']) == 33
    items_row = get_order_items(order_id, version=1)
    assert len(items_row) == 1
    item = items_row[0]
    assert item['eats_item_id'] == 'item-3'
    utils.check_updated_item_measure(
        item, measure_value=500, price=25, quantity=33, quantum=0.75,
    )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_replace_2_items_to_one_of_them(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 1
    assert set(items['item-2']['replacement_of_items']) == {'item-1', 'item-2'}
    assert _get_item_quantity(items['item-2']) == 3
    items_row = get_order_items(order_id, version=1)
    assert len(items_row) == 1
    item = items_row[0]
    assert item['eats_item_id'] == 'item-2'
    utils.check_updated_item_measure(
        item, measure_value=500, price=25, quantity=3, quantum=0.75,
    )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_cross_replacement(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
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
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    db_items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id, version=1)
    }
    assert len(db_items) == len(items) == 2
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 2, ['item-2']),
            ('item-2', 1, ['item-1']),
    ):
        assert (
            items[eats_item_id]['replacement_of_items'] == replacement_of_items
        )
        assert _get_item_quantity(items[eats_item_id]) == quantity
        utils.check_updated_item_measure(
            db_items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize('query_by', ['barcode', 'vendor_code'])
@utils.send_order_events_config()
async def test_update_order_multi_replacements_200(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        sold_by_weight,
        query_by,
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

    params = {'eats_id': eats_id}
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=headers,
        params=params,
        json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {item['id']: item for item in response.json()['items']}
    db_items = {
        item['eats_item_id']: item
        for item in get_order_items(order_id, version=1)
    }
    assert len(db_items) == len(items) == 5
    for eats_item_id, quantity, replacement_of_items in (
            ('item-1', 10, set()),
            ('item-3', 11, {'item-2', 'item-3', 'item-4'}),
            ('item-4', 4, {'item-3'}),
            ('item-5', 66, {'item-4', 'item-5'}),
            ('item-6', 32, {'item-4'}),
    ):
        assert (
            set(items[eats_item_id]['replacement_of_items'])
            == replacement_of_items
        )
        assert _get_item_quantity(items[eats_item_id]) == quantity
        utils.check_updated_item_measure(
            db_items[eats_item_id],
            measure_value=500,
            price=25,
            quantity=quantity,
            quantum=0.75,
        )


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@utils.send_order_events_config()
async def test_update_order_2_replacements(
        taxi_eats_picker_orders,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        mock_edadeal,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
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
            '/4.0/eats-picker/api/v1/order',
            headers=utils.make_headers(picker_id, measure_version),
            params={'eats_id': eats_id},
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

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 2
    assert items['item-3']['replacement_of_items'] == ['item-1']
    assert items['item-4']['replacement_of_items'] == ['item-2']


def _get_item_quantity(item):
    if item['is_catch_weight']:
        return item['measure']['value'] / item['measure']['quantum']
    return item['count']


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
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
        get_order_items,
        new_item_price,
        limit_exceeded,
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
        expected_item['price'] = (
            new_item_price * expected_item['measure']['quantum']
        )
        expected_item['price'] = str(expected_item['price'])
        return {
            'matched_items': [
                {'barcode': None, 'sku': '7777', 'item': expected_item},
            ],
            'not_matched_items': [],
        }

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    params = {'eats_id': eats_id}
    headers = utils.make_headers(picker_id, measure_version)
    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=headers,
        params=params,
        json=request_body,
    )

    if limit_exceeded:
        assert response.status_code == 422
        assert response.json()['details']['limit_overrun'] == '4500.00'
        return

    assert response.status_code == 200

    assert mock_processing.times_called == 1

    new_items = load_json('expected_response_items.json')
    new_items['items'][0]['price'] = '%.2f' % new_item_price
    response_data = response.json()
    for item in response_data['items']:
        item.pop('measure_v2', None)
        item['measure']['relative_quantum'] = pytest.approx(
            item['measure']['relative_quantum'],
        )
    assert response_data == new_items

    order_row = get_order_by_eats_id(eats_id)
    assert float(order_row['payment_limit']) == final_limit
    assert order_row['last_version'] == 1

    items_row = get_order_items(order_id, version=1)[0]
    assert items_row['eats_item_id'] == new_items['items'][0]['id']
    assert items_row['quantity'] == request_body['items'][0]['quantity']


# TODO перенести в test_order_update_v2_200.py
@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v2/order', '/api/v1/order'],
)
@pytest.mark.parametrize(
    'testcase_filename',
    [
        'add_by_eats_item_id.json',
        'add_by_barcodes_and_vendor_code.json',
        'add_by_barcode_and_vendor_code.json',
        'add_by_vendor_code.json',
        'add_by_barcodes_and_sku.json',
        'add_by_barcode_and_sku.json',
        'add_by_sku.json',
        'add_by_item_barcodes.json',
        'add_by_barcode.json',
        'priority_eats_item_id.json',
        'priority_vendor_code.json',
        'priority_sku.json',
        'skip_matching_barcode.json',
        'fail_add_item_id_is_present_but_not_matched.json',
    ],
)
@utils.send_order_events_config()
async def test_match_integration_items(
        mockserver,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        generate_integration_item_data,
        create_order,
        create_order_item,
        testcase_filename,
        load_json,
        handle,
        mock_processing,
):
    testcase_data = load_json(testcase_filename)
    request_items = testcase_data['request_items']
    response_items = testcase_data['response_items']
    expected_code = testcase_data['expected_code']

    initial_quantity = {'ITEM-1': 10, 'ITEM-2': 20}

    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for eats_item_id, quantity in initial_quantity.items():
        create_order_item(
            order_id=order_id, eats_item_id=eats_item_id, quantity=quantity,
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
                    measure_quantum=0.75,
                    **etc['item'],
                ),
                'barcode': etc.get('barcode'),
                'vendor_code': etc.get('sku'),
            }
            for eats_item_id, etc in response_items.items()
        ]
        for item in matched_items:
            item['item']['price'] = str(item['item']['price'])
        print(f'matched_items: {matched_items}')
        return {'matched_items': matched_items, 'not_matched_items': []}

    mock_eatspickeritemcategories()
    mock_eats_products_public_id()

    response = await taxi_eats_picker_orders.put(
        handle,
        headers=utils.make_headers(picker_id),
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json=request_items,
    )
    assert response.status_code == expected_code

    assert mock_processing.times_called == (1 if expected_code == 200 else 0)
