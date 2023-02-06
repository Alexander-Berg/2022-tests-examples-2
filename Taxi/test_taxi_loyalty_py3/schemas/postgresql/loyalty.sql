CREATE SCHEMA loyalty;

CREATE TYPE loyalty.block_t AS (
  reason TEXT,
  created TIMESTAMP,
  current_value FLOAT,
  min_value FLOAT
);

CREATE TABLE loyalty.loyalty_accounts(
  id TEXT NOT NULL UNIQUE,
  unique_driver_id TEXT NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  updated TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  next_recount TIMESTAMP NOT NULL,
  last_active_at TIMESTAMPTZ,
  status TEXT NOT NULL,
  block loyalty.block_t[] DEFAULT '{}',
  send_notification BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY(id)
);

CREATE UNIQUE INDEX loyalty_unique_driver_id ON loyalty.loyalty_accounts (unique_driver_id);
CREATE INDEX loyalty_next_recount ON loyalty.loyalty_accounts (next_recount);
CREATE INDEX loyalty_last_active_at ON loyalty.loyalty_accounts (last_active_at);
CREATE INDEX loyalty_status ON loyalty.loyalty_accounts (status);

CREATE TABLE loyalty.status_logs(
  log_id SERIAL,
  created TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  status TEXT NOT NULL,
  unique_driver_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  points INTEGER,
  PRIMARY KEY(log_id)
);

CREATE INDEX status_logs_unique_driver_id ON loyalty.status_logs (unique_driver_id);
CREATE INDEX status_logs_created ON loyalty.status_logs (created);

CREATE TABLE loyalty.statistics(
  log_id SERIAL,
  created TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  updated TIMESTAMP NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
  home_zone TEXT NOT NULL UNIQUE,
  newbie INTEGER,
  returnee INTEGER,
  PRIMARY KEY(log_id)
);

CREATE INDEX statistics_home_zone ON loyalty.statistics (home_zone);
CREATE INDEX statistics_created ON loyalty.statistics (created);

CREATE TABLE loyalty.dms_loyalty_accounts (LIKE loyalty.loyalty_accounts INCLUDING DEFAULTS);
CREATE TABLE loyalty.dms_status_logs (LIKE loyalty.status_logs INCLUDING DEFAULTS);

CREATE TABLE loyalty.yt_loyalty_accounts (LIKE loyalty.loyalty_accounts INCLUDING DEFAULTS);
CREATE TABLE loyalty.yt_status_logs (LIKE loyalty.status_logs INCLUDING DEFAULTS);
