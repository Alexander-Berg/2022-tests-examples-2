import datetime

import pytest


@pytest.mark.parametrize('comment', [None, 'comment'])
async def test_prolongate_confirmation_200(
        taxi_eats_picker_orders,
        create_order,
        get_order,
        get_last_order_status,
        comment,
):
    customer_id = 'customer_id'
    order_created_at = datetime.datetime.fromisoformat(
        '2021-02-09 15:00:00+03:00',
    )
    order_id = create_order(
        eats_id='123',
        picker_id='1122',
        state='waiting_confirmation',
        created_at=order_created_at,
    )
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status/prolongate-confirmation',
        params={'eats_id': '123'},
        json={
            'eats_id': '123',
            'customer_id': customer_id,
            'comment': comment,
        },
    )
    assert response.status_code == 200
    order = get_order(order_id)
    assert order['state'] == 'waiting_confirmation'
    assert order['updated_at'] > order_created_at
    status = get_last_order_status(order_id)
    assert status['state'] == 'waiting_confirmation'
    assert status['author_id'] == customer_id
    assert status['comment'] == comment
    assert status['created_at'] > order_created_at


async def test_prolongate_confirmation_no_customer_id_400(
        taxi_eats_picker_orders,
):
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status/prolongate-confirmation',
        params={'eats_id': '123'},
        json={'eats_id': '123'},
    )
    assert response.status_code == 400


async def test_prolongate_confirmation_order_not_found_404(
        taxi_eats_picker_orders,
):
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status/prolongate-confirmation',
        params={'eats_id': '123'},
        json={'eats_id': '123', 'customer_id': 'customer_id'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('status', ['new', 'picking', 'confirmed'])
async def test_prolongate_confirmation_wrong_status_409(
        taxi_eats_picker_orders, create_order, status,
):
    create_order(eats_id='123', picker_id='1122', state=status)
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/status/prolongate-confirmation',
        params={'eats_id': '123'},
        json={'eats_id': '123', 'customer_id': 'customer_id'},
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'wrong_order_state'
