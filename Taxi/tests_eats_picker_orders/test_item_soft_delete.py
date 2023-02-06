from typing import Optional

import pytest

from . import utils


async def soft_delete_request(
        taxi_eats_picker_orders,
        eats_id: str,
        picker_id: str,
        order_item_id: str,
):
    headers = utils.da_headers(picker_id)
    body = {'order_item_id': order_item_id}
    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/soft-delete',
        params=params,
        headers=headers,
        json=body,
    )
    return response


async def revert_soft_delete_request(
        taxi_eats_picker_orders,
        eats_id: str,
        picker_id: str,
        order_item_id: str,
        measure_version: Optional[str],
):
    headers = utils.da_headers(picker_id)
    if measure_version:
        headers['X-Measure-Version'] = measure_version
    body = {'order_item_id': order_item_id}
    params = {'eats_id': eats_id}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/revert-soft-delete',
        params=params,
        headers=headers,
        json=body,
    )
    return response


def assert_deleted(response, order, items, deleted_by_map, version):
    assert response.status_code == 200
    assert response.json()['order_version'] == version
    assert order['last_version'] == version
    assert len(items) == len(deleted_by_map)

    for item in items:
        deleted_by = deleted_by_map[item['eats_item_id']]
        if deleted_by:
            assert item['is_deleted_by'] == deleted_by['id']
            assert item['deleted_by_type'] == deleted_by['type']
            assert item['reason'] == 'soft-delete'
        else:
            assert item['is_deleted_by'] is None
            assert item['deleted_by_type'] is None
            assert item['reason'] is None


def check_operation_context(items, author, author_type):
    for item in items:
        assert item['author'] == author
        assert item['author_type'] == author_type


async def get_order_request(
        taxi_eats_picker_orders, eats_id: str, picker_id: str, version: int,
):
    headers = utils.da_headers(picker_id)
    params = {'eats_id': eats_id, 'version': version}
    response = await taxi_eats_picker_orders.get(
        '4.0/eats-picker/api/v1/order', params=params, headers=headers,
    )
    return response


@utils.send_order_events_config()
async def test_item_soft_delete_200(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        is_deleted_by='unknown_picker',
        version=0,
    )
    create_order_item(order_id=order_id, eats_item_id='2', version=0)

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1',
    )
    order = get_order(order_id)
    items = get_order_items(order_id=order_id, version=1)
    assert_deleted(
        response,
        order,
        items,
        {'1': {'id': picker_id, 'type': 'picker'}, '2': None},
        1,
    )
    check_operation_context(items, picker_id, 'picker')

    assert mock_processing.times_called == 1

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '2',
    )
    order = get_order(order_id)
    items = get_order_items(order_id=order_id, version=2)
    assert_deleted(
        response,
        order,
        items,
        {
            '1': {'id': picker_id, 'type': 'picker'},
            '2': {'id': picker_id, 'type': 'picker'},
        },
        2,
    )
    check_operation_context(items, picker_id, 'picker')

    assert mock_processing.times_called == 2


@pytest.mark.parametrize(
    'author, author_type, expected_status',
    [
        ['someone', None, 200],
        ['customer', 'customer', 200],
        [None, 'system', 200],
        ['1122', 'system', 200],
        ['1122', 'picker', 200],
        ['another_picker', 'system', 404],
        ['another_picker', 'picker', 404],
    ],
)
@utils.send_order_events_config()
async def test_item_soft_delete_version_author(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        author,
        author_type,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        version=0,
        author=author,
        author_type=author_type,
    )

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1',
    )
    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


