import pytest

from . import utils


async def test_order_payments_404(taxi_eats_picker_orders):
    eats_id = 'eats-id'
    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/payments', params={'eats_id': eats_id},
    )
    assert response.status_code == 404


@pytest.mark.parametrize('picker_id', ['picker-id', None])
@pytest.mark.parametrize('picker_card_type', ['TinkoffBank', None])
@pytest.mark.parametrize('picker_card_value', ['cid_1', None])
@pytest.mark.parametrize('receipt_loaded', [False, True])
@pytest.mark.parametrize('spent', [1024, None])
@pytest.mark.parametrize(
    'state, has_spent',
    [
        ('new', False),
        ('picking', False),
        ('picked_up', False),
        ('receipt_processing', False),
        ('paid', True),
        ('complete', True),
    ],
)
async def test_order_payments_no_picked_items_200(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        picker_id,
        picker_card_type,
        picker_card_value,
        receipt_loaded,
        spent,
        state,
        has_spent,
):
    eats_id = 'eats-id'
    payment_limit = 2048
    receipt = '{"s": "4346.39"}'

    create_order(
        eats_id=eats_id,
        state=state,
        picker_id=picker_id,
        picker_card_type=picker_card_type,
        picker_card_value=picker_card_value,
        spent=spent,
        payment_limit=payment_limit,
        receipt=(receipt if receipt_loaded else '{}'),
    )

    @mockserver.json_handler('/eats-picker-payments/api/v1/limit')
    def mock_eats_picker_payment(request):
        assert request.method == 'GET'
        return mockserver.make_response(status=500)

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/payments', params={'eats_id': eats_id},
    )
    assert response.status_code == 200

    expected_response = {
        'receipt_loaded': receipt_loaded,
        'pickedup_total': '0.00',
        'payment_limit': str(payment_limit) + '.00',
    }

    if spent and has_spent:
        expected_response['spent'] = str(spent) + '.00'

    assert mock_eats_picker_payment.has_calls == bool(
        picker_card_type and picker_card_value,
    )

    assert response.json() == expected_response


@pytest.mark.parametrize(
    'state, do_calc_spent',
    [
        ('new', None),
        ('picking', None),
        ('picked_up', True),
        ('receipt_processing', True),
        ('paid', False),
        ('complete', False),
    ],
)
@pytest.mark.parametrize('payment_limit', [2048, 4096])
@pytest.mark.parametrize('current_limit', [2048, 4096])
async def test_order_payments_full_200(
        taxi_eats_picker_orders,
        create_order,
        init_currencies,
        init_measure_units,
        create_order_item,
        create_picked_item,
        mockserver,
        state,
        do_calc_spent,
        payment_limit,
        current_limit,
):
    eats_id = 'eats-id'
    picker_id = 'picker-id'
    spent = 1024

    order_id = create_order(
        eats_id=eats_id,
        state=state,
        picker_id=picker_id,
        spent=spent,
        payment_limit=payment_limit,
    )

    measure_quantum = 200
    quantum_price = 30

    item_id = create_order_item(
        order_id=order_id,
        measure_quantum=measure_quantum,
        quantum_price=quantum_price,
    )
    create_picked_item(order_item_id=item_id, picker_id=picker_id, count=2)

    @mockserver.json_handler('/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        assert request.method == 'GET'
        return mockserver.make_response(
            json={'amount': current_limit}, status=200,
        )

    response = await taxi_eats_picker_orders.get(
        '/api/v1/order/payments', params={'eats_id': eats_id},
    )
    assert response.status_code == 200

    expected_response = {
        'receipt_loaded': False,
        'pickedup_total': '60.00',
        'payment_limit': str(payment_limit) + '.00',
        'current_limit': str(current_limit) + '.00',
    }
    if do_calc_spent is not None:
        expected_response['spent'] = (
            str(payment_limit - current_limit if do_calc_spent else spent)
            + '.00'
        )

    assert response.json() == expected_response


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', 'api/v1/order'],
)
@pytest.mark.experiments3(filename='exp3_payment_coefficient.json')
@pytest.mark.parametrize(
    'order, payment_limit_coefficient',
    [
        (
            {'eats_id': '111111-123456', 'picker_id': '1', 'payment_limit': 0},
            10,
        ),
        (
            {
                'eats_id': '111111-123456',
                'picker_id': '1122',
                'place_id': '222',
                'brand_id': '111',
                'payment_limit': 0,
            },
            50,
        ),
        (
            {
                'eats_id': '111111-123456',
                'picker_id': '1122',
                'place_id': '222',
                'brand_id': '111',
                'payment_value': 100,
                'payment_limit': 166,
            },
            66,
        ),
    ],
)
async def test_get_order_payment_limit_coefficient(
        taxi_eats_picker_orders,
        create_order,
        handle,
        order,
        payment_limit_coefficient,
):
    create_order(**order)
    response = await taxi_eats_picker_orders.get(
        handle,
        params={'eats_id': order['eats_id']},
        headers=utils.da_headers(order['picker_id']),
    )
    assert (
        response.json()['payload']['payment_limit_coefficient']
        == payment_limit_coefficient
    )


@pytest.mark.parametrize(
    'handle', ['/4.0/eats-picker/api/v1/order', 'api/v1/order'],
)
async def test_get_order_payment_limit_coefficient_no_config(
        taxi_eats_picker_orders, create_order, handle,
):
    orders = [
        ({'eats_id': '111111-123456', 'picker_id': '1', 'payment_limit': 0}),
    ]

    for order in orders:
        create_order(**order)
        response = await taxi_eats_picker_orders.get(
            handle,
            params={'eats_id': order['eats_id']},
            headers=utils.da_headers(order['picker_id']),
        )
        assert response.json()['payload']['payment_limit_coefficient'] == 0
