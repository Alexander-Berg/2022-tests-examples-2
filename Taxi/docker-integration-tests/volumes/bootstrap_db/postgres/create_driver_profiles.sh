#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
CREATE DATABASE driver_profiles;
\connect driver_profiles

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

CREATE SCHEMA driver_profiles;

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';

SET default_tablespace = '';

SET default_with_oids = false;

CREATE TABLE IF NOT EXISTS driver_profiles.streams_status(
  stream_id TEXT NOT NULL UNIQUE,
  cursor TEXT,
  PRIMARY KEY(stream_id)
);

CREATE TABLE IF NOT EXISTS driver_profiles.distlock_importer(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS driver_profiles.queue_imports (
  park_driver_id TEXT NOT NULL UNIQUE,
  label BOOL DEFAULT FALSE,
  cursor TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS queue_imports_park_driver_id_idx ON driver_profiles.queue_imports(park_driver_id);
CREATE INDEX IF NOT EXISTS queue_imports_cursor_idx ON driver_profiles.queue_imports(cursor);

CREATE TABLE IF NOT EXISTS driver_profiles.queue_worker (LIKE driver_profiles.queue_imports INCLUDING ALL);

EOSQL
