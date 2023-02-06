create function clownductor.set_updated() returns trigger as $set_updated$
    begin
        new.updated_at = now();
        return new;
    end;
$set_updated$ language plpgsql;

create function clownductor.set_deleted() returns trigger as $set_deleted$
    begin
        if new.is_deleted and not old.is_deleted then new.deleted_at = now(); end if;
        if not new.is_deleted and old.is_deleted then new.deleted_at = null; end if;
        return new;
    end;
$set_deleted$ language plpgsql;

create table clownductor.namespaces (
    id serial primary key,
    name text not null,

    created_at timestamp not null default now(),
    updated_at timestamp not null default now(),
    deleted_at timestamp default null,
    is_deleted boolean default false
);

create unique index clownductor_namespaces_name_unique
    on clownductor.namespaces(name)
    where not is_deleted;

alter table clownductor.namespaces
    add constraint check_deleted_with_time
        check ( is_deleted != (deleted_at is null) ),
    add constraint check_name_as_slug
        check (
            length(name) > 1
            and length(name) <= 100
            and name ~ '^[a-z][a-z0-9_-]*$'
            )
;

create trigger clownductor_namespaces_set_updated
    before update or insert on clownductor.namespaces
    for each row execute procedure clownductor.set_updated();

create trigger clownductor_namespaces_set_deleted
    before update on clownductor.namespaces
    for each row execute procedure clownductor.set_deleted();

alter table clownductor.projects
    add column namespace_id integer;

alter table clownductor.projects
    add constraint projects_namespace_id_fkey
    foreign key (namespace_id)
    references clownductor.namespaces (id);
