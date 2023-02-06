#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE lookup;
\connect lookup

DROP SCHEMA IF EXISTS lookup CASCADE;

CREATE SCHEMA lookup;

CREATE TABLE lookup.order
(
  id           VARCHAR(64) NOT NULL UNIQUE,
  generation   INTEGER NOT NULL,
  version      INTEGER NOT NULL,
  wave         INTEGER NOT NULL,
  candidate    TEXT        NULL,
  frozen       BOOLEAN     NULL,
  wait_count   INTEGER NOT NULL DEFAULT 0,
  found_count  INTEGER NOT NULL DEFAULT 0,
  updated      TIMESTAMPTZ NOT NULL DEFAULT current_timestamp,
  PRIMARY KEY(id)
);

CREATE INDEX order_updated_idx ON lookup.order (updated);

EOSQL
