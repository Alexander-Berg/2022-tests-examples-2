INSERT INTO alert_manager.templates (name, namespace,repo_meta)
VALUES
    (
        'oom', 'default',
        ROW('templates/oom.yaml', 'oom.yaml', 'default')::alert_manager.repo_meta_t
    )
;
