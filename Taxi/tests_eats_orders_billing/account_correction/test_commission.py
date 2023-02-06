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
                    kind='OrderDelivered',
                    external_event_ref=f'{consts.ORDER_NR}/OrderDelivered',
                    data=helpers.make_order_delivered_ie(),
                ),
                helpers.make_db_row(
                    kind='TLogAccountingCorrection',
                    external_event_ref=f'/TLogAccountingCorrection/'
                    f'{consts.ORDER_NR}/1',
                    data=helpers.make_tlog_accounting_correction(
                        amount='50.00',
                        correction_id='1',
                        correction_type='commission_marketplace',
                        correction_group='commission',
                        originator='tariff_editor',
                        product='eats_order_commission_marketplace',
                        detailed_product='eats_order_commission_marketplace',
                    ),
                ),
            ],
            # expected_input_stq_fail
            False,
            4,
            [
                helpers.make_create_request(
                    external_id=f'CommissionAccountingCorrection/1',
                    kind='commission_accounting_correction',
                    data=helpers.make_commission_correction(
                        amount='50',
                        correction_id='1',
                        originator='tariff_editor',
                        product='eats_order_commission_marketplace',
                        detailed_product='eats_order_commission_marketplace',
                    ),
                ),
                helpers.make_create_request(
                    external_id=f'OrderCreated/{consts.ORDER_NR}',
                    kind='order_created',
                    data=helpers.make_order_created_data(),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_gmv',
                    kind='order_gmv',
                    data=helpers.make_order_gmv_data(gmv_amount='100'),
                ),
                helpers.make_create_request(
                    external_id=f'OrderDelivered/{consts.ORDER_NR}'
                    f'/order_delivered',
                    kind='order_delivered',
                    data=helpers.make_order_delivered_data(),
                ),
            ],
            id='Test accounting correction commission, happy path',
        ),
    ],
)
async def test_payments(
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
