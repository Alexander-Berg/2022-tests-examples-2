START TRANSACTION;

ALTER TABLE clownductor.services ADD COLUMN service_url TEXT;

COMMIT;
