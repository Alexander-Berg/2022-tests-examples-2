BEGIN;

ALTER TABLE storage.s3_backup_timestamp
    ADD COLUMN places_latest_revision_id BIGINT NOT NULL DEFAULT 0,
    ADD COLUMN zones_latest_revision_id  BIGINT NOT NULL DEFAULT 0;

ALTER TABLE storage.s3_backup_timestamp
    RENAME TO s3_metadata;

COMMIT;
