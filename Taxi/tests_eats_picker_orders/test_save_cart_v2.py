import pytest

from . import utils


async def test_save_cart_order_not_found_404(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=125',
        json={
            'cart_version': 1,
            'picker_items': [{'id': '1', 'count': 1, 'weight': None}],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 404
    assert response.json()['code'] == 'order_not_found_for_picker'


async def test_save_cart_by_wrong_picker_404(
        create_order, taxi_eats_picker_orders,
):
    create_order(state='picking', eats_id='123', picker_id='1')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 1,
            'picker_items': [{'id': '1', 'count': 1, 'weight': None}],
        },
        headers=utils.da_headers('42'),
    )
    assert response.status == 404
    assert response.json()['code'] == 'order_not_found_for_picker'


@pytest.mark.parametrize('status', ('picking', 'picked_up'))
@utils.send_order_events_config()
async def test_save_cart_success_200(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        get_picked_items,
        get_picked_item_positions,
        status,
        mock_processing,
):
    order_id = create_order(state=status, eats_id='123', picker_id='1122')

    order_item_ids = []
    order_item_ids.append(
        create_order_item(order_id=order_id, eats_item_id='item-1'),
    )
    order_item_ids.append(
        create_order_item(order_id=order_id, eats_item_id='item-2'),
    )
    order_item_ids.append(
        create_order_item(order_id=order_id, eats_item_id='item-3'),
    )
    order_item_ids.append(
        create_order_item(order_id=order_id, eats_item_id='item-4'),
    )

    picker_items = [
        {
            'id': 'item-1',
            'count': 42,
            'weight': None,
            'positions': [
                {'barcode': 'barcode_1', 'count': 42, 'weight': None},
            ],
        },
        {
            'id': 'item-2',
            'count': 21,
            'weight': None,
            'positions': [
                {
                    'barcode': 'barcode_2',
                    'count': 15,
                    'weight': None,
                    'mark': 'mark_2',
                },
            ],
        },
        {
            'id': 'item-3',
            'count': None,
            'weight': 200,
            'positions': [
                {
                    'barcode': 'barcode_3_1',
                    'count': None,
                    'weight': 50,
                    'mark': 'mark_3_1',
                },
                {
                    'barcode': 'barcode_3_2',
                    'count': None,
                    'weight': 150,
                    'mark': 'mark_3_2',
                },
            ],
        },
        # все проверки будут выполняться в конце сборки
        {
            'id': 'item-4',
            'count': 42,
            'weight': None,
            'positions': [{'count': None, 'weight': 500}],
        },
    ]

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={'cart_version': 0, 'picker_items': picker_items},
        headers=utils.da_headers('1122'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    for i, order_item_id in enumerate(order_item_ids):
        picked_items = get_picked_items(order_item_id)
        assert len(picked_items) == 1
        utils.check_picked_item(
            picked_items[0],
            get_picked_item_positions(picked_items[0]['id']),
            dict(
                **picker_items[i],
                cart_version=1,
                order_item_id=order_item_id,
                picker_id='1122',
            ),
        )


@utils.send_order_events_config()
async def test_save_cart_with_multiple_items_success_200(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        get_picked_items,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    order_item_ids = tuple(
        create_order_item(order_id=order_id, eats_item_id=str(i))
        for i in range(3)
    )
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [
                {'id': str(i), 'count': 42, 'weight': None} for i in range(3)
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    picked_items = get_picked_items(order_item_ids=order_item_ids)
    assert len(picked_items) == 3
    assert tuple(item['id'] for item in picked_items) == order_item_ids


@pytest.mark.parametrize(
    'status', ('assigned', 'paid', 'cancelled', 'complete'),
)
async def test_error_saving_cart_on_wrong_order_status_409(
        create_order, create_order_item, taxi_eats_picker_orders, status,
):
    order_id = create_order(state=status, eats_id='123', picker_id='1')
    create_order_item(order_id=order_id, eats_item_id='item-1')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [{'id': 'item-1', 'count': 42, 'weight': None}],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 409
    assert response.json()['code'] == 'WRONG_ORDER_STATE'


@utils.send_order_events_config()
async def test_change_order_status_on_success_200(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        get_order,
        get_last_order_status,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    create_order_item(order_id=order_id, eats_item_id='item-1')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [{'id': 'item-1', 'count': 42, 'weight': None}],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200

    assert mock_processing.times_called == 1

    order = get_order(order_id)
    assert order['state'] == 'picking'

    order_status = get_last_order_status(order_id)
    assert order_status['state'] == 'picking'


@utils.send_order_events_config()
async def test_version_mismatch_with_same_cart_409(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    create_order_item(order_id=order_id, eats_item_id='item-1')
    create_order_item(order_id=order_id, eats_item_id='item-2')

    async def send_cart(cart_version, picked_items):
        return await taxi_eats_picker_orders.post(
            '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
            json={'cart_version': cart_version, 'picker_items': picked_items},
            headers=utils.da_headers('1'),
        )

    cart_one = [{'id': 'item-1', 'count': 42, 'weight': None}]
    cart_two = cart_one + [{'id': 'item-2', 'count': None, 'weight': 100}]

    response = await send_cart(cart_version=0, picked_items=cart_one)
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    response = await send_cart(cart_version=1, picked_items=cart_two)
    assert response.status == 200
    assert response.json()['cart_version'] == 2

    assert mock_processing.times_called == 2

    response = await send_cart(cart_version=0, picked_items=cart_one)
    assert response.status == 409
    assert response.json()['code'] == 'CART_VERSION_OUTDATED'
    assert response.json()['details']['current_cart_version'] == 2

    assert mock_processing.times_called == 2


@pytest.mark.parametrize('count,weight', [(None, None), (1, 1)])
async def test_forbid_saving_item_without_one_of_count_or_weight_400(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        count,
        weight,
):
    eats_id = '123'
    picker_id = '1122'
    order_id = create_order(eats_id=eats_id, picker_id=picker_id)
    create_order_item(order_id=order_id, eats_item_id='item-1')
    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 0,
            'picker_items': [
                {'id': 'item-1', 'count': count, 'weight': weight},
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 400
    assert response.json()['code'] == 'INCONSISTENT_CART_ITEM'


async def test_error_saving_empty_cart(create_order, taxi_eats_picker_orders):
    create_order(eats_id='125', state='picking', picker_id='12')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=125',
        json={'cart_version': 0, 'picker_items': []},
        headers=utils.da_headers('12'),
    )
    assert response.status == 400


@utils.send_order_events_config()
async def test_save_cart_no_new_version_if_cart_doesnt_change(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        mock_processing,
):
    order_id = create_order(
        eats_id='201125-111111', state='picking', picker_id='25',
    )
    create_order_item(order_id=order_id, eats_item_id='item-1')
    create_order_item(order_id=order_id, eats_item_id='item-2')

    async def send_cart(cart_version):
        return await taxi_eats_picker_orders.post(
            '/4.0/eats-picker/api/v2/order/cart?eats_id=201125-111111',
            json={
                'cart_version': cart_version,
                'picker_items': [
                    {
                        'id': 'item-1',
                        'count': 200,
                        'weight': None,
                        'positions': [
                            {
                                'count': 5,
                                'weight': None,
                                'barcode': 'barcode1',
                                'mark': 'mark1',
                            },
                        ],
                    },
                    {'id': 'item-2', 'count': 100, 'weight': None},
                ],
            },
            headers=utils.da_headers('25'),
        )

    response = await send_cart(cart_version=0)
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    response = await send_cart(cart_version=1)
    assert response.status == 202
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1


@utils.send_order_events_config()
async def test_same_cart_in_different_order(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    for i in range(4):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [
                {
                    'id': '1',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {'count': 20, 'weight': None, 'barcode': 'barcode1'},
                        {'count': 22, 'weight': None, 'barcode': 'barcode2'},
                    ],
                },
                {
                    'id': '3',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {'count': 20, 'weight': None, 'barcode': 'barcode3'},
                        {'count': 22, 'weight': None, 'barcode': 'barcode4'},
                    ],
                },
                {'id': '2', 'count': 42, 'weight': None},
                {'id': '0', 'count': 42, 'weight': None},
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 1,
            'picker_items': [
                {'id': '0', 'count': 42, 'weight': None},
                {'id': '2', 'count': 42, 'weight': None},
                {
                    'id': '1',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {'count': 20, 'weight': None, 'barcode': 'barcode1'},
                        {'count': 22, 'weight': None, 'barcode': 'barcode2'},
                    ],
                },
                {
                    'id': '3',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {'count': 20, 'weight': None, 'barcode': 'barcode3'},
                        {'count': 22, 'weight': None, 'barcode': 'barcode4'},
                    ],
                },
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 202
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1


@utils.send_order_events_config()
async def test_same_cart_different_positions_200(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    for i in range(4):
        create_order_item(order_id=order_id, eats_item_id=str(i))

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [
                {
                    'id': '1',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {'count': 20, 'weight': None, 'barcode': 'barcode1'},
                        {'count': 22, 'weight': None, 'barcode': 'barcode2'},
                    ],
                },
                {'id': '3', 'count': 42, 'weight': None},
                {'id': '2', 'count': 42, 'weight': None},
                {'id': '0', 'count': 42, 'weight': None},
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 1,
            'picker_items': [
                {
                    'id': '1',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {
                            'count': 20,
                            'weight': None,
                            'barcode': 'barcode1',
                            'mark': 'mark1',
                        },
                        {
                            'count': 22,
                            'weight': None,
                            'barcode': 'barcode2',
                            'mark': 'mark1',
                        },
                    ],
                },
                {'id': '3', 'count': 42, 'weight': None},
                {'id': '2', 'count': 42, 'weight': None},
                {'id': '0', 'count': 42, 'weight': None},
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 2

    assert mock_processing.times_called == 2


@utils.send_order_events_config()
async def test_positions_data_matrix_formatting_200(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        get_picked_items,
        get_picked_item_positions,
        mock_processing,
):
    order_id = create_order(state='picking', eats_id='123', picker_id='1')
    order_item_id = create_order_item(order_id=order_id, eats_item_id='item-0')

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
        json={
            'cart_version': 0,
            'picker_items': [
                {
                    'id': 'item-0',
                    'count': 42,
                    'weight': None,
                    'positions': [
                        {
                            'count': 20,
                            'weight': None,
                            'barcode': 'barcode1',
                            'mark': '  m a r k  0',
                        },
                        {
                            'count': 21,
                            'weight': None,
                            'barcode': 'barcode2',
                            'mark': (
                                chr(29) + 'ma' + chr(29) + 'rk' + chr(29) + '1'
                            ),
                        },
                    ],
                },
            ],
        },
        headers=utils.da_headers('1'),
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    picked_items = get_picked_items(order_item_id)
    assert len(picked_items) == 1
    positions = get_picked_item_positions(picked_items[0]['id'])
    assert positions[0]['mark'] == 'mark0'
    assert positions[1]['mark'] == 'mark1'


@utils.send_order_events_config()
async def test_allow_any_greater_version(
        create_order,
        create_order_item,
        taxi_eats_picker_orders,
        mock_processing,
):
    order_id = create_order(eats_id='123', picker_id='1122', state='picking')
    create_order_item(order_id=order_id, eats_item_id='item-1')
    create_order_item(order_id=order_id, eats_item_id='item-2')

    async def send_cart(cart_version, picked_items):
        return await taxi_eats_picker_orders.post(
            '/4.0/eats-picker/api/v2/order/cart?eats_id=123',
            json={'cart_version': cart_version, 'picker_items': picked_items},
            headers=utils.da_headers('1122'),
        )

    response = await send_cart(
        cart_version=0,
        picked_items=[{'id': 'item-1', 'count': 42, 'weight': None}],
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 1

    assert mock_processing.times_called == 1

    response = await send_cart(
        cart_version=10,
        picked_items=[{'id': 'item-2', 'count': 42, 'weight': None}],
    )
    assert response.status == 200
    assert response.json()['cart_version'] == 11

    assert mock_processing.times_called == 2


@pytest.mark.parametrize(
    'is_deleted_by, deleted_by_type',
    [
        ['picker_id', 'picker'],
        ['picker_id', None],
        ['system', 'system'],
        ['system', None],
        ['customer_id', 'customer'],
    ],
)
async def test_cart_items_mismatch_410(
        taxi_eats_picker_orders,
        create_order,
        create_order_item,
        is_deleted_by,
        deleted_by_type,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state='picking',
    )
    create_order_item(
        order_id=order_id, eats_item_id='item_0', version=0, name='name_0_v0',
    )
    create_order_item(
        order_id=order_id, eats_item_id='item_1', version=0, name='name_1_v0',
    )
    create_order_item(
        order_id=order_id, eats_item_id='item_0', version=1, name='name_0_v1',
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item_1',
        version=1,
        is_deleted_by=is_deleted_by,
        deleted_by_type=deleted_by_type,
        name='name_1_v1',
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='item_3',
        version=1,
        is_deleted_by='another_picker',
        name='name_3_v0',
    )
    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 0,
            'picker_items': [
                {'id': 'item_0', 'count': 1},
                {'id': 'item_1', 'count': 1},
                {'id': 'item_2', 'count': 1},
                {'id': 'item_3', 'count': 1},
            ],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 410
    response = response.json()
    assert response['code'] == 'CART_ITEMS_MISMATCH'
    assert response['details']['items_mismatch'] == ['item_1', 'item_2']
    assert (
        response['message'].split(': ', 1)[1]
        == 'name_1_v1 (item_1), Неизвестный товар (item_2)'
    )


@pytest.mark.parametrize(
    'author, author_type, expected_status',
    [
        ['someone', None, 200],
        ['customer', 'customer', 200],
        [None, 'system', 200],
        ['picker_id', 'system', 200],
        ['picker_id', 'picker', 200],
        ['another_picker', 'system', 410],
        ['another_picker', 'picker', 410],
    ],
)
@utils.send_order_events_config()
async def test_save_cart_version_author(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        create_order_item,
        author,
        author_type,
        expected_status,
        mock_processing,
):
    eats_id = 'eats_id'
    picker_id = 'picker_id'
    order_id = create_order(
        eats_id=eats_id, picker_id=picker_id, state='picking',
    )
    create_order_item(
        order_id=order_id, eats_item_id='deleted_item', version=0,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id='added_item',
        version=1,
        author=author,
        author_type=author_type,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return {'order_id': eats_id}

    response = await taxi_eats_picker_orders.post(
        f'/4.0/eats-picker/api/v2/order/cart?eats_id={eats_id}',
        json={
            'cart_version': 0,
            'picker_items': [{'id': 'added_item', 'count': 1}],
        },
        headers=utils.da_headers(picker_id),
    )
    assert response.status == expected_status

    assert mock_processing.times_called == (1 if expected_status == 200 else 0)
