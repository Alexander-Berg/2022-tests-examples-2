INSERT INTO alert_manager.templates (name, namespace, repo_meta)
VALUES
    (
        'oom', 'default',
        ROW('templates/oom.yaml', 'oom.yaml', 'taxi')::alert_manager.repo_meta_t
    ),
    (
        'pkgver', 'default',
        ROW('templates/pkgver.yaml', 'pkgver.yaml', 'taxi')::alert_manager.repo_meta_t
    )
;

INSERT INTO alert_manager.events (name, template_id, settings)
VALUES
(
    'oom', 1,
    ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            TRUE, -- ignore_nodata
            NULL, -- flaps
            ARRAY[(ARRAY['Mon', 'Sun'], ARRAY[0, 23], (0, NULL), (0, NULL))]::alert_manager.time_settings_t[], -- times
            NULL, -- startrek
            NULL, -- responsibles
            NULL, -- unreach
            NULL, -- active
            NULL -- active_kwargs
        )::alert_manager.overridable_settings_t
);
