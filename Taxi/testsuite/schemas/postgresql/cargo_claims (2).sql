CREATE SCHEMA IF NOT EXISTS cargo_matcher;

CREATE TABLE IF NOT EXISTS cargo_matcher.distlock_claim_estimator(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
