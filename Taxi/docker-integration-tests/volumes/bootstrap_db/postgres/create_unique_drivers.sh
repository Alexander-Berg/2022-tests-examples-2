#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE unique_drivers;
\connect unique_drivers

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

CREATE SCHEMA unique_drivers;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE unique_drivers.distlock_importer (
    key text NOT NULL,
    owner text,
    expiration_time timestamp with time zone
);

CREATE TABLE unique_drivers.distlock_events(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE unique_drivers.imports_status (
    worker_id text NOT NULL,
    cursor text NOT NULL
);

CREATE TABLE unique_drivers.queue_imports (
    license text NOT NULL,
    label boolean DEFAULT false,
    cursor text NOT NULL
);

CREATE TABLE unique_drivers.queue_unique_drivers (
    license text NOT NULL,
    label boolean DEFAULT false,
    cursor text NOT NULL
);

CREATE TABLE unique_drivers.workers_status (
    worker_id text NOT NULL,
    cursor text NOT NULL,
    lagging_cursor text NOT NULL
);

ALTER TABLE ONLY unique_drivers.distlock_importer
    ADD CONSTRAINT distlock_importer_pkey PRIMARY KEY (key);

ALTER TABLE ONLY unique_drivers.imports_status
    ADD CONSTRAINT imports_status_pkey PRIMARY KEY (worker_id);

ALTER TABLE ONLY unique_drivers.queue_imports
    ADD CONSTRAINT queue_imports_license_key UNIQUE (license);

ALTER TABLE ONLY unique_drivers.queue_unique_drivers
    ADD CONSTRAINT queue_unique_drivers_license_key UNIQUE (license);

ALTER TABLE ONLY unique_drivers.workers_status
    ADD CONSTRAINT workers_status_pkey PRIMARY KEY (worker_id);

CREATE INDEX queue_imports_cursor_idx ON unique_drivers.queue_imports USING btree (cursor);

CREATE INDEX queue_imports_license_idx ON unique_drivers.queue_imports USING btree (license);

CREATE INDEX queue_unique_drivers_cursor_idx ON unique_drivers.queue_unique_drivers USING btree (cursor);

INSERT INTO unique_drivers.workers_status (worker_id, cursor, lagging_cursor)
VALUES
( 'unique-drivers-importer-worker', '0_0', '0_0'),
( 'unique-drivers-importer-worker-full-update', '0_0', '0_0')
ON CONFLICT DO NOTHING;

EOSQL
