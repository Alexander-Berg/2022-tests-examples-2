import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args, input_events, expected_input_stq_fail,'
    'times_called, expected_requests',
    [
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
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
                        is_reimbursement_required=False,
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            1,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
            ],
            id='OrderCancelled, payment not expected, '
            'no reimbursement, no fault',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
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
                        is_payment_expected=True,
                        is_reimbursement_required=False,
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            2,
            [
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
            ],
            id='OrderCancelled, payment not expected',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
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
                                value_amount='100.00', product_type='product',
                            ),
                        ],
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_cancelled',
                    kind='order_cancelled',
                    data=helpers.make_order_cancelled_data(
                        is_place_fault=False,
                        is_payment_expected=False,
                        is_reimbursement_required=True,
                        products=[
                            helpers.make_request_product(
                                product_id='product/native/native',
                                product_type='product',
                                value_amount='100',
                            ),
                        ],
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
            ],
            id='OrderCancelled, reimbursement required',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='100.00', goods_gmv_amount='100.00',
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
                        is_place_fault=True,
                        is_payment_expected=False,
                        is_reimbursement_required=False,
                        products=[
                            helpers.make_product(
                                value_amount='100.00', product_type='product',
                            ),
                        ],
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            2,
            [
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_cancelled',
                    kind='order_cancelled',
                    data=helpers.make_order_cancelled_data(
                        is_place_fault=True,
                        is_payment_expected=False,
                        is_reimbursement_required=False,
                        products=[
                            helpers.make_request_product(
                                product_id='product/native/native',
                                product_type='product',
                                value_amount='100',
                            ),
                        ],
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
            ],
            id='OrderCancelled, place fault',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='OrderCreated',
                    external_event_ref=f'{consts.ORDER_NR}/OrderCreated',
                    data=helpers.make_order_created_ie(
                        goods_price='160.00', goods_gmv_amount='160.00',
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
                                        discount_type='marketing',
                                        amount='20.00',
                                        discount_provider='own',
                                    ),
                                    helpers.make_discount(
                                        discount_type='marketing',
                                        amount='20.00',
                                        discount_provider='own',
                                    ),
                                    helpers.make_discount(
                                        discount_type='marketing',
                                        amount='20.00',
                                        discount_provider='place',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            3,
            [
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_cancelled',
                    kind='order_cancelled',
                    data=helpers.make_order_cancelled_data(
                        is_place_fault=False,
                        is_payment_expected=False,
                        is_reimbursement_required=True,
                        products=[
                            helpers.make_request_product(
                                product_id='product/native/native',
                                product_type='product',
                                value_amount='40',
                                payment_type='marketing',
                            ),
                            helpers.make_request_product(
                                product_id='product/native/native',
                                product_type='product',
                                value_amount='100',
                            ),
                        ],
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='160'),
                ),
            ],
            id='OrderCancelled, discount product merge',
        ),
    ],
)
async def test_order_cancelled(
        stq_runner,
        experiments3,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
        expected_requests,
        mock_customer_service_retrieve,
        mock_customer_service_retrieve_new,
        mock_order_revision_list,
        mock_order_revision_list_new,
):
    mock_order_revision_list(revisions=[{'revision_id': '123-321'}])
    mock_order_revision_list_new(revisions=[{'origin_revision_id': '123-321'}])

    experiments3.add_experiment(**helpers.make_use_core_revisions_exp())

    await helpers.input_events_process_test_func(
        stq_runner,
        mock_eats_billing_processor_create,
        insert_billing_input_events,
        input_stq_args,
        input_events,
        expected_input_stq_fail,
        times_called,
        expected_requests,
    )
