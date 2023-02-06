INSERT INTO alert_manager.services (id, service_name, project_name, type, repo_meta)
VALUES (1, 'service', 'project', 'rtc'::alert_manager.service_type_e, ROW('', 'some', 'taxi')::alert_manager.repo_meta_t)
;
