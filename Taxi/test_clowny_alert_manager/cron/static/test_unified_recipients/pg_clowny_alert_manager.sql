INSERT INTO alert_manager.services
(id, clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
    (1, 1, 150, 'clownductor', 'project', 'rtc', ROW('', '', '')),
    (2, 666, 150, 'service_without_stable', 'project', 'rtc', ROW('', '', '')),
    (3, 139, 150, 'hejmdal', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
(service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('', '', ''), '{1, 10}'::INTEGER[], '{branch1}'::TEXT[], 'taxi.platform.test', 'branch', 'clownductor_stable'),
    (2, ROW('', '', ''), '{666}'::INTEGER[], '{service_without_stable_testing}'::TEXT[], 'taxi.platform.test', 'service_without_stable_testing', 'service_without_stable_testing'),
    (3, ROW('', '', ''), '{16, 17}'::INTEGER[], '{taxi_hejmdal_testing, taxi_hejmdal_testing2}'::TEXT[], 'taxi.platform.test', 'taxi_hejmdal_testing', 'taxi_hejmdal_testing'),
    (3, ROW('', '', ''), '{18, 19}'::INTEGER[], '{taxi_hejmdal_stable, taxi_hejmdal_pre_stable}'::TEXT[], 'taxi.platform.test', 'taxi_hejmdal_stable', 'taxi_hejmdal_stable')
;
