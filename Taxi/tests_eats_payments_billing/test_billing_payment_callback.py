import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, expect_fail,'
    'billing_data_times_called, billing_storage_times_called, '
    'expected_output_stq_args, eats_billing_processor_times_called,'
    'eats_billing_processor_requests, flow_type, order_type',
    [
        pytest.param(
            # stq_kwargs
            helpers.make_stq_kwargs(transaction_type='payment', items=[]),
            # request_arg
            None,
            # expect_fail
            False,
            # billing_data_times_called
            0,
            # billing_storage_times_called
            0,
            # expected_output_stq_args
            None,
            # eats_billing_processor_times_called
            0,
            # eats_billing_processor_requests
            None,
            'native',  # flow_type
            'native',  # order_type
            id='Test payment with no items',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='1000',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='product', amount='499.99',
                    ),
                    helpers.make_stq_item(
                        item_id='4', item_type='delivery', amount='100',
                    ),
                    helpers.make_stq_item(  # option заменится на product
                        item_id='5', item_type='option', amount='42.5',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='2', item_type='delivery', amount='1000',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='3', item_type='product', amount='499.99',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='4', item_type='delivery', amount='100',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='5', item_type='option', amount='42.5',
                    ),
                ],
                amount='2642.51',
                goods_amount='1542.51',
                delivery_amount='1100',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            2,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='1100',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/native/native',
                    ),
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1542.51',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test with payment goods and delivery',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.03',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='0',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000.03',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='2', item_type='delivery', amount='0',
                    ),
                ],
                amount='1000.03',
                goods_amount='1000.03',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='pickup',
                order_type='marketplace',
            ),
            False,
            1,
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            1,  # eats_billing_processor_times_called
            # eats_billing_processor_requests
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pickup',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000.03',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pickup/marketplace',
                    ),
                ],
            ),
            'pickup',  # flow_type
            'marketplace',  # order_type
            id='Test with payment goods and zero delivery for pickup',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                ],
                amount='500',
                goods_amount='500',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            1,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='500',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test with payment goods only',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='donation', amount='500',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='donation', amount='500',
                    ),
                ],
                amount='500',
                goods_amount='500',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
                transaction_date=consts.EVENT_AT,
            ),
            False,
            0,
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(
                order_nr=consts.ORDER_ID,
                billing_extra_data={
                    'order_created': consts.EVENT_AT.replace('Z', '+00:00'),
                    'flow_type': 'native',
                },
            ),
            1,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='donation',
                        amount='500',
                        counteragent_id=consts.PLACE_ID,
                        product_id='donation/native/native',
                    ),
                ],
                transaction_date=consts.EVENT_AT,
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test with payment donation only',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_optional(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                ],
            ),
            helpers.make_request_arg_payment_no_opt(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                ],
                amount='500',
                goods_amount='500',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            1,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='500',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
                payment_terminal_id=None,
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test payment without terminal id',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                ],
                payment_service='yandex_market',
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                ],
                amount='1000.02',
                goods_amount='1000.02',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
                payment_service='yandex_market',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            1,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000.02',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
                payment_service='yandex_market',
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test passing payment service',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='service_fee', amount='9.00',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='2', item_type='service_fee', amount='9.00',
                    ),
                ],
                amount='1000.02',
                goods_amount='1000.02',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            1,
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000.02',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
            ),
            'native',  # flow_type
            'native',  # order_type
            id='Test skip service fee',
        ),
        pytest.param(
            # stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='product',
                        amount='1000.02',
                        deal_id='good_deal',
                    ),
                    helpers.make_stq_item(
                        item_id='2',
                        item_type='service_fee',
                        amount='9.00',
                        deal_id='average_deal',
                    ),
                ],
            ),
            # request_arg
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000.02',
                    ),
                    helpers.make_request_arg_old_item(
                        item_id='2', item_type='service_fee', amount='9.00',
                    ),
                ],
                amount='1000.02',
                goods_amount='1000.02',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            # expect_fail
            False,
            # billing_data_times_called
            1,
            # billing_storage_times_called
            1,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            # eats_billing_processor_requests
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    # TODO: add deal_id when billing-processor is ready
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000.02',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
            ),
            'native',  # flow_type
            'native',  # order_type
            id='test_deal_id',
        ),
    ],
)
async def test_stq_proxy_callback(
        stq_runner,
        stq,
        experiments3,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        stq_kwargs,
        request_arg,
        expect_fail,
        billing_data_times_called,
        billing_storage_times_called,
        expected_output_stq_args,
        eats_billing_processor_times_called,
        eats_billing_processor_requests,
        flow_type,
        order_type,
):
    experiments3.add_config(**helpers.make_billing_events_experiment())

    order_billing_data_mock = mock_order_billing_data(
        order_id=consts.ORDER_ID,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
        flow_type=flow_type,
        order_type=order_type,
    )

    billing_storage_mock = mock_eats_billing_storage(expected_data=request_arg)
    eats_billing_processor_mock = mock_eats_billing_processor(
        expected_requests=eats_billing_processor_requests,
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID, kwargs=stq_kwargs, expect_fail=expect_fail,
    )

    assert order_billing_data_mock.times_called == billing_data_times_called
    assert billing_storage_mock.times_called == billing_storage_times_called
    assert (
        eats_billing_processor_mock.times_called
        == eats_billing_processor_times_called
    )


