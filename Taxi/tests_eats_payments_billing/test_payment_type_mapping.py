import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'input_stq_kwargs, expected_storage_request, '
    'expected_eats_billing_processor_request, input_stq_fails',
    [
        # Маппинг card => card
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='card',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
            ),
            False,
            id='card  =>  card',
        ),
        # Маппинг applepay => card
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='applepay',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='card',
            ),
            False,
            id='applepay  =>  card',
        ),
        # Маппинг googlepay => card
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='googlepay',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='card',
            ),
            False,
            id='googlepay  =>  card',
        ),
        # Маппинг sbp => card
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='sbp',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='card',
            ),
            False,
            id='sbp  =>  card',
        ),
        # Маппинг corp => corporate
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='corp',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='corporate',
                old_payment_type='corporate',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='corporate',
            ),
            False,
            id='corp  =>  corporate',
        ),
        # Маппинг badge => badge_corporate
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='badge',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='badge_corporate',
                old_payment_type='badge_corporate',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type=consts.PRODUCT_TYPE,
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id=f'{consts.PRODUCT_TYPE}/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='badge_corporate',
            ),
            False,
            id='badge  =>  badge_corporate',
        ),
        # Маппинг product = tips, payment_type = card => eda_tips
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='card',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='tips', amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='tips', amount='1000',
                    ),
                ],
                amount='0',
                goods_amount='0',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='eda_tips',
                old_payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='tips',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='tips/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='eda_tips',
            ),
            False,
            id='tips  =>  eda_tips',
        ),
        # Маппинг product = restaurant_tips => restaurant_tips
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='card',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='restaurant_tips',
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1',
                        item_type='restaurant_tips',
                        amount='1000',
                    ),
                ],
                amount='0',
                goods_amount='0',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                payment_type='restaurant_tips',
                old_payment_type='card',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type=consts.FLOW_TYPE,
                order_type=consts.ORDER_TYPE,
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='restaurant_tips',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='restaurant_tips/'
                        f'{consts.FLOW_TYPE}/{consts.ORDER_TYPE}',
                    ),
                ],
                payment_type='restaurant_tips',
            ),
            False,
            id='restaurant_tips  =>  restaurant_tips',
        ),
        # Неизвестный тип платежа, STQ-таска падает
        pytest.param(
            # input_stq_kwargs
            helpers.make_stq_kwargs(
                transaction_type='payment',
                payment_type='spasibo',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type=consts.PRODUCT_TYPE,
                        amount='1000',
                    ),
                ],
            ),
            # expected_storage_request
            None,
            None,
            True,
            id='Unknown payment type.',
        ),
    ],
)
async def test_counteragent_id(
        stq_runner,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        input_stq_kwargs,
        expected_storage_request,
        expected_eats_billing_processor_request,
        input_stq_fails,
):
    mock_order_billing_data()

    mock_eats_billing_storage(expected_data=expected_storage_request)
    mock_eats_billing_processor(
        expected_requests=expected_eats_billing_processor_request,
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task',
        kwargs=input_stq_kwargs,
        expect_fail=input_stq_fails,
    )
