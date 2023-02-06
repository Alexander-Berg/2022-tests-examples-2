import json

SELECT_NOTIFICATION_SQL = """
SELECT
    order_id,
    x_yandex_login,
    tanker_key,
    notification_type,
    notification_title,
    notification_text,
    intent,
    source,
    personal_phone_id,
    taxi_user_id,
    delivered
FROM communications.notifications
WHERE order_id = %s
"""

SELECT_DEFERRED_NOTIFICATION_SQL = """
SELECT
    order_id,
    group_type,
    notification_type,
    is_sent,
    payload
FROM communications.deferred_notifications
WHERE order_id = %s AND group_type = %s AND notification_type = %s
"""

SELECT_NOTIFICATIONS_AVAILABILITY_SQL = """
SELECT
    order_id,
    taxi_user_id,
    are_notifications_available,
    features
FROM communications.notifications_availability
WHERE order_id = %s
"""

INSERT_NOTIFICATION_SQL = """
INSERT INTO communications.notifications AS notification (order_id,
                                                          x_yandex_login,
                                                          tanker_key,
                                                          notification_type,
                                                          notification_title,
                                                          notification_text,
                                                          intent,
                                                          source,
                                                          personal_phone_id,
                                                          taxi_user_id,
                                                          delivered)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT DO NOTHING
"""

INSERT_DEFERRED_NOTIFICATION_SQL = """
INSERT INTO communications.deferred_notifications AS notification (
    order_id,
    group_type,
    notification_type,
    is_sent,
    payload
)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (order_id, group_type, notification_type) DO NOTHING
"""

INSERT_NOTIFICATIONS_AVAILABILITY_SQL = """
INSERT INTO communications.notifications_availability AS notification (
    order_id,
    taxi_user_id,
    are_notifications_available,
    features
)
VALUES (%s, %s, %s, %s)
ON CONFLICT DO NOTHING
"""

SELECT_EMAILS_SQL = """
SELECT
    grocery_email_id,
    yandex_uid,
    personal_email_id,
    deleted,
    source,
    maillist_slug
FROM communications.emails
WHERE yandex_uid = %s
"""

INSERT_EMAILS_SQL = """
INSERT INTO communications.emails
    (yandex_uid, personal_email_id, updated, deleted, source, maillist_slug)
VALUES (%s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
RETURNING grocery_email_id
"""


class Notification:
    def __init__(
            self,
            pgsql,
            order_id,
            x_yandex_login=None,
            tanker_key=None,
            notification_type=None,
            notification_title=None,
            notification_text=None,
            intent=None,
            source=None,
            personal_phone_id=None,
            taxi_user_id=None,
            delivered=None,
    ):
        self.pg_db = pgsql['grocery_communications']
        self.order_id = order_id
        self.x_yandex_login = x_yandex_login
        self.tanker_key = tanker_key
        self.notification_type = notification_type
        self.notification_title = notification_title
        self.notification_text = notification_text
        self.intent = intent
        self.source = source
        self.personal_phone_id = personal_phone_id
        self.taxi_user_id = taxi_user_id
        self.delivered = delivered

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_NOTIFICATION_SQL, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_id,
            x_yandex_login,
            tanker_key,
            notification_type,
            notification_title,
            notification_text,
            intent,
            source,
            personal_phone_id,
            taxi_user_id,
            delivered,
        ) = result

        self.order_id = order_id
        self.x_yandex_login = x_yandex_login
        self.tanker_key = tanker_key
        self.notification_type = notification_type
        self.notification_title = notification_title
        self.notification_text = notification_text
        self.intent = intent
        self.source = source
        self.personal_phone_id = personal_phone_id
        self.taxi_user_id = taxi_user_id
        self.delivered = delivered

    def insert(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_NOTIFICATION_SQL,
            [
                self.order_id,
                self.x_yandex_login,
                self.tanker_key,
                self.notification_type,
                self.notification_title,
                self.notification_text,
                self.intent,
                self.source,
                self.personal_phone_id,
                self.taxi_user_id,
                self.delivered,
            ],
        )


class DeferredNotification:
    def __init__(
            self,
            pgsql,
            order_id,
            group_type='assigned_courier',
            notification_type='courier_picked_up_order',
            is_sent=False,
            payload=None,
    ):
        self.pg_db = pgsql['grocery_communications']
        self.order_id = order_id
        self.group_type = group_type
        self.notification_type = notification_type
        self.is_sent = is_sent
        self.payload = payload

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_DEFERRED_NOTIFICATION_SQL,
            [
                self.order_id,
                self.group_type,
                self.notification_type,
                self.is_sent,
                json.dumps(self.payload),
            ],
        )

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            SELECT_DEFERRED_NOTIFICATION_SQL,
            [self.order_id, self.group_type, self.notification_type],
        )
        result = cursor.fetchone()
        assert result
        (order_id, group_type, notification_type, is_sent, payload) = result

        assert self.order_id == order_id
        assert self.group_type == group_type
        assert self.notification_type == notification_type
        assert self.is_sent == is_sent
        if not (payload == {} and self.payload is None):
            assert self.payload == payload


class NotificationsAvailability:
    def __init__(
            self,
            pgsql,
            order_id,
            taxi_user_id,
            are_notifications_available,
            features,
    ):
        self.pg_db = pgsql['grocery_communications']
        self.order_id = order_id
        self.taxi_user_id = taxi_user_id
        self.are_notifications_available = are_notifications_available
        self.features = features

    def update_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_NOTIFICATIONS_AVAILABILITY_SQL,
            [
                self.order_id,
                self.taxi_user_id,
                self.are_notifications_available,
                json.dumps(self.features),
            ],
        )

    def compare_with_db(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_NOTIFICATIONS_AVAILABILITY_SQL, [self.order_id])
        result = cursor.fetchone()
        assert result
        (
            order_id,
            taxi_user_id,
            are_notifications_available,
            features,
        ) = result

        assert self.order_id == order_id
        assert self.taxi_user_id == taxi_user_id
        assert self.are_notifications_available == are_notifications_available
        assert self.features == features


class Emails:
    def __init__(
            self,
            pgsql,
            grocery_email_id=None,
            personal_email_id=None,
            yandex_uid=None,
            deleted=False,
            source='user',
            maillist_slug=None,
    ):
        self.pg_db = pgsql['grocery_communications']
        self.grocery_email_id = grocery_email_id
        self.personal_email_id = personal_email_id
        self.yandex_uid = yandex_uid
        self.deleted = deleted
        self.source = source
        self.maillist_slug = maillist_slug

    def update(self):
        cursor = self.pg_db.cursor()
        cursor.execute(SELECT_EMAILS_SQL, [self.yandex_uid])
        result = cursor.fetchone()
        if result is None:
            self.grocery_email_id = None
            self.personal_email_id = None
            return
        (
            grocery_email_id,
            yandex_uid,
            personal_email_id,
            deleted,
            source,
            maillist_slug,
        ) = result
        self.grocery_email_id = grocery_email_id
        self.yandex_uid = yandex_uid
        self.personal_email_id = personal_email_id
        self.deleted = deleted
        self.source = source
        self.maillist_slug = maillist_slug

    def insert(self):
        cursor = self.pg_db.cursor()
        cursor.execute(
            INSERT_EMAILS_SQL,
            [
                self.yandex_uid,
                self.personal_email_id,
                self.deleted,
                self.source,
                self.maillist_slug,
            ],
        )
        result = cursor.fetchone()
        assert result
        print(self.__dict__)
        self.grocery_email_id = result[0]
