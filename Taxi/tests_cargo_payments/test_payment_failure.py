async def test_payment_failure(
        taxi_cargo_payments,
        state_payment_confirmed,
        payment_success,
        payment_failure,
        exp_cargo_payments_nfc_callback,
        mock_payment_transaction_id,
        driver_headers,
):
    """
        Check status not changed if validation not passed.
    """
    await exp_cargo_payments_nfc_callback(api_validation=True)
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert 'timer' in json['ui']

    response = await payment_failure(
        payment_id=state.payment_id, payment_revision=1,
    )

    assert 'timer' not in response['ui']

    mock_payment_transaction_id.transactions = []

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/state',
        json={'payment_id': state.payment_id},
        headers=driver_headers,
    )

    assert response.status_code == 200
    json = response.json()
    assert 'timer' not in json['ui']
