BEGIN;

CREATE SCHEMA IF NOT EXISTS eats_surge_notify;

CREATE TABLE IF NOT EXISTS eats_surge_notify.place_update_distlock (
                                             key TEXT PRIMARY KEY,
                                             owner TEXT,
                                             expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS eats_surge_notify.subscriptions(
                              id BIGSERIAL PRIMARY KEY,
                              eater_id TEXT NOT NULL,
                              session_id TEXT NOT NULL,
                              place_id TEXT NOT NULL,
                              place_slug TEXT NOT NULL,
                              locale TEXT NOT NULL,
                              surge_level INTEGER NOT NULL,
                              location POINT NOT NULL,
                              device_id TEXT NOT NULL,
                              personal_phone_id TEXT NOT NULL,
                              idempotency_token TEXT NOT NULL,
                              created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
                              updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- for searching
CREATE INDEX IF NOT EXISTS subscriptions_created_at_idx ON eats_surge_notify.subscriptions (created_at);
CREATE INDEX IF NOT EXISTS subscriptions_updated_at_idx ON eats_surge_notify.subscriptions (updated_at);
CREATE INDEX IF NOT EXISTS subscriptions_eater_id_idx ON eats_surge_notify.subscriptions (eater_id);

ALTER TABLE eats_surge_notify.subscriptions ADD UNIQUE (idempotency_token);

CREATE TYPE eats_surge_notify.subscription_v1 AS (
    eater_id TEXT,
    session_id TEXT,
    place_id TEXT,
    place_slug TEXT,
    locale TEXT,
    surge_level INTEGER,
    location POINT,
    device_id TEXT,
    personal_phone_id TEXT,
    idempotency_token TEXT
);

COMMIT;
