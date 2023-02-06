#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL

CREATE DATABASE dbtags;

\connect dbtags

CREATE SCHEMA db;

CREATE TABLE db.version(
  db_0_2 INTEGER
);

CREATE TYPE db.entity_type AS ENUM (
  'driver_license',
  'car_number',
  'park'
  -- To be extended later on
);

CREATE SCHEMA meta;

CREATE TABLE meta.tag_names (
  id SERIAL PRIMARY KEY,
  name varchar(255) NOT NULL UNIQUE
);

CREATE SCHEMA state;

CREATE TABLE state.entities (
  id SERIAL PRIMARY KEY,
  value varchar(255) NOT NULL UNIQUE,
  type db.entity_type NOT NULL
);

CREATE TABLE state.providers (
  id SERIAL PRIMARY KEY,
  name varchar(255) NOT NULL UNIQUE,
  description varchar(255) NOT NULL,
  active boolean NOT NULL DEFAULT True
);

CREATE TABLE state.tags (
  tag_name_id int NOT NULL REFERENCES meta.tag_names (id),
  provider_id int NOT NULL REFERENCES state.providers (id),
  entity_id int NOT NULL REFERENCES state.entities (id),
  updated timestamp NOT NULL,
  ttl timestamp NOT NULL
);

ALTER TABLE ONLY state.tags ADD CONSTRAINT tags_key PRIMARY KEY (
  tag_name_id,
  provider_id,
  entity_id
);

CREATE SCHEMA service;

CREATE TABLE service.requests (
  confirmation_token varchar(255) NOT NULL PRIMARY KEY,
  created timestamp NOT NULL,
  response_code smallint NOT NULL,
  response_body text
);

/* V3 */

ALTER TABLE db.version RENAME COLUMN db_0_2 TO db_0_3;

CREATE FUNCTION refresh_updated_by_name() RETURNS trigger AS '
BEGIN
  UPDATE state.tags SET updated=NOW() WHERE provider_id=NEW.id;
  RETURN NEW;
END;
' LANGUAGE plpgsql;

CREATE TRIGGER update_on_activation_status
AFTER UPDATE OF active ON state.providers
FOR EACH ROW EXECUTE PROCEDURE refresh_updated_by_name();

/* V4 fixes entities type usage */

CREATE UNIQUE INDEX entities_value_type_key ON state.entities (value, type);

ALTER TABLE state.entities
  ADD CONSTRAINT entities_value_type_key UNIQUE
  USING INDEX entities_value_type_key;
ALTER TABLE db.version RENAME COLUMN db_0_3 TO db_0_4;

/* V5 */

ALTER TABLE state.entities DROP CONSTRAINT entities_value_key;
ALTER TABLE db.version RENAME COLUMN db_0_4 TO db_0_5;

/* V6 */

ALTER TABLE db.version RENAME COLUMN db_0_5 TO db_0_6;

CREATE FUNCTION service.erase_tokens_on_insert() RETURNS trigger AS '
BEGIN
  DELETE FROM service.requests WHERE created < NOW() - interval ''1 day'';
  RETURN NEW;
END
' LANGUAGE plpgsql;

CREATE TRIGGER remove_old_tokens AFTER INSERT ON service.requests
FOR EACH ROW EXECUTE PROCEDURE service.erase_tokens_on_insert();

ALTER FUNCTION refresh_updated_by_name()
RENAME TO refresh_updated_by_provider_status;

ALTER FUNCTION refresh_updated_by_provider_status()
SET SCHEMA state;

/* V7 */

ALTER TABLE db.version RENAME COLUMN db_0_6 TO db_0_7;

-- Unique driver identifier
ALTER TYPE db.entity_type ADD VALUE 'udid';

/* V8 */

ALTER TABLE db.version RENAME COLUMN  db_0_7 TO db_0_8;

CREATE INDEX state_tags_provider_id_index ON state.tags (provider_id);
CREATE INDEX state_tags_ttl_index ON state.tags (ttl);
CREATE INDEX state_tags_updated_index ON state.tags (updated);

/* V9 */

ALTER TABLE db.version RENAME COLUMN  db_0_8 TO db_0_9;

CREATE INDEX state_entities_type_index ON state.entities (type);

/* V10 */

ALTER TABLE db.version RENAME COLUMN  db_0_9 TO db_0_10;