async def test_item_soft_delete_404_item_not_found(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(order_id=order_id, eats_item_id='1', version=0)
    create_order_item(order_id=order_id, eats_item_id='2', version=0)

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '3',
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'ORDER_ITEM_NOT_FOUND'


async def test_item_soft_delete_404_wrong_picker(
        taxi_eats_picker_orders, init_measure_units, create_order,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, 'unknown_picker', '3',
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found_for_picker'


@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, expected_status',
    [
        ['1122', None, 202],
        ['system', None, 202],
        ['1122', 'system', 202],
        [None, 'system', 202],
        # системные удаления распространяются на всех сборщиков,
        # если они были 'закреплены' версией покупателя
        ['another_picker', 'system', 202],
        ['customer', 'customer', 202],
        ['another_picker', 'picker', 200],
    ],
)
@utils.send_order_events_config()
async def test_item_soft_delete_202_already_deleted(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        is_deleted_by,
        deleted_by_type,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        version=0,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        reason='soft-delete',
    )

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1',
    )
    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@utils.send_order_events_config()
async def test_item_soft_delete_200_and_get_order(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(order_id=order_id, eats_item_id='1', version=0)
    create_order_item(order_id=order_id, eats_item_id='2', version=0)

    async def assert_order(version, deleted_map):
        response = await get_order_request(
            taxi_eats_picker_orders, eats_id, picker_id, version,
        )
        picker_items = response.json()['payload']['picker_items']
        for item in picker_items:
            assert item['soft_deleted'] == deleted_map[item['id']]

    await assert_order(0, {'1': False, '2': False})

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1',
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 1

    await assert_order(0, {'1': False, '2': False})
    await assert_order(1, {'1': True, '2': False})

    assert mock_processing.times_called == 1

    response = await soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '2',
    )
    assert response.status_code == 200
    assert response.json()['order_version'] == 2

    await assert_order(0, {'1': False, '2': False})
    await assert_order(1, {'1': True, '2': False})
    await assert_order(2, {'1': True, '2': True})

    assert mock_processing.times_called == 2


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
async def test_item_revert_soft_delete_200(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        measure_version,
        is_deleted_by,
        deleted_by_type,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=1,
    )
    create_order_item(order_id=order_id, eats_item_id='1', version=0)
    create_order_item(order_id=order_id, eats_item_id='2', version=0)
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        reason='soft-delete',
        version=1,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='2',
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        reason='soft-delete',
        version=1,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1', measure_version,
    )
    expected_version = 2
    order = get_order(order_id)
    items = get_order_items(order_id=order_id, version=expected_version)
    assert_deleted(
        response,
        order,
        items,
        {'1': None, '2': {'id': is_deleted_by, 'type': deleted_by_type}},
        expected_version,
    )
    check_operation_context(items, picker_id, 'picker')

    assert mock_processing.times_called == 1

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '2', measure_version,
    )
    expected_version = 3
    order = get_order(order_id)
    items = get_order_items(order_id=order_id, version=expected_version)
    assert_deleted(
        response, order, items, {'1': None, '2': None}, expected_version,
    )
    check_operation_context(items, picker_id, 'picker')

    assert mock_processing.times_called == 2


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'author, author_type, expected_status',
    [
        ['someone', None, 200],
        ['customer', 'customer', 200],
        [None, 'system', 200],
        ['1122', 'system', 200],
        ['1122', 'picker', 200],
        ['another_picker', 'system', 404],
        ['another_picker', 'picker', 404],
    ],
)
@utils.send_order_events_config()
async def test_item_revert_soft_delete_version_author(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        author,
        author_type,
        expected_status,
        measure_version,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        is_deleted_by=picker_id,
        deleted_by_type='picker',
        version=0,
        author=author,
        author_type=author_type,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1', measure_version,
    )
    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_item_revert_soft_delete_404_item_not_found(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        is_deleted_by=picker_id,
        reason='soft-delete',
        version=0,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '2', measure_version,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'ORDER_ITEM_NOT_FOUND'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_item_revert_soft_delete_404_wrong_picker(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        measure_version,
):
    eats_id = '123'
    picker_id = '1122'
    create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    response = await revert_soft_delete_request(
        taxi_eats_picker_orders,
        eats_id,
        'unknown_picker',
        '2',
        measure_version,
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'order_not_found_for_picker'


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type, expected_status',
    [
        ['1122', None, 200],
        ['system', None, 200],
        ['1122', 'system', 200],
        [None, 'system', 200],
        # системные удаления распространяются на всех сборщиков,
        # если они были 'закреплены' версией покупателя
        ['another_picker', 'system', 200],
        ['customer', 'customer', 200],
        ['another_picker', 'picker', 202],
        [None, None, 202],
    ],
)
@utils.send_order_events_config()
async def test_item_revert_soft_delete_202_not_deleted_or_wrong_picker(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        measure_version,
        is_deleted_by,
        deleted_by_type,
        expected_status,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned', eats_id=eats_id, picker_id=picker_id, last_version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        reason='soft-delete',
        version=0,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1', measure_version,
    )
    assert response.status_code == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
@pytest.mark.parametrize(
    'price, status_code', [(10, 200), (20, 200), (30, 402)],
)
@pytest.mark.parametrize('is_deleted_by', ['1122', 'system'])
@utils.send_order_events_config()
async def test_item_revert_soft_delete_402_limit_exceeded(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        price,
        status_code,
        measure_version,
        is_deleted_by,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=0,
        payment_limit=20,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        price=price,
        is_deleted_by=is_deleted_by,
        reason='soft-delete',
        version=0,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1', measure_version,
    )
    assert response.status_code == status_code
    if status_code == 402:
        assert response.json()['details']['limit_overrun'] == '10.00'

    assert mock_processing.times_called == (1 if status_code == 200 else 0)


@pytest.mark.parametrize(
    'measure_version, quantum_price, status_code',
    [[None, 1000, 200], ['1', 1000, 200], ['2', 20, 200], ['2', 21, 402]],
)
@pytest.mark.parametrize('is_deleted_by', ['1122', 'system'])
@utils.send_order_events_config()
async def test_item_revert_soft_delete_402_limit_exceeded_measure_v2(
        taxi_eats_picker_orders,
        init_measure_units,
        create_order,
        create_order_item,
        measure_version,
        quantum_price,
        status_code,
        is_deleted_by,
        mock_processing,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=0,
        payment_limit=20,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='1',
        measure_value=1000,
        measure_quantum=1000,
        quantity=1,
        quantum_quantity=1,
        price=10,
        quantum_price=quantum_price,
        is_deleted_by=is_deleted_by,
        reason='soft-delete',
        version=0,
    )

    response = await revert_soft_delete_request(
        taxi_eats_picker_orders, eats_id, picker_id, '1', measure_version,
    )
    assert response.status_code == status_code
    if status_code == 402:
        assert response.json()['details']['limit_overrun'] == '1.00'

    assert mock_processing.times_called == (1 if status_code == 200 else 0)


async def test_revert_soft_delete_400(taxi_eats_picker_orders):
    body = {'order_item_id': '1'}
    params = {'eeets_id': '123'}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/revert-soft-delete',
        params=params,
        json=body,
        headers=utils.da_headers('1'),
    )
    assert response.status_code == 400


async def test_revert_soft_delete_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    body = {'order_item_id': '1'}
    params = {'eats_id': '123'}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/revert-soft-delete',
        params=params,
        json=body,
        headers=bad_header,
    )
    assert response.status_code == 401


async def test_soft_delete_400(taxi_eats_picker_orders):
    body = {'order_item_id': '1'}
    params = {'eeeets_id': '123'}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/soft-delete',
        params=params,
        json=body,
        headers=utils.da_headers('1'),
    )
    assert response.status_code == 400


async def test_soft_delete_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    body = {'order_item_id': '1'}
    params = {'eats_id': '123'}
    response = await taxi_eats_picker_orders.post(
        '4.0/eats-picker/api/v1/item/soft-delete',
        params=params,
        json=body,
        headers=bad_header,
    )
    assert response.status_code == 401
