insert into external_events (link, start_ts, event_type, event_data)
values ('drillslavkataxiiva', now(), 'drills', '{"datacenters": ["iva"], "project_ids": [1, 2, 3]}');

insert into external_events (link, start_ts, event_type, event_data)
values ('deploy999testing', now(), 'deploy', '{"service_id": 999, "env": "testing"}');

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers)
values (999, 'service_for_project_1', 'nanny', now() at time zone 'utc', false, 1,
        'taxi-infra', '{}');

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers)
values (9999, 'service_for_project_2', 'nanny', now() at time zone 'utc', false, 2,
        'taxi', '{}');

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers)
values (99999, 'service_for_project_3', 'nanny', now() at time zone 'utc', false, 3,
        'lavka', '{}');
