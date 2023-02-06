start transaction;

alter table task_manager.jobs add column change_doc_id text default null;

create unique index change_doc_id_key on task_manager.jobs(change_doc_id)
where status = 'in_progress' and change_doc_id is not null;

commit;
