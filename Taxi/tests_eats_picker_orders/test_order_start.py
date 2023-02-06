import copy
import datetime

import pytest

from . import utils


# pylint: disable=too-many-lines


CARGO_INFO_MOCK_RESPONSE = {
    'id': 'CLAIM_ID_20',
    'items': [
        {
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Плюмбус',
            'cost_value': '2.00',
            'cost_currency': 'RUB',
            'quantity': 1,
        },
    ],
    'route_points': [
        {
            'visit_order': 1,
            'id': 6987,
            'contact': {'name': 'Точкович', 'phone': '+7100'},
            'address': {
                'fullname': (
                    'Москва, Садовническая набережная, 82с2, БЦ Аврора'
                ),
                'coordinates': [0.00, 0.00],
            },
            'type': 'source',
            'visit_status': 'visited',
        },
        {
            'visit_order': 2,
            'id': 9999,
            'contact': {'name': 'Точкович', 'phone': '+7101'},
            'address': {
                'fullname': 'Санкт-Петербург, Большая Монетная улица, 1к1А',
                'coordinates': [101.23, 22.22],
            },
            'type': 'destination',
            'visit_status': 'arrived',
        },
    ],
    'status': 'pickup_arrived',
    'version': 1,
    'revision': 1,
    'emergency_contact': {'name': 'name_emergency', 'phone': '+7123'},
    'created_ts': '2020-09-19T14:42:27.642389+00:00',
    'updated_ts': '2020-09-19T14:42:27.642389+00:00',
    'performer_info': {
        'courier_name': 'Иван Мирошников',
        'legal_name': 'ООО Столовая №10',
    },
}


CARGO_INFO_MOCK_404_RESPONSE = {
    'code': 'not_found',
    'message': 'Заявка не найдена',
}

SYSTEM = 'system'
OUT_OF_STOCK = 'out of stock'


@pytest.mark.parametrize(
    ['eats_id', 'picker_id'], [['12345', '1'], ['123', '11']],
)
async def test_not_found_order_404(
        taxi_eats_picker_orders, create_order, eats_id, picker_id,
):
    create_order(eats_id='123', picker_id='1', state='assigned')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 404

    payload = response.json()
    assert payload['code'] == 'order_not_found_for_picker'
    assert payload['message'] == 'Заказ не найден для этого сборщика'


