CREATE SCHEMA communications;

CREATE TYPE communications.notification_type AS ENUM (
    'push',
    'sms',
    'init_chat'
);

CREATE TYPE communications.notification_source AS ENUM (
    'admin',
    'compensation'
);

CREATE TABLE communications.notifications (
    order_id TEXT NOT NULL,
    x_yandex_login TEXT NULL,
    ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tanker_key TEXT NULL,
    notification_type communications.notification_type NOT NULL,
    notification_title TEXT NULL,
    notification_text TEXT NOT NULL,
    intent TEXT NOT NULL,
    source communications.notification_source NOT NULL,
    personal_phone_id TEXT NULL,
    taxi_user_id TEXT NULL,
    delivered BOOLEAN NULL
);

CREATE INDEX notifications_order_id_index ON communications.notifications (order_id);
CREATE INDEX notifications_x_yandex_login_index ON communications.notifications (x_yandex_login);
