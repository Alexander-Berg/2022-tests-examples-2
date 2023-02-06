from eats_corp_orders.stq import cancel


async def test_success(
        stq3_context,
        stq,
        order_id,
        mock_eats_payments_py3,
        load_json,
        check_redis_array,
        check_order_status_db,
        terminal_id,
        idempotency_key,
):
    @mock_eats_payments_py3('/v1/orders/retrieve')
    async def retrieve_handler(request):
        assert request.json == {'id': order_id}
        return load_json('eats_payments_retrieve_order.json')

    @mock_eats_payments_py3('/v1/orders/cancel')
    async def cancel_handler(request):
        assert request.json == {
            'id': order_id,
            'revision': order_id,
            'version': 2,
        }
        return {}

    check_order_status_db(order_id, 'new', False)

    await cancel.task(stq3_context, order_id)

    check_order_status_db(order_id, 'new', True)

    assert retrieve_handler.has_calls
    assert cancel_handler.has_calls
    assert stq.eats_corp_orders_billing_events.has_calls
