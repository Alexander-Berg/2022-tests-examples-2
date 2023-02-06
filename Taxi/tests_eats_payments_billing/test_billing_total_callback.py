import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import eats_plus_helpers
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, eats_billing_processor_arg, expect_fail,'
    'billing_data_times_called, billing_storage_times_called, '
    'expected_output_stq_args, processing_type',
    [
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                payment_type='personal_wallet',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                currency=consts.CURRENCY,
                payment_type='cashback',
                processing_type=None,
            ),
            eats_plus_helpers.make_b_processor_cashback_total(
                amount='1000', order_id=consts.ORDER_ID,
            ),
            False,
            1,
            0,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            None,
            id='Test regular total',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                payment_type='personal_wallet',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                currency=consts.CURRENCY,
                payment_type='cashback',
                processing_type='store',
            ),
            eats_plus_helpers.make_b_processor_cashback_total(
                amount='1000',
                processing_type='store',
                order_id=consts.ORDER_ID,
            ),
            False,
            1,
            0,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            'store',
            id='Test passing processing type',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='option', amount='100',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='delivery', amount='49',
                    ),
                ],
                payment_type='personal_wallet',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1100',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='49',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/native/native',
                    ),
                ],
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                currency=consts.CURRENCY,
                payment_type='cashback',
            ),
            None,
            False,
            1,
            0,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            None,
            id='Test total with few items',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                payment_type='card',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[],
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                currency=consts.CURRENCY,
                payment_type='cashback',
            ),
            eats_plus_helpers.make_b_processor_cashback_total(
                amount='1000', order_id=consts.ORDER_ID,
            ),
            True,
            1,
            0,
            None,
            None,
            id='Test total with wrong payment type',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='product',
                        amount='1000',
                        deal_id='terrible_deal',
                    ),
                    helpers.make_stq_item(
                        item_id='2',
                        item_type='option',
                        amount='100',
                        deal_id='terrible_deal',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='delivery', amount='49',
                    ),
                ],
                payment_type='personal_wallet',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='49',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/native/native',
                    ),
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1100',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                        deal_id='terrible_deal',
                    ),
                ],
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                currency=consts.CURRENCY,
                payment_type='cashback',
            ),
            None,
            False,
            1,
            0,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            None,
            id='test_deal_id',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='total',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='0',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='0',
                    ),
                ],
                payment_type='personal_wallet',
            ),
            helpers.make_request_total_event(
                kind='BillingPaymentUpdatePlusCashback',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='0',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pickup/marketplace',
                    ),
                ],
                transaction_type='payment',
                flow_type='pickup',
                order_type='marketplace',
                currency=consts.CURRENCY,
                payment_type='cashback',
                processing_type=None,
            ),
            eats_plus_helpers.make_b_processor_cashback_total(
                amount='0',
                order_id=consts.ORDER_ID,
                flow_type='pickup',
                order_type='marketplace',
            ),
            False,
            1,
            0,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            None,
            id='Test zero amount',
        ),
    ],
)
async def test_stq_proxy_callback(
        stq_runner,
        stq,
        mock_order_billing_data,
        mock_eats_billing_storage,
        stq_kwargs,
        request_arg,
        eats_billing_processor_arg,
        expect_fail,
        billing_data_times_called,
        billing_storage_times_called,
        expected_output_stq_args,
        mock_eats_billing_processor,
        processing_type,
):
    flow_type = (
        'native' if not request_arg else request_arg[0]['data']['flow_type']
    )
    order_type = (
        'native' if not request_arg else request_arg[0]['data']['order_type']
    )
    order_billing_data_mock = mock_order_billing_data(
        order_id=consts.ORDER_ID,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
        processing_type=processing_type,
        flow_type=flow_type,
        order_type=order_type,
    )
    mock_eats_billing_processor = mock_eats_billing_processor(
        expected_requests=eats_billing_processor_arg,
    )

    billing_storage_mock = mock_eats_billing_storage(expected_data=request_arg)

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID, kwargs=stq_kwargs, expect_fail=expect_fail,
    )

    assert order_billing_data_mock.times_called == billing_data_times_called
    assert billing_storage_mock.times_called == billing_storage_times_called
    assert mock_eats_billing_processor.times_called == 0 if expect_fail else 1


async def test_total_callback_grocery_order_cycle(
        stq_runner,
        stq,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        grocery_orders,
):
    order_id = consts.GROCERY_CYCLE_ORDER_ID
    mocked_order = grocery_orders.add_order(
        order_id=order_id, created='2020-03-03T10:04:37Z',
    )
    mock_eats_billing_processor = mock_eats_billing_processor(
        eats_plus_helpers.make_b_processor_cashback_total(
            amount='1000',
            processing_type='store',
            order_id=consts.GROCERY_CYCLE_ORDER_ID,
        ),
    )

    order_billing_data_mock = mock_order_billing_data()

    request_arg = helpers.make_request_total_event(
        kind='BillingPaymentUpdatePlusCashback',
        items=[
            helpers.make_request_arg_new_item(
                product_type='product',
                amount='1000',
                counteragent_id=consts.PLACE_ID,
                product_id='product/native/native',
            ),
        ],
        transaction_type='payment',
        flow_type='native',
        order_type='native',
        currency=consts.CURRENCY,
        payment_type='cashback',
        order_id=order_id,
        transaction_date=mocked_order['created'],
        processing_type='store',
    )

    billing_storage_mock = mock_eats_billing_storage(expected_data=request_arg)

    stq_kwargs = helpers.make_stq_kwargs(
        order_id=order_id,
        transaction_type='total',
        items=[
            helpers.make_stq_item(
                item_id='1', item_type='product', amount='1000',
            ),
        ],
        payment_type='personal_wallet',
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id=consts.TASK_ID, kwargs=stq_kwargs,
    )

    assert mock_eats_billing_processor.times_called == 1
    assert order_billing_data_mock.times_called == 0
    assert billing_storage_mock.times_called == 0
    assert grocery_orders.info_times_called() == 1
