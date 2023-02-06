START TRANSACTION;

ALTER TABLE clownductor.services ADD COLUMN new_service_ticket TEXT;

COMMIT;
