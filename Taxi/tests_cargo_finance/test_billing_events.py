FLOW_CLAIMS = 'claims'
FLOW_TAXI_PARK = 'taxi_park'
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/'
    'upsert?flow={}&entity_id=test_id'
)


async def test_cargo_claim(
        taxi_cargo_finance, load_json, mock_v2_process_async,
):
    request = {
        'revision': 123,
        'is_service_complete': True,
        'taxi': {
            'taxi_order_id': 'test_order_id',
            'claims_agent_payments': load_json(
                'flow_claims/s2p_billing_cargo_claim.json',
            ),
        },
    }
    response = await taxi_cargo_finance.post(
        UPSERT_URI.format(FLOW_CLAIMS), json=request,
    )
    assert response.status == 200
    assert mock_v2_process_async.times_called == 1


async def test_cargo_order(
        taxi_cargo_finance, load_json, mock_v2_process_async,
):
    request = {
        'revision': 123,
        'is_service_complete': True,
        'taxi_park': {
            'batch_order_event': load_json(
                'flow_taxi_park/s2p_batch_order_event.json',
            ),
        },
    }
    response = await taxi_cargo_finance.post(
        UPSERT_URI.format(FLOW_TAXI_PARK), json=request,
    )
    assert response.status == 200
    assert mock_v2_process_async.times_called == 1
