BEGIN;

ALTER TABLE product_session.user_session
    ADD COLUMN auth_session TEXT NOT NULL DEFAULT '';

CREATE TYPE product_session.user_session_v2 AS (
    id BIGINT,
    auth_session TEXT,
    yandex_uid TEXT,
    visited_places JSONB,
    seen_recommendations JSONB,
    created TIMESTAMPTZ,
    updated TIMESTAMPTZ
);

CREATE INDEX idx__product_session__user_session__auth_session
    ON product_session.user_session(auth_session);

COMMIT;