@pytest.mark.parametrize(
    'expect_fail, order_id, processing_type, expected_times_called',
    [
        pytest.param(False, consts.ORDER_ID, 'store', 1, id='Test happy path'),
        pytest.param(
            False,
            consts.ORDER_ID,
            'processing_type',
            0,
            id='Test with another processing_type',
        ),
        pytest.param(
            False,
            consts.GROCERY_CYCLE_ORDER_ID,
            'store',
            0,
            id='Test with grocery order',
        ),
    ],
)
async def test_stq_grocery_callback(
        stq_runner,
        stq,
        experiments3,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        grocery_orders,
        expect_fail,
        order_id,
        processing_type,
        expected_times_called,
):
    stq_kwargs = helpers.make_stq_kwargs(
        order_id=order_id,
        transaction_type='payment',
        items=[
            helpers.make_stq_item(
                item_id='1', item_type='product', amount='1000.02',
            ),
            helpers.make_stq_item(
                item_id='2', item_type='delivery', amount='1000',
            ),
            helpers.make_stq_item(
                item_id='3', item_type='tips', amount='499.99',
            ),
        ],
    )

    experiments3.add_config(**helpers.make_billing_events_experiment())

    mock_order_billing_data(
        order_id=order_id,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
        processing_type=processing_type,
    )

    grocery_orders.add_order(
        order_id=order_id,
        courier_info={
            'id': 'qwe',
            'transport_type': 'pedestrian',
            'eats_courier_id': 'asd',
        },
    )

    mock_eats_billing_storage()
    mock_eats_billing_processor()

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID, kwargs=stq_kwargs, expect_fail=expect_fail,
    )

    assert (
        stq.grocery_payments_billing_eats_orders.times_called
        == expected_times_called
    )
    if expected_times_called == 0:
        return

    call_kwargs = stq.grocery_payments_billing_eats_orders.next_call()[
        'kwargs'
    ]
    del call_kwargs['log_extra']
    assert call_kwargs == {
        'order_id': stq_kwargs['order_id'],
        'receipt_type': stq_kwargs['transaction_type'],
        'currency': stq_kwargs['currency'],
        'event_at': consts.EVENT_AT_TIMEZONE,
        'transaction_date': consts.TRANSACTION_DATE_TIMEZONE,
        'external_payment_id': stq_kwargs['external_payment_id'],
        'courier_id': consts.COURIER_ID,
        'terminal_id': stq_kwargs['terminal_id'],
        'items': [
            {
                'item_id': item['item_id'],
                'item_type': item['item_type'],
                'amount': item['amount'],
                'balance_client_id': item['balance_client_id'],
                'place_id': item['place_id'],
            }
            for item in stq_kwargs['items']
        ],
    }
