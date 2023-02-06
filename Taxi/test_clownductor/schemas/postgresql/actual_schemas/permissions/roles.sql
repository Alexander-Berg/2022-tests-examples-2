create table permissions.roles (
    id bigserial primary key,
    role text not null,
    login text not null,

    project_id bigint references clownductor.projects(id) on delete set null,
    service_id bigint references clownductor.services(id) on delete set null,

    deleted_project bigint default null,
    deleted_service bigint default null,

    fired boolean default false,

    created_at timestamp default now(),
    updated_at timestamp not null,
    deleted_at timestamp default null,
    is_deleted boolean default false,
    is_super boolean not null default false
);

create unique index uniq_login_role_project_idx
    on permissions.roles(login, role, project_id)
    where not is_deleted and project_id is not null;

create unique index uniq_login_role_service_idx
    on permissions.roles(login, role, service_id)
    where not is_deleted and service_id is not null;

alter table permissions.roles
    add constraint check_fired_is_deleted check ( not fired or fired and is_deleted),
    add constraint check_deleted_with_time check ( is_deleted <> (deleted_at is null) ),
    add constraint check_exclusive_project_or_service
        check (
            case
                when not is_super then
                        (project_id is not null or deleted_project is not null) <>
                        (service_id is not null or deleted_service is not null)
                else (
                        project_id is null and
                        deleted_project is null and
                        service_id is null and
                        deleted_service is null
                    )
                end
            )
;

create trigger permissions_role_set_updated before update or insert on permissions.roles
    for each row execute procedure permissions.set_updated();
create trigger permissions_role_set_deleted before update on permissions.roles
    for each row execute procedure permissions.set_deleted();
create trigger permissions_role_delete_reference before update on permissions.roles
    for each row execute procedure permissions.service_project_deleted();
