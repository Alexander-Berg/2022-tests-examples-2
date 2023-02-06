start transaction;

alter table task_processor.cubes add column output_parameters jsonb default  '[]'::jsonb;
alter table task_processor.tasks add column output_parameters jsonb default  '[]'::jsonb;

commit;
