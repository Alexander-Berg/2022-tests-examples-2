INSERT INTO alert_manager.services
    (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
    (1, 150, 'clownductor', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('', '', ''), '{1, 10}'::INTEGER[], '{branch1}'::TEXT[], 'taxi.platform.test', 'branch', 'clownductor_stable')
;
