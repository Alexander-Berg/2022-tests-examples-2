# pylint: disable=too-many-lines

import pytest
import pytz


async def test_cart_items_diff_no_changes_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    item_id = create_order_item(order_id=order_id)

    create_picked_item(order_item_id=item_id, picker_id=picker_id, count=1)

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == ['eats-123']


async def test_cart_items_diff_deleted_picked_item_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    create_order_item(order_id=order_id, eats_item_id='item_1', version=0)
    item_id1 = create_order_item(
        order_id=order_id, eats_item_id='item_1', version=1,
    )
    item_id2 = create_order_item(
        order_id=order_id, eats_item_id='item_2', version=1,
    )
    create_order_item(order_id=order_id, eats_item_id='item_1', version=2)

    create_picked_item(order_item_id=item_id1, picker_id=picker_id, count=1)
    create_picked_item(order_item_id=item_id2, picker_id=picker_id, count=1)

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == ['item_1']


@pytest.mark.parametrize('is_picked', [False, True])
async def test_cart_items_diff_1to1_replacement_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        is_picked,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=1,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id2,
        replacements=[(eats_item_id1, item_id1)],
    )

    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, cart_version=0, count=1,
    )
    if is_picked:
        create_picked_item(
            order_item_id=item_id2,
            picker_id=picker_id,
            cart_version=1,
            count=1,
        )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    replacements = cart_diff['replace']
    if is_picked:
        assert len(replacements) == 1
        assert replacements[0]['from_item']['id'] == eats_item_id1
        assert replacements[0]['to_item']['id'] == eats_item_id2
        assert cart_diff['picked_items'] == [eats_item_id2]
    else:
        assert not replacements
        assert not cart_diff['picked_items']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']


async def test_cart_items_diff_1to2_replacement_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    eats_item_id3 = 'eats_item_id_3'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=1,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id2,
        replacements=[(eats_item_id1, item_id1)],
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id3,
        replacements=[(eats_item_id1, item_id1)],
    )

    create_picked_item(
        order_item_id=item_id2, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    replacements = cart_diff['replace']
    assert len(replacements) == 2
    assert replacements[0]['from_item']['id'] == eats_item_id1
    assert replacements[0]['to_item']['id'] in (eats_item_id2, eats_item_id3)
    assert replacements[1]['from_item']['id'] == eats_item_id1
    assert replacements[1]['to_item']['id'] in (eats_item_id2, eats_item_id3)
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert sorted(cart_diff['picked_items']) == [eats_item_id2, eats_item_id3]


async def test_cart_items_diff_2to1_replacement_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    eats_item_id3 = 'eats_item_id_3'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=1,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id2,
    )

    item_id3 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id3,
        replacements=[(eats_item_id1, item_id1), (eats_item_id1, item_id2)],
    )

    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    replacements = cart_diff['replace']
    assert len(replacements) == 2
    assert replacements[0]['from_item']['id'] in (eats_item_id1, eats_item_id2)
    assert replacements[0]['to_item']['id'] == eats_item_id3
    assert replacements[1]['from_item']['id'] in (eats_item_id1, eats_item_id2)
    assert replacements[1]['to_item']['id'] == eats_item_id3
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == [eats_item_id3]


async def test_cart_items_diff_self_replacement_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=2,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id2,
        replacements=[(eats_item_id1, item_id1)],
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=2,
        eats_item_id=eats_item_id1,
        replacements=[(eats_item_id2, item_id2)],
    )

    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=2, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == [eats_item_id1]


async def test_cart_items_diff_replacements_chain_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    eats_item_id3 = 'eats_item_id_3'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=2,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id2,
        replacements=[(eats_item_id1, item_id1)],
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=2,
        eats_item_id=eats_item_id3,
        replacements=[(eats_item_id2, item_id2)],
    )

    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=2, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    replacements = cart_diff['replace']
    assert len(replacements) == 1
    assert replacements[0]['from_item']['id'] == eats_item_id1
    assert replacements[0]['to_item']['id'] == eats_item_id3
    assert cart_diff['picked_items'] == [eats_item_id3]


