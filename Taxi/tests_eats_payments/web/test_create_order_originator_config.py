import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import helpers


@configs.DISABLED_CONFIG
@pytest.mark.tvm2_eats_corp_orders
async def test_crete_order_maintenance_unavailable(
        check_create_order, mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='card', items=items, response_status=503,
    )


@pytest.mark.tvm2_eats_corp_orders
async def test_crete_order_debt_unavailable(
        check_create_order,
        experiments3,
        stq,
        mockserver,
        mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    experiments3.add_config(**helpers.make_debts_experiment(True, True, True))

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/create')
    def transactions_create_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/transactions-eda/v2/invoice/update')
    def transactions_update_invoice_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    # pylint: disable=unused-variable
    # pylint: disable=invalid-name
    @mockserver.json_handler('/user-state/internal/v1/last-payment-methods')
    def user_state_last_payment_methods_handler(request):
        return mockserver.make_response(**{'status': 200, 'json': {}})

    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='card',
        items=items,
        additional_request_part={'originator': consts.DEFAULT_ORIGINATOR},
    )
    helpers.check_callback_mock(
        times_called=0,
        callback_mock=stq.eda_order_processing_payment_events_callback,
        task_id='test_order:debt',
        queue='eda_order_processing_payment_events_callback',
    )
    helpers.check_callback_mock(
        times_called=0,
        callback_mock=stq.eats_payments_debt_check_invoice_status,
        task_id='test_order',
        queue='eats_payments_debt_check_invoice_status',
    )


@pytest.mark.tvm2_eats_corp_orders
async def test_crete_order_payment_method_unavailable(
        check_create_order, mock_api_proxy_4_list_payment_methods,
):
    mock_api_proxy_4_list_payment_methods()
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='cash', items=items, response_status=400,
    )
