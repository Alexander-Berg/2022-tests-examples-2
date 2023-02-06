import pytest

from . import utils


EATS_ID = '123'
PICKER_ID = '1122'


@pytest.mark.parametrize(
    'url, headers',
    [
        ['/4.0/eats-picker/api/v1/order/cart', utils.da_headers(PICKER_ID)],
        ['/api/v1/order/cart', {}],
    ],
)
async def test_get_cart_success_200(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        create_picked_item,
        create_picked_item_position,
        url,
        headers,
):
    eats_item_id = 'item-1'
    cart_version = 1
    picked_item_weight = 200
    picked_item_count = 100

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    order_item_id = create_order_item(
        order_id=order_id, eats_item_id=eats_item_id,
    )
    picked_item_id = create_picked_item(
        order_item_id=order_item_id,
        weight=picked_item_weight,
        count=picked_item_count,
        cart_version=cart_version,
        picker_id=PICKER_ID,
    )

    create_picked_item_position(
        picked_item_id,
        count=picked_item_count,
        weight=picked_item_weight,
        barcode='barcode_1',
        mark='mark_1',
    )
    create_picked_item_position(
        picked_item_id, count=picked_item_count, weight=picked_item_weight,
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': EATS_ID}, headers=headers,
    )

    assert response.status == 200

    cart = response.json()
    assert len(cart['picker_items']) == 1
    assert cart['picker_items'][0]['id'] == eats_item_id
    assert cart['picker_items'][0]['weight'] == picked_item_weight
    assert cart['picker_items'][0]['count'] == picked_item_count
    assert cart['picker_items'][0]['positions'] == [
        {
            'barcode': 'barcode_1',
            'count': picked_item_count,
            'weight': picked_item_weight,
            'mark': 'mark_1',
        },
        {'count': picked_item_count, 'weight': picked_item_weight},
    ]
    assert cart['cart_version'] == cart_version


@pytest.mark.parametrize(
    'url, headers',
    [
        ['/4.0/eats-picker/api/v1/order/cart', utils.da_headers(PICKER_ID)],
        ['/api/v1/order/cart', {}],
    ],
)
async def test_get_cart_last_version_success_200(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        create_picked_item,
        url,
        headers,
):
    eats_item_id = 'item-1'

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    order_item_id = create_order_item(
        order_id=order_id, eats_item_id=eats_item_id,
    )
    create_picked_item(
        order_item_id=order_item_id,
        weight=200,
        count=100,
        cart_version=1,
        picker_id=PICKER_ID,
    )
    create_picked_item(
        order_item_id=order_item_id,
        weight=400,
        count=200,
        cart_version=2,
        picker_id=PICKER_ID,
    )
    create_picked_item(
        order_item_id=order_item_id,
        weight=600,
        count=300,
        cart_version=3,
        picker_id='other_picker_id',
    )

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': EATS_ID}, headers=headers,
    )

    assert response.status == 200

    cart = response.json()
    assert len(cart['picker_items']) == 1
    assert cart['picker_items'][0]['id'] == eats_item_id
    assert cart['picker_items'][0]['weight'] == 400
    assert cart['picker_items'][0]['count'] == 200
    assert cart['cart_version'] == 2


@pytest.mark.parametrize(
    'url, headers',
    [
        ['/4.0/eats-picker/api/v1/order/cart', utils.da_headers(PICKER_ID)],
        ['/api/v1/order/cart', {}],
    ],
)
async def test_get_cart_empty_success_200(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        url,
        headers,
):
    eats_item_id = 'item-1'

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': EATS_ID}, headers=headers,
    )

    assert response.status == 200

    cart = response.json()
    assert cart['picker_items'] == []


@pytest.mark.parametrize(
    'url, headers',
    [
        ['/4.0/eats-picker/api/v1/order/cart', utils.da_headers(PICKER_ID)],
        ['/api/v1/order/cart', {}],
    ],
)
async def test_get_cart_picker_not_assigned_404(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        url,
        headers,
):
    eats_item_id = 'item-1'

    order_id = create_order(eats_id=EATS_ID)
    create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    response = await taxi_eats_picker_orders.get(
        url, params={'eats_id': EATS_ID}, headers=headers,
    )

    assert response.status == 404


@pytest.mark.parametrize(
    'url, wrong_eats_id_status, wrong_picker_id_status',
    [
        ['/4.0/eats-picker/api/v1/order/cart', 404, 404],
        ['/api/v1/order/cart', 404, 200],
    ],
)
async def test_get_cart_by_wrong_data_404(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        create_picked_item,
        url,
        wrong_eats_id_status,
        wrong_picker_id_status,
):
    eats_item_id = 'item-1'
    other_picker_id = '2211'

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    order_item_id = create_order_item(
        order_id=order_id, eats_item_id=eats_item_id,
    )
    create_picked_item(
        order_item_id=order_item_id, cart_version=1, picker_id=PICKER_ID,
    )
    create_picked_item(
        order_item_id=order_item_id, cart_version=2, picker_id=other_picker_id,
    )

    response_wrong_picker = await taxi_eats_picker_orders.get(
        url,
        params={'eats_id': EATS_ID},
        headers=utils.da_headers(other_picker_id),
    )
    assert response_wrong_picker.status == wrong_picker_id_status

    response_wrong_order = await taxi_eats_picker_orders.get(
        url, params={'eats_id': '321'}, headers=utils.da_headers(PICKER_ID),
    )
    assert response_wrong_order.status == wrong_eats_id_status


@pytest.mark.parametrize(
    'url, headers',
    [
        ['/4.0/eats-picker/api/v1/order/cart', utils.da_headers(PICKER_ID)],
        ['/api/v1/order/cart', {}],
    ],
)
async def test_get_request_with_mistakes(
        init_currencies,
        init_measure_units,
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        url,
        headers,
):
    eats_item_id = 'item-1'

    order_id = create_order(eats_id=EATS_ID, picker_id=PICKER_ID)
    create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    response = await taxi_eats_picker_orders.get(
        url, params={'eaats_id': EATS_ID}, headers=headers,
    )

    assert response.status == 400