async def test_cart_items_diff_replacement_to_existed_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=1,
    )

    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id1)
    item_id2 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id2,
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id1,
        replacements=[(eats_item_id2, item_id2)],
    )

    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=1, count=5,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']

    updates = cart_diff['update']
    assert len(updates) == 1
    update = cart_diff['update'][0]
    from_item = update['from_item']
    to_item = update['to_item']
    assert from_item['id'] == eats_item_id1
    assert from_item['count'] == 1
    assert to_item['id'] == eats_item_id1
    assert to_item['count'] == 5

    replacements = cart_diff['replace']
    assert len(replacements) == 1
    assert replacements[0]['from_item']['id'] == eats_item_id2
    assert replacements[0]['to_item']['id'] == eats_item_id1

    assert cart_diff['picked_items'] == [eats_item_id1]


async def test_cart_items_diff_updated_item_count_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    ordered_count = 1
    item_id1 = create_order_item(
        order_id=order_id, eats_item_id=eats_item_id1, quantity=ordered_count,
    )

    picked_count = 3
    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, count=picked_count,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['update']) == 1
    update = cart_diff['update'][0]
    from_item = update['from_item']
    to_item = update['to_item']
    assert from_item['id'] == eats_item_id1
    assert from_item['count'] == ordered_count
    assert to_item['id'] == eats_item_id1
    assert to_item['count'] == picked_count
    assert cart_diff['picked_items'] == [eats_item_id1]


async def test_cart_items_diff_updated_item_weight_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    measure_value = 1000
    ordered_weight = 4000
    item_id1 = create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        quantity=ordered_weight / measure_value,
        sold_by_weight=True,
        measure_value=measure_value,
    )

    picked_weight = 4002
    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, weight=picked_weight,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['update']) == 1
    update = cart_diff['update'][0]
    from_item = update['from_item']
    to_item = update['to_item']
    assert from_item['id'] == eats_item_id1
    assert from_item['measure']['value'] == ordered_weight
    assert from_item['measure_v2']['absolute_quantity'] == ordered_weight
    assert to_item['id'] == eats_item_id1
    assert to_item['measure']['value'] == picked_weight
    assert to_item['measure_v2']['absolute_quantity'] == picked_weight
    assert (
        to_item['measure_v2']['quantum_quantity']
        == picked_weight / measure_value
    )
    assert cart_diff['picked_items'] == [eats_item_id1]


@pytest.mark.now('2021-07-29T16:00:00+03:00')
@pytest.mark.parametrize(
    'measure_quantum, old_price, old_quantum_price, new_price, '
    'new_quantum_price, do_update',
    [
        (None, 150, None, 150, None, False),
        (100, 150, 150, 150, 150, False),
        (None, 150, None, 200, None, True),
        (100, 150, 150, 200, 200, True),
        # невозможные ситуации, quantum_price должен меняться вместе с price:
        (100, 150, 150, 200, 150, True),
        (100, 150, 150, 150, 200, False),
    ],
)
async def test_cart_items_diff_updated_item_price_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        now,
        measure_quantum,
        old_price,
        old_quantum_price,
        new_price,
        new_quantum_price,
        do_update,
):
    now = now.replace(tzinfo=pytz.utc)
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    item_id1 = create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        version=0,
        measure_quantum=measure_quantum,
        quantity=1,
        quantum_quantity=1,
        absolute_quantity=1,
        price=old_price,
        quantum_price=old_quantum_price,
    )

    create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        version=1,
        measure_quantum=measure_quantum,
        quantity=1,
        quantum_quantity=1,
        absolute_quantity=1,
        price=new_price,
        quantum_price=new_quantum_price,
        price_updated_at=now,
    )

    create_picked_item(order_item_id=item_id1, picker_id=picker_id, count=1)

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['update']) == int(do_update)
    if do_update:
        update = cart_diff['update'][0]
        from_item = update['from_item']
        to_item = update['to_item']
        assert from_item['id'] == eats_item_id1
        assert to_item['id'] == eats_item_id1
        if new_price:
            assert from_item['price'] == f'{old_price:.2f}'
            assert to_item['price'] == f'{new_price:.2f}'
        if new_quantum_price:
            assert (
                from_item['measure_v2']['quantum_price']
                == f'{old_quantum_price:.2f}'
            )
            assert (
                to_item['measure_v2']['quantum_price']
                == f'{new_quantum_price:.2f}'
            )
        assert 'price_updated_at' not in from_item
        assert to_item['price_updated_at'] == now.isoformat()

    assert cart_diff['picked_items'] == [eats_item_id1]


