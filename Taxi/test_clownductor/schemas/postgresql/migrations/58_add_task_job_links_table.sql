-- Build connection between meta cubes and jobs created by them
-- TAXIPLATFORM-5996
--
CREATE TABLE task_manager.task_job_links (
    id BIGSERIAL PRIMARY KEY,
    -- the job that the task triggers
    child_job_id INTEGER UNIQUE
        REFERENCES task_manager.jobs(id),
--     meta task which creates the job
    parent_task_id INTEGER
        REFERENCES task_manager.tasks(id),
    -- the job that the meta task belongs to
    parent_job_id INTEGER
        REFERENCES task_manager.jobs(id)
);

CREATE INDEX task_job_links_child_job_id
    ON task_manager.task_job_links (child_job_id);
CREATE INDEX task_job_links_parent_task_id
    ON task_manager.task_job_links (parent_task_id);
CREATE INDEX task_job_links_parent_job_id
    ON task_manager.task_job_links (parent_job_id);
