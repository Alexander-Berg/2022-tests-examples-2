# pylint: disable=too-many-lines

import pytest

from tests_eats_payments import helpers


@pytest.mark.tvm2_eats_corp_orders
async def test_create_order_rejected_purchase(
        check_create_order,
        mock_api_proxy_4_list_payment_methods,
        mockserver,
        stq,
):
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

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {'users': [{'uid': {'value': '100500'}}]}

    mock_api_proxy_4_list_payment_methods()
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    await check_create_order(
        payment_type='corp',
        payment_method_id='badge:yandex_badge:RUB',
        items=items,
        response_status=200,
    )
    helpers.check_callback_mock(
        callback_mock=stq.eats_corp_orders_payment_callback,
        task_id='test_order',
        queue='eats_corp_orders_payment_callback',
    )
    assert mock_blackbox.times_called == 1
