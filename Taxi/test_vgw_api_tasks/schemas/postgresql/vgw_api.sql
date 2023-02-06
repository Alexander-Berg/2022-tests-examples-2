-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

DROP SCHEMA IF EXISTS common CASCADE;

CREATE SCHEMA common;

CREATE TYPE common.client_type_t AS ENUM (
  'passenger',
  'driver',
  'dispatcher'
);

CREATE TYPE common.geo_point_t AS (
  lon double precision,
  lat double precision
);

DROP SCHEMA IF EXISTS consumers CASCADE;

CREATE SCHEMA consumers;

CREATE TYPE consumers.consumer_t AS (
  id integer,
  name text,
  enabled boolean,
  quota integer,
  gateway_ids text[]
);

CREATE TABLE consumers.consumers(
  id serial PRIMARY KEY,
  name text NOT NULL,
  enabled boolean NOT NULL,
  quota integer NOT NULL DEFAULT 0
);

CREATE SCHEMA voice_gateways;

CREATE TYPE voice_gateways.info_t AS (
  host text,
  ignore_certificate boolean
);

CREATE TYPE voice_gateways.settings_t AS (
  weight integer,
  disabled boolean,
  name text,
  idle_expires_in integer
);

CREATE TABLE voice_gateways.voice_gateways(
  id text NOT NULL UNIQUE,
  enabled_at timestamptz,
  disabled_at timestamptz,
  info voice_gateways.info_t NOT NULL,
  settings voice_gateways.settings_t NOT NULL,
  token text NOT NULL,
  deleted boolean NOT NULL DEFAULT FALSE,
  PRIMARY KEY(id)
);

CREATE TABLE consumers.consumer_voice_gateways(
  consumer_id integer NOT NULL REFERENCES consumers.consumers(id) ON DELETE CASCADE,
  gateway_id text NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  PRIMARY KEY (consumer_id, gateway_id)
);

DROP SCHEMA IF EXISTS vgw_api CASCADE;
CREATE SCHEMA vgw_api;

CREATE TABLE vgw_api.blacklisted_meta (
  file_id TEXT PRIMARY KEY,
  phones_hash TEXT NOT NULL,
  phones_count integer NOT NULL,
  clean_phones_count integer NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp
);

DROP SCHEMA IF EXISTS regions CASCADE;

CREATE SCHEMA regions;

CREATE TYPE regions.consumer_settings_t AS (
  consumer_id INTEGER,
  enabled BOOLEAN
);

CREATE TYPE regions.settings_t AS (
  gateway_id TEXT,
  enabled BOOLEAN,
  city_id TEXT,
  enabled_for common.client_type_t[],
  consumers regions.consumer_settings_t[]
);

CREATE TYPE regions.region_t AS (
  region_id integer,
  gateways regions.settings_t[]
);

CREATE TABLE regions.regions(
  id integer PRIMARY KEY,
  deleted boolean NOT NULL DEFAULT false,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp
);

CREATE INDEX regions_updated_idx ON regions.regions (updated_at);

CREATE TABLE regions.gateway_region_settings(
  region_id integer NOT NULL REFERENCES regions.regions(id) ON DELETE CASCADE,
  gateway_id text NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  enabled boolean NOT NULL DEFAULT FALSE,
  city_id text NOT NULL,
  enabled_for common.client_type_t[],
  PRIMARY KEY (region_id, gateway_id)
);

CREATE TABLE regions.vgw_enable_settings(
  region_id INTEGER NOT NULL REFERENCES regions.regions(id) ON DELETE CASCADE,
  gateway_id TEXT NOT NULL REFERENCES voice_gateways.voice_gateways(id) ON DELETE CASCADE,
  consumer_id INTEGER NOT NULL REFERENCES consumers.consumers(id) ON DELETE CASCADE,
  enabled BOOLEAN NOT NULL,
  updated_at timestamptz DEFAULT current_timestamp,
  PRIMARY KEY (gateway_id, region_id, consumer_id)
);

CREATE FUNCTION regions.updated() RETURNS TRIGGER
AS $$
BEGIN
  IF tg_table_name = 'gateway_region_settings' THEN
    UPDATE regions.regions SET updated_at = default
    WHERE id = NEW.region_id;
  END IF;
  IF tg_table_name = 'vgw_enable_settings' THEN
      UPDATE regions.regions SET updated_at = default
      WHERE id = NEW.region_id;
  END IF;
  IF tg_table_name = 'regions' THEN
    NEW.updated_at := current_timestamp;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER regions_settings_updated_tr
  BEFORE INSERT OR UPDATE ON regions.gateway_region_settings
  FOR EACH ROW
