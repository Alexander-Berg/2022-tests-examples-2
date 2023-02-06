import uuid


TRANSACTION_ID = 'E54906D4-92A1-43A5-8016-D50F0EEEFB34'


async def test_2can_handler(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        load_json_var,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'fiscal_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'finished'
    assert payment['is_paid']


async def test_wrong_order(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        load_json_var,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var('fiscal_event.json', payment_id=state.payment_id),
    )
    assert response.status_code == 409

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='50',
        ),
    )
    assert response.status_code == 200

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'
    assert payment['is_paid']


async def test_fiscal_data(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        load_json_var,
):
    state = await state_payment_confirmed()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['fiscal_data']['rrn'] == '539107198347'
    assert 'invoice' not in payment['fiscal_data']

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var('fiscal_event.json', payment_id=state.payment_id),
    )
    assert response.status_code == 200
    payment = await get_payment(state.payment_id)
    assert payment['fiscal_data']['rrn'] == '539107198347'
    assert payment['fiscal_data']['invoice'] == '43V7LGPAK7EF'
    assert (
        payment['fiscal_data']['invoice_link']
        == 'http://ofd.net//0000000020005880/112/3910020199'
    )


async def test_callback_after_fast_nfc(
        state_payment_confirmed,
        payment_success,
        get_payment,
        exp_cargo_payments_nfc_callback,
        taxi_cargo_payments,
        load_json_var,
        get_last_transaction,
):
    """
        Check transaction is stored in the case of
        fast nfc flow.
    """
    await exp_cargo_payments_nfc_callback()
    state = await state_payment_confirmed()

    response = await payment_success(
        payment_id=state.payment_id, transaction_id=TRANSACTION_ID,
    )

    assert response['payment']['status'] == 'authorized'

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    # check payment status is changed,transaction data updated,
    # transaction stored
    response = await get_payment(state.payment_id)
    assert 'rrn' in response['fiscal_data']
    assert (
        get_last_transaction(state.payment_id)['transaction_id']
        == TRANSACTION_ID
    )


async def test_2can_retry_transaction_status(
        mock_payment_transaction_id, state_payment_confirmed, stq_runner, stq,
):
    state = await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())

    mock_payment_transaction_id.status_code = 400

    await stq_runner.cargo_payments_2can_transaction_status.call(
        task_id='retry_2can_status',
        kwargs={
            'payment_id': state.payment_id,
            'transaction_id': transaction_id,
            'service_name': 'test',
        },
    )

    assert stq.cargo_payments_2can_transaction_status.times_called == 1
