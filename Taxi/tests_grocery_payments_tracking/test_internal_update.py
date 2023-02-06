import pytest

from tests_grocery_payments_tracking import consts


@pytest.fixture(name='internal_tracking_update')
async def _internal_tracking_update(taxi_grocery_payments_tracking):
    async def _inner(payload):
        request = {'order_id': consts.ORDER_ID, 'payload': payload}

        response = await taxi_grocery_payments_tracking.post(
            '/internal/v1/payments-tracking/update', json=request,
        )

        assert response.status_code == 200

    return _inner


@pytest.mark.parametrize('payload', [consts.CARD_PAYLOAD])
async def test_insert(
        internal_tracking_update, grocery_payments_tracking_db, payload,
):
    await internal_tracking_update(payload=payload)

    payment = grocery_payments_tracking_db.get_payment()

    assert payment is not None
    assert payment.order_id == consts.ORDER_ID
    assert payment.status == 'wait_user_action'
    assert payment.payload == payload


@pytest.mark.parametrize('payload', [consts.CARD_PAYLOAD])
@pytest.mark.parametrize(
    'existing_status, expected_status',
    [('init', 'wait_user_action'), ('fail', 'fail')],
)
async def test_update(
        internal_tracking_update,
        grocery_payments_tracking_db,
        payload,
        existing_status,
        expected_status,
):
    grocery_payments_tracking_db.insert_payment(status=existing_status)

    await internal_tracking_update(payload=payload)

    payment = grocery_payments_tracking_db.get_payment()

    assert payment is not None
    assert payment.order_id == consts.ORDER_ID
    assert payment.status == expected_status
    assert payment.payload == payload
