insert into custom_checks (id, name, description, service_id, schema_id, flows, alert_details, revision, deleted, updated)
values
(1, 'custom_check_1', 'custom_check_1_description', 1, 'schema_id_1', '{}', 'alert_details_1', 1, true, '2020-06-09 18:00:00');

insert into incident_history (circuit_id, out_point_id, start_time, end_time, alert_status, description)
values
('test_circuit_1', 'op1', '2020-06-09 03:51:00', '2020-06-09 03:52:00', 'WARN', ''),
('test_circuit_2', 'op1', '2019-01-01 03:51:00', '2019-01-01 03:52:00', 'WARN', '');

insert into services_uptime (service_id, uptime_1d, uptime_7d, uptime_30d, updated)
values
(3, 97.0, 98.0, 99.0, '2021-09-25 10:00:00');

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service_1', 'nanny', '2020-06-09T17:52:40+0000', false, -1, 'test_project',
 '{}'),
(2, 'test_service_2', 'nanny', '2020-06-09T17:56:40+0000', true, -1, 'test_project',
 '{}'),
(3, 'test_service_3', 'nanny', '2020-06-09T16:52:40+0000', false, -1, 'test_project',
 '{}'),
(4, 'test_service_4', 'nanny', '2020-06-09T16:52:40+0000', true, -1, 'test_project',
 '{}');

insert into spec_template_mods
(id, login, ticket, spec_template_id, service_id, env, host_name,
 domain_name, circuit_id, type, mod_data, updated, deleted)
values
(1, 'some-login', 'SOMETICKET', 'spec_template_id_1', -1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '2020-06-09T17:52:40+0000', false),
(2, 'some-login', 'SOMETICKET', 'spec_template_id_2', -1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '2020-06-09T17:52:40+0000', true ),
(3, 'some-login', 'SOMETICKET', 'spec_template_id_3', -1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '2020-06-09T16:52:40+0000', false),
(4, 'some-login', 'SOMETICKET', 'spec_template_id_4', -1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '2020-06-09T16:52:40+0000', true);

insert into external_events (id, link, start_ts, finish_ts, is_finished, event_type, event_data)
values
(1, 'drillslavkataxiiva1', now(), '2020-06-09T17:52:40+0000', false,
 'drills', '{"datacenters": ["iva"], "project_ids": [1, 2, 3]}'),
(2, 'drillslavkataxiiva2', now(), '2020-06-09T17:52:40+0000', true,
 'drills', '{"datacenters": ["iva"], "project_ids": [1, 2, 3]}'),
(3, 'drillslavkataxiiva3', now(), '2020-05-09T17:52:40+0000', false,
 'drills', '{"datacenters": ["iva"], "project_ids": [1, 2, 3]}'),
(4, 'drillslavkataxiiva4', now(), '2020-05-09T17:52:40+0000', true,
 'drills', '{"datacenters": ["iva"], "project_ids": [1, 2, 3]}');