@pytest.mark.parametrize(
    ['state'], [['new'], ['picked_up'], ['paid'], ['cancelled'], ['complete']],
)
async def test_start_order_from_incorrect_state_409(
        taxi_eats_picker_orders, create_order, state,
):
    create_order(state=state, eats_id='12345', picker_id='1')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 409

    payload = response.json()
    assert payload['code'] == '409'
    assert (
        payload['message'] == 'Сборка заказа не может быть начата,'
        ' т.к. заказ не назначен ни на одного сборщика'
    )


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize(
    'require_approval, brand_id, payment_limit',
    [
        (False, 111, 4500),
        (False, 333, 3300),
        (True, 111, 4500),
        (True, 333, 3300),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@pytest.mark.parametrize(
    'eats_products_called',
    [
        pytest.param(False),
        pytest.param(
            False,
            marks=[
                utils.update_prices_and_availability_experiment(False, False),
            ],
        ),
        pytest.param(
            True,
            marks=[
                utils.update_prices_and_availability_experiment(False, True),
            ],
        ),
        pytest.param(
            True,
            marks=[
                utils.update_prices_and_availability_experiment(True, False),
            ],
        ),
        pytest.param(
            True,
            marks=[
                utils.update_prices_and_availability_experiment(True, True),
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'zero_limit',
    [
        False,
        pytest.param(
            False, marks=[utils.zero_limit_on_picking_start_experiment(False)],
        ),
        pytest.param(
            True,
            marks=[utils.zero_limit_on_picking_start_experiment(enabled=True)],
        ),
    ],
)
@pytest.mark.parametrize('state', ['assigned', 'picking'])
@utils.send_order_events_config()
async def test_start_order_204(
        taxi_eats_picker_orders,
        require_approval,
        brand_id,
        payment_limit,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order_items,
        get_order_by_eats_id,
        get_last_order_status,
        stq,
        eats_products_called,
        zero_limit,
        state,
        mock_processing,
):
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state=state,
        eats_id=eats_id,
        picker_id=picker_id,
        require_approval=require_approval,
        payment_limit=0,
        payment_value=3000,
        brand_id=brand_id,
        place_id=222,
        picker_card_type='TinkoffBank',
        picker_card_value='test_cid_1',
    )

    weight_item_id = '1'
    not_weight_item_id = '2'

    create_order_item(
        order_id=order_id,
        eats_item_id=weight_item_id,
        sold_by_weight=True,
        quantity=1.5,
        price=10,
        measure_value=1000,
        measure_quantum=750,
        quantum_quantity=2,
        absolute_quantity=1500,
        quantum_price=7.5,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=not_weight_item_id,
        sold_by_weight=False,
        quantity=3,
        price=20,
        measure_value=0,
        measure_quantum=0,
        quantum_quantity=3,
        absolute_quantity=0,
        quantum_price=20,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json.get('amount') == (
            0 if zero_limit else payment_limit
        )
        assert request.json.get('order_id') == '12345'
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def _mock_b2b(request):
        assert request.query.get('claim_id') == 'CLAIM_ID_20'
        assert (
            request.headers['Authorization']
            == 'Bearer testsuite-api-cargo-token'
        )
        return mockserver.make_response(
            status=200, json=CARGO_INFO_MOCK_RESPONSE,
        )

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {
            'products': [
                {
                    'origin_id': weight_item_id,
                    'name': '',
                    'description': '',
                    'is_available': True,
                    'price': 7.5,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                    'measure': {'unit': 'GRM', 'value': 1000, 'quantum': 0.75},
                },
                {
                    'origin_id': not_weight_item_id,
                    'name': '',
                    'description': '',
                    'is_available': True,
                    'price': 20,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                },
            ],
            'categories': [],
        }

    original_items = {
        item['eats_item_id']: item for item in get_order_items(order_id, 0)
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    if state == 'assigned':
        assert mock_processing.times_called == 1

        order = get_order_by_eats_id(eats_id)
        assert order['state'] == 'picking'
        assert order['payment_limit'] == payment_limit

        last_order_status = get_last_order_status(order_id)
        assert last_order_status['author_id'] == picker_id

        assert stq.send_start_picking_billing_event.times_called == 1
        kwargs = stq.send_start_picking_billing_event.next_call()['kwargs']
        assert kwargs['start_picking_at'] == '2020-06-18T13:00:00'
        assert kwargs['picker_id'] == picker_id
        assert kwargs['eats_id'] == '12345'
        assert kwargs['order_id'] == 1

        assert order['last_version'] == 0
        assert _mock_eats_products.times_called == int(eats_products_called)
        updated_original_items = {
            item['eats_item_id']: item for item in get_order_items(order_id, 0)
        }
        assert updated_original_items == original_items
    elif state == 'picking':
        assert mock_processing.times_called == 0
        assert stq.send_start_picking_billing_event.times_called == 0
        assert _mock_eats_picker_payment.times_called == 0
        assert _mock_b2b.times_called == 0
        assert _mock_eats_products.times_called == 0


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize(
    'require_approval, brand_id, payment_limit',
    [
        (False, 111, 4500),
        (False, 333, 3300),
        (True, 111, 4500),
        (True, 333, 3300),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@pytest.mark.parametrize('update_prices', [False, True])
@pytest.mark.parametrize('update_availability', [False, True])
@utils.send_order_events_config()
async def test_start_order_prices_change_204(
        taxi_eats_picker_orders,
        require_approval,
        brand_id,
        payment_limit,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order_items,
        get_order_by_eats_id,
        get_last_order_status,
        stq,
        now,
        experiments3,
        update_prices,
        update_availability,
        mock_processing,
):
    experiments3.add_experiment3_from_marker(
        utils.update_prices_and_availability_experiment(
            update_prices=update_prices,
            update_availability=update_availability,
        ),
        None,
    )
    now = now.replace(tzinfo=datetime.timezone.utc)
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        require_approval=require_approval,
        payment_limit=0,
        payment_value=3000,
        brand_id=brand_id,
        place_id=222,
        picker_card_type='TinkoffBank',
        picker_card_value='test_cid_1',
    )

    weight_item_id = '1'
    not_weight_item_id = '2'

    create_order_item(
        order_id=order_id,
        eats_item_id=weight_item_id,
        sold_by_weight=True,
        quantity=1.5,
        price=10,
        measure_value=1000,
        measure_quantum=750,
        quantum_quantity=2,
        absolute_quantity=1500,
        quantum_price=7.5,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=not_weight_item_id,
        sold_by_weight=False,
        quantity=3,
        price=20,
        measure_value=0,
        measure_quantum=0,
        quantum_quantity=3,
        absolute_quantity=0,
        quantum_price=20,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json.get('amount') == payment_limit
        assert request.json.get('order_id') == '12345'
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def _mock_b2b(request):
        assert request.query.get('claim_id') == 'CLAIM_ID_20'
        assert (
            request.headers['Authorization']
            == 'Bearer testsuite-api-cargo-token'
        )
        return mockserver.make_response(
            status=200, json=CARGO_INFO_MOCK_RESPONSE,
        )

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {
            'products': [
                {
                    'origin_id': weight_item_id,
                    'name': '',
                    'description': '',
                    'is_available': True,
                    'price': 15,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                    'measure': {'unit': 'GRM', 'value': 1000, 'quantum': 0.75},
                },
                {
                    'origin_id': not_weight_item_id,
                    'name': '',
                    'description': '',
                    'is_available': True,
                    'price': 15,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                },
            ],
            'categories': [],
        }

    original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 0)
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id)
    assert order['state'] == 'picking'
    assert order['payment_limit'] == payment_limit

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['author_id'] == picker_id

    assert stq.send_start_picking_billing_event.times_called == 1
    kwargs = stq.send_start_picking_billing_event.next_call()['kwargs']
    assert kwargs['start_picking_at'] == '2020-06-18T13:00:00'
    assert kwargs['picker_id'] == picker_id
    assert kwargs['eats_id'] == '12345'
    assert kwargs['order_id'] == 1

    assert _mock_eats_products.times_called == int(
        update_prices or update_availability,
    )
    updated_original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 0)
    }
    expected_items = copy.deepcopy(original_items)
    assert expected_items == updated_original_items
    assert order['last_version'] == int(update_prices)
    if update_prices:
        new_items = {
            item['eats_item_id']: dict(item)
            for item in get_order_items(order_id, 1)
        }
        for item in expected_items.values():
            for key in 'created_at', 'updated_at', 'id', 'version':
                del item[key]
            item['author'] = picker_id
            item['author_type'] = SYSTEM
        expected_items[weight_item_id]['price'] = 20
        expected_items[weight_item_id]['quantum_price'] = 15
        expected_items[weight_item_id]['price_updated_at'] = now
        expected_items[not_weight_item_id]['price'] = 15
        expected_items[not_weight_item_id]['quantum_price'] = 15
        expected_items[not_weight_item_id]['price_updated_at'] = now
        for eats_item_id, item in new_items.items():
            utils.compare_db_with_expected_data(
                item, expected_items[eats_item_id],
            )


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize(
    'require_approval, brand_id, payment_limit',
    [
        (False, 111, 4500),
        (False, 333, 3300),
        (True, 111, 4500),
        (True, 333, 3300),
    ],
)
@utils.update_prices_and_availability_experiment(
    update_prices=True, update_availability=True,
)
@pytest.mark.parametrize(
    'author, author_type, expected_quantity',
    [
        ['someone', None, 2],
        ['customer', 'customer', 2],
        [None, 'system', 2],
        ['1122', 'system', 2],
        ['1122', 'picker', 2],
        ['another_picker', 'system', 1],
        ['another_picker', 'picker', 1],
    ],
)
@utils.send_order_events_config()
async def test_start_order_version_author_204(
        taxi_eats_picker_orders,
        require_approval,
        brand_id,
        payment_limit,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order,
        get_order_items,
        author,
        author_type,
        expected_quantity,
        mock_processing,
):
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        last_version=1,
        require_approval=require_approval,
        payment_limit=0,
        payment_value=3000,
        brand_id=brand_id,
        place_id=222,
        picker_card_type='TinkoffBank',
        picker_card_value='test_cid_1',
    )

    not_weight_item_id = '2'

    create_order_item(
        order_id=order_id,
        eats_item_id=not_weight_item_id,
        version=0,
        sold_by_weight=False,
        quantity=1,
        price=20,
        measure_value=0,
        measure_quantum=0,
        quantum_quantity=1,
        absolute_quantity=0,
        quantum_price=20,
    )
    create_order_item(
        order_id=order_id,
        eats_item_id=not_weight_item_id,
        version=1,
        sold_by_weight=False,
        quantity=2,
        price=20,
        measure_value=0,
        measure_quantum=0,
        quantum_quantity=2,
        absolute_quantity=0,
        quantum_price=20,
        author=author,
        author_type=author_type,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json.get('amount') == payment_limit
        assert request.json.get('order_id') == '12345'
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def _mock_b2b(request):
        assert request.query.get('claim_id') == 'CLAIM_ID_20'
        assert (
            request.headers['Authorization']
            == 'Bearer testsuite-api-cargo-token'
        )
        return mockserver.make_response(
            status=200, json=CARGO_INFO_MOCK_RESPONSE,
        )

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {
            'products': [
                {
                    'origin_id': not_weight_item_id,
                    'name': '',
                    'description': '',
                    'is_available': False,
                    'price': 15,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                },
            ],
            'categories': [],
        }

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    assert mock_processing.times_called == 1

    assert get_order(order_id)['last_version'] == 2
    updated_items = get_order_items(order_id, 2)
    assert len(updated_items) == 1
    assert updated_items[0]['eats_item_id'] == not_weight_item_id
    assert updated_items[0]['quantity'] == expected_quantity


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize(
    'require_approval, brand_id, payment_limit',
    [
        (False, 111, 4500),
        (False, 333, 3300),
        (True, 111, 4500),
        (True, 333, 3300),
    ],
)
@pytest.mark.now('2020-06-18T10:00:00')
@pytest.mark.parametrize('update_prices', [False, True])
@pytest.mark.parametrize('update_availability', [False, True])
@utils.send_order_events_config()
async def test_start_order_items_unavailable_204(
        taxi_eats_picker_orders,
        require_approval,
        brand_id,
        payment_limit,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order_items,
        get_order_by_eats_id,
        get_last_order_status,
        stq,
        now,
        experiments3,
        update_prices,
        update_availability,
        mock_processing,
):
    experiments3.add_experiment3_from_marker(
        utils.update_prices_and_availability_experiment(
            update_prices=update_prices,
            update_availability=update_availability,
        ),
        None,
    )
    now = now.replace(tzinfo=datetime.timezone.utc)
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        require_approval=require_approval,
        payment_limit=0,
        payment_value=3000,
        brand_id=brand_id,
        place_id=222,
        picker_card_type='TinkoffBank',
        picker_card_value='test_cid_1',
    )

    out_of_stock_item_id = '3'
    not_found_item_id = '4'

    create_order_item(
        order_id=order_id,
        eats_item_id=out_of_stock_item_id,
        sold_by_weight=True,
        quantity=1.5,
        price=10,
        measure_value=1000,
        measure_quantum=750,
        quantum_quantity=2,
        absolute_quantity=1500,
        quantum_price=7.5,
    )

    create_order_item(order_id=order_id, eats_item_id=not_found_item_id)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json.get('amount') == payment_limit
        assert request.json.get('order_id') == '12345'
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def _mock_b2b(request):
        assert request.query.get('claim_id') == 'CLAIM_ID_20'
        assert (
            request.headers['Authorization']
            == 'Bearer testsuite-api-cargo-token'
        )
        return mockserver.make_response(
            status=200, json=CARGO_INFO_MOCK_RESPONSE,
        )

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {
            'products': [
                {
                    'origin_id': out_of_stock_item_id,
                    'name': '',
                    'description': '',
                    'is_available': False,
                    'price': 15,
                    'adult': False,
                    'shipping_type': '',
                    'images': [],
                },
            ],
            'categories': [],
        }

    original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 0)
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    assert mock_processing.times_called == 1

    order = get_order_by_eats_id(eats_id)
    assert order['state'] == 'picking'
    assert order['payment_limit'] == payment_limit

    last_order_status = get_last_order_status(order_id)
    assert last_order_status['author_id'] == picker_id

    assert stq.send_start_picking_billing_event.times_called == 1
    kwargs = stq.send_start_picking_billing_event.next_call()['kwargs']
    assert kwargs['start_picking_at'] == '2020-06-18T13:00:00'
    assert kwargs['picker_id'] == picker_id
    assert kwargs['eats_id'] == '12345'
    assert kwargs['order_id'] == 1

    order_updated = update_prices or update_availability
    assert _mock_eats_products.times_called == int(order_updated)
    assert order['last_version'] == int(order_updated)
    updated_original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 0)
    }
    expected_items = copy.deepcopy(original_items)
    assert expected_items == updated_original_items
    if order_updated:
        new_items = {
            item['eats_item_id']: dict(item)
            for item in get_order_items(order_id, 1)
        }
        for item in expected_items.values():
            for key in 'created_at', 'updated_at', 'id', 'version':
                del item[key]
            item['author'] = picker_id
            item['author_type'] = SYSTEM
        if update_prices:
            expected_items[out_of_stock_item_id]['price'] = 20
            expected_items[out_of_stock_item_id]['quantum_price'] = 15
            expected_items[out_of_stock_item_id]['price_updated_at'] = now
        if update_availability:
            expected_items[out_of_stock_item_id]['is_deleted_by'] = SYSTEM
            expected_items[out_of_stock_item_id]['deleted_by_type'] = SYSTEM
            expected_items[out_of_stock_item_id]['reason'] = OUT_OF_STOCK
            expected_items[not_found_item_id]['is_deleted_by'] = SYSTEM
            expected_items[not_found_item_id]['deleted_by_type'] = SYSTEM
            expected_items[not_found_item_id]['reason'] = OUT_OF_STOCK
        for eats_item_id, item in new_items.items():
            utils.compare_db_with_expected_data(
                item, expected_items[eats_item_id],
            )


