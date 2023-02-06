create function task_processor.trigger_update_at() returns trigger as $$
begin
    new.updated_at := extract (epoch from now());
    return new;
end;
$$ language plpgsql;

create trigger recipes_date_updater before insert or update on task_processor.recipes for each row
execute procedure task_processor.trigger_update_at();
create trigger recipes_cubes_date_updater before insert or update on task_processor.recipes_cubes for each row
execute procedure task_processor.trigger_update_at();
