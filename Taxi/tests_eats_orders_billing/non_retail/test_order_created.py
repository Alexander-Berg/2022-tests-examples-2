import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'flow_type, order_type, '
    'processing_type, expected_rule, '
    'expected_input_stq_fail',
    [
        pytest.param('native', 'native', None, 'restaurant', False),
        pytest.param('native', 'native', 'store', 'grocery_eats_flow', False),
        pytest.param('pickup', 'marketplace', 'pickup', 'pickup', False),
        pytest.param('shop', 'native', None, 'shop', False),
        pytest.param('shop', 'marketplace', None, 'shop_marketplace', False),
        pytest.param('pharmacy', 'native', None, 'restaurant', False),
        pytest.param('fuelfood', 'marketplace', None, 'marketplace', False),
        pytest.param('retail', 'native', None, 'retail', False),
        pytest.param('fuelfood_rosneft', 'marketplace', None, None, True),
        pytest.param('burger_king', 'marketplace', None, None, True),
        pytest.param('inplace', 'marketplace', None, None, True),
    ],
)
async def test_order_created(
        stq_runner,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        flow_type,
        order_type,
        processing_type,
        expected_rule,
        expected_input_stq_fail,
):
    input_events = [
        helpers.make_db_row(
            kind='OrderCreated',
            external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
            data=helpers.make_order_created_ie(
                goods_price='100.00',
                goods_gmv_amount='100.00',
                flow_type=flow_type,
                order_type=order_type,
                processing_type=processing_type,
            ),
        ),
    ]

    expected_requests = []
    times_called = 0
    if not expected_input_stq_fail:
        expected_requests = [
            helpers.make_create_request(
                external_id=f'OrderCreated/{consts.ORDER_NR}',
                kind='order_created',
                data=helpers.make_order_created_data(rules=expected_rule),
            ),
        ]
        times_called = 1

    await helpers.input_events_process_test_func(
        stq_runner,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        helpers.make_events_process_stq_args(consts.ORDER_NR),
        input_events,
        expected_input_stq_fail,
        times_called,
        expected_requests,
    )
