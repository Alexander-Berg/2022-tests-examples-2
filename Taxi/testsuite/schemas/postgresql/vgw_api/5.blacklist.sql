DROP SCHEMA IF EXISTS vgw_api CASCADE;
CREATE SCHEMA vgw_api;

CREATE TABLE vgw_api.blacklisted_meta (
  file_id TEXT PRIMARY KEY,
  phones_hash TEXT NOT NULL,
  phones_count INTEGER NOT NULL,
  clean_phones_count INTEGER NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT current_timestamp
);

CREATE TABLE vgw_api.blacklisted_drafts (
  id SERIAL PRIMARY KEY,
  external_ref_id TEXT NOT NULL,
  consumer_id INTEGER NOT NULL,
  created_at timestamptz NOT NULL DEFAULT current_timestamp,
  caller TEXT NOT NULL,
  callee TEXT NOT NULL,
  caller_phone TEXT NOT NULL,
  callee_phone TEXT NOT NULL,
  call_location common.geo_point_t NOT NULL,
  region_id INTEGER,
  dry_run BOOLEAN DEFAULT TRUE
);
