import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, expect_fail,'
    'billing_data_times_called, billing_storage_times_called, '
    'expected_output_stq_args, eats_billing_processor_times_called, '
    'eats_billing_processor_requests',
    [
        pytest.param(
            # stq_kwargs
            helpers.make_stq_kwargs(transaction_type='refund', items=[]),
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
            0,
            None,
            id='Test refund with no items',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='refund',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='delivery', amount='1000',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='product', amount='500',
                    ),
                    helpers.make_stq_item(
                        item_id='4', item_type='delivery', amount='100',
                    ),
                    helpers.make_stq_item(
                        item_id='5', item_type='option', amount='42',
                    ),
                ],
            ),
            helpers.make_request_arg_refund(
                old_kind=None,
                old_items=[],
                new_kind='BillingRefund',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            0,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            2,
            helpers.make_billing_processor_request(
                kind='payment_refund',
                transaction_type='refund',
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
                        amount='1542',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
            ),
            id='Test with refund goods and delivery',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='refund',
                items=[
                    helpers.make_stq_item(
                        item_id='3', item_type='product', amount='500',
                    ),
                ],
            ),
            helpers.make_request_arg_refund(
                old_kind=None,
                old_items=[],
                new_kind='BillingRefund',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            0,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            helpers.make_billing_processor_request(
                kind='payment_refund',
                transaction_type='refund',
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
            id='Test with refund goods only',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_optional(
                transaction_type='refund',
                items=[
                    helpers.make_stq_item(
                        item_id='3', item_type='product', amount='500',
                    ),
                ],
            ),
            helpers.make_request_arg_refund_no_opt(
                old_kind=None,
                old_items=[],
                new_kind='BillingRefund',
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            0,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            helpers.make_billing_processor_request(
                kind='payment_refund',
                transaction_type='refund',
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
            id='Test refund without terminal id',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='refund',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                payment_service='yandex_market',
            ),
            helpers.make_request_arg_refund(
                old_kind=None,
                old_items=[],
                new_kind='BillingRefund',
                new_items=[],
                flow_type='native',
                order_type='native',
                payment_service='yandex_market',
            ),
            False,
            1,
            0,
            # expected_output_stq_args
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            helpers.make_billing_processor_request(
                kind='payment_refund',
                transaction_type='refund',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/native/native',
                    ),
                ],
                payment_service='yandex_market',
            ),
            id='Test passing payment service',
        ),
    ],
)
async def test_stq_proxy_callback(
        stq_runner,
        stq,
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
):
    order_billing_data_mock = mock_order_billing_data(
        order_id=consts.ORDER_ID,
        response_code=200,
        transaction_date=consts.TRANSACTION_DATE,
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
