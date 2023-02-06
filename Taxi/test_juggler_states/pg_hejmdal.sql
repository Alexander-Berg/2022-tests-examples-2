insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');

insert into branches (id, service_id, env, direct_link)
values (11, 1, 'stable', 'test_service_stable');
