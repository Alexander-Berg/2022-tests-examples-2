INSERT INTO alert_manager.services
    (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
    (139, 1, 'service1', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('', '', ''), '{1, 2}'::INTEGER[], '{branch1, branch2}'::TEXT[], 'taxi.platform.prod', 'branch', 'hejmdal_stable'),
    (1, ROW('', '', ''), '{3}'::INTEGER[], '{branch3}'::TEXT[], 'taxi.platform.test', 'branch', 'hejmdal_testing')
;
