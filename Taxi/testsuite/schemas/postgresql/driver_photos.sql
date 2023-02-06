-- Below are just 8 concatenated files from py3
-- TODO: combine them into one

-- 1

CREATE TABLE IF NOT EXISTS driver_photos (
    id VARCHAR PRIMARY KEY,
    driver_id VARCHAR NOT NULL,
    photo_name VARCHAR NOT NULL,
    group_id INTEGER NOT NULL,
    photo_type VARCHAR NOT NULL,
    photo_status VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE driver_photos DROP COLUMN IF EXISTS error;

DROP INDEX IF EXISTS driver_photos_search_idx;

CREATE INDEX IF NOT EXISTS driver_photos_search_idx ON driver_photos (photo_type, created_at DESC, id);

CREATE TABLE IF NOT EXISTS driver_photos_errors (
    error VARCHAR)
  INHERITS (
    driver_photos
);

CREATE INDEX IF NOT EXISTS driver_photos_errors_search_idx ON driver_photos_errors (photo_type, created_at DESC, id);

CREATE TABLE IF NOT EXISTS driver_photos_retries (
    idempotency_key VARCHAR PRIMARY KEY,
    retries SMALLINT NOT NULL DEFAULT 1
);

-- 2

ALTER TABLE driver_photos
    ADD COLUMN park_id VARCHAR DEFAULT NULL,
    ADD COLUMN driver_profile_id VARCHAR DEFAULT NULL;

-- 3

CREATE TYPE photo_priority AS ENUM ('admin', 'taximeter');

ALTER TABLE driver_photos
    ADD COLUMN priority photo_priority DEFAULT 'admin';

ALTER TABLE driver_photos
    ADD COLUMN reason VARCHAR DEFAULT NULL;

-- 4

DROP INDEX IF EXISTS driver_photos_driver_id_idx;

CREATE INDEX IF NOT EXISTS driver_photos_driver_id_idx ON driver_photos (driver_id);

-- 5

DROP INDEX IF EXISTS driver_photos_photo_name_idx;
CREATE INDEX IF NOT EXISTS driver_photos_photo_name_idx ON driver_photos (photo_name);

DROP INDEX IF EXISTS driver_photos_status_idx;
CREATE INDEX IF NOT EXISTS driver_photos_status_idx ON driver_photos (photo_status);

-- 6

ALTER TABLE driver_photos DROP COLUMN IF EXISTS updated_at;
ALTER TABLE driver_photos ADD COLUMN updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

DROP FUNCTION IF EXISTS set_updated;
CREATE FUNCTION set_updated() RETURNS trigger AS $set_updated$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
$set_updated$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated ON driver_photos;
CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON driver_photos
FOR EACH ROW EXECUTE PROCEDURE set_updated();

-- 7

BEGIN;
    DROP TRIGGER IF EXISTS set_updated ON driver_photos;
    UPDATE driver_photos SET updated_at = created_at where priority = 'admin';
    CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON driver_photos
    FOR EACH ROW EXECUTE PROCEDURE set_updated();
COMMIT;

-- 8

CREATE TABLE IF NOT EXISTS distlocks(
  key TEXT PRIMARY KEY,
  owner TEXT,
  expiration_time TIMESTAMPTZ
);
