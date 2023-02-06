DROP SCHEMA IF EXISTS routehistory_ph CASCADE;
--
-- Phone history shards, version 5
--
CREATE SCHEMA routehistory_ph;

CREATE TABLE routehistory_ph.version
(
  "id"         SERIAL,
  "version"    TEXT NOT NULL,
  "applied_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE routehistory_ph.users
(
  "yandex_uid"    BIGINT NOT NULL,
  "is_portal_uid" BOOLEAN NOT NULL,
  "phone_id"      UUID NOT NULL,
  "updated"       TIMESTAMPTZ NOT NULL,
  "shard_key"     INT NOT NULL
);
CREATE UNIQUE INDEX ON routehistory_ph.users (yandex_uid, phone_id);
CREATE INDEX ON routehistory_ph.users (is_portal_uid, updated);

INSERT INTO routehistory_ph.version(version)
VALUES ('v05');

CREATE TABLE routehistory_ph.phone_history2
(
  "order_id"         UUID NOT NULL UNIQUE,
  "shard_key"        INT NOT NULL,
  "yandex_uid"       BIGINT,
  "is_portal_uid"    BOOL NOT NULL,
  "phone_id"         UUID NOT NULL,
  "created"          TIMESTAMPTZ NOT NULL,
  "brand"            INT NOT NULL, -- Common_string
  "format"           INT NOT NULL,
  "data"             BYTEA NOT NULL
);
CREATE INDEX ON routehistory_ph.phone_history2 (phone_id, created);
CREATE INDEX ON routehistory_ph.phone_history2 (is_portal_uid, created);
ALTER TABLE routehistory_ph.phone_history2 ALTER COLUMN data SET STORAGE MAIN;
