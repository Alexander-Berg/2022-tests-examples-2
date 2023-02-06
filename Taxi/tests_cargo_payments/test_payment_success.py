import uuid


async def test_callback_app_basic(
        state_payment_confirmed,
        payment_success,
        exp_cargo_payments_nfc_callback,
):
    """
        Check happypath nfc callback.
    """
    state = await state_payment_confirmed()

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'authorized'


async def test_callback_app_status_new(state_agent_unblocked, payment_success):
    """
        Check happypath new -> authorized.
    """
    state = await state_agent_unblocked()

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'authorized'


async def test_callback_app_2can_authorized(
        state_agent_unblocked, load_json_var, taxi_cargo_payments, get_payment,
):
    """
        Check happypath new -> authorized.
    """
    state = await state_agent_unblocked()

    response = await taxi_cargo_payments.post(
        '2can/status',
        json=load_json_var(
            'pay_event.json', payment_id=state.payment_id, amount='40',
        ),
    )
    assert response.status_code == 200

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'


async def test_callback_app_api_validation(
        state_payment_confirmed,
        payment_success,
        exp_cargo_payments_nfc_callback,
        get_last_transaction,
):
    """
        Check nfc callback with api validation.
    """
    await exp_cargo_payments_nfc_callback(api_validation=True)
    state = await state_payment_confirmed()

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'authorized'
    assert (
        get_last_transaction(state.payment_id)['transaction_id']
        == transaction_id
    )


async def test_fallback_error(
        state_payment_confirmed,
        payment_success,
        exp_cargo_payments_nfc_callback,
        mock_payment_transaction_id,
):
    """
        Check status not changed if validation not passed.
    """
    await exp_cargo_payments_nfc_callback(api_validation=True)
    state = await state_payment_confirmed()

    mock_payment_transaction_id.transactions = []

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'confirmed'


async def test_fallback_ok(
        state_payment_confirmed,
        payment_success,
        exp_cargo_payments_nfc_callback,
        mock_payment_transaction_id,
):
    """
        Check payment authorized without validation if
        fallback is ok.
    """
    await exp_cargo_payments_nfc_callback(
        api_validation=True, api_validation_fallback='ok',
    )
    state = await state_payment_confirmed()

    mock_payment_transaction_id.transactions = []

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'authorized'


async def test_fallback_stq(
        state_payment_confirmed,
        payment_success,
        get_payment,
        exp_cargo_payments_nfc_callback,
        mock_payment_transaction_id,
        autorun_stq,
        get_last_transaction,
):
    """
        Check validation fallback stq flow.
        -> nfc_callback
        -> validation via api failed
        -> set up stq
        -> check stq stored transaction
    """
    await exp_cargo_payments_nfc_callback(
        api_validation=True, api_validation_fallback='async_retry',
    )
    state = await state_payment_confirmed()

    # failed on callback, retry in stq
    mock_payment_transaction_id.status_code = 500

    transaction_id = str(uuid.uuid4())
    response = await payment_success(
        payment_id=state.payment_id, transaction_id=transaction_id,
    )

    assert response['payment']['status'] == 'confirmed'
    assert get_last_transaction(state.payment_id) is None

    mock_payment_transaction_id.status_code = 200
    await autorun_stq('cargo_payments_2can_transaction_status')

    # check payment status is changed,transaction data updated,
    # transaction stored
    response = await get_payment(payment_id=state.payment_id)
    assert response['status'] == 'authorized'
    assert 'rrn' in response['fiscal_data']
    assert (
        get_last_transaction(state.payment_id)['transaction_id']
        == transaction_id
    )
