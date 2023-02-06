-- id entity_type
create table task_processor.entity_types (
    id serial unique primary key,
    entity_type text unique not null
);

-- id external_entities_links
create table task_processor.external_entities_links (
    id serial unique primary key,
    external_id text not null,
    entity_type_id integer not null references
        task_processor.entity_types (id) on delete cascade,
    job_id integer not null references
        task_processor.jobs (id) on delete cascade
);

create index external_entities_links_job_id
    on task_processor.external_entities_links(job_id);

create index external_entities_links_external_id_entity_type_id
    on task_processor.external_entities_links(entity_type_id, external_id);
