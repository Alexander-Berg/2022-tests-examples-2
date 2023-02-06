UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/'
    'upsert?flow=claims&entity_id=test_id'
)


async def test_completed_amended(taxi_cargo_finance, load_json, mockserver):
    @mockserver.json_handler('/billing-orders/v1/process_event')
    def _handler(request):
        return mockserver.make_response(status=200, json={'doc': {'id': 123}})

    request = {
        'revision': 123,
        'is_service_complete': True,
        'taxi': {
            'taxi_order_id': 'test_order_id',
            'taxi_event': {
                'type': 'order_completed',
                'data': load_json('context.json'),
            },
        },
    }
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert _handler.times_called == 1
