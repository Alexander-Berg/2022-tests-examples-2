CREATE SCHEMA common;

CREATE TYPE common.geo_point_t AS (
  lon DOUBLE PRECISION,
  lat DOUBLE PRECISION
);

CREATE SCHEMA forwardings;

CREATE TYPE forwardings.state_t AS ENUM (
  'draft',
  'broken',
  'created'
);

CREATE TABLE forwardings.forwardings(
  id TEXT NOT NULL,
  external_ref_id TEXT NOT NULL,
  gateway_id TEXT NOT NULL,
  consumer_id INTEGER NOT NULL,
  state forwardings.state_t NOT NULL,
  created_at timestamptz NOT NULL DEFAULT current_timestamp,
  expires_at timestamptz NOT NULL,
  src_type TEXT,
  dst_type TEXT,
  caller_phone TEXT NOT NULL,
  caller_phone_id TEXT,
  callee_phone TEXT NOT NULL,
  callee_phone_id TEXT,
  redirection_phone TEXT,
  ext TEXT,
  nonce TEXT NOT NULL UNIQUE,
  call_location common.geo_point_t NOT NULL,
  region_id INTEGER,
  PRIMARY KEY (id),
  CONSTRAINT fwd_src_type_not_null CHECK (src_type IS NOT NULL),
  CONSTRAINT fwd_dst_type_not_null CHECK (dst_type IS NOT NULL)
);

CREATE TABLE forwardings.talks (
  id TEXT NOT NULL,
  created_at timestamptz NOT NULL,
  length INTEGER NOT NULL,
  forwarding_id TEXT NOT NULL REFERENCES forwardings.forwardings(id) ON DELETE RESTRICT,
  caller_phone TEXT,
  caller_phone_id TEXT,
  voip_succeeded boolean DEFAULT NULL,
  s3_key TEXT DEFAULT NULL,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp,
  succeeded boolean,
  status TEXT,
  dial_time INTEGER,
  PRIMARY KEY (id)
);

CREATE INDEX forwardings_nonce_idx ON forwardings.forwardings (nonce);
CREATE INDEX forwardings_external_ref_idx ON forwardings.forwardings (external_ref_id);
CREATE INDEX forwarding_talks_replication_idx ON forwardings.talks (updated_at);
CREATE INDEX talks_forwarding_id_idx ON forwardings.talks (forwarding_id);
CREATE INDEX forwardings_redirection_phone_idx ON forwardings.forwardings (redirection_phone);
CREATE INDEX forwardings_replication_idx ON forwardings.forwardings (created_at);
CREATE INDEX forwardings_expires_at_idx ON forwardings.forwardings (expires_at);

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
