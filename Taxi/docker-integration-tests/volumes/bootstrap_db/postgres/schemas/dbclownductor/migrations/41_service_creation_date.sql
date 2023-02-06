BEGIN TRANSACTION;

ALTER TABLE clownductor.services ADD COLUMN created_at INTEGER NOT NULL DEFAULT extract(epoch from now())::INTEGER;

CREATE INDEX clownductor_service_created_at
    ON clownductor.services (created_at);

COMMIT TRANSACTION;
