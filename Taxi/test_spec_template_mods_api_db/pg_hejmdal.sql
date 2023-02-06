insert into spec_template_mods
(id, login, ticket, spec_template_id, service_id, env, host_name,
 domain_name, circuit_id, type, mod_data, updated)
values
(101, 'some-login', 'SOMETICKET', 'spec_template_id1', -1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '1970-01-15T06:58:08.001+00:00'),
(102, 'some-login', 'SOMETICKET', 'spec_template_id2', -1,
 'stable', '', '', '', 'schema_override', '{"params":{}}', '1970-01-15T07:58:08.001+00:00'),
(103, 'some-login', 'SOMETICKET', 'spec_template_id3', 1,
 'any', '', '', '', 'spec_disable', '{"disable":true}', '1970-01-15T08:58:08.001+00:00'),
(104, 'some-login', 'SOMETICKET', 'spec_template_id4', 1,
 'any', '', 'domain1', '', 'spec_disable', '{"disable":true}', '1970-01-15T09:58:08.001+00:00'),
(105, 'some-login', 'SOMETICKET', 'spec_template_id5', 1,
 'stable', '', '', '', 'spec_disable', '{"disable":true}', '1970-01-15T10:58:08.001+00:00'),
(106, 'some-login', 'SOMETICKET', 'spec_template_id6', 1,
 'any', 'host1', '', '', 'spec_disable', '{"disable":true}', '1970-01-15T11:58:08.001+00:00');

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');
