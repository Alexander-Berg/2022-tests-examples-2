DROP SCHEMA IF EXISTS order_events_producer CASCADE;

CREATE SCHEMA order_events_producer;

CREATE TABLE order_events_producer.distlocks (
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

DROP SCHEMA IF EXISTS lb CASCADE;

CREATE SCHEMA lb;

CREATE TABLE lb.offsets (
	topic_partition TEXT NOT NULL UNIQUE PRIMARY KEY,
   	offsets BIGINT
);
