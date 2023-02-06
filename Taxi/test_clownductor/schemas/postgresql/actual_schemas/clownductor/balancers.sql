create table clownductor.balancers (
    id serial unique primary key,
    awacs_namespace text not null unique,
    is_https boolean default false,
    hosts text[] not null,

    -- sets then awacs namespace was created
    is_ready boolean default false,

    created_at integer default extract (epoch from now()),
    updated_at integer default null,
    deleted_at integer default null
);

create index balancers_awacs_namespace_idx on clownductor.balancers(awacs_namespace);

create function set_updated() returns trigger as $set_updated$
    begin
        if new.updated_at is null then
            new.updated_at = extract (epoch from now());
        end if;
        return new;
    end;
$set_updated$ language plpgsql;

create trigger balancers_set_updated before update or insert on clownductor.balancers
    for each row execute procedure set_updated();
