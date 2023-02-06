INSERT INTO alert_manager.services
    (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
    (1, 1, 'some', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('', '', ''), '{1}'::INTEGER[], '{branch1}'::TEXT[], 'default', 'branch1', 'branch1'),
    (1, ROW('', '', ''), '{2}'::INTEGER[], '{branch2}'::TEXT[], 'default', 'branch2', 'branch2'),
    (1, ROW('', '', ''), '{3}'::INTEGER[], '{branch3}'::TEXT[], 'default', 'branch3', 'branch3')
;

INSERT INTO alert_manager.configs_queue
    (branch_id, data, status, updated_at, job_id, applied_at)
VALUES
    (1, '{}', 'pending', '2020.06.08T12:00:00'::TIMESTAMP, NULL, NULL),
    (2, '{}', 'failed', '2020.06.08T12:00:00'::TIMESTAMP, 1, NULL),
    (2, '{}', 'applied', '2020.06.08T12:10:00'::TIMESTAMP, 2, '2020.06.08T12:10:00'::TIMESTAMP),
    (3, '{}', 'applied', '2020.06.08T12:10:00'::TIMESTAMP, 3, '2020.06.08T12:10:00'::TIMESTAMP),
    (3, '{}', 'failed', '2020.06.08T12:20:00'::TIMESTAMP, 4, NULL)
;
