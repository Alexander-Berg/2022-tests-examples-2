start transaction;

alter table task_processor.cubes add column invalid boolean not null default false;
alter table task_processor.providers add column hostname text not null;
alter table task_processor.providers add column tvm_name text not null;
create index task_processor_cubes_invalid on task_processor.cubes (invalid);

commit;
