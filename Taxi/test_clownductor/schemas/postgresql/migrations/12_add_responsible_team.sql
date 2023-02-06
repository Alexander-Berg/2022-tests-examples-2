START TRANSACTION;

ALTER TABLE
    clownductor.projects
ADD COLUMN
    responsible_team JSONB NOT NULL DEFAULT '{}'::JSONB;

COMMIT;
