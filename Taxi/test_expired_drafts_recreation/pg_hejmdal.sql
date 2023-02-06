insert into incident_history(id, circuit_id, out_point_id, incident_status, start_time, end_time, alert_status,
                             description, meta_data) values
(1, 'taxi_hejmdal_stable::rtc_cpu_low_usage_testing', 'low_usage', 'closed', '2021-11-23T00:00:00Z', '2021-11-30T00:00:00Z',
 'WARN', 'desc', '{"env": "testing", "service_id": 139}'::JSONB);

insert into services (id, name, cluster_type, grafana_url, tvm_name, project_id, project_name, maintainers) values
(139, 'hejmdal', 'nanny', '', '', 100500, 'project100500', '{"atsinin"}');

insert into branches (id, service_id, env, direct_link) values
(1, 139, 'testing', 'direct_link');

insert into change_resource_drafts(id, branch_id, approve_status, apply_status, approve_status_age, apply_status_age,
                                   changes) values
(123456, 1, 'no_decision', 'not_started', 1, 1, '{"(cpu,1000)"}');

insert into digests(id, digest_name, sticker_uid, last_broadcast, period_hours, digest_format, description,
                    circuit_id_like, out_point_id_like, params) values
(123, 'LOW usage - CPU - rtc - stat', 'atsinin@myandex-team.ru', '2021-11-23T00:00:00Z', 168,
 'personalized_resource_usage', 'description', '{%::rtc_cpu_low_usage%}', 'low_usage',
 '{"filters": {"env": ["testing"]}, "cluster_types": ["nanny"], "service_stat_id": "cpu_low_usage"}');

insert into service_stats(stat_id, service_id, period_start, period_end, updated, stat_data) values
('cpu_low_usage', 139, '2021-11-23T00:00:00Z', '2021-11-30T00:00:00Z', '2021-11-23T00:00:00Z', '{"not_ok_percent": 100.0}'::JSONB)
