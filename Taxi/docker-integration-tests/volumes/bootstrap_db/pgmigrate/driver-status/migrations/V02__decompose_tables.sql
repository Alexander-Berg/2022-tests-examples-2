DROP SCHEMA IF EXISTS ds CASCADE;

CREATE SCHEMA ds;

CREATE TYPE ds.flow_version AS ENUM ('v0', 'v1');
CREATE TYPE ds.status AS ENUM ('offline', 'online', 'busy');
CREATE TYPE ds.source AS ENUM ('service', 'client', 'periodical-updater');
CREATE TYPE ds.order_status AS ENUM ('none', 'driving', 'waiting', 'calling',
  'transporting', 'complete', 'failed', 'cancelled', 'expired');

CREATE TABLE ds.app_families (
  id SMALLSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

INSERT INTO ds.app_families(name)
VALUES ('taximeter'),
       ('uberdriver');

CREATE TABLE ds.blocked_reasons (
  id SMALLSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

INSERT INTO ds.blocked_reasons(name)
VALUES ('none'),
       ('by_driver'),
       ('fns_unbound'),
       ('driver_taximeter_disabled'),
       ('driver_balance_debt'),
       ('driver_blacklist'),
       ('car_blacklist'),
       ('driver_dkk'),
       ('driver_license_verification'),
       ('driver_sts'),
       ('driver_identity'),
       ('driver_biometry'),
       ('pending_park_order'),
       ('car_is_used');

CREATE TABLE ds.providers (
  id SMALLSERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE
);

INSERT INTO ds.providers(name)
VALUES ('park'),
       ('yandex'),
       ('upup'),
       ('formula'),
       ('offtaxi'),
       ('app');

CREATE TABLE ds.drivers (
  id SERIAL PRIMARY KEY,
  park_id VARCHAR(32) NOT NULL,
  driver_id VARCHAR(32) NOT NULL,
  app_family_id SMALLINT NOT NULL REFERENCES ds.app_families(id),
  flow_version ds.flow_version NOT NULL DEFAULT 'v0',
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  CONSTRAINT unique_driver UNIQUE (park_id, driver_id, app_family_id)
);

CREATE TABLE ds.statuses (
  driver_id INTEGER PRIMARY KEY REFERENCES ds.drivers(id),
  status ds.status NOT NULL,
  source ds.source NOT NULL,
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ds_statuses_updated_ts_index ON ds.statuses(updated_ts);

CREATE TABLE ds.blocks (
  driver_id INTEGER PRIMARY KEY REFERENCES ds.drivers(id),
  reason_id SMALLINT REFERENCES ds.blocked_reasons(id),      -- NULL or reason_id = 1 ('none') means driver don't have blocks
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ds_blocks_updated_ts_index ON ds.blocks(updated_ts);

CREATE TABLE ds.orders (
  id VARCHAR(32) PRIMARY KEY,
  driver_id INTEGER NOT NULL REFERENCES ds.drivers(id),
  status ds.order_status,
  provider_id SMALLINT NOT NULL REFERENCES ds.providers(id),
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ds_orders_driver_id_index ON ds.orders(driver_id);
CREATE INDEX ds_orders_updated_ts_index ON ds.orders(updated_ts);

CREATE TABLE ds.modifiers (
  driver_id INTEGER PRIMARY KEY REFERENCES ds.drivers(id),
  card_only BOOLEAN NOT NULL DEFAULT FALSE,
  comment TEXT,
  driver_provider_ids SMALLINT[],
  integration_event BOOLEAN NOT NULL DEFAULT FALSE,
  updated_ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX ds_modifiers_updated_ts_index ON ds.modifiers(updated_ts);
