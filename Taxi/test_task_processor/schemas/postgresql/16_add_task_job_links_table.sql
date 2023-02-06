-- Build connection between meta cubes and jobs created by them
-- TAXIPLATFORM-5996
--
create table task_processor.task_job_links (
    id BIGSERIAL primary key,
    -- the job that the task triggers
    child_job_id integer unique
        REFERENCES task_processor.jobs(id),
--     meta task which creates the job
    parent_task_id integer
        REFERENCES task_processor.tasks(id),
    -- the job that the meta task belongs to
    parent_job_id integer
        REFERENCES task_processor.jobs(id)
);

create index task_job_links_child_job_id
    on task_processor.task_job_links (child_job_id);
create index task_job_links_parent_task_id
    on task_processor.task_job_links (parent_task_id);
create index task_job_links_parent_job_id
    on task_processor.task_job_links (parent_job_id);
