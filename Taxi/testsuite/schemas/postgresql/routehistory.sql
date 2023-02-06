DROP SCHEMA IF EXISTS routehistory CASCADE;
--
-- Default shard, version 1
--
CREATE SCHEMA routehistory;
CREATE TABLE routehistory.version
(
  "id"         SERIAL,
  "version"    VARCHAR NOT NULL,
  "applied_at" TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

--
-- Default shard, version 2
--
INSERT INTO routehistory.version(version)
VALUES ('v02');

CREATE TABLE routehistory.distlocks
(
  "key"             TEXT PRIMARY KEY,
  "owner"           TEXT,
  "expiration_time" TIMESTAMPTZ
);

--
-- Default shard, version 6
--
INSERT INTO routehistory.version(version)
VALUES ('v06');

CREATE TABLE routehistory.rerouting
(
  "host"    TEXT PRIMARY KEY,
  "online"  TIMESTAMPTZ NOT NULL,
  "version" INT NOT NULL
);

--
-- Default shard, version 8
--
INSERT INTO routehistory.version(version)
VALUES ('v08');

CREATE TABLE routehistory.drive_history
(
  "yandex_uid" BIGINT NOT NULL,
  "created"    TIMESTAMPTZ NOT NULL,
  "format"     INTEGER NOT NULL,
  "data"       BYTEA NOT NULL /* protobuf  */
);

CREATE INDEX ON routehistory.drive_history (created);
CREATE UNIQUE INDEX ON routehistory.drive_history (yandex_uid, created DESC);

--
-- Default shard, version 9
--
INSERT INTO routehistory.version(version)
VALUES ('v09');
CREATE TABLE routehistory.common_strings
(
  "id"  SERIAL PRIMARY KEY,
  "str" TEXT NOT NULL UNIQUE
);
INSERT INTO routehistory.common_strings (id, str)
VALUES (0, '');

CREATE TABLE routehistory.processes
(
  "id"            TEXT NOT NULL UNIQUE,
  "host"          TEXT NOT NULL,
  "version"       BIGINT NOT NULL,
  "period_ms"     INT NOT NULL,
  "period_exc_ms" INT NOT NULL,
  "max_attempts"  INT NOT NULL,
  "state"         TEXT NOT NULL, -- created, running, paused, done
  "type"          TEXT NOT NULL,
  "data"          JSONB NOT NULL
);
CREATE INDEX ON routehistory.processes (host, id);

--
-- Default shard, version A
--
INSERT INTO routehistory.version(version)
VALUES ('v0A');

CREATE TABLE routehistory.search_history
(
  "yandex_uid" BIGINT NOT NULL,
  "created"    TIMESTAMPTZ NOT NULL,
  "brand"      INT NOT NULL, -- Common_string
  "format"     INTEGER NOT NULL,
  "data"       BYTEA NOT NULL
);

CREATE INDEX ON routehistory.search_history (created);
CREATE UNIQUE INDEX ON routehistory.search_history (yandex_uid, created);
ALTER TABLE routehistory.search_history ALTER COLUMN data SET STORAGE MAIN;

--
-- Default shard, version B
--
INSERT INTO routehistory.version(version)
VALUES ('v0B');

ALTER TABLE routehistory.drive_history ADD COLUMN origin INT NULL;

--
-- Default shard, version C
--
INSERT INTO routehistory.version(version)
VALUES ('v0C');

CREATE TABLE routehistory.grocery_order
(
  "yandex_uid"     BIGINT NOT NULL,
  "created"        TIMESTAMPTZ NOT NULL,
  "protobuf_data"  BYTEA NOT NULL,
  PRIMARY KEY(yandex_uid, created)
);

CREATE INDEX ON routehistory.grocery_order (created); -- for cleanup

--
-- Default shard, version D
--
INSERT INTO routehistory.version(version)
VALUES ('v0D');

CREATE TABLE routehistory.shuttle_order
(
  "yandex_uid"     BIGINT NOT NULL,
  "created"        TIMESTAMPTZ NOT NULL,
  "protobuf_data"  BYTEA NOT NULL,
  PRIMARY KEY(yandex_uid, created)
);

CREATE INDEX ON routehistory.shuttle_order (created);
