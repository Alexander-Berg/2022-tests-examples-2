INSERT INTO alert_manager.services (clown_service_id, clown_project_id, project_name, service_name, type, repo_meta)
VALUES
   (NULL, NULL, 'taxi-infra', 'some', 'rtc'::alert_manager.service_type_e, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t),
   (1, 150, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t),
   (2, 2, 'taxi-infra', 'clowny-alerts', 'rtc'::alert_manager.service_type_e, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (3, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, '{3}', '{"clowny-alerts"}', 'taxi', 'clowny-alerts', 'clowny-alerts')
;

INSERT INTO alert_manager.configs (branch_id, repo_meta)
VALUES (1, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.events (config_id, name, settings)
VALUES
(
    1,
    'oom',
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
)
;

INSERT INTO alert_manager.templates (repo_meta, name, namespace)
VALUES
    (
        ROW('templates/pkgver.yaml', 'pkgver.yaml', 'taxi')::alert_manager.repo_meta_t,
        'pkgver',
        'default'
    )
;
INSERT INTO alert_manager.events
    (name, config_id, template_id, settings)
VALUES
    (
        'pkgver',
        NULL,
        1,
        ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            True, -- ignore_nodata
            NULL, -- flaps
            ARRAY[(ARRAY['Mon', 'Sun'], ARRAY[0, 23], (0, NULL), (0, NULL))]::alert_manager.time_settings_t[], -- times
            NULL, -- startrek
            NULL, -- responsibles
            NULL, -- unreach
            NULL, -- active
            NULL -- active_kwargs
        )::alert_manager.overridable_settings_t
    )
;
INSERT INTO alert_manager.configs_templates_m2m
    (config_id, template_id, overrides)
VALUES
    (
        1,
        1,
        ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            FALSE, -- ignore_nodata
            NULL, -- flaps
            NULL, -- times
            NULL, -- startrek
            NULL, -- responsibles
            NULL, -- unreach
            NULL, -- active
            NULL -- active_kwargs
        )::alert_manager.overridable_settings_t
    )
;
INSERT INTO alert_manager.notification_options
    (repo_meta, name, logins, statuses, type)
VALUES
    (
        ('', '', '')::alert_manager.repo_meta_t,
        'telegram_option1',
        '{"d1mbas"}'::TEXT[],
        ARRAY[('OK', 'WARN')]::alert_manager.no_status_t[],
        'telegram'
    )
;

INSERT INTO alert_manager.configs_templates_notifications_m2m
    (config_template_id, notification_option_id)
VALUES
    (1, 1)
;
