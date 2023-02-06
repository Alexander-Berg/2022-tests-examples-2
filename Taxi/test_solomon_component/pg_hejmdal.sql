insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(1, 'test_service', 'nanny', now() at time zone 'utc', false, -1, 'test_project',
 '{}');

insert into branches (id, service_id, env, direct_link)
values (11, 1, 'stable', 'direct_link_stable'),
       (12, 1, 'testing', 'direct_link_testing');

insert into branch_hosts (host_name, branch_id)
values ('host_name_1', 11),
       ('host_name_2', 11);
