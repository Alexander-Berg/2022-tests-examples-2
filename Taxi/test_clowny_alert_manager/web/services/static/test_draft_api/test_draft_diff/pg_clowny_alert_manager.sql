INSERT INTO alert_manager.services
    (clown_service_id, clown_project_id, project_name, service_name, type, repo_meta)
VALUES
    (1, 1, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW('b1.yaml', 'b1.yaml', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('b1.yaml', 'b1.yaml', 'taxi')::alert_manager.repo_meta_t, '{}', '{taxi_clownductor_stable}'::TEXT[], 'ns1', 'taxi_clownductor_stable', 'taxi_clownductor_stable')
;
