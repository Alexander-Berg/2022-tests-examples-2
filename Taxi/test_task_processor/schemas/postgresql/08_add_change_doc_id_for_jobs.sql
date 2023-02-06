start transaction;

alter table task_processor.jobs add column change_doc_id text not null;

CREATE UNIQUE INDEX change_doc_id_key ON task_processor.jobs(change_doc_id)
WHERE status = 'in_progress';

commit;
