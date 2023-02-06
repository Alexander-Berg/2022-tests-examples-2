CREATE SCHEMA eats_offers;

CREATE TABLE eats_offers.offers(
    session_id TEXT NOT NULL PRIMARY KEY,
    location POINT NOT NULL,
    delivery_time TIMESTAMPTZ,
    request_time TIMESTAMPTZ NOT NULL,
    expiration_time TIMESTAMPTZ NOT NULL,
    prolong_count INTEGER NOT NULL,
    payload JSON NOT NULL
);

-- for removing obsolete offers
CREATE INDEX offers_expiration_time ON eats_offers.offers(expiration_time);

CREATE TYPE eats_offers.offer_v1 AS (
    session_id TEXT,
    location POINT,
    delivery_time TIMESTAMPTZ,
    request_time TIMESTAMPTZ,
    expiration_time TIMESTAMPTZ,
    prolong_count INTEGER,
    payload JSON);

-- MIGRATION 1

ALTER TABLE eats_offers.offers ADD COLUMN user_id TEXT;

CREATE INDEX index_offers_user_id ON eats_offers.offers(user_id);

CREATE TYPE eats_offers.offer_v2 AS (
    session_id TEXT,
    user_id TEXT,
    location POINT,
    delivery_time TIMESTAMPTZ,
    request_time TIMESTAMPTZ,
    expiration_time TIMESTAMPTZ,
    prolong_count INTEGER,
    payload JSON
);

CREATE TABLE eats_offers.users(
    user_id TEXT NOT NULL PRIMARY KEY
);
