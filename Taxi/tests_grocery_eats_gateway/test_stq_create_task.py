import pytest

from tests_grocery_eats_gateway import headers


async def test_new_order(taxi_grocery_eats_gateway, stq, load_json):
    request = load_json('request_from_processing.json')
    response = await taxi_grocery_eats_gateway.post(
        path='/orders/v1/tracking/stq/order?order_id=123456-grocery',
        json=request,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    queue = stq.eats_orders_tracking_orders
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == '123456-grocery.4.42'
    assert task['kwargs']['order'] == load_json(
        'expected_stq_orders_task_kwarg_order.json',
    )


async def test_new_courier(taxi_grocery_eats_gateway, stq, load_json):
    request = {
        'suffix_stq_task_id': '42',
        'courier_name': 'courier name',
        'transport_type': 'car',
        'eats_courier_id': '123456',
        'claim_id': 'claim_id_123',
        'personal_phone_id': 'phone_id_123',
    }

    response = await taxi_grocery_eats_gateway.post(
        path='/orders/v1/tracking/stq/courier?order_id=123456-grocery',
        json=request,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    queue = stq.eats_orders_tracking_couriers
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == '123456-grocery.123456.42'
    assert task['kwargs']['courier'] == {
        'courier_id': '123456',
        'name': 'courier name',
        'type': 'vehicle',
        'courier_is_hard_of_hearing': False,
        'order_nr': '123456-grocery',
        'claim_alias': 'grocery_ru',
        'claim_id': 'claim_id_123',
        'personal_phone_id': 'phone_id_123',
    }


@pytest.mark.parametrize(
    'status, dispatch_cargo_status, is_hold_money_finished,' 'eats_status',
    [
        ('checked_out', 'new', False, '8'),
        ('reserving', 'new', False, '8'),
        ('delivering', 'performer_lookup', True, '3'),
        ('delivering', 'pickuped', True, '9'),
        ('delivering', 'delivery_arrived', True, '6'),
    ],
)
async def test_status_match(
        taxi_grocery_eats_gateway,
        stq,
        load_json,
        status,
        dispatch_cargo_status,
        is_hold_money_finished,
        eats_status,
):
    request = load_json('request_from_processing.json')
    request['status'] = status
    request['dispatch_cargo_status'] = dispatch_cargo_status
    request['is_hold_money_finished'] = is_hold_money_finished
    response = await taxi_grocery_eats_gateway.post(
        path='/orders/v1/tracking/stq/order?order_id=123456-grocery',
        json=request,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    queue = stq.eats_orders_tracking_orders
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['kwargs']['order']['status'] == eats_status
    assert task['kwargs']['order']['created_at'] != request['created']
    assert task['kwargs']['order']['created_at'] == request['created'].replace(
        '.00', '',
    )


GROCERY_NEW_CORP_ENABLED = pytest.mark.experiments3(
    name='grocery_eats_gateway_new_corp',
    consumers=['grocery-eats-gateway/new-corp'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'corp_id': 'grocery_product_delivery'},
        },
    ],
    default_value={'corp_id': 'grocery_ru'},
    is_config=True,
)


@GROCERY_NEW_CORP_ENABLED
async def test_new_courier_new_corp(taxi_grocery_eats_gateway, stq, load_json):
    request = {
        'suffix_stq_task_id': '42',
        'courier_name': 'courier name',
        'transport_type': 'car',
        'eats_courier_id': '123456',
        'claim_id': 'claim_id_123',
        'personal_phone_id': 'phone_id_123',
    }

    response = await taxi_grocery_eats_gateway.post(
        path='/orders/v1/tracking/stq/courier?order_id=123456-grocery',
        json=request,
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status_code == 200
    queue = stq.eats_orders_tracking_couriers
    assert queue.times_called == 1
    task = queue.next_call()
    assert task['id'] == '123456-grocery.123456.42'
    assert task['kwargs']['courier'] == {
        'courier_id': '123456',
        'name': 'courier name',
        'type': 'vehicle',
        'courier_is_hard_of_hearing': False,
        'order_nr': '123456-grocery',
        'claim_alias': 'grocery_product_delivery',
        'claim_id': 'claim_id_123',
        'personal_phone_id': 'phone_id_123',
    }
