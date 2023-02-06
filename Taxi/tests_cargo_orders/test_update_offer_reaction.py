DEFAULT_HEADERS = {
    'Accept-Language': 'en',
    'X-Remote-IP': '12.34.56.78',
    'X-YaTaxi-Driver-Profile-Id': 'driver_id1',
    'X-YaTaxi-Park-Id': 'park_id1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.40',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


async def test_acceptance(taxi_cargo_orders, stq, default_order_id):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/update-offer-reaction',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'offer_id': 'new_waybill_1',
            'offer_revision': 3,
            'reaction': 'acceptance',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.cargo_alive_batch_confirmation.times_called == 1
    stq_call = stq.cargo_alive_batch_confirmation.next_call()
    assert stq_call['id'] == 'new_waybill_1_3'

    kwargs = stq_call['kwargs']
    assert kwargs['new_waybill_ref'] == 'new_waybill_1'
    assert kwargs['waybill_revision'] == 3
    assert kwargs['is_offer_accepted']


async def test_rejection(taxi_cargo_orders, stq, default_order_id):
    response = await taxi_cargo_orders.post(
        '/driver/v1/cargo-claims/v1/cargo/update-offer-reaction',
        headers=DEFAULT_HEADERS,
        json={
            'cargo_ref_id': 'order/' + default_order_id,
            'offer_id': 'new_waybill_1',
            'offer_revision': 3,
            'reaction': 'rejection',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.cargo_alive_batch_confirmation.times_called == 1
    stq_call = stq.cargo_alive_batch_confirmation.next_call()
    assert stq_call['id'] == 'new_waybill_1_3'

    kwargs = stq_call['kwargs']
    assert kwargs['new_waybill_ref'] == 'new_waybill_1'
    assert kwargs['waybill_revision'] == 3
    assert not kwargs['is_offer_accepted']
