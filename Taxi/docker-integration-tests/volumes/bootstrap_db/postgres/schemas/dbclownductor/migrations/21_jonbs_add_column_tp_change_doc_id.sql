ALTER TYPE JOB_STATUS ADD VALUE 'inited';
START TRANSACTION;

ALTER TABLE task_manager.jobs ADD COLUMN tp_change_doc_id TEXT DEFAULT NULL;
ALTER TABLE task_manager.jobs ADD COLUMN remote_job_id integer DEFAULT NULL;

COMMIT;