@pytest.mark.parametrize(
    'order_state, is_paid',
    [
        ('picking', False),
        ('waiting_confirmation', False),
        ('confirmed', False),
        ('picked_up', False),
        ('receipt_processing', False),
        ('receipt_rejected', False),
        ('paid', True),
        ('packing', True),
        ('cancelled', True),
        ('complete', True),
    ],
)
async def test_cart_items_diff_deletion_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        order_state,
        is_paid,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state=order_state,
    )

    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id1)
    item_id2 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id2,
    )

    create_picked_item(
        order_item_id=item_id2, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    removed = cart_diff['remove']
    assert cart_diff['picked_items'] == [eats_item_id2]
    if is_paid:
        assert len(removed) == 1
        assert removed[0]['id'] == eats_item_id1
    else:
        assert not removed


@pytest.mark.parametrize(
    'order_state, is_paid, is_deleted_by, deleted_by_type, '
    'soft_delete_expected',
    [
        ('picking', False, 'picker_id', 'picker', True),
        ('picking', False, None, 'system', True),
        ('picking', False, 'another_picker_id', 'picker', False),
        ('picked_up', False, 'picker_id', 'picker', True),
        ('receipt_processing', False, 'picker_id', 'picker', True),
        ('receipt_rejected', False, 'picker_id', 'picker', True),
        ('paid', 'picker_id', True, 'picker', False),
        ('complete', True, 'picker_id', 'picker', False),
    ],
)
async def test_cart_items_diff_soft_deletion_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        order_state,
        is_paid,
        is_deleted_by,
        deleted_by_type,
        soft_delete_expected,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state=order_state,
    )

    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id1)
    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id2)

    item_id1 = create_order_item(
        order_id=order_id, version=1, eats_item_id=eats_item_id1,
    )
    create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id2,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
    )

    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['update']

    if is_paid:
        assert not cart_diff['soft_delete']
        removed = cart_diff['remove']
        assert len(removed) == 1
        assert removed[0]['id'] == eats_item_id2
    elif soft_delete_expected:
        assert not cart_diff['remove']
        soft_deleted = cart_diff['soft_delete']
        assert len(soft_deleted) == 1
        assert soft_deleted[0]['id'] == eats_item_id2
    else:
        assert not cart_diff['soft_delete']
        assert not cart_diff['remove']

    cart_diff['picked_items'] = [eats_item_id1]


async def test_cart_items_diff_soft_deletion_mid_version_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state='picking',
    )

    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id1)

    create_order_item(order_id=order_id, version=1, eats_item_id=eats_item_id1)
    create_order_item(order_id=order_id, version=1, eats_item_id=eats_item_id2)

    item_id1 = create_order_item(
        order_id=order_id, version=2, eats_item_id=eats_item_id1,
    )
    create_order_item(
        order_id=order_id,
        version=2,
        eats_item_id=eats_item_id2,
        is_deleted_by=picker_id,
        deleted_by_type='picker',
    )

    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['update']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == [eats_item_id1]


async def test_cart_items_diff_addition_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    original_item_id = 'original_item_id'
    added_item_id = 'added_item_id'
    soft_deleted_item_id = 'soft_deleted_item_id'
    added_and_replaced_item_id = 'added_and_replaced_item_id'
    replacement_item_id = 'replacement_item_id'

    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    create_order_item(
        order_id=order_id, version=0, eats_item_id=original_item_id,
    )

    create_order_item(order_id=order_id, version=1, eats_item_id=added_item_id)
    create_order_item(
        order_id=order_id, version=1, eats_item_id=added_and_replaced_item_id,
    )
    create_order_item(
        order_id=order_id, version=1, eats_item_id=soft_deleted_item_id,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=2, eats_item_id=original_item_id,
    )
    item_id2 = create_order_item(
        order_id=order_id, version=2, eats_item_id=added_item_id,
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=2,
        eats_item_id=soft_deleted_item_id,
        is_deleted_by=picker_id,
        deleted_by_type='picker',
    )
    item_id4 = create_order_item(
        order_id=order_id, version=2, eats_item_id=replacement_item_id,
    )

    for order_item_id in item_id1, item_id2, item_id3, item_id4:
        create_picked_item(
            order_item_id=order_item_id,
            picker_id=picker_id,
            cart_version=0,
            count=1,
        )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff', params={'eats_id': eats_id},
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['replace']
    assert not cart_diff['update']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['add']) == 2
    add = cart_diff['add']
    assert {item['id'] for item in add} == {added_item_id, replacement_item_id}
    assert sorted(cart_diff['picked_items']) == sorted(
        [original_item_id, added_item_id, replacement_item_id],
    )


