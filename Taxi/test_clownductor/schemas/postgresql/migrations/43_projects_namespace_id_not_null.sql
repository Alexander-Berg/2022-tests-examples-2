alter table clownductor.projects
    alter column namespace_id set not null;

create index clownductor_projects_namespace_id
    on clownductor.projects (namespace_id);
