INSERT INTO alert_manager.templates (name, namespace, repo_meta)
VALUES
    (
        'oom',
        'default',
        ROW('templates/oom.yaml', 'oom.yaml', 'default')::alert_manager.repo_meta_t
    ),
    (
        'pkgver',
        'default',
        ROW('templates/pkgver.yaml', 'pkgver.yaml', 'default')::alert_manager.repo_meta_t
    )
;

INSERT INTO alert_manager.events (name, template_id, ignore_nodata, times)
VALUES
(
'oom', 1, TRUE,
ARRAY[(ARRAY['Mon', 'Sun'], ARRAY[0, 23], (0, NULL), (0, NULL))]::alert_manager.time_settings_t[]
)
