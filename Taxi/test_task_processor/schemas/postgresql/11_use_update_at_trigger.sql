create trigger tasks_date_updater before update on task_processor.tasks for each row
execute procedure task_processor.trigger_update_at();
create trigger cubes_date_updater before update on task_processor.cubes for each row
execute procedure task_processor.trigger_update_at();
create trigger providers_date_updater before update on task_processor.providers for each row
execute procedure task_processor.trigger_update_at();
