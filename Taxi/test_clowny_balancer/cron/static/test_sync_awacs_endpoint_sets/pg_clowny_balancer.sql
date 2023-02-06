insert into balancers.namespaces (project_id, awacs_namespace, env, abc_quota_source)
values (1, 'stable-ns.yandex.net', 'stable', 'abcstable'),
       (1, 'testing-ns.yandex.net', 'testing', 'abctesting')
;

insert into balancers.entry_points (
    namespace_id, awacs_upstream_id, is_external,
    can_share_namespace, protocol, dns_name,
    env, domain_id
)
values (1, 'default', false, false, 'http', 'service.taxi.yandex-team.ru', 'stable', 'service.taxi.yandex-team.ru'),
(2, 'testing-upstream', false, false, 'https', 'service.taxi.yandex-team.ru', 'testing', 'service.taxi.tst.yandex-team.ru')
;

insert into balancers.upstreams (branch_id, service_id, awacs_backend_id, env)
values (123, 15, 'taxi-infra_task-processor_stable', 'stable'),
(124, 16, 'taxi-infra_task-processor_pre_stable', 'prestable'),
(125, 16, 'taxi_clownductor_testing', 'testing')
;

insert into balancers.entry_points_upstreams (entry_point_id, upstream_id)
values (1, 1), -- stable
       (1, 2), -- prestable
       (2, 3)
;
