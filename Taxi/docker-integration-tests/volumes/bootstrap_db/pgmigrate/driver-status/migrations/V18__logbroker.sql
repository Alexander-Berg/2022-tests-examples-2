DROP SCHEMA IF EXISTS lb CASCADE;

CREATE SCHEMA lb;

CREATE TABLE lb.offsets (
	topic_partition TEXT NOT NULL UNIQUE PRIMARY KEY,
   	offsets BIGINT
);
