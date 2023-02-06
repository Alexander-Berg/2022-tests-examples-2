INSERT INTO alert_manager.services (clown_service_id, clown_project_id, project_name, service_name, type, repo_meta)
VALUES
   (NULL, NULL, 'taxi', 'crons', 'cgroup'::alert_manager.service_type_e, ROW(NULL, NULL, 'taxi')::alert_manager.repo_meta_t),
   (1, 1, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW(NULL, NULL, 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.branches
    (service_id, clown_branch_ids, names, repo_meta, namespace, basename, juggler_host)
VALUES
    (1, '{}', '{"some"}', ROW('b1.yaml', 'b1.yaml', 'taxi')::alert_manager.repo_meta_t, 'ns1', 'some', 'some'),
    (2, '{1, 2}', '{"branch1", "branch2"}', ROW('b2.yaml', 'b2.yaml', 'taxi')::alert_manager.repo_meta_t, 'ns1', 'branch1', 'branch1')
;

INSERT INTO alert_manager.configs (branch_id, repo_meta)
VALUES (1, ROW('b1.yaml', 'b1.yaml', 'taxi')::alert_manager.repo_meta_t),
       (2, ROW('b2.yaml', 'b2.yaml', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.events (config_id, name, settings)
VALUES
   (
        1, 'oom',
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
   ),
   (
        1, 'vhost500',
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
   ),
   (
        2, 'oom',
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

INSERT INTO alert_manager.notification_options (name, logins, statuses, type, repo_meta)
VALUES ('telegram_option1', ARRAY['d1mbas']::TEXT[], ARRAY[('OK', 'WARN')]::alert_manager.no_status_t[], 'telegram', ('', '', '')::alert_manager.repo_meta_t),
       ('telegram_option2', ARRAY['mvpetrov']::TEXT[], ARRAY[('OK', 'WARN')]::alert_manager.no_status_t[], 'telegram', ('', '', '')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.events_notifications_m2m (event_id, notification_option_id)
VALUES (1, 1)
;

INSERT INTO alert_manager.configs_notifications_m2m (config_id, notification_option_id)
VALUES (1, 1)
;

INSERT INTO alert_manager.templates(name, namespace, repo_meta)
VALUES ('pkgver', 'default', ROW('templates/pkgver.yaml', 'pkgver.yaml', 'taxi')::alert_manager.repo_meta_t);

INSERT INTO alert_manager.events (template_id, name, settings)
VALUES
    (
        1, 'pkgver',
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

INSERT INTO alert_manager.configs_templates_m2m (config_id, template_id, overrides)
VALUES
    (
        1, 1,
        ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            TRUE, -- ignore_nodata
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

INSERT INTO alert_manager.configs_templates_notifications_m2m (config_template_id, notification_option_id)
VALUES (1, 2)
;
