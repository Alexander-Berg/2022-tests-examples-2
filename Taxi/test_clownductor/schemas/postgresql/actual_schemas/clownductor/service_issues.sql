create table clownductor.service_issues (
    -- just an id
    id serial unique primary key,
    -- part of what service this issue is
    service_id integer not null references
        clownductor.services (id) on delete cascade,
    -- key of the problem
    issue_key text not null,
    -- additional parameters of the issue
    issue_parameters jsonb not null
);

create unique index service_issues_service_id_key_unique
    on clownductor.service_issues (service_id, issue_key);
