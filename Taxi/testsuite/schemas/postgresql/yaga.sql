CREATE SCHEMA yaga_metrolog;

CREATE TABLE yaga_metrolog.distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
