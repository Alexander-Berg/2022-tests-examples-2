INSERT INTO alert_manager.services
    (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
    (1, 1, 'service1', 'project', 'rtc', ROW('', '', '')),
    (2, 2, 'service2', 'project', 'rtc', ROW('', '', ''))
;

INSERT INTO alert_manager.branches
    (service_id, repo_meta, clown_branch_ids, names, namespace, basename, juggler_host)
VALUES
    (1, ROW('', '', ''), '{11, 12, 13}'::INTEGER[], '{branch12, branch22, branch23}'::TEXT[], 'default', 'branch', 'branch'),
    (2, ROW('', '', ''), '{21, 22}'::INTEGER[], '{branch21, branch22}'::TEXT[], 'default', 'branch', 'branch'),
    (2, ROW('', '', ''), '{23}'::INTEGER[], '{branch23}'::TEXT[], 'default', 'branch', 'branch')
;

INSERT INTO alert_manager.configs (branch_id, repo_meta)
VALUES
    (1, ROW('b11.yaml', 'b11.yaml', 'taxi')::alert_manager.repo_meta_t),
    (1, ROW('b12.yaml', 'b12.yaml', 'taxi')::alert_manager.repo_meta_t),
    (2, ROW('b2.yaml', 'b2.yaml', 'taxi')::alert_manager.repo_meta_t),
    (3, ROW('b3.yaml', 'b3.yaml', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.templates (name, namespace, repo_meta)
VALUES
    (
        'template1',
        'default',
        ROW('', '', '')::alert_manager.repo_meta_t
    )
;

INSERT INTO alert_manager.events
    (name, config_id, template_id, settings)
VALUES
    (
        'event1',
        4,
        NULL,
        ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            FALSE, -- ignore_nodata
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
        'event2',
        NULL,
        1,
        ROW(
            NULL, -- children_event
            NULL, -- children
            NULL, -- refresh_time
            NULL, -- ttl
            NULL, -- escalation_method
            FALSE, -- ignore_nodata
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

INSERT INTO alert_manager.notification_options
    (name, logins, statuses, type, repo_meta)
VALUES
    ('tgm1', '{user1, user2}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi1')::alert_manager.repo_meta_t),
    ('tgm2', '{user1, user2}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi2')::alert_manager.repo_meta_t),
    ('tgm3', '{user1, user2}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi3')::alert_manager.repo_meta_t),
    ('tgm4', '{user3}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi4')::alert_manager.repo_meta_t),
    ('tgm5', '{user4}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi5')::alert_manager.repo_meta_t),
    ('tgm6', '{user5}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi6')::alert_manager.repo_meta_t),
    ('tgm7', '{user6}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi7')::alert_manager.repo_meta_t),
    ('tgm8', '{chat7}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi8')::alert_manager.repo_meta_t),
    ('tgm9', '{user8}'::TEXT[], '{}'::alert_manager.no_status_t[], 'telegram'::alert_manager.notification_type_e, ROW(null, null, 'taxi9')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.configs_templates_m2m
    (config_id, template_id, overrides)
VALUES
    (
        2,
        1,
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

INSERT INTO alert_manager.configs_notifications_m2m (config_id, notification_option_id)
VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (3, 5),
    (4, 6)
;

INSERT INTO alert_manager.events_notifications_m2m (event_id, notification_option_id)
VALUES
    (1, 7),
    (2, 8)
;

INSERT INTO alert_manager.configs_templates_notifications_m2m (config_template_id, notification_option_id)
VALUES
    (1, 9)
;
