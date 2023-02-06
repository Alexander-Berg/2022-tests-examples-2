BEGIN;

ALTER TABLE eats_surge_notify.subscriptions
    ADD COLUMN delivery_time TIMESTAMPTZ DEFAULT NULL;

CREATE TYPE eats_surge_notify.subscription_v2 AS (
    eater_id TEXT,
    session_id TEXT,
    place_id TEXT,
    place_slug TEXT,
    locale TEXT,
    surge_level INTEGER,
    location POINT,
    device_id TEXT,
    personal_phone_id TEXT,
    idempotency_token TEXT,
    delivery_time TIMESTAMPTZ
);

COMMIT;
