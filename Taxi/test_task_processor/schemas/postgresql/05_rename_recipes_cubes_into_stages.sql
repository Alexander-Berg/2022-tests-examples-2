start transaction;

alter table task_processor.recipes_cubes rename to stages;

commit;
