import pytest

from . import utils


def _get_item_quantity(item):
    if item['is_catch_weight']:
        return item['measure']['value'] / item['measure']['quantum']
    return item['count']


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['1122', 'picker'],
        ['1122', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
@utils.send_order_events_config()
async def test_update_order_self_replacement_soft_deleted(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        measure_version,
        is_deleted_by,
        deleted_by_type,
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
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
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
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 1
    item = items['item-1']
    assert item['replacement_of_items'] == ['item-1']
    assert _get_item_quantity(item) == 1

    item = get_order_items(order_id, version=1)[0]
    assert item['is_deleted_by'] is None
    assert item['deleted_by_type'] is None


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['1122', 'picker'],
        ['1122', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
@utils.send_order_events_config()
async def test_update_order_replace_is_delete_by_unchanged(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        measure_version,
        is_deleted_by,
        deleted_by_type,
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
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        reason='soft-delete',
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-2',
        quantity=20,
        sold_by_weight=False,
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
                    'old_item_id': 'item-2',
                    'eats_item_id': 'item-3',
                    'barcode': '1',
                    'quantity': 1,
                },
            ],
        },
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 2
    assert items['item-3']['replacement_of_items'] == ['item-2']
    assert _get_item_quantity(items['item-1']) == 10
    assert _get_item_quantity(items['item-3']) == 1

    items = get_order_items(order_id, version=1)
    items = {item['eats_item_id']: item for item in items}
    assert items['item-1']['is_deleted_by'] == is_deleted_by
    assert items['item-1']['deleted_by_type'] == deleted_by_type
    assert items['item-1']['reason'] == 'soft-delete'


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
        expected_quantity,
        measure_version,
        is_deleted_by,
        deleted_by_type,
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
    assert _get_item_quantity(items['item-2']) == expected_quantity

    item = get_order_items(order_id, version=1)[0]
    assert item['is_deleted_by'] is None
    assert item['deleted_by_type'] is None


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'soft_deleted_1, soft_deleted_2, expected_quantity',
    [
        (False, False, 21),
        (False, True, 21),
        (True, False, 21),
        (True, True, 21),
    ],
)
@pytest.mark.parametrize('deleted_by_type', ['picker', None])
@utils.send_order_events_config()
async def test_update_order_replace_soft_deleted_by_another_picker_2_items(
        taxi_eats_picker_orders,
        mock_edadeal,
        mock_eatspickeritemcategories,
        mock_eats_products_public_id,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order_items,
        soft_deleted_1,
        soft_deleted_2,
        expected_quantity,
        measure_version,
        deleted_by_type,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    unknown_picker_id = 'unknown_picker'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=f'item-1',
        quantity=10,
        sold_by_weight=False,
        is_deleted_by=unknown_picker_id if soft_deleted_1 else None,
        deleted_by_type=deleted_by_type if soft_deleted_1 else None,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=f'item-2',
        quantity=20,
        sold_by_weight=False,
        is_deleted_by=unknown_picker_id if soft_deleted_2 else None,
        deleted_by_type=deleted_by_type if soft_deleted_2 else None,
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
    assert _get_item_quantity(items['item-2']) == expected_quantity

    item = get_order_items(order_id, version=1)[0]
    assert item['is_deleted_by'] is None
    assert item['deleted_by_type'] is None


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('sold_by_weight', [False, True])
@pytest.mark.parametrize('query_by', ['barcode', 'vendor_code'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['1122', 'picker'],
        ['1122', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
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
        sold_by_weight,
        query_by,
        measure_version,
        is_deleted_by,
        deleted_by_type,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id,
    )
    for i in [1, 3, 5]:
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=sold_by_weight,
            measure_quantum=0.75,
        )
    for i in [2, 4]:
        create_order_item(
            order_id=order_id,
            eats_item_id=f'item-{i}',
            quantity=i * 10,
            sold_by_weight=sold_by_weight,
            is_deleted_by=is_deleted_by,
            deleted_by_type=deleted_by_type,
            measure_quantum=0.75,
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
    response = await taxi_eats_picker_orders.put(
        '/4.0/eats-picker/api/v1/order',
        headers=utils.make_headers(picker_id, measure_version),
        params=params,
        json=request_body,
    )
    assert response.status_code == 200

    assert mock_processing.times_called == 1

    items = {item['id']: item for item in response.json()['items']}
    assert len(items) == 5
    assert items['item-1']['replacement_of_items'] == []
    assert set(items['item-3']['replacement_of_items']) == {
        'item-2',
        'item-3',
        'item-4',
    }
    assert items['item-4']['replacement_of_items'] == ['item-3']
    assert set(items['item-5']['replacement_of_items']) == {'item-4', 'item-5'}
    assert items['item-6']['replacement_of_items'] == ['item-4']
    assert _get_item_quantity(items['item-1']) == 10
    assert _get_item_quantity(items['item-3']) == 11  # 1 + 2 + 8
    assert _get_item_quantity(items['item-4']) == 4
    assert _get_item_quantity(items['item-5']) == 66  # 50 + 16
    assert _get_item_quantity(items['item-6']) == 32

    items = get_order_items(order_id, version=1)
    items = {item['eats_item_id']: item for item in items}
    assert items['item-4']['is_deleted_by'] is None
    assert items['item-4']['deleted_by_type'] is None
