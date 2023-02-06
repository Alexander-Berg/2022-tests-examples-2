import pytest

from tests_grocery_communications import consts
from tests_grocery_communications import models

ORDER_ID = '123'
X_YANDEX_LOGIN = 'some_login'
TANKER_KEY = 'some key'
NOTIFICATION_TYPE = 'sms'
NOTIFICATION_TEXT = 'some text'
NOTIFICATION_TITLE = 'some title'
INTENT = 'some intent'
SOURCE = 'admin'
PERSONAL_PHONE_ID = '123'
TAXI_USER_ID = '123'


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('notification_type', ['push', 'sms', 'init_chat'])
async def test_basic(pgsql, taxi_grocery_communications, notification_type):

    notifications = models.Notification(
        pgsql,
        order_id=ORDER_ID,
        x_yandex_login=X_YANDEX_LOGIN,
        tanker_key=TANKER_KEY,
        notification_type=notification_type,
        notification_text=NOTIFICATION_TEXT,
        notification_title=NOTIFICATION_TITLE,
        intent=INTENT,
        source=SOURCE,
        personal_phone_id=PERSONAL_PHONE_ID,
        taxi_user_id=TAXI_USER_ID,
        delivered=True,
    )

    notifications.insert()

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/get-logged-notifications',
        json={'order_id': '123'},
    )

    assert response.status_code == 200

    logged_notifications = response.json()
    notification = logged_notifications['notifications'][0]

    assert notification['delivered']
    assert notification['intent'] == INTENT
    assert notification['notification_type'] == notification_type
    assert notification['order_id'] == ORDER_ID
    assert notification['personal_phone_id'] == PERSONAL_PHONE_ID
    assert notification['source'] == SOURCE
    assert notification['tanker_key'] == TANKER_KEY
    assert notification['taxi_user_id'] == TAXI_USER_ID
    assert notification['text'] == NOTIFICATION_TEXT
    assert notification['timestamp'] is not None
    assert notification['title'] == NOTIFICATION_TITLE
    assert notification['x_yandex_login'] == X_YANDEX_LOGIN


async def test_multiple_notifications(pgsql, taxi_grocery_communications):
    notifications = models.Notification(
        pgsql,
        order_id=ORDER_ID,
        x_yandex_login=X_YANDEX_LOGIN,
        tanker_key=TANKER_KEY,
        notification_type=NOTIFICATION_TYPE,
        notification_text=NOTIFICATION_TEXT,
        notification_title=NOTIFICATION_TITLE,
        intent=INTENT,
        source=SOURCE,
        personal_phone_id=PERSONAL_PHONE_ID,
        taxi_user_id=TAXI_USER_ID,
        delivered=True,
    )

    notifications.insert()
    notifications.insert()
    notifications.insert()

    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/get-logged-notifications',
        json={'order_id': '123'},
    )

    assert response.status_code == 200

    logged_notifications = response.json()
    assert len(logged_notifications['notifications']) == 3


async def test_missing_order(pgsql, taxi_grocery_communications):
    response = await taxi_grocery_communications.post(
        '/admin/communications/v1/support/get-logged-notifications',
        json={'order_id': 'missing_id'},
    )

    assert response.status_code == 200

    logged_notifications = response.json()
    assert not logged_notifications['notifications']