EXECUTE PROCEDURE regions.updated();

CREATE TRIGGER vgw_enable_settings_updated_tr
    BEFORE INSERT OR UPDATE ON regions.vgw_enable_settings
    FOR EACH ROW
EXECUTE PROCEDURE regions.updated();

CREATE TRIGGER regions_updated_tr
  BEFORE UPDATE OF deleted ON regions.regions
  FOR EACH ROW
EXECUTE PROCEDURE regions.updated();


DROP SCHEMA IF EXISTS forwardings CASCADE;

CREATE SCHEMA forwardings;

CREATE TYPE forwardings.state_t AS ENUM (
  'draft',
  'broken',
  'created'
);

CREATE TABLE forwardings.forwardings(
  id text NOT NULL,
  external_ref_id text NOT NULL,
  gateway_id text NOT NULL,
  consumer_id integer NOT NULL,
  state forwardings.state_t NOT NULL,
  created_at timestamptz NOT NULL DEFAULT current_timestamp,
  expires_at timestamptz NOT NULL,
  src_type TEXT,
  dst_type TEXT,
  caller_phone text NOT NULL,
  caller_phone_id text,
  callee_phone text NOT NULL,
  callee_phone_id text,
  redirection_phone text,
  ext text,
  nonce text NOT NULL UNIQUE,
  call_location common.geo_point_t NOT NULL,
  region_id integer,
  PRIMARY KEY (id),
  CONSTRAINT fwd_src_type_not_null CHECK (src_type IS NOT NULL),
  CONSTRAINT fwd_dst_type_not_null CHECK (dst_type IS NOT NULL)
);

CREATE TABLE forwardings.talks (
  id text NOT NULL,
  created_at timestamptz NOT NULL,
  length integer NOT NULL,
  forwarding_id text NOT NULL REFERENCES forwardings.forwardings(id) ON DELETE RESTRICT,
  caller_phone text,
  caller_phone_id text,
  voip_succeeded boolean,
  s3_key text DEFAULT NULL,
  succeeded boolean,
  status text,
  dial_time integer,
  PRIMARY KEY (id)
);

CREATE INDEX forwardings_nonce_idx ON forwardings.forwardings (nonce);
CREATE INDEX forwardings_external_ref_idx ON forwardings.forwardings (external_ref_id);

/* v04 */

ALTER TABLE forwardings.talks ADD COLUMN
  updated_at timestamptz NOT NULL DEFAULT current_timestamp;

CREATE FUNCTION forwardings.talk_updated() RETURNS TRIGGER
AS $$
BEGIN
  NEW.updated_at := current_timestamp;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER forwardings_talks_set_updated_at
  BEFORE UPDATE ON forwardings.talks
  FOR EACH ROW
EXECUTE PROCEDURE forwardings.talk_updated();

/* v08 */

ALTER TABLE voice_gateways.voice_gateways ADD column disable_reason TEXT;

/* v11 */

CREATE TYPE voice_gateways.check_status_t AS ENUM (
    'FORWARDING_FAILED',
    'SESSION_FAILED',
    'CHECK_FAILED',
    'SESSION_CANCELED',
    'ANSWER_TIMEOUT',
    'CHECK_TIMEOUT',
    'UNKNOWN_FAILURE',
    'SUCCESS',
    'UNKNOWN_STATUS'
);

CREATE TABLE voice_gateways.check_results (
    id BIGSERIAL PRIMARY KEY,
    gateway_id TEXT NOT NULL,
    location common.geo_point_t NOT NULL,
    forwarding_phone TEXT,
    status voice_gateways.check_status_t NOT NULL,
    logs_to_save TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT current_timestamp
);

/* v12 */

CREATE INDEX check_results_created_at_idx ON voice_gateways.check_results (created_at);


ALTER TABLE voice_gateways.check_results
    ADD COLUMN forwarding_id TEXT,
    ADD COLUMN talk_id TEXT,
    ADD COLUMN octonode_call_session_id TEXT;

/* v18 */

ALTER TABLE voice_gateways.check_results
    ADD COLUMN forwarding_ext TEXT,
    ADD COLUMN forwarding_expires_at TIMESTAMPTZ;
