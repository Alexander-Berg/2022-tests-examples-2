START TRANSACTION;

ALTER TABLE clownductor.projects ADD COLUMN pgaas_root_abc TEXT;

COMMIT;
