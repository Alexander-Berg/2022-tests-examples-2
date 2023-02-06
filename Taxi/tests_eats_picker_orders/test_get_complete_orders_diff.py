import datetime

import pytest

from . import utils


PICKER_ID = '10'
COURIER_ID = '11'
EATS_ID = 'eats_id'
PICKER_PHONE_ID = '123'
COURIER_PHONE_ID = '321'


@pytest.mark.now('2021-07-12T12:00:00+03:00')
@pytest.mark.parametrize('status', ['complete', 'paid', 'packing', 'handing'])
@pytest.mark.parametrize('is_picked', [False, True])
async def test_cart_items_diff_1to1_replacement_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        status,
        is_picked,
):
    eats_item_id1 = 'eats_item_id_1'
    eats_item_id2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        courier_id=COURIER_ID,
        last_version=1,
        state=status,
        picker_phone_id=PICKER_PHONE_ID,
        courier_phone_id=COURIER_PHONE_ID,
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
        order_item_id=item_id1, picker_id=PICKER_ID, cart_version=0, count=1,
    )
    if is_picked:
        create_picked_item(
            order_item_id=item_id2,
            picker_id=PICKER_ID,
            cart_version=1,
            count=1,
        )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history', json={'limit': 1},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['eats_id'] == EATS_ID
    assert orders[0]['status'] == status
    assert orders[0]['picker_id'] == PICKER_ID
    assert orders[0]['courier_id'] == COURIER_ID
    assert orders[0]['picker_phone_id'] == PICKER_PHONE_ID
    assert orders[0]['courier_phone_id'] == COURIER_PHONE_ID
    cart_diff = orders[0]['cart_diff']
    assert not cart_diff['add']
    replacements = cart_diff['replace']
    remove = cart_diff['remove']
    if is_picked:
        assert len(replacements) == 1
        assert replacements[0]['from_item']['id'] == eats_item_id1
        assert replacements[0]['to_item']['id'] == eats_item_id2
        assert not remove
        assert cart_diff['picked_items'] == [eats_item_id2]
    else:
        assert not replacements
        assert len(remove) == 1
        assert remove[0]['id'] == eats_item_id1
        assert not cart_diff['picked_items']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']


@pytest.mark.now('2021-07-12T12:00:00+03:00')
@pytest.mark.parametrize('status', ['complete', 'paid', 'packing', 'handing'])
async def test_cart_items_diff_no_changes_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        status,
):
    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        courier_id=None,
        state=status,
        picker_phone_id=None,
        courier_phone_id=None,
    )

    eats_item_id = 'item_0'
    item_id = create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    create_picked_item(order_item_id=item_id, picker_id=PICKER_ID, count=1)

    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history', json={'limit': 1},
    )
    assert response.status_code == 200
    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['eats_id'] == EATS_ID
    assert orders[0]['status'] == status
    assert orders[0]['picker_id'] == PICKER_ID
    assert 'courier_id' not in orders[0]
    assert 'picker_phone_id' not in orders[0]
    assert 'courier_phone_id' not in orders[0]
    cart_diff = orders[0]['cart_diff']
    assert not cart_diff['add']
    assert not cart_diff['replace']
    assert not cart_diff['remove']
    assert not cart_diff['update']
    assert not cart_diff['soft_delete']
    assert cart_diff['picked_items'] == [eats_item_id]


@pytest.mark.now('2021-07-12T12:00:00+03:00')
async def test_cart_items_diff_updated_after_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, state='complete',
    )

    item_id = create_order_item(order_id=order_id)
    create_picked_item(order_item_id=item_id, picker_id=PICKER_ID, count=1)
    updated_after = (
        datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(hours=1)
    ).isoformat()
    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history',
        json={'updated_after': updated_after, 'limit': 1},
    )
    assert response.status_code == 200
    assert not response.json()['orders']


