insert into digests (digest_name, sticker_uid, last_broadcast, period_hours, digest_format, circuit_id_like, out_point_id_like, description, params)
values (
           'HIGH usage - CPU - rtc',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'incidents_duration_by_service',
           '{"%:rtc_cpu_usage"}',
           'high_usage',
           '',
           '{"service_stat_id": "cpu_high_usage", "cluster_types": ["nanny"]}'
       ),
       (
           'LOW usage - CPU - rtc',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'incidents_duration_by_service',
           '{"%:rtc_cpu_usage"}',
           'low_usage',
           '',
        '{"service_stat_id": "cpu_low_usage", "cluster_types": ["nanny"]}'
       ),
       (
           'HIGH usage - RAM - rtc',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'incidents_duration_by_service',
           '{"%:rtc_ram_usage"}',
           'high_usage',
           '',
           '{"service_stat_id": "ram_high_usage", "cluster_types": ["nanny"]}'
       ),
       (
           'LOW usage - RAM - rtc',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'incidents_duration_by_service',
           '{"%:rtc_ram_usage"}',
           'low_usage',
           '',
           '{"service_stat_id": "ram_low_usage", "cluster_types": ["nanny"]}'
       ),
       (
           'HIGH usage - CPU - pg',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'db_by_host',
           '{"%:pg_cpu_usage"}',
           'high_usage',
           '',
           '{"service_stat_id": "cpu_high_usage", "cluster_types": ["postgres"]}'
       ),
       (
           'LOW usage - CPU - pg',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'db_by_host',
           '{"%:pg_cpu_usage"}',
           'low_usage',
           '',
           '{"service_stat_id": "cpu_low_usage", "cluster_types": ["postgres"]}'
       ),
       (
           'HIGH usage - RAM - pg',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'db_by_host',
           '{"%:pg_ram_usage"}',
           'high_usage',
           '',
           '{"service_stat_id": "ram_high_usage", "cluster_types": ["postgres"]}'
       ),
       (
           'LOW usage - RAM - pg',
           'hejmdal-digest-admin@yandex-team.ru',
           '2020-08-31 09:00:00.000000',
           168,
           'db_by_host',
           '{"%:pg_ram_usage"}',
           'low_usage',
           '',
           '{"service_stat_id": "ram_low_usage", "cluster_types": ["postgres"]}'
       );

insert into incident_history (circuit_id, out_point_id, start_time, end_time, alert_status,
                              description, meta_data)
values (
            'some_host::rtc_cpu_usage', 'low_usage', '2020-08-31 09:00:01.000000',
            '2020-09-05 09:00:00.000000',
            'WARN', '', '{"service_id": 2}'
       ),
       (
            'some_host::pg_ram_usage', 'high_usage', '2020-08-31 09:00:01.000000',
            '2020-09-05 09:00:00.000000',
            'WARN', '', '{"service_id": 3}'
       );

insert into services (id, name, cluster_type, updated, deleted, project_id,
                      project_name, maintainers) values
(2, 'test_service2', 'nanny', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}'),
(3, 'test_pg', 'postgres', '1970-01-15T08:58:08.001+00:00', false, 39, 'test_project',
 '{}');

insert into branches (id, service_id, env, direct_link) values
(21, 2, 'stable', 'test_service_stable'),
(22, 3, 'stable', 'test_pg_stable');

insert into branch_hosts (host_name, branch_id) values
('test_service_host_name_1', 21),
('test_pg_host_name_1', 22),
('test_pg_host_name_2', 22);
