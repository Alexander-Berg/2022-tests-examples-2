start transaction;

alter table task_processor.recipes drop constraint recipes_provider_id_name_key;
alter table task_processor.recipes add column version integer not null default 1::integer;
create unique index recipes_provider_id_name_version_key
    on task_processor.recipes (provider_id, name, version);

commit;
