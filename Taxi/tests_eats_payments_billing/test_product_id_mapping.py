import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.config(
    EATS_PAYMENTS_BILLING_PRODUCT_ID_MAP={
        'assembly/fuelfood/native': {
            'product': 'assembly',
            'flow_type': 'fuelfood',
            'order_type': 'native',
        },
        'delivery/fuelfood_rosneft/marketplace': {
            'product': 'delivery',
            'flow_type': 'fuelfood_rosneft',
            'order_type': 'marketplace',
        },
        'product/pharmacy/marketplace': {
            'product': 'product',
            'flow_type': 'pharmacy',
            'order_type': 'marketplace',
        },
        'restaurant_tips/pickup/native': {
            'product': 'restaurant_tips',
            'flow_type': 'pickup',
            'order_type': 'native',
        },
        'retail/retail/marketplace': {
            'product': 'retail',
            'flow_type': 'retail',
            'order_type': 'marketplace',
        },
        'tips/shop/native': {
            'product': 'tips',
            'flow_type': 'shop',
            'order_type': 'native',
        },
    },
)
@pytest.mark.parametrize(
    'stq_kwargs, request_arg, '
    'eats_billing_processor_request_args, '
    'flow_type, order_type, expect_fail',
    [
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='assembly', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='assembly', amount='1000',
                    ),
                ],
                amount='0',
                goods_amount='0',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='fuelfood',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='fuelfood',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='assembly',
                        amount='1000',
                        counteragent_id=consts.PICKER_ID,
                        product_id='assembly/fuelfood/native',
                    ),
                ],
            ),
            'fuelfood',
            'native',
            False,
            id='assembly/fuelfood/native => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='delivery', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='delivery', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='0',
                delivery_amount='1000',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='fuelfood_rosneft',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='fuelfood_rosneft',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/fuelfood_rosneft/marketplace',
                    ),
                ],
            ),
            'fuelfood_rosneft',
            'marketplace',
            False,
            id='delivery/fuelfood_rosneft/marketplace => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='pharmacy',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pharmacy',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pharmacy/marketplace',
                    ),
                ],
            ),
            'pharmacy',
            'marketplace',
            False,
            id='product/pharmacy/marketplace => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='option', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='option', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='pharmacy',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pharmacy',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        # option из stq меняется на product
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pharmacy/marketplace',
                    ),
                ],
            ),
            'pharmacy',
            'marketplace',
            False,
            id='product/pharmacy/marketplace => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1',
                        item_type='restaurant_tips',
                        amount='1000',
                    ),
                ],
            ),
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
                flow_type='pickup',
                order_type='native',
                payment_type='restaurant_tips',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pickup',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='restaurant_tips',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='restaurant_tips/pickup/native',
                    ),
                ],
                payment_type='restaurant_tips',
            ),
            'pickup',
            'native',
            False,
            id='restaurant_tips/pickup/native => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='retail', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='retail', amount='1000',
                    ),
                ],
                amount='0',
                goods_amount='0',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='retail',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='retail',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='retail',
                        amount='1000',
                        counteragent_id=consts.PICKER_ID,
                        product_id='retail/retail/marketplace',
                    ),
                ],
            ),
            'retail',
            'marketplace',
            False,
            id='retail/retail/marketplace => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='tips', amount='1000',
                    ),
                ],
            ),
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
                flow_type='shop',
                order_type='native',
                payment_type='eda_tips',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='shop',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='tips',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='tips/shop/native',
                    ),
                ],
                payment_type='eda_tips',
            ),
            'shop',
            'native',
            False,
            id='tips/shop/native => Ok',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='delivery', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='delivery', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='0',
                delivery_amount='1000',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='pharmacy',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pharmacy',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/pharmacy/marketplace',
                    ),
                ],
            ),
            'pharmacy',
            'marketplace',
            True,
            id='delivery/pharmacy/marketplace => Fail',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='native',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='product/native/marketplace',
                    ),
                ],
            ),
            'native',
            'marketplace',
            True,
            id='product/native/marketplace => Fail',
        ),
        pytest.param(
            helpers.make_stq_kwargs(
                transaction_type='payment',
                items=[
                    helpers.make_stq_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
            ),
            helpers.make_request_arg_payment(
                old_kind='PaymentReceived',
                old_items=[
                    helpers.make_request_arg_old_item(
                        item_id='1', item_type='product', amount='1000',
                    ),
                ],
                amount='1000',
                goods_amount='1000',
                delivery_amount='0',
                new_kind='BillingPayment',
                new_items=[],
                flow_type='pharmacy',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pharmacy',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='product/pharmacy/native',
                    ),
                ],
            ),
            'pharmacy',
            'native',
            True,
            id='product/pharmacy/native => Fail',
        ),
    ],
)
async def test_product_id_mapping(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        stq_kwargs,
        request_arg,
        eats_billing_processor_request_args,
        flow_type,
        order_type,
        expect_fail,
):
    mock_order_billing_data(flow_type=flow_type, order_type=order_type)

    mock_eats_billing_storage(expected_data=request_arg)
    mock_eats_billing_processor(
        expected_requests=eats_billing_processor_request_args,
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task', kwargs=stq_kwargs, expect_fail=expect_fail,
    )
