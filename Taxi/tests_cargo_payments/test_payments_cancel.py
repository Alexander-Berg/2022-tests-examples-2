async def test_happy_path(
        state_payment_created,
        driver_headers,
        taxi_cargo_payments,
        cancel_payment,
):
    state = await state_payment_created()
    await cancel_payment(payment_id=state.payment_id)

    response = await taxi_cargo_payments.post(
        'v1/payment/info', params={'payment_id': state.payment_id},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'canceled'


async def test_idempotency(
        state_payment_created, driver_headers, taxi_cargo_payments,
):
    """
        Test request idempotency.
        200 on retry and same revision on second call
    """
    state = await state_payment_created()

    response = await taxi_cargo_payments.post(
        '/v1/payment/cancel', json={'payment_id': state.payment_id},
    )

    assert response.status_code == 200
    revision = response.json()['revision']

    response = await taxi_cargo_payments.post(
        '/v1/payment/cancel', json={'payment_id': state.payment_id},
    )

    assert response.status_code == 200
    assert revision == response.json()['revision']


async def test_expired_payment_cancel(
        state_payment_authorized, taxi_cargo_payments, mocked_time,
):
    """
    Check that after expiration time, order is not canceled
    """
    state = await state_payment_authorized()

    mocked_time.sleep(3600 * 24 * 60)  # 60 days
    response = await taxi_cargo_payments.post(
        'v1/payment/cancel', json={'payment_id': state.payment_id},
    )
    assert response.status_code == 404


async def test_stq_check_if_canceled_refund_operation_main_case(
        state_payment_confirmed,
        load_json_var,
        taxi_cargo_payments,
        get_active_operations,
        stq,
        stq_runner,
        cancel_payment,
):
    """
    Main use case of stq:
      1. Payment was confirmed
      2. 2can callback is late, so user cancels the payment
      3. 2can callback comes through and we init refund
    """
    state = await state_payment_confirmed()

    await cancel_payment(payment_id=state.payment_id)

    operations = get_active_operations()
    assert len(operations) == 1

    await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert stq.cargo_payments_autorefund_canceled.times_called == 1
    await stq_runner.cargo_payments_autorefund_canceled.call(
        task_id='test',
        kwargs={'payment_id': state.payment_id, 'source': 'test'},
    )

    operations = get_active_operations()
    assert len(operations) == 2
    assert operations[-1]['refund_id'] == ''
