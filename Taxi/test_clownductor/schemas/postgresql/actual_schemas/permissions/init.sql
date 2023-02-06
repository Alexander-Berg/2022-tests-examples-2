create schema permissions;

create function permissions.set_updated() returns trigger as $set_updated$
    begin
        new.updated_at = now();
        return new;
    end;
$set_updated$ language plpgsql;

create function permissions.set_deleted() returns trigger as $set_deleted$
    begin
        if new.is_deleted and not old.is_deleted then new.deleted_at = now(); end if;
        if not new.is_deleted and old.is_deleted then new.deleted_at = null; end if;
        return new;
    end;
$set_deleted$ language plpgsql;

create function permissions.service_project_deleted() returns trigger as $service_project_deleted$
    begin
        if old.project_id is not null and new.project_id is null
            then
                new.deleted_project = old.project_id;
                new.is_deleted = true;
        end if;
        if old.service_id is not null and new.service_id is null
            then
                new.deleted_service = old.service_id;
                new.is_deleted = true;
        end if;
        return new;
    end;
$service_project_deleted$ language plpgsql;