@pytest.mark.parametrize('state', ['picking', 'paid'])
async def test_cart_items_diff_replacement_of_not_original_item_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        state,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id0 = 'eats_item_id_0'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'

    order_id = create_order(eats_id=eats_id, picker_id=picker_id, state=state)

    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id0)

    # добавили товар 1
    create_order_item(order_id=order_id, version=1, eats_item_id=eats_item_id0)
    create_order_item(order_id=order_id, version=1, eats_item_id=eats_item_id1)

    # и удалили товар 0
    item_id1 = create_order_item(
        order_id=order_id, version=2, eats_item_id=eats_item_id1,
    )

    # заменили товар 1 на 1 и 2
    item_id2 = create_order_item(
        order_id=order_id,
        version=3,
        eats_item_id=eats_item_id1,
        replacements=[(eats_item_id1, item_id1)],
    )
    item_id3 = create_order_item(
        order_id=order_id,
        version=3,
        eats_item_id=eats_item_id2,
        replacements=[(eats_item_id1, item_id1)],
    )

    create_picked_item(
        order_item_id=item_id2, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item_id3, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['replace']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['add']) == 2
    assert {item['id'] for item in cart_diff['add']} == {
        eats_item_id1,
        eats_item_id2,
    }
    assert sorted(cart_diff['picked_items']) == [eats_item_id1, eats_item_id2]
    if state == 'paid':
        assert len(cart_diff['remove']) == 1
        assert cart_diff['remove'][0]['id'] == eats_item_id0
    else:
        assert not cart_diff['remove']


@pytest.mark.parametrize(
    'order_state, picked_items_expected',
    [
        ('picking', True),
        ('waiting_confirmation', True),
        ('confirmed', True),
        ('picked_up', True),
        ('receipt_processing', True),
        ('receipt_rejected', True),
        ('paid', True),
        ('packing', True),
        ('cancelled', True),
        ('complete', True),
    ],
)
async def test_cart_items_diff_picked_items_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        order_state,
        picked_items_expected,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    eats_item_id3 = 'eats_item_id_3'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state=order_state,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id2,
    )
    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id3)

    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item_id2, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    if picked_items_expected:
        assert len(cart_diff['picked_items']) == 2
        assert sorted(cart_diff['picked_items']) == [
            eats_item_id1,
            eats_item_id2,
        ]
    else:
        assert not cart_diff['picked_items']