@pytest.mark.now('2021-07-12T12:00:00+03:00')
async def test_cart_items_diff_limit_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        get_order,
):
    order_ids = []
    for i in range(4):
        order_id = create_order(
            eats_id=str(i), picker_id=str(i), state='complete',
        )

        item_id = create_order_item(order_id=order_id)
        create_picked_item(order_item_id=item_id, picker_id=str(i), count=1)
        order_ids.append(order_id)

    updated_after = get_order(order_ids[1])['updated_at']
    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history',
        json={'updated_after': updated_after.isoformat(), 'limit': 2},
    )
    assert response.status_code == 200
    response_body = response.json()
    assert len(response_body['orders']) == 2
    assert (
        utils.parse_datetime(response_body['last_updated_at'])
        == get_order(order_ids[2])['updated_at']
    )
    assert response_body['last_order_id'] == order_ids[2]


@pytest.mark.now('2021-07-12T12:00:00+03:00')
@pytest.mark.parametrize(
    'status, picker_id', [['complete', None], ['picking', PICKER_ID]],
)
async def test_cart_items_diff_incomplete_or_no_picker_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        status,
        picker_id,
):
    order_id = create_order(eats_id=EATS_ID, picker_id=picker_id, state=status)

    item_id = create_order_item(order_id=order_id)

    create_picked_item(order_item_id=item_id, picker_id=picker_id, count=1)

    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history', json={'limit': 1},
    )
    assert response.status_code == 200
    assert not response.json()['orders']


@pytest.mark.now('2021-07-12T12:00:00+03:00')
async def test_cart_items_diff_empty_cart_200(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
):
    order_id = create_order(
        eats_id=EATS_ID, picker_id=PICKER_ID, state='complete',
    )

    create_order_item(order_id=order_id, version=0, eats_item_id='0')
    create_order_item(order_id=order_id, version=0, eats_item_id='1')

    create_order_item(order_id=order_id, version=1, eats_item_id='0')
    create_order_item(
        order_id=order_id,
        version=1,
        eats_item_id='1',
        is_deleted_by=PICKER_ID,
        deleted_by_type='picker',
    )

    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history', json={'limit': 1},
    )
    assert response.status_code == 200
    assert not response.json()['orders']


@pytest.mark.parametrize(
    'last_version_author, last_version_author_type, expected_replace',
    [
        ['someone', None, True],
        [PICKER_ID, 'picker', True],
        [PICKER_ID, 'system', True],
        ['customer', 'customer', True],
        [None, 'system', True],
        ['another_picker', 'picker', False],
        ['another_picker', 'system', False],
    ],
)
async def test_cart_items_diff_version_author(
        taxi_eats_picker_orders,
        init_currencies,
        init_measure_units,
        create_order,
        create_order_item,
        create_picked_item,
        last_version_author,
        last_version_author_type,
        expected_replace,
):
    eats_item_id_1 = 'eats_item_id_1'
    eats_item_id_2 = 'eats_item_id_2'
    order_id = create_order(
        eats_id=EATS_ID,
        picker_id=PICKER_ID,
        last_version=100,
        state='complete',
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

    create_picked_item(order_item_id=item_id_1, picker_id=PICKER_ID, count=1)
    create_picked_item(order_item_id=item_id_2, picker_id=PICKER_ID, count=2)

    response = await taxi_eats_picker_orders.post(
        '/api/v1/orders/cart/diff-for-history', json={'limit': 1},
    )
    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['eats_id'] == EATS_ID
    cart_diff = orders[0]['cart_diff']
    for key in 'add', 'update', 'remove', 'soft_delete':
        assert not cart_diff[key]
    if expected_replace:
        assert cart_diff['picked_items'] == [eats_item_id_2]
        assert len(cart_diff['replace']) == 1
        replacement = cart_diff['replace'][0]
        from_item = replacement['from_item']
        to_item = replacement['to_item']
        assert from_item['id'] == eats_item_id_1
        assert from_item['count'] == 1
        assert to_item['id'] == eats_item_id_2
        assert to_item['count'] == 2
    else:
        assert cart_diff['picked_items'] == [eats_item_id_1]
        assert not cart_diff['replace']
