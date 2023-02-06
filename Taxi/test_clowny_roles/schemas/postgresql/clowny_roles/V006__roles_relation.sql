create table roles.roles_relation (
    main_role_id integer not null references
        roles.roles (id) on delete cascade,
    related_role_id integer not null references
        roles.roles (id) on delete cascade,
    primary key (main_role_id, related_role_id)
);
