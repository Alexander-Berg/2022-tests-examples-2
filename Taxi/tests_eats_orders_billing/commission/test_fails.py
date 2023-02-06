import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args, input_events, expected_input_stq_fail, times_called',
    [
        pytest.param(
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00',
                        goods_gmv_amount='100.00',
                        order_type='marketplace',
                    ),
                ),
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            True,
            0,
            id='Fail when no confirmed event',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
            ],
            True,
            0,
            id='Fail when no OrderCreated or OrderChanged',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='160.00',
                        goods_gmv_amount='160.00',
                        promocode=helpers.make_promocode(promocode_type=None),
                    ),
                ),
                helpers.make_db_row(
                    kind='ConfirmedByPlace',
                    external_event_ref=f'{consts.ORDER_NR}/ConfirmedByPlace',
                    data=helpers.make_confirmed_ie(),
                ),
                helpers.make_db_row(
                    kind='OrderCancelled',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCancelled',
                    data=helpers.make_order_cancelled_ie(
                        is_place_fault=False,
                        is_payment_expected=False,
                        is_reimbursement_required=True,
                        products=[
                            helpers.make_product(
                                value_amount='100.00',
                                product_type='product',
                                discounts=[
                                    helpers.make_discount(
                                        discount_type='marketing_promocode',
                                        amount='20.00',
                                        discount_provider='own',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
            # expected_input_stq_fail
            True,
            0,
            id='OrderCancelled, no promocode type',
        ),
    ],
)
async def test_billing_input_events_fails(
        stq_runner,
        mock_create_handler,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
        mock_customer_service_retrieve,
        mock_customer_service_retrieve_new,
        mock_order_revision_list,
        mock_order_revision_list_new,
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])
    mock_order_revision_list_new(revisions=[{'origin_revision_id': '123-321'}])

    await helpers.input_events_process_test_func(
        stq_runner,
        mock_create_handler,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
    )
