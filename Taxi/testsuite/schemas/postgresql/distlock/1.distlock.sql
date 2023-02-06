CREATE SCHEMA distlocks;

CREATE TABLE distlocks.supply_diagnostics_locks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
