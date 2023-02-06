start transaction;

create unique index services_project_id_service_name_type_deleted_at_unique
    on clownductor.services
        (project_id, name, cluster_type)
where
    deleted_at is null
;

drop index clownductor.clownductor_project_id_service_name_type_deleted_at_idx;

create unique index branches_service_id_name_key_deleted_at_unique
    on clownductor.branches
        (service_id, name)
where
    deleted_at is null
;

drop index clownductor.branches_service_id_name_key_deleted_at_idx;

commit;
