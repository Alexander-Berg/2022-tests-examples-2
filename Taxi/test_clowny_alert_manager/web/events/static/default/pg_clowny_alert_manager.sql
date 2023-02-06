INSERT INTO alert_manager.services (clown_service_id, clown_project_id, service_name, project_name, type, repo_meta)
VALUES
   (NULL, NULL, 'taxi', 'crons', 'cgroup'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t),
   (1, 1, 'taxi-infra', 'clownductor', 'rtc'::alert_manager.service_type_e, ROW('', '', 'taxi')::alert_manager.repo_meta_t)
;

INSERT INTO alert_manager.branches
    (service_id, clown_branch_ids, names, namespace, repo_meta, basename, juggler_host)
VALUES
    (1, '{}', '{"some"}', 'default', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'some', 'some'),
    (2, '{1, 2}', '{"branch1", "branch2"}', 'default', ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t, 'branch1', 'branch1')
;

INSERT INTO alert_manager.configs (branch_id, repo_meta)
VALUES (1, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t),
       (2, ROW('b.yaml', 'b.yaml', 'taxi')::alert_manager.repo_meta_t)
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