ALTER TYPE db.entity_type ADD VALUE 'clid_uuid';
ALTER TYPE db.entity_type ADD VALUE 'phone';
ALTER TYPE db.entity_type ADD VALUE 'phone_hash_id';
ALTER TYPE db.entity_type ADD VALUE 'user_id';
ALTER TYPE db.entity_type ADD VALUE 'user_phone_id';

CREATE OR REPLACE FUNCTION service.erase_tokens_on_insert()
RETURNS trigger AS '
BEGIN
  DELETE FROM service.requests WHERE created <= NEW.created - interval ''1 day'';
  RETURN NEW;
END
' LANGUAGE plpgsql;

/* V11 */

CREATE OR REPLACE FUNCTION state.refresh_updated_by_provider_status()
RETURNS trigger AS '
BEGIN
  UPDATE state.tags SET updated=NOW() AT TIME ZONE ''utc''
  WHERE provider_id=NEW.id;
  RETURN NEW;
END
' LANGUAGE plpgsql;

/* V12 */

/* V11 column change was forgotten */
ALTER TABLE db.version RENAME COLUMN db_0_10 TO db_0_12;

CREATE SEQUENCE state.tags_revision START 1;

CREATE FUNCTION state.set_tags_revision() RETURNS TRIGGER as '
  BEGIN
    NEW.revision = nextval(''state.tags_revision'');
    return NEW;
  END;
' LANGUAGE plpgsql;

CREATE TRIGGER set_tags_revision BEFORE UPDATE ON state.tags FOR EACH ROW
  EXECUTE PROCEDURE state.set_tags_revision();

ALTER TABLE state.tags
  ADD revision integer NOT NULL UNIQUE DEFAULT nextval('state.tags_revision');

CREATE UNIQUE INDEX CONCURRENTLY state_tags_revision_idx ON state.tags (revision);

/* V13 */
ALTER TABLE db.version RENAME COLUMN db_0_12 TO db_0_13;

-- Cron-task on the service side does this job
DROP TRIGGER remove_old_tokens ON service.requests;
DROP FUNCTION service.erase_tokens_on_insert();

-- Not needed anymore after revision mechanics introduction
DROP INDEX CONCURRENTLY state.state_tags_updated_index;

-- Is duplicate of tags_revision_key
DROP INDEX CONCURRENTLY state.state_tags_revision_idx;

-- To fasten time-to-live cron-task query
CREATE INDEX CONCURRENTLY state_tags_ttl_more_than_updated ON state.tags (
  (ttl > updated)
);

/* V14 */
ALTER TABLE db.version RENAME COLUMN db_0_13 TO db_0_14;

ALTER TYPE db.entity_type ADD VALUE 'personal_phone_id';

/* V15 */
ALTER TABLE db.version RENAME COLUMN db_0_14 TO db_0_15;

CREATE TYPE db.yql_status AS ENUM (
  'running',
  'completed',
  'failed'
);

CREATE TABLE service.yql_operations (
  operation_id varchar(64) NOT NULL PRIMARY KEY,
  provider_id int NOT NULL REFERENCES state.providers (id),
  entity_type db.entity_type NOT NULL,
  status db.yql_status NOT NULL,
  started timestamp NOT NULL
);

/* V16 */
ALTER TABLE db.version RENAME COLUMN db_0_15 TO db_0_16;

ALTER TYPE db.entity_type ADD VALUE 'dbid_uuid';

/* V17 */
ALTER TABLE db.version RENAME COLUMN db_0_16 TO db_0_17;

ALTER TABLE state.tags
    ADD COLUMN entity_type db.entity_type;

/* V18 */
ALTER TABLE db.version RENAME COLUMN db_0_17 TO db_0_18;

CREATE TABLE meta.topics (
  id SERIAL PRIMARY KEY,
  name varchar(255) NOT NULL UNIQUE,
  description varchar(255) NOT NULL
);

CREATE TABLE meta.relations (
  topic_id integer NOT NULL REFERENCES meta.topics (id) ON DELETE CASCADE,
  tag_name_id integer NOT NULL REFERENCES meta.tag_names (id),

  CONSTRAINT relations_key PRIMARY KEY (topic_id,tag_name_id)
);

/* V19 */
ALTER TABLE db.version RENAME COLUMN db_0_18 TO db_0_19;

CREATE INDEX CONCURRENTLY ON state.tags (revision, entity_type) WHERE
entity_type IN ('car_number', 'udid', 'driver_license', 'dbid_uuid', 'park');

EOSQL
