INSERT INTO alert_manager.services (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
   (NULL, NULL, 'taxi', 'crons', 'cgroup'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t),
   (1, 1, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.branches
    (service_id, clown_branch_ids, names, repo_meta, namespace, basename, juggler_host)
VALUES
    (1, '{}', '{"some"}', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'default', 'some', 'some'),
    (2, '{1, 2}', '{"branch1", "branch2"}', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'default', 'branch1', 'branch1')
;
