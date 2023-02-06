start transaction;

alter table task_processor.stages drop constraint recipes_cubes_recipe_id_fkey,
add constraint recipes_cubes_recipe_id_fkey
foreign key (recipe_id) references task_processor.recipes (id) on delete cascade;

commit;
