import pytest

from . import utils


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize('request_version', [None, 0])
@pytest.mark.parametrize(
    'customer_id, author_type, expected_author_type',
    [[None, 'system', 'system'], ['1122', 'customer', 'customer']],
)
@pytest.mark.parametrize('reason', [None, 'delete-reason'])
@pytest.mark.parametrize('require_approval', [None, False, True])
@utils.send_order_events_config()
async def test_remove_items_200(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        require_approval,
        customer_id,
        author_type,
        expected_author_type,
        reason,
        request_version,
        measure_version,
        mock_processing,
):
    payment_limit = 1000
    eats_id = '123'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id='1122',
        payment_limit=payment_limit,
        require_approval=require_approval,
        last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        quantity=1,
        price=11,
        version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item-2',
        quantity=2,
        price=12,
        version=0,
    )

    # новые поля не соответствуют старым, чтобы можно было увидеть разный
    # результат вычислений
    create_order_item(
        order_id=order_id,
        eats_item_id='item-3',
        quantity=3,
        price=13,
        version=0,
        measure_value=1000,
        measure_quantum=500,
        quantum_quantity=10,
        quantum_price=2,
        absolute_quantity=5000,
    )
    params = {'eats_id': eats_id, 'author_type': author_type}
    if request_version:
        params['version'] = request_version
    headers = {}
    if measure_version:
        headers['X-Measure-Version'] = measure_version
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        headers=headers,
        params=params,
        json={
            'item_ids': ['item-2', 'item-3'],
            'reason': reason,
            'customer_id': customer_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 1
    assert get_order(order_id)['last_version'] == 1
    items = get_order_items(order_id=order_id, version=1)
    assert len(items) == 1
    assert items[0]['eats_item_id'] == 'item-1'
    assert items[0]['author'] == customer_id
    assert items[0]['author_type'] == expected_author_type
    original_items = get_order_items(order_id=order_id, version=0)
    assert len(original_items) == 3
    for item in original_items:
        if item['eats_item_id'] != 'item-1':
            assert item['reason'] == reason
            assert item['is_deleted_by'] == customer_id
            assert item['deleted_by_type'] == expected_author_type

    assert mock_processing.times_called == 1


async def test_remove_items_204(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
):
    eats_id = '123'
    order_id = create_order(state='assigned', eats_id=eats_id, last_version=0)
    create_order_item(order_id=order_id, eats_item_id='item-1', version=0)
    create_order_item(order_id=order_id, eats_item_id='item-2', version=0)
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={'item_ids': ['item-3']},
    )
    assert response.status_code == 204
    assert get_order(order_id)['last_version'] == 0


async def test_remove_items_too_many_removals_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    order_id = create_order(state='assigned', eats_id=eats_id)
    create_order_item(order_id=order_id, eats_item_id='item-1')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={'item_ids': ['item-1']},
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'too_many_removals'


async def test_remove_items_no_author_type_400(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
):
    eats_id = '123'
    order_id = create_order(state='assigned', eats_id=eats_id)
    create_order_item(order_id=order_id, eats_item_id='item-1')
    create_order_item(order_id=order_id, eats_item_id='item-2')
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={'eats_id': eats_id},
        json={'item_ids': ['item-1']},
    )
    assert response.status_code == 400


async def test_remove_items_404(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={'eats_id': '123', 'author_type': 'customer'},
        json={'item_ids': ['item-1']},
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found'


@pytest.mark.parametrize(
    'request_version, expected_status, expected_code',
    [[0, 204, None], [2, 409, 'order_version_mismatch']],
)
async def test_remove_items_order_version(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        request_version,
        expected_status,
        expected_code,
):
    eats_id = '123'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id='1122', last_version=1,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1', version=0)
    create_order_item(order_id=order_id, eats_item_id='item-2', version=0)
    create_order_item(order_id=order_id, eats_item_id='item-1', version=1)
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={
            'eats_id': eats_id,
            'version': request_version,
            'author_type': 'customer',
        },
        json={'item_ids': ['item-2']},
    )
    assert response.status_code == expected_status
    if expected_code:
        assert response.json().get('code') == expected_code


@pytest.mark.parametrize(
    'author, author_type, expected_status',
    [
        ['someone', None, 400],
        ['customer', 'customer', 400],
        [None, 'system', 400],
        ['1122', 'system', 400],
        ['1122', 'picker', 400],
        ['another_picker', 'system', 200],
        ['another_picker', 'picker', 200],
    ],
)
@utils.send_order_events_config()
async def test_remove_items_version_author(
        taxi_eats_picker_orders,
        init_measure_units,
        init_currencies,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        author,
        author_type,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=1,
    )
    create_order_item(order_id=order_id, eats_item_id='item-1', version=0)
    create_order_item(order_id=order_id, eats_item_id='item-2', version=0)
    create_order_item(
        order_id=order_id,
        eats_item_id='item-1',
        version=1,
        author=author,
        author_type=author_type,
    )
    response = await taxi_eats_picker_orders.post(
        '/api/v1/order/delete-items',
        params={'eats_id': eats_id, 'author_type': 'customer'},
        json={'item_ids': ['item-1']},
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert get_order(order_id)['last_version'] == 2
        order_items = get_order_items(order_id=order_id, version=2)
        assert len(order_items) == 1
        assert order_items[0]['eats_item_id'] == 'item-2'
        assert mock_processing.times_called == 1
    else:
        assert mock_processing.times_called == 0
