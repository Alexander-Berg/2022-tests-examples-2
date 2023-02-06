async def test_basic_internal(state_payment_created, taxi_cargo_payments):
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        'v1/payment/status', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 200

    json = response.json()
    assert json['payment_id'] == state.payment_id
    assert json['status'] == 'new'
    assert not json['is_paid']
