import pytest

from tests_eats_orders_billing import consts
from tests_eats_orders_billing import helpers


@pytest.mark.parametrize(
    'input_stq_args, input_events,expected_input_stq_fail,'
    'times_called,expected_requests',
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
                    kind='FineAppeal',
                    external_event_ref=f'{consts.ORDER_NR}/FineAppeal/1',
                    data=helpers.make_fine_appeal_ie(amount='50.00'),
                ),
            ],
            # expected_input_stq_fail
            False,
            2,
            [
                helpers.make_create_request(
                    external_id=f'FineAppeal/'
                    f'{consts.ORDER_NR}/{consts.FINE_ID}',
                    kind='fine_appeal',
                    data=helpers.make_fine_appeal_data(
                        amount='50', product_id='product/native/native',
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
            ],
            id='Test happy path',
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
                        products=[],
                    ),
                ),
                helpers.make_db_row(
                    kind='FineAppeal',
                    external_event_ref=f'{consts.ORDER_NR}/FineAppeal/1',
                    data=helpers.make_fine_appeal_ie(
                        amount='100.00', fine_reason='cancel',
                    ),
                ),
                helpers.make_db_row(
                    kind='AccountingCorrection',
                    external_event_ref=f'{consts.ORDER_NR}/'
                    f'AccountingCorrection/1',
                    data=helpers.make_accounting_correction_ie(
                        amount='50.00',
                        correction_id='1',
                        account_correction_type='goods',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            4,
            [
                helpers.make_create_request(
                    external_id=f'FineAppeal/'
                    f'{consts.ORDER_NR}/{consts.FINE_ID}',
                    kind='fine_appeal',
                    data=helpers.make_fine_appeal_data(
                        amount='100',
                        product_id='product/native/native',
                        fine_reason='cancel',
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCancelled/{consts.ORDER_NR}'
                    f'/order_cancelled',
                    kind='order_cancelled',
                    data=helpers.make_order_cancelled_data(
                        is_place_fault=True,
                        is_payment_expected=False,
                        is_reimbursement_required=False,
                        products=[],
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'AccountingCorrection/{consts.ORDER_NR}/1'
                    f'/order_gmv/1',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='50'),
                ),
            ],
            id='Test appeal + correction',
        ),
        pytest.param(
            # input_stq_args
            helpers.make_events_process_stq_args(consts.ORDER_NR),
            [
                helpers.make_db_row(
                    kind='FineAppeal',
                    external_event_ref=f'{consts.ORDER_NR}/FineAppeal/1',
                    data=helpers.make_fine_appeal_ie(amount='50.00'),
                ),
            ],
            # expected_input_stq_fail
            True,
            0,
            [],
            id='Test fail',
        ),
    ],
)
async def test_order_cancelled(
        stq_runner,
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
        experiments3,
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
