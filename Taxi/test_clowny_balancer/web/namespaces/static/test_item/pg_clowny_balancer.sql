INSERT INTO balancers.namespaces
    (id, project_id, awacs_namespace, env, abc_quota_source, is_shared, is_external, created_at, updated_at)
VALUES
    (1, 1, 'aaa.net', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z'),
    (2, 1, 'bbb.net', 'stable', 'some', FALSE, FALSE, '2020-06-05T12:00:00Z', '2020-06-05T12:10:00Z')
;
