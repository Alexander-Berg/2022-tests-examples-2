import pytest

from tests_grocery_communications import consts
from tests_grocery_communications import models


@pytest.mark.parametrize('found_in_db', [True, False])
async def test_basic(pgsql, taxi_grocery_communications, found_in_db):
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
    if found_in_db:
        notifications_availability = models.NotificationsAvailability(
            pgsql=pgsql,
            order_id=consts.ORDER_ID,
            taxi_user_id=consts.TAXI_USER_ID,
            are_notifications_available='yes',
            features=features,
        )
        notifications_availability.update_db()

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/get-notifications-options',
        json={'order_id': consts.ORDER_ID},
    )
    assert response.status_code == 200

    if found_in_db:
        are_notifications_available = 'yes'
    else:
        are_notifications_available = 'unknown'
    assert response.json() == {
        'are_notifications_available': are_notifications_available,
    }
