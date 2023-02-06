CREATE TABLE IF NOT EXISTS ds.distlock(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
