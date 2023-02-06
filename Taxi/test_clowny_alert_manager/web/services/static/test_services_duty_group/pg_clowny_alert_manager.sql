INSERT INTO alert_manager.services (id, clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
   (1, NULL, NULL, 'taxi', 'crons', 'cgroup'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t),
   (2, 1, 1, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t),
   (3, 139, 150, 'hejmdal', 'project', 'rtc', ROW('', '', '')),
   (4, 1234, 1234, 'some-service', 'project', 'rtc', ROW('', '', '')),
   (5, 13, 13, 'clowny-alert-manager', 'project', 'rtc', ROW('', '', '')),
   (6, 100500, 13, '', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
    (service_id, clown_branch_ids, names, repo_meta, namespace, basename, juggler_host)
VALUES
    (1, '{}', '{"some"}', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'default', 'some', 'some'),
    (2, '{1, 2}', '{"branch1", "branch2"}', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'default', 'branch1', 'branch1'),
    (3, '{18, 19}'::INTEGER[], '{taxi_hejmdal_stable, taxi_hejmdal_pre_stable}'::TEXT[], ROW('', '', ''), 'taxi.platform.test', 'taxi_hejmdal_stable', 'taxi_hejmdal_stable'),
    (4, '{1, 2}'::INTEGER[], '{stable_branch, pre_stable_branch}'::TEXT[], ROW('', '', ''), 'taxi.platform.test', 'some-service_stable', 'some-service_stable'),
    (5, '{13}'::INTEGER[], '{clowny-alert-manager_stable}'::TEXT[], ROW('', '', ''), 'taxi.platform.test', 'some-service_stable', 'some-service_stable'),
    (6, '{100500}'::INTEGER[], '{smth_stable}'::TEXT[], ROW('', '', ''), 'taxi.platform.test', 'smth_stable', 'smth_stable')
;
