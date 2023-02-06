import pytest

from tests_grocery_payments_tracking import consts


@pytest.fixture(name='internal_tracking_update_status')
async def _internal_tracking_update_status(taxi_grocery_payments_tracking):
    async def _inner(status):
        request = {'order_id': consts.ORDER_ID, 'status': status}

        response = await taxi_grocery_payments_tracking.post(
            '/internal/v1/payments-tracking/update-status', json=request,
        )

        assert response.status_code == 200

    return _inner


@pytest.mark.parametrize('status', ['fail', 'success', 'cancel'])
async def test_insert(
        internal_tracking_update_status, grocery_payments_tracking_db, status,
):
    await internal_tracking_update_status(status=status)

    payment = grocery_payments_tracking_db.get_payment()

    assert payment is not None
    assert payment.order_id == consts.ORDER_ID
    assert payment.status == status


@pytest.mark.parametrize('status', ['fail', 'success', 'cancel'])
@pytest.mark.parametrize(
    'existing_status, expected_status',
    [
        ('init', 'status'),
        ('wait_user_action', 'status'),
        ('success', 'success'),
        ('cancel', 'cancel'),
        ('fail', 'fail'),
    ],
)
async def test_update(
        internal_tracking_update_status,
        grocery_payments_tracking_db,
        status,
        existing_status,
        expected_status,
):
    grocery_payments_tracking_db.insert_payment(status=existing_status)

    await internal_tracking_update_status(status=status)

    payment = grocery_payments_tracking_db.get_payment()

    assert payment is not None
    assert payment.order_id == consts.ORDER_ID
    assert (
        payment.status == status
        if expected_status == 'status'
        else expected_status
    )
