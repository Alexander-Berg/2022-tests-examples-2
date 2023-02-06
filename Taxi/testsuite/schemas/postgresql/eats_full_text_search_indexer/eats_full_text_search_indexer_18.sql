BEGIN;

CREATE SCHEMA lb;

CREATE TABLE lb.offsets (
	topic_partition   TEXT NOT NULL UNIQUE PRIMARY KEY,
   	offsets           BIGINT
);

CREATE TABLE fts_indexer.distlocks
(
    key             TEXT PRIMARY KEY,
    owner           TEXT,
    expiration_time TIMESTAMPTZ
);

COMMIT;
