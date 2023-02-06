BEGIN TRANSACTION;

CREATE SCHEMA product_session;

CREATE TABLE product_session.user_session (
    id BIGSERIAL PRIMARY KEY,
    yandex_uid TEXT NOT NULL,
    visited_places JSONB NOT NULL,
    seen_recommendations JSONB NOT NULL,
    created TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TYPE product_session.user_session_v1 AS (
    id BIGINT,
    yandex_uid TEXT,
    visited_places JSONB,
    seen_recommendations JSONB,
    created TIMESTAMPTZ,
    updated TIMESTAMPTZ
);

CREATE INDEX idx__product_session__user_session__yandex_uid
    ON product_session.user_session(yandex_uid);

CREATE INDEX idx__product_session__user_session__created
    ON product_session.user_session(created);

CREATE INDEX idx__product_session__user_session__updated
    ON product_session.user_session(updated);

COMMIT TRANSACTION;