@pytest.mark.parametrize(
    'order_state, is_paid',
    [
        ('picking', False),
        ('waiting_confirmation', False),
        ('confirmed', False),
        ('picked_up', False),
        ('receipt_processing', False),
        ('receipt_rejected', False),
        ('paid', True),
        ('packing', True),
        ('cancelled', True),
        ('complete', True),
    ],
)
async def test_cart_items_diff_all_together_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        order_state,
        is_paid,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    eats_item_id3 = 'eats_item_id_3'
    eats_item_id4 = 'eats_item_id_4'
    eats_item_id5 = 'eats_item_id_5'
    eats_item_id6 = 'eats_item_id_6'

    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state=order_state,
    )

    item_id1 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id1,
    )
    item_id2 = create_order_item(
        order_id=order_id, version=0, eats_item_id=eats_item_id2,
    )
    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id3)
    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id6)

    create_order_item(order_id=order_id, version=1, eats_item_id=eats_item_id2)
    item_id4 = create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id4,
        replacements=[('item1', item_id1)],
    )
    item_id5 = create_order_item(
        order_id=order_id, version=1, eats_item_id=eats_item_id5,
    )
    create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id=eats_item_id6,
        is_deleted_by=picker_id,
        deleted_by_type='picker',
    )

    create_picked_item(
        order_item_id=item_id2, picker_id=picker_id, cart_version=0, count=3,
    )
    create_picked_item(
        order_item_id=item_id4, picker_id=picker_id, cart_version=0, count=1,
    )
    create_picked_item(
        order_item_id=item_id5, picker_id=picker_id, cart_version=0, count=1,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']

    assert len(cart_diff['add']) == 1
    added = cart_diff['add'][0]
    assert added['id'] == eats_item_id5

    assert len(cart_diff['replace']) == 1
    replaced = cart_diff['replace'][0]
    assert replaced['from_item']['id'] == eats_item_id1
    assert replaced['to_item']['id'] == eats_item_id4

    assert len(cart_diff['update']) == 1
    updated = cart_diff['update'][0]
    assert updated['from_item']['id'] == eats_item_id2
    assert updated['from_item']['count'] == 1
    assert updated['to_item']['id'] == eats_item_id2
    assert updated['to_item']['count'] == 3

    assert sorted(cart_diff['picked_items']) == [
        eats_item_id2,
        eats_item_id4,
        eats_item_id5,
    ]

    if is_paid:
        assert len(cart_diff['remove']) == 2
        removed = sorted(cart_diff['remove'], key=lambda item: item['id'])
        assert removed[0]['id'] == eats_item_id3
        assert removed[1]['id'] == eats_item_id6
        assert not cart_diff['soft_delete']
    else:
        assert not cart_diff['remove']
        assert len(cart_diff['soft_delete']) == 1
        soft_deleted = cart_diff['soft_delete'][0]
        assert soft_deleted['id'] == eats_item_id6


async def test_cart_items_diff_no_order_404(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=123',
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'


async def test_cart_items_diff_no_cart_404(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    eats_item_id1 = 'eats_item_id'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)
    create_order_item(order_id=order_id, version=0, eats_item_id=eats_item_id1)
    response = await taxi_eats_picker_orders.get(
        f'/api/v1/order/cart/diff?eats_id={eats_id}',
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'cart_not_found'


async def test_cart_items_diff_updated_item_count_measure_v2_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    ordered_count_v1 = 1
    ordered_count_v2 = 2
    picked_count = 3
    measure_value = 200

    item_id1 = create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        quantity=ordered_count_v1,
        measure_value=measure_value,
        measure_quantum=measure_value,
        quantum_quantity=ordered_count_v2,
        absolute_quantity=measure_value * ordered_count_v1,
        price=20,
        quantum_price=20,
    )

    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, count=picked_count,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff', params={'eats_id': eats_id},
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['update']) == 1
    update = cart_diff['update'][0]
    from_item = update['from_item']
    to_item = update['to_item']
    assert from_item['id'] == eats_item_id1
    assert from_item['count'] == ordered_count_v1
    assert from_item['measure_v2']['quantum_quantity'] == ordered_count_v2
    assert (
        from_item['measure_v2']['absolute_quantity']
        == ordered_count_v1 * measure_value
    )
    assert to_item['id'] == eats_item_id1
    assert to_item['count'] == picked_count
    assert to_item['measure_v2']['quantum_quantity'] == picked_count
    assert (
        to_item['measure_v2']['absolute_quantity']
        == picked_count * measure_value
    )

    assert cart_diff['picked_items'] == [eats_item_id1]


async def test_cart_items_diff_updated_item_weight_measure_v2_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id1 = 'eats_item_id_1'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)

    ordered_weight = 150
    measure_value = 200
    measure_quantum = 100
    item_id1 = create_order_item(
        order_id=order_id,
        eats_item_id=eats_item_id1,
        sold_by_weight=True,
        measure_value=measure_value,
        quantity=ordered_weight / measure_value,
        measure_quantum=measure_quantum,
        quantum_quantity=ordered_weight / measure_quantum,
        absolute_quantity=ordered_weight,
        price=20,
        quantum_price=10,
    )

    picked_weight = 153
    create_picked_item(
        order_item_id=item_id1, picker_id=picker_id, weight=picked_weight,
    )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff?eats_id=' + eats_id,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['soft_delete']
    assert len(cart_diff['update']) == 1
    update = cart_diff['update'][0]
    from_item = update['from_item']
    to_item = update['to_item']
    assert from_item['id'] == eats_item_id1
    assert from_item['measure']['value'] == ordered_weight
    assert from_item['measure']['quantum'] == measure_value
    assert from_item['measure_v2']['value'] == measure_value
    assert from_item['measure_v2']['quantum'] == measure_quantum
    assert from_item['measure_v2']['absolute_quantity'] == ordered_weight
    assert (
        from_item['measure_v2']['quantum_quantity']
        == ordered_weight / measure_quantum
    )
    assert to_item['id'] == eats_item_id1
    assert to_item['measure']['value'] == picked_weight
    assert to_item['measure']['quantum'] == measure_value
    assert to_item['measure_v2']['value'] == measure_value
    assert to_item['measure_v2']['quantum'] == measure_quantum
    assert to_item['measure_v2']['absolute_quantity'] == picked_weight
    assert (
        round(to_item['measure_v2']['quantum_quantity'], 2)
        == picked_weight / measure_quantum
    )
    assert cart_diff['picked_items'] == [eats_item_id1]


