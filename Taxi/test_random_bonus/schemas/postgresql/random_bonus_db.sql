CREATE SCHEMA IF NOT EXISTS random_bonus;

CREATE TABLE IF NOT EXISTS random_bonus.key_value (
  key    TEXT PRIMARY KEY,
  value  TEXT NOT NULL
);

CREATE TYPE random_bonus.STATUS AS ENUM (
  'online',
  'offline',
  'onorder'
);

CREATE TABLE IF NOT EXISTS random_bonus.progress (
  park_id            TEXT NOT NULL,
  driver_id          TEXT NOT NULL,
  progress           FLOAT NOT NULL,
  is_first           BOOLEAN NOT NULL,
  last_status        random_bonus.STATUS NOT NULL,
  status_updated_at  TIMESTAMPTZ NOT NULL,
  last_online_at     TIMESTAMPTZ NOT NULL,
  last_bonus_at      TIMESTAMPTZ NOT NULL,
  PRIMARY KEY(park_id, driver_id)
);

CREATE INDEX IF NOT EXISTS
  idx_updated_at ON random_bonus.progress(last_online_at);

CREATE TABLE IF NOT EXISTS random_bonus.idempotency_keys (
  key               TEXT PRIMARY KEY,
  event_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS
  idx_idempotency_created_at ON random_bonus.idempotency_keys(event_at);

CREATE TABLE IF NOT EXISTS random_bonus.bonuses (
  id                 TEXT NOT NULL,
  park_id            TEXT NOT NULL,
  driver_id          TEXT NOT NULL,
  slug               TEXT NOT NULL,
  shown_at           TIMESTAMPTZ,
  PRIMARY KEY(id, park_id, driver_id)
);
