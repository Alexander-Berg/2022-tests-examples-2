drop index balancers.uniq_non_deleted_branch_id_idx;

create unique index branch_id_awacs_backend_id_unique
    on balancers.upstreams (
        branch_id,
        awacs_backend_id
    )
where
    not is_deleted
;
