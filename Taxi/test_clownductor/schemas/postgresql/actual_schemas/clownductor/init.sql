DROP SCHEMA IF EXISTS clownductor;
CREATE SCHEMA clownductor;

--
-- Types
--

create type cluster_type as enum (
    'conductor',
    'nanny',
    'postgres',
    'redis_mdb',
    'mongo_mdb',
    'mongo_lxc',
    'redis_lxc',
    'clickhouse',
    'mysql',
    'market_service',
    'ydb'
);

create type environment_type as enum (
    'unstable',
    'testing',
    'prestable',
    'stable'
);

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