@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, expected_replace',
    [
        ['someone', None, True],
        ['picker_id', 'picker', True],
        ['picker_id', 'system', True],
        ['customer', 'customer', True],
        [None, 'system', True],
        ['another_picker', 'picker', False],
        ['another_picker', 'system', False],
    ],
)
@pytest.mark.parametrize('requested_version', [None, 0, 1])
@pytest.mark.parametrize('state', ['picking', 'paid'])
async def test_cart_items_diff_version_author(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        requested_version,
        last_version_author,
        last_version_author_type,
        expected_replace,
        state,
):
    picker_id = 'picker_id'
    eats_id = 'eats_id'
    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, last_version=100, state=state,
    )

    item_id_1 = create_order_item(
        version=0,
        order_id=order_id,
        eats_item_id=eats_item_id_1,
        quantity=1,
        author='someone',
    )
    item_id_2 = create_order_item(
        version=1,
        order_id=order_id,
        eats_item_id=eats_item_id_2,
        quantity=2,
        author=last_version_author,
        author_type=last_version_author_type,
        replacements=[(eats_item_id_1, item_id_1)],
    )

    create_picked_item(order_item_id=item_id_1, picker_id=picker_id, count=1)
    create_picked_item(order_item_id=item_id_2, picker_id=picker_id, count=2)
    params = {'eats_id': eats_id}
    if requested_version is not None:
        params['version'] = requested_version
    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/cart/diff', params=params,
    )
    assert response.status_code == 200
    cart_diff = response.json()['cart_diff']
    if expected_replace and requested_version != 1:
        for key in 'add', 'update', 'remove', 'soft_delete':
            assert not cart_diff[key]
        assert len(cart_diff['replace']) == 1
        replacement = cart_diff['replace'][0]
        from_item = replacement['from_item']
        to_item = replacement['to_item']
        assert from_item['id'] == eats_item_id_1
        assert from_item['count'] == 1
        assert to_item['id'] == eats_item_id_2
        assert to_item['count'] == 2
        assert cart_diff['picked_items'] == [eats_item_id_2]
    else:
        for key in 'add', 'update', 'replace', 'soft_delete':
            assert not cart_diff[key]
        if not expected_replace and requested_version == 1:
            # запросили дифф с первой версией, а последняя видимая для
            # сборщика версия = 0 -> получили пустой список товаров в
            # финальном составе заказа
            if state == 'paid':
                assert len(cart_diff['remove']) == 1
                assert cart_diff['remove'][0]['id'] == eats_item_id_2
            else:
                assert not cart_diff['remove']
            assert not cart_diff['picked_items']
        else:
            assert not cart_diff['remove']
            if expected_replace and requested_version == 1:
                assert cart_diff['picked_items'] == [eats_item_id_2]
            else:
                assert cart_diff['picked_items'] == [eats_item_id_1]
