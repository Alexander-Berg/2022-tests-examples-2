alter table clownductor.variables rename to parameters;

alter table clownductor.parameters
    rename constraint variables_pkey to parameters_pkey;
alter table clownductor.parameters
    rename constraint variables_branch_id_fkey to parameters_branch_id_fkey;
alter table clownductor.parameters
    rename constraint variables_service_id_fkey to parameters_service_id_fkey;

alter index clownductor.variables_service_id rename to parameters_service_id;
alter index clownductor.variables_branch_id rename to parameters_branch_id;
alter index clownductor.variables_subsystem_name_service_id_branch_id
    rename to parameters_subsystem_name_service_id_branch_id_unique;

alter sequence clownductor.variables_id_seq rename to parameters_id_seq;

alter function clownductor.variables_update_at()
    rename to parameters_update_at;
