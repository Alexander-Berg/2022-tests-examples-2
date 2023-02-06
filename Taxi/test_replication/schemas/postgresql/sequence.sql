CREATE SCHEMA sequence;

CREATE TABLE sequence.table (
  id serial PRIMARY KEY,
  example_value integer NOT NULL
);

CREATE TABLE sequence.table_by_ts (
  id serial PRIMARY KEY,
  replica_ts TIMESTAMP NOT NULL
);

CREATE TABLE sequence.table_indexed (
  id serial PRIMARY KEY,
  updated TIMESTAMP NOT NULL
);

CREATE INDEX ON sequence.table_indexed (
  updated
);
