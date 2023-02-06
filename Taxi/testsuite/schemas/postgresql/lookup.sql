CREATE SCHEMA lookup;

CREATE TABLE IF NOT EXISTS lookup.candidates_distlock(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