@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.now('2020-06-18T10:00:00')
@pytest.mark.parametrize(
    [
        'flow_type',
        'claim_id',
        'cargo_api_status',
        'claim_status',
        'status',
        'cargo_api_times_called',
    ],
    [
        ['picking_packing', '1', 200, 'pickup_arrived', 204, 0],
        ['picking_only', None, 200, 'pickup_arrived', 204, 0],
        ['picking_only', '1', 200, 'pickup_arrived', 204, 1],
        ['picking_only', '1', 404, 'pickup_arrived', 424, 1],
        ['picking_only', '1', 200, 'ololo', 500, 1],
        ['picking_only', '1', 200, 'accepted', 409, 1],
    ],
)
@utils.send_order_events_config()
async def test_start_order_claim_id_check(
        taxi_eats_picker_orders,
        mockserver,
        create_order,
        get_order_by_eats_id,
        stq,
        flow_type,
        claim_id,
        cargo_api_status,
        claim_status: str,
        status,
        cargo_api_times_called,
        mock_processing,
):
    eats_id = '12345'
    create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id='1',
        payment_value=3000,
        picker_card_type='TinkoffBank',
        picker_card_value='test_cid_1',
        claim_id=claim_id,
        flow_type=flow_type,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.query.get('card_type') == 'TinkoffBank'
        assert request.query.get('card_value') == 'test_cid_1'
        assert request.json.get('amount') == 3300
        assert request.json.get('order_id') == '12345'
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/b2b-taxi/b2b/cargo/integration/v2/claims/info')
    def _mock_b2b(request):
        assert request.query.get('claim_id') == claim_id
        assert (
            request.headers['Authorization']
            == 'Bearer testsuite-api-cargo-token'
        )
        response = (
            CARGO_INFO_MOCK_RESPONSE
            if cargo_api_status == 200
            else CARGO_INFO_MOCK_404_RESPONSE
        )
        response['status'] = claim_status
        return mockserver.make_response(json=response, status=cargo_api_status)

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return mockserver.make_response(status=404)

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=utils.da_headers('1'),
    )
    assert response.status == status
    assert _mock_b2b.times_called == cargo_api_times_called

    if status == 204:

        order = get_order_by_eats_id(eats_id)
        assert order['state'] == 'picking'

        assert stq.send_start_picking_billing_event.times_called == 1
        kwargs = stq.send_start_picking_billing_event.next_call()['kwargs']
        assert kwargs['start_picking_at'] == '2020-06-18T13:00:00'
        assert kwargs['picker_id'] == '1'
        assert kwargs['eats_id'] == '12345'
        assert kwargs['order_id'] == 1

        assert mock_processing.times_called == 1


