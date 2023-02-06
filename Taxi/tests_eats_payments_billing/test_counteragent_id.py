import pytest

from tests_eats_payments_billing import consts
from tests_eats_payments_billing import helpers


@pytest.mark.parametrize(
    'stq_kwargs, request_arg, eats_billing_processor_arg, '
    'flow_type, order_type',
    [
        # -------------- product/option ---------------
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
                flow_type='retail',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='retail',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='product/retail/native',
                    ),
                ],
            ),
            'retail',
            'native',
            id='product/retail/*  =>  courier',
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
                flow_type='retail',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='retail',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='product/retail/native',
                    ),
                ],
            ),
            'retail',
            'native',
            id='option/retail/*  =>  courier',
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
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
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
            ),
            'native',
            'native',
            id='product/*/*  =>  place',
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
                flow_type='pickup',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pickup',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pickup/marketplace',
                    ),
                ],
            ),
            'pickup',
            'marketplace',
            id='product/*/*  =>  place',
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
                flow_type='native',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
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
            ),
            'native',
            'native',
            id='option/*/*  =>  place',
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
                flow_type='pickup',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='pickup',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='product',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='product/pickup/marketplace',
                    ),
                ],
            ),
            'pickup',
            'marketplace',
            id='option/*/*  =>  place',
        ),
        # -------------- delivery ---------------
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
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='delivery/native/marketplace',
                    ),
                ],
            ),
            'native',
            'marketplace',
            id='delivery/native/marketplace  =>  place',
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
                flow_type='native',
                order_type='native',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='native',
                order_type='native',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/native/native',
                    ),
                ],
            ),
            'native',
            'native',
            id='delivery/*/*  =>  courier',
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
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='delivery/retail/marketplace',
                    ),
                ],
            ),
            'retail',
            'marketplace',
            id='delivery/*/*  =>  courier',
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
                flow_type='shop',
                order_type='marketplace',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='shop',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='delivery',
                        amount='1000',
                        counteragent_id=consts.PLACE_ID,
                        product_id='delivery/shop/marketplace',
                    ),
                ],
            ),
            'shop',
            'marketplace',
            id='delivery/*/*  =>  place',
        ),
        # -------------- others ---------------
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
                        product_type='retail',
                        amount='1000',
                        counteragent_id=consts.PICKER_ID,
                        product_id='retail/fuelfood/native',
                    ),
                ],
            ),
            'fuelfood',
            'native',
            id='*/*/*  =>  courier',
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
                new_kind='',
                new_items=[],
                flow_type='shop',
                order_type='marketplace',
                payment_type='eda_tips',
            ),
            helpers.make_billing_processor_request(
                kind='payment_received',
                transaction_type='payment',
                flow_type='shop',
                order_type='marketplace',
                items=[
                    helpers.make_request_arg_new_item(
                        product_type='tips',
                        amount='1000',
                        counteragent_id=consts.COURIER_ID,
                        product_id='tips/shop/marketplace',
                    ),
                ],
                payment_type='eda_tips',
            ),
            'shop',
            'marketplace',
            id='*/*/*  =>  courier',
        ),
    ],
)
async def test_counteragent_id(
        stq_runner,
        mockserver,
        mock_order_billing_data,
        mock_eats_billing_storage,
        mock_eats_billing_processor,
        stq_kwargs,
        request_arg,
        eats_billing_processor_arg,
        flow_type,
        order_type,
):
    mock_order_billing_data(flow_type=flow_type, order_type=order_type)

    mock_eats_billing_storage(expected_data=request_arg)
    mock_eats_billing_processor(expected_requests=eats_billing_processor_arg)

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task', kwargs=stq_kwargs,
    )


async def test_courier_id_grocery_order_cycle(
        stq_runner,
        mockserver,
        mock_eats_billing_storage,
        grocery_orders,
        mock_eats_billing_processor,
):
    order_id = consts.GROCERY_CYCLE_ORDER_ID
    created = '2020-03-03T10:04:37Z'
    grocery_courier_id = 'grocery_courier_id_123'
    eats_courier_id = '2809'

    grocery_orders.add_order(
        order_id=order_id,
        created=created,
        courier_info={
            'id': grocery_courier_id,
            'transport_type': 'pedestrian',
            'eats_courier_id': eats_courier_id,
        },
    )

    request_arg = helpers.make_request_arg_payment(
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
        flow_type='native',
        order_type='native',
        order_id=order_id,
        transaction_date=created,
    )

    mock_eats_billing_storage(expected_data=request_arg)

    eats_billing_processor_request = helpers.make_billing_processor_request(
        order_nr=order_id,
        transaction_date=created,
        kind='payment_received',
        transaction_type='payment',
        flow_type='native',
        order_type='native',
        items=[
            helpers.make_request_arg_new_item(
                product_type='delivery',
                amount='1000',
                counteragent_id=eats_courier_id,
                product_id='delivery/native/native',
            ),
        ],
    )

    mock_eats_billing_processor(
        expected_requests=eats_billing_processor_request,
    )

    stq_kwargs = helpers.make_stq_kwargs(
        transaction_type='payment',
        items=[
            helpers.make_stq_item(
                item_id='1', item_type='delivery', amount='1000',
            ),
        ],
        order_id=order_id,
    )

    await stq_runner.eats_payments_billing_proxy_callback.call(
        task_id='sample_task', kwargs=stq_kwargs,
    )
