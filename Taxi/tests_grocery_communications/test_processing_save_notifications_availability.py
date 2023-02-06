import datetime

import pytest

from tests_grocery_communications import consts
from tests_grocery_communications import models
from tests_grocery_communications import processing_noncrit


@pytest.mark.parametrize('app_name', [consts.APP_IPHONE, consts.MARKET_IPHONE])
async def test_basic(
        pgsql, taxi_grocery_communications, ucommunications, app_name,
):
    features = {
        'is_notifications_enabled_by_system': {
            'value': 'yes',
            'updated_at': '2020-01-01T02:03:00+00:00',
        },
        'is_subscribed': {
            'value': True,
            'updated_at': '2020-01-01T02:03:00+00:00',
        },
    }
    notifications_availability = models.NotificationsAvailability(
        pgsql=pgsql,
        order_id=consts.ORDER_ID,
        taxi_user_id=consts.TAXI_USER_ID,
        are_notifications_available='yes',
        features=features,
    )

    ucommunications.check_request(user_id=consts.TAXI_USER_ID)

    response = await taxi_grocery_communications.post(
        '/processing/v1/save-notifications-availability',
        json={
            'order_id': consts.ORDER_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'app_name': app_name,
        },
    )
    assert response.status_code == 200

    if app_name == consts.APP_IPHONE:
        assert ucommunications.times_user_diagnostics_called() == 1
        notifications_availability.compare_with_db()
    else:
        assert ucommunications.times_user_diagnostics_called() == 0


async def test_empty_user_id(taxi_grocery_communications, ucommunications):
    ucommunications.check_request(user_id='')

    response = await taxi_grocery_communications.post(
        '/processing/v1/save-notifications-availability',
        json={
            'order_id': consts.ORDER_ID,
            'taxi_user_id': '',
            'app_name': consts.APP_IPHONE,
        },
    )
    assert response.status_code == 400

    assert ucommunications.times_user_diagnostics_called() == 0


async def test_response404(taxi_grocery_communications, ucommunications):
    ucommunications.set_error_code(404)

    response = await taxi_grocery_communications.post(
        '/processing/v1/save-notifications-availability',
        json={
            'order_id': consts.ORDER_ID,
            'taxi_user_id': consts.TAXI_USER_ID,
            'app_name': consts.APP_IPHONE,
        },
    )
    assert response.status_code == 400

    assert ucommunications.times_user_diagnostics_called() == 1


@processing_noncrit.NOTIFICATION_CONFIG
@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'now_delta_minutes, should_try', [(-10, False), (10, True)],
)
async def test_stop_retry_after(
        taxi_grocery_communications,
        ucommunications,
        processing,
        now_delta_minutes,
        should_try,
):
    ucommunications.set_error_code(400)

    delta = datetime.timedelta(minutes=now_delta_minutes)
    request_stop_retry_after = consts.NOW_DT + delta
    retry_count = 10

    request = {
        'order_id': consts.ORDER_ID,
        'taxi_user_id': consts.TAXI_USER_ID,
        'app_name': consts.APP_IPHONE,
        'event_policy': {
            'retry_count': retry_count,
            'stop_retry_after': request_stop_retry_after.isoformat(),
            'retry_interval': 30,
        },
    }

    response = await taxi_grocery_communications.post(
        '/processing/v1/save-notifications-availability', json=request,
    )
    assert response.status_code == 200

    if should_try:
        idempotency_token = (
            f'created-non-critical-{consts.ORDER_ID}'
            f'retry-policy-{retry_count + 1}'
        )
    else:
        idempotency_token = None

    processing_payload = processing_noncrit.check_noncrit_event(
        processing,
        consts.ORDER_ID,
        reason='created',
        idempotency_token=idempotency_token,
    )

    if should_try:
        assert ucommunications.times_user_diagnostics_called() == 1
        assert processing_payload is not None
        assert processing_payload['order_id'] == consts.ORDER_ID
    else:
        assert ucommunications.times_user_diagnostics_called() == 0
        assert processing_payload is None
