START TRANSACTION;

ALTER TABLE task_manager.jobs ADD COLUMN idempotency_token TEXT;

COMMIT;

CREATE INDEX task_manager_jobs_token
    ON task_manager.jobs (idempotency_token);
