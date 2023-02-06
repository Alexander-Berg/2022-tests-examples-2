BEGIN;

ALTER TABLE eats_surge_notify.subscriptions
    ADD COLUMN IF NOT EXISTS region_id INTEGER DEFAULT NULL;

CREATE TYPE eats_surge_notify.subscription_v4 AS (
    eater_id TEXT,
    session_id TEXT,
    place_id TEXT,
    place_slug TEXT,
    place_name TEXT,
    place_business_type TEXT,
    locale TEXT,
    surge_level INTEGER,
    location POINT,
    region_id INTEGER,
    device_id TEXT,
    personal_phone_id TEXT,
    idempotency_token TEXT,
    delivery_time TIMESTAMPTZ
);

COMMIT;
