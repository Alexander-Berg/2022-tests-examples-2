CREATE SCHEMA categories;

CREATE TABLE categories.categories(
  name       TEXT        NOT NULL PRIMARY KEY,
  type       TEXT        NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  jdoc       JSONB
);
CREATE INDEX type_idx    ON categories.categories(type);
CREATE INDEX updated_idx ON categories.categories(updated_at);

CREATE TABLE categories.park_categories(
  park_id    TEXT        NOT NULL PRIMARY KEY,
  categories TEXT[]      NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  jdoc       JSONB
);
CREATE INDEX updated_parks_idx ON categories.park_categories(updated_at);

CREATE TABLE categories.car_categories(
  park_id    TEXT        NOT NULL,
  car_id     TEXT        NOT NULL,
  categories TEXT[]      NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  jdoc       JSONB,
  PRIMARY KEY (park_id, car_id)
);
CREATE INDEX updated_cars_idx ON categories.car_categories(updated_at);

CREATE TABLE categories.driver_restrictions(
  park_id    TEXT        NOT NULL,
  driver_id  TEXT        NOT NULL,
  categories TEXT[]      NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  jdoc       JSONB,
  PRIMARY KEY(park_id, driver_id)
);
CREATE INDEX updated_restrictions_idx ON categories.driver_restrictions(updated_at);

DROP TABLE IF EXISTS categories.distlock CASCADE;
CREATE TABLE categories.distlock(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
