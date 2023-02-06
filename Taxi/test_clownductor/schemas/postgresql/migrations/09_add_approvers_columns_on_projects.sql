START TRANSACTION;

ALTER TABLE clownductor.projects ADD approving_managers JSONB NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE clownductor.projects ADD approving_devs JSONB NOT NULL DEFAULT '{}'::jsonb;

COMMIT;
