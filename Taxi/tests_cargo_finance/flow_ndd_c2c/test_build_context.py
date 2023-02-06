async def test_order_context(
        mock_py2_fiscal_data,
        mock_py2_products,
        mock_logistic_platform_c2c_payment_context,
        build_billing_context,
        get_event,
):
    ndd_order_id = '123'
    order_context = await build_billing_context(ndd_order_id)

    expected_context = get_event('billing_context')['payload']['data']
    order_context['due'] = expected_context['due']
    assert order_context == expected_context