@pytest.mark.parametrize(
    'products',
    [
        {
            '1': {
                'origin_id': '1',
                'name': '',
                'description': '',
                'is_available': True,
                'price': 15,
                'adult': False,
                'shipping_type': '',
                'images': [],
                'in_stock': 123,
            },
            '2': {
                'origin_id': '2',
                'name': '',
                'description': '',
                'is_available': True,
                'price': 15,
                'adult': False,
                'shipping_type': '',
                'images': [],
                'in_stock': None,
            },
        },
    ],
)
@utils.send_order_events_config()
async def test_start_order_items_in_stock(
        taxi_eats_picker_orders,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order_items,
        products,
        experiments3,
        mock_processing,
):
    experiments3.add_experiment3_from_marker(
        utils.update_prices_and_availability_experiment(
            update_prices=True, update_availability=True,
        ),
        None,
    )
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        claim_id='1',
        flow_type='picking_packing',
    )
    for eats_item_id in products:
        create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': '12345'}, status=200)

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {'products': list(products.values()), 'categories': []}

    original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 0)
    }
    for _, item in original_items.items():
        assert not item['in_stock']

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    assert mock_processing.times_called == 1

    updated_original_items = {
        item['eats_item_id']: dict(item)
        for item in get_order_items(order_id, 1)
    }

    for eats_item_id, item in updated_original_items.items():
        assert products[eats_item_id]['in_stock'] == (
            int(item['in_stock']) if item['in_stock'] else None
        )

    response = await taxi_eats_picker_orders.get(
        '/4.0/eats-picker/api/v1/order',
        params={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )

    for item in response.json()['payload']['picker_items']:
        if products[item['id']]['in_stock']:
            assert products[item['id']]['in_stock'] == (
                int(item['in_stock']) if item['in_stock'] else None
            )
        else:
            assert 'in_stock' not in item


@pytest.mark.parametrize(
    'products',
    [
        {
            '1': {
                'origin_id': '1',
                'name': '',
                'description': '',
                'is_available': False,
                'price': 15,
                'adult': False,
                'shipping_type': '',
                'images': [],
            },
        },
    ],
)
@utils.send_order_events_config()
async def test_start_order_set_customer_order_count_with_customer_id(
        taxi_eats_picker_orders,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order,
        products,
        mock_processing,
):
    eats_id = '12345'
    picker_id = '1122'
    customer_id = 'vpupkin'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        customer_id=customer_id,
        flow_type='picking_packing',
    )
    for eats_item_id in products:
        create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {'products': list(products.values()), 'categories': []}

    assert get_order(order_id)['customer_id'] == customer_id

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )
    assert response.status == 204

    assert mock_processing.times_called == 1


