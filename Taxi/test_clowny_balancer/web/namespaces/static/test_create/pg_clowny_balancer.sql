INSERT INTO balancers.namespaces
    (project_id, awacs_namespace, env, abc_quota_source, is_deleted, deleted_at)
VALUES (1, 'some', 'stable', 'aaa', TRUE, NOW()),
       (2, 'existing', 'stable', 'aaa', FALSE, NULL)
;
