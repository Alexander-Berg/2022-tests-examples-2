start transaction;

alter table clownductor.parameters
    drop constraint parameters_service_id_fkey;

alter table clownductor.parameters
    drop constraint parameters_branch_id_fkey;

alter table clownductor.parameters
    add constraint parameters_service_id_fkey
    foreign key (service_id)
    references clownductor.services(id)
    on delete cascade;

alter table clownductor.parameters
    add constraint parameters_branch_id_fkey
    foreign key (branch_id)
    references clownductor.branches(id)
    on delete cascade;

commit;
