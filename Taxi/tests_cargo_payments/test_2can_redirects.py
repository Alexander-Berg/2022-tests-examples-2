import datetime
import uuid

import pytest


@pytest.mark.parametrize(
    'paid_at', ['2022-05-27T08:59:23.07', '2022-05-27T08:59:23'],
)
async def test_2can_link_status_redirect(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        stq,
        stq_runner,
        mock_payment_transaction_id,
        paid_at: str,
):
    """
      Returns 200 with OK message if everything is good with transaction.
    """
    mock_payment_transaction_id.date = paid_at

    state = await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())
    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 1,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'OK'
    assert response.json()['status'] == 'ok'
    await stq_runner.cargo_payments_2can_transaction_status.call(
        task_id='%s/%s' % (state.payment_id, transaction_id),
        kwargs={
            'payment_id': state.payment_id,
            'transaction_id': transaction_id,
            'service_name': 'test',
        },
    )

    assert stq.cargo_payments_2can_transaction_status.times_called == 1

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'
    assert payment['paid_at'] == paid_at + '+00:00'


async def test_2can_link_status_redirect_fail(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        stq,
        exp_cargo_payments_2can_redirect_message,
        mock_payment_transaction_id,
):
    """
      Returns reasonable error message if transaction fails.
    """
    state = await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())

    mock_payment_transaction_id.state = 400
    mock_payment_transaction_id.substate = 402
    mock_payment_transaction_id.code = 1

    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 0,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'FAIL'
    assert response.json()['description'] == 'No money.'
    assert response.json()['status'] == 'fail'

    assert stq.cargo_payments_2can_transaction_status.times_called == 0

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'confirmed'


async def test_2can_link_status_redirect_bad_redirect(
        state_payment_confirmed,
        taxi_cargo_payments,
        get_payment,
        stq,
        exp_cargo_payments_2can_redirect_message,
        mock_payment_transaction_id,
):
    """
      Returns 200 with "bad redirect" message on unknown
      state/substate/code combination
    """
    state = await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())

    mock_payment_transaction_id.state = 999
    mock_payment_transaction_id.substate = 999
    mock_payment_transaction_id.code = 1

    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 0,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'BAD REDIRECT'
    assert response.json()['status'] == 'fail'

    assert stq.cargo_payments_2can_transaction_status.times_called == 0

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'confirmed'


async def test_2can_link_status_redirect_404(
        state_payment_confirmed,
        taxi_cargo_payments,
        mock_payment_transaction_id,
):
    """
      Returns 404 on non-existing payment id.
    """
    await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())

    mock_payment_transaction_id.state = 400
    mock_payment_transaction_id.substate = 402
    mock_payment_transaction_id.code = 1

    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': '6' * 32,
            'dm': 0,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 404


async def test_2can_link_status_redirect_idempotency_on_authorized(
        state_payment_authorized,
        taxi_cargo_payments,
        get_payment,
        stq,
        stq_runner,
):
    state = await state_payment_authorized()
    transaction_id = str(uuid.uuid4())
    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 1,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200

    await stq_runner.cargo_payments_2can_transaction_status.call(
        task_id='%s/%s' % (state.payment_id, transaction_id),
        kwargs={
            'payment_id': state.payment_id,
            'transaction_id': transaction_id,
            'service_name': 'test',
        },
    )

    assert stq.cargo_payments_2can_transaction_status.times_called == 1

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'


async def test_2can_link_status_redirect_idempotency_on_created(
        state_payment_created,
        taxi_cargo_payments,
        get_payment,
        stq,
        stq_runner,
):
    state = await state_payment_created()
    transaction_id = str(uuid.uuid4())
    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 1,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200

    await stq_runner.cargo_payments_2can_transaction_status.call(
        task_id='%s/%s' % (state.payment_id, transaction_id),
        kwargs={
            'payment_id': state.payment_id,
            'transaction_id': transaction_id,
            'service_name': 'test',
        },
    )

    assert stq.cargo_payments_2can_transaction_status.times_called == 1

    payment = await get_payment(state.payment_id)
    assert payment['status'] == 'authorized'


async def test_2can_link_status_redirect_paid_at(
        mock_payment_transaction_id,
        state_payment_confirmed,
        taxi_cargo_payments,
        stq,
        stq_runner,
        get_payment,
):
    """
      Check that redirect adds paid_at field for transaction
    """
    state = await state_payment_confirmed()
    transaction_id = str(uuid.uuid4())
    response = await taxi_cargo_payments.post(
        'api/b2b/cargo-payments/2can/link-status',
        params={
            'orderId': state.payment_id,
            'dm': 1,
            'operation': 100,
            'tranId': transaction_id,
        },
    )
    assert response.status_code == 200
    assert response.json()['message'] == 'OK'
    assert response.json()['status'] == 'ok'
    await stq_runner.cargo_payments_2can_transaction_status.call(
        task_id='%s/%s' % (state.payment_id, transaction_id),
        kwargs={
            'payment_id': state.payment_id,
            'transaction_id': transaction_id,
            'service_name': 'test',
        },
    )

    assert stq.cargo_payments_2can_transaction_status.times_called == 1
    assert mock_payment_transaction_id

    paid_at_time = (
        datetime.datetime.fromisoformat(mock_payment_transaction_id.date)
        .replace(tzinfo=datetime.timezone.utc)
        .astimezone(tz=datetime.timezone.utc)
        .isoformat()
    )
    payment = await get_payment(state.payment_id)
    assert payment['paid_at'] == paid_at_time
