DROP SCHEMA IF EXISTS order_metrics CASCADE;

CREATE SCHEMA order_metrics;

-- distlocks table
CREATE TABLE order_metrics.distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);

-- logbroker schema and offsets table
CREATE SCHEMA lb;
CREATE TABLE lb.offsets (
	topic_partition TEXT PRIMARY KEY,
   	offsets BIGINT
);
