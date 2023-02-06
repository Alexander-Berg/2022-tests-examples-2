async def test_happy_path(
        state_payment_confirmed, driver_headers, taxi_cargo_payments,
):
    """
        Tests payment's status 'new' after reset-confirm.
    """
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '/v1/admin/payment/reset-confirm',
        params={'payment_id': state.payment_id},
        json={'ticket': 'some ticket', 'comment': 'some comment'},
    )

    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'new'


async def test_idempotency(
        state_payment_confirmed, driver_headers, taxi_cargo_payments,
):
    """
        Test request idempotency.
        200 on retry and same revision on second call
    """
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '/v1/admin/payment/reset-confirm',
        params={'payment_id': state.payment_id},
        json={'ticket': 'some ticket', 'comment': 'some comment'},
    )

    assert response.status_code == 200
    revision = response.json()['revision']

    response = await taxi_cargo_payments.post(
        '/v1/admin/payment/reset-confirm',
        params={'payment_id': state.payment_id},
        json={'ticket': 'some ticket', 'comment': 'some comment'},
    )

    assert response.status_code == 200
    assert revision == response.json()['revision']


async def test_not_allowed(
        state_payment_authorized, driver_headers, taxi_cargo_payments,
):
    """
        Tests payment's status change is not allowed after authorized.
    """
    state = await state_payment_authorized()

    response = await taxi_cargo_payments.post(
        '/v1/admin/payment/reset-confirm',
        params={'payment_id': state.payment_id},
        json={'ticket': 'some ticket', 'comment': 'some comment'},
    )

    assert response.status_code == 410
