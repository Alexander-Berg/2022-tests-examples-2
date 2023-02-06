import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, expect_fail,'
    'billing_data_times_called, billing_storage_times_called, '
    'expected_output_stq_args, eats_billing_processor_times_called,'
    'eats_billing_processor_requests',
    [
        pytest.param(
            # stq_kwargs
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment', items=[],
            ),
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
            None,
            id='Test payment not received with no items',
        ),
        pytest.param(
            # stq_kwargs
            helpers.make_stq_kwargs_no_payment(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='product',
                        amount='500',
                        balance_client_id=None,
                    ),
                ],
            ),
            # request_arg
            None,
            # expect_fail
            True,
            # billing_data_times_called
            1,
            # billing_storage_times_called
            0,
            # expected_output_stq_args
            None,
            # eats_billing_processor_times_called
            0,
            None,
            id='Test payment incorrect balance_client_id',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                ],
                external_payment_id=None,
            ),
            # request_arg
            helpers.make_request_arg_no_payment(
                old_kind='PaymentNotReceived',
                new_kind=None,
                new_items=[],
                flow_type='native',
                order_type='native',
                external_payment_id=None,
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            [
                helpers.make_eats_billing_nopay_request(
                    kind='payment_not_received',
                    items=[
                        helpers.make_request_arg_new_item(
                            product_type='product',
                            amount='500',
                            counteragent_id=consts.PLACE_ID,
                            product_id='product/native/native',
                        ),
                    ],
                    flow_type='native',
                    order_type='native',
                    external_payment_id=None,
                ),
            ],
            id='Test payment not received',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='500',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='product', amount='100',
                    ),
                    helpers.make_stq_item(
                        item_id='3', item_type='delivery', amount='150',
                    ),
                ],
            ),
            # request_arg
            helpers.make_request_arg_no_payment(
                old_kind='PaymentNotReceived',
                new_kind=None,
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            [
                helpers.make_eats_billing_nopay_request(
                    kind='payment_not_received',
                    items=[
                        helpers.make_request_arg_new_item(
                            product_type='delivery',
                            amount='150',
                            counteragent_id=consts.COURIER_ID,
                            product_id='delivery/native/native',
                        ),
                        helpers.make_request_arg_new_item(
                            product_type='product',
                            amount='600',
                            counteragent_id=consts.PLACE_ID,
                            product_id='product/native/native',
                        ),
                    ],
                    flow_type='native',
                    order_type='native',
                ),
            ],
            id='Test payment not received few items',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment',
                items=[
                    helpers.make_stq_item(
                        item_id='4', item_type='delivery', amount='49',
                    ),
                ],
            ),
            # request_arg
            helpers.make_request_arg_no_payment(
                old_kind='PaymentNotReceived',
                new_kind=None,
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            [
                helpers.make_eats_billing_nopay_request(
                    kind='payment_not_received',
                    items=[
                        helpers.make_request_arg_new_item(
                            product_type='delivery',
                            amount='49',
                            counteragent_id=consts.COURIER_ID,
                            product_id='delivery/native/native',
                        ),
                    ],
                    flow_type='native',
                    order_type='native',
                ),
            ],
            id='Test payment not received delivery only',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='service_fee',
                        amount='49',
                        place_id='',
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='product', amount='500',
                    ),
                ],
            ),
            # request_arg
            helpers.make_request_arg_no_payment(
                old_kind='PaymentNotReceived',
                new_kind=None,
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            [
                helpers.make_eats_billing_nopay_request(
                    kind='payment_not_received',
                    items=[
                        helpers.make_request_arg_new_item(
                            product_type='product',
                            amount='500',
                            counteragent_id=consts.PLACE_ID,
                            product_id='product/native/native',
                        ),
                    ],
                    flow_type='native',
                    order_type='native',
                ),
            ],
            id='Test service fee',
        ),
        pytest.param(
            helpers.make_stq_kwargs_no_payment(
                transaction_type='no_payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='service_fee',
                        amount='49',
                        place_id='',
                        balance_client_id=None,
                    ),
                    helpers.make_stq_item(
                        item_id='2', item_type='product', amount='500',
                    ),
                ],
            ),
            # request_arg
            helpers.make_request_arg_no_payment(
                old_kind='PaymentNotReceived',
                new_kind=None,
                new_items=[],
                flow_type='native',
                order_type='native',
            ),
            False,
            1,
            1,
            helpers.make_billing_events_stq_kwargs(order_nr=consts.ORDER_ID),
            # eats_billing_processor_times_called
            1,
            [
                helpers.make_eats_billing_nopay_request(
                    kind='payment_not_received',
                    items=[
                        helpers.make_request_arg_new_item(
                            product_type='product',
                            amount='500',
                            counteragent_id=consts.PLACE_ID,
                            product_id='product/native/native',
                        ),
                    ],
                    flow_type='native',
                    order_type='native',
                ),
            ],
            id='Test incorrect service fee',
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