@pytest.mark.parametrize(
    'products',
    [
        {
            '1': {
                'origin_id': '1',
                'name': '',
                'description': '',
                'is_available': False,
                'price': 15,
                'adult': False,
                'shipping_type': '',
                'images': [],
            },
        },
    ],
)
@utils.send_order_events_config()
async def test_start_order_set_customer_order_count_no_customer_id(
        taxi_eats_picker_orders,
        mockserver,
        init_measure_units,
        create_order,
        create_order_item,
        get_order,
        products,
        mock_processing,
):
    eats_id = '12345'
    picker_id = '1122'

    order_id = create_order(
        state='assigned',
        eats_id=eats_id,
        picker_id=picker_id,
        flow_type='picking_packing',
    )
    for eats_item_id in products:
        create_order_item(order_id=order_id, eats_item_id=eats_item_id)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(json={'order_id': eats_id}, status=200)

    @mockserver.json_handler('/eats-products/api/v2/place/assortment/details')
    def _mock_eats_products(request):
        return {'products': list(products.values()), 'categories': []}

    assert get_order(order_id)['customer_id'] is None

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': eats_id},
        headers=utils.da_headers(picker_id),
    )

    assert get_order(order_id)['customer_orders_count'] is None

    # implicitly checking for 0 requests to eats-orders-stats

    assert response.status == 204

    assert mock_processing.times_called == 1


async def test_request_with_mistakes_400(
        taxi_eats_picker_orders, create_order,
):
    create_order(eats_id='123', picker_id='1', state='assigned')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eeets_id': '12345'},
        headers=utils.da_headers('1'),
    )
    assert response.status == 400


async def test_start_order_401(taxi_eats_picker_orders):
    bad_header = {
        'X-Request-Application-Version': '9.99 (9999)',
        'X-YaEda-CourierId': '123',
    }
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/start',
        json={'eats_id': '12345'},
        headers=bad_header,
    )
    assert response.status == 401
