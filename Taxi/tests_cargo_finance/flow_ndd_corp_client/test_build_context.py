async def test_order_billing_context_delivery_client_b2b_logistics_payment(
        build_order_billing_context_client_b2b, get_event,
):
    order_billing_context = (
        await build_order_billing_context_client_b2b()  # noqa: E501
    )

    assert (
        order_billing_context['context']
        == get_event(
            'order_billing_context_delivery_client_b2b_logistics_payment',
        )['payload']['data']
    )


async def test_order_billing_context_delivery_client_b2b_logistics_payment_request(  # noqa: E501
        build_order_billing_context_client_b2b,
        mock_build_order_billing_context_client_b2b,
        ndd_order_id,
):
    await build_order_billing_context_client_b2b()

    assert (
        mock_build_order_billing_context_client_b2b.times_called  # noqa: E501
        == 1
    )
    request = (
        mock_build_order_billing_context_client_b2b.next_call()[  # noqa: E501
            'request'
        ]
    )
    assert request.query == {
        'event_kind': 'delivery_client_b2b_logistics_payment',
        'ndd_order_id': ndd_order_id,
    }
