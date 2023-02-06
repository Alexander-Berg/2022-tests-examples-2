insert into services (id, name, cluster_type, grafana_url, tvm_name, project_id, project_name) values
(139, 'hejmdal', 'nanny', '', '', 100500, 'project100500'),
(12345, 'service_name', 'conductor', '', '', 100501, 'project100501');

insert into branches (id, service_id, env, direct_link) values
(1, 139, 'stable', 'direct_link');

insert into branch_hosts (host_name, branch_id, datacenter) values
('hejmdal-stable.yandex.net', 1, 'datacenter');

insert into external_events (id, link, start_ts, deadline_ts, event_type, event_data, revision, finish_ts, is_finished)
 values
(1, 'deploy139stable', '2021-10-21T04:00:00Z', null, 'deploy', '{}'::jsonb, 0, '2021-10-21T04:40:00Z', true),
(2, 'deploy139stable', '2021-10-21T05:00:00Z', null, 'deploy', '{}'::jsonb, 0, '2021-10-21T05:20:00Z', true),
(3, 'drillstaxivlasas', '2021-10-21T01:00:00Z', null, 'drills',
 '{"datacenters":["vla", "sas"], "project_ids":[100500, 100501]}'::jsonb, 0, '2021-10-21T10:00:00Z', true),
(4, 'drillstaximan', '2021-10-19T00:00:00Z', null, 'drills', '{"datacenters":["man"], "project_ids":[100500]}'::jsonb,
 0, '2021-10-19T10:00:00Z', true),
(5, 'drillstaxisas', '2021-10-23T00:00:00Z', null, 'drills', '{"datacenters":["sas"], "project_ids":[100501]}'::jsonb, 0, NULL, false);

insert into incident_history (circuit_id, out_point_id, start_time, end_time, alert_status, description, meta_data)
 values
('hejmdal-stable.yandex.net::template_id', 'alert', '2021-10-21T03:00:00Z', '2021-10-21T04:30:00Z', 'WARN', 'descr',
 '{"yandex_monitoring_link":{"address": "yandex_monitoring_link_address"}}'::jsonb),
('direct_link::template_id', 'alert', '2021-10-21T04:50:00Z', '2021-10-21T08:00:00Z', 'CRIT', 'descr','{}'::jsonb);

insert into circuit_states (circuit_id, out_point_id, alert_status, incident_start_time, description, meta_data, updated)
 values
('hejmdal-stable.yandex.net::other_template_id', 'alert', 'WARN', '2021-10-24T04:00:00', 'description', '{}'::jsonb, NOW());
