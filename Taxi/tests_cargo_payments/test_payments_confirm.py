async def test_happy_path(
        state_performer_found, driver_headers, taxi_cargo_payments,
):
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
        },
        headers=driver_headers,
    )

    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'confirmed'


async def test_revision_conflict(
        state_performer_found, taxi_cargo_payments, driver_headers,
):
    state = await state_performer_found()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision - 1,
        },
        headers=driver_headers,
    )

    assert response.status_code == 409
    # assert response.json()['code'] == 'taximeter_expected_code


async def test_update_confirmed(
        update_items,
        state_payment_created,
        taxi_cargo_payments,
        driver_headers,
):
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        'v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
        },
        headers=driver_headers,
    )
    assert response.status_code == 200

    await update_items(
        status_code=410, payment_id=state.payment_id, snapshot_token='token1',
    )

    # assert response.json()['code'] == 'taximeter_expected_code


async def test_confirm_confirmed(
        state_payment_confirmed, taxi_cargo_payments, driver_headers,
):
    # Test cases from CARGODEV-3402
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
        },
        headers=driver_headers,
    )
    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
            'payment_method': 'link',
        },
        headers=driver_headers,
    )
    assert response.status_code == 409
    assert response.json()['code'] == 'wait_another_payment'

    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision + 1,
        },
        headers=driver_headers,
    )
    assert response.status_code == 409


async def test_wrong_performer(
        state_performer_found, driver_headers, taxi_cargo_payments,
):
    state = await state_performer_found()

    driver_headers['X-YaTaxi-Driver-Profile-Id'] = 'anotherone'
    response = await taxi_cargo_payments.post(
        'driver/v1/cargo-payments/v1/payment/confirm',
        json={
            'payment_id': state.payment_id,
            'revision': state.payment_revision,
        },
        headers=driver_headers,
    )

    assert response.status_code == 403
