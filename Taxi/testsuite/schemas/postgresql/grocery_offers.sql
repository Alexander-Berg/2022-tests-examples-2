BEGIN;

CREATE SCHEMA offers;

CREATE TABLE offers.offers(
    offer_id TEXT NOT NULL PRIMARY KEY,
    created TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due TIMESTAMPTZ NOT NULL,
    tag TEXT NOT NULL,
    params JSONB NOT NULL,
    payload JSONB NOT NULL
);

-- for searching
CREATE INDEX offers_tag_created ON offers.offers (tag, created);
CREATE INDEX offers_tag_params_created ON offers.offers (tag, params, created);

-- for removing obsolete offers
CREATE INDEX offers_due ON offers.offers(due);

COMMIT;

CREATE TYPE offers.offer_v1 AS (
    offer_id TEXT,
    due TIMESTAMPTZ,
    tag TEXT,

    -- fixme: move to jsonb when driver supports it
    params JSON,
    payload JSON);

CREATE TYPE offers.id_and_tag AS (
    id TEXT,
    tag TEXT);

CREATE TYPE offers.tag_and_params AS (
    tag TEXT,

    -- fixme: move to jsonb when driver supports it
    params JSON);
