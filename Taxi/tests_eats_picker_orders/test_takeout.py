import pytest

from . import utils

ORDER_NR = 'order_nr'
PICKER_ID = 'picker_id'
PERSONAL_DATA = {
    'customer_name',
    'customer_phone_id',
    'customer_forwarded_phone',
    'customer_picker_phone_forwarding',
}


@pytest.mark.parametrize('takeout_enabled', [True, False])
async def test_delete_phone_data_on_cancel(
        taxi_eats_picker_orders,
        experiments3,
        create_order,
        get_order,
        mockserver,
        takeout_enabled,
):
    experiments3.add_experiment(
        name='eats_picker_orders_takeout',
        consumers=['eats-picker-orders/takeout'],
        default_value={'enabled': takeout_enabled},
    )

    order_id = create_order(state='new', eats_id=ORDER_NR)

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(
            json={'order_id': ORDER_NR}, status=200,
        )

    response = await taxi_eats_picker_orders.post(
        f'/api/v1/order/cancel?eats_id={ORDER_NR}',
        json={'comment': 'Foo bar'},
    )
    assert response.status_code == 204

    order = get_order(order_id)
    for key in PERSONAL_DATA:
        if takeout_enabled:
            assert not order[key]
        else:
            assert order[key]


@pytest.mark.parametrize('takeout_enabled', [True, False])
async def test_delete_phone_data_on_finish_picking(
        taxi_eats_picker_orders,
        experiments3,
        create_order,
        get_order,
        mockserver,
        takeout_enabled,
):
    experiments3.add_experiment(
        name='eats_picker_orders_takeout',
        consumers=['eats-picker-orders/takeout'],
        default_value={'enabled': takeout_enabled},
    )

    order_id = create_order(
        state='picking', eats_id=ORDER_NR, picker_id=PICKER_ID,
    )

    @mockserver.json_handler(f'/eats-picker-payments/api/v1/limit')
    def _mock_eats_picker_payment(request):
        return mockserver.make_response(
            json={'order_id': ORDER_NR}, status=200,
        )

    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/order/finish-picking',
        json={'eats_id': ORDER_NR},
        headers=utils.da_headers(PICKER_ID),
    )
    assert response.status_code == 204

    order = get_order(order_id)
    for key in PERSONAL_DATA:
        if takeout_enabled:
            assert not order[key]
        else:
            assert order[key]
