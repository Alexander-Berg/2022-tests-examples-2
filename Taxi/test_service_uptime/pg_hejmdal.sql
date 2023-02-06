insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers, grafana_url)
values
(139, 'hejmdal', 'nanny', '2021-10-26 13:49:51.398231+03', false, 38,
 'taxi-infra', '{}',
 'https://grafana.yandex-team.ru/d/NtHGGv-Zz/nanny_taxi_hejmdal_stable');

insert into branches (id, service_id, env, direct_link, grafana_url)
values
(18, 139, 'stable', 'taxi_hejmdal_stable',
 'https://grafana.yandex-team.ru/d/NtHGGv-Zz/nanny_taxi_hejmdal_stable');
