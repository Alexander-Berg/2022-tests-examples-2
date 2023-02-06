INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env,
                                  abc_quota_source, updated_at)
VALUES (1, 1, 'weird-name1.taxi.yandex-team.ru', 'testing', 'abcstable',
        now()), -- id 1
       (2, 1, 'nother-name.taxi.yandex.net', 'stable', 'abctesting',
        now()) -- id 2
;
INSERT INTO balancers.entry_points (id, created_at, updated_at, deleted_at,
                                    is_deleted, namespace_id,
                                    awacs_upstream_id, is_external,
                                    can_share_namespace, protocol, dns_name,
                                    env, domain_id)
VALUES (1, now(), now(), null, false, 1, 'default', false, false, 'http',
        'weird-name1.taxi.yandex-team.ru', 'testing',
        'weird-name1.taxi.yandex-team.ru'),
       (2, now(), now(), null, false, 1, 'testing-upstream', false, false,
        'https', 'weird-name1.taxi.tst.yandex-team.ru', 'unstable',
        'weird-name1.taxi.tst.yandex-team.ru'),
       (3, now(), now(), null, false, 1, 'testing-upstream', false, false,
        'https', 'weird-name2.taxi.tst.yandex-team.ru', 'testing',
        'weird-name2.taxi.tst.yandex-team.ru')
;
INSERT INTO balancers.upstreams (id, created_at, updated_at, deleted_at,
                                 is_deleted, branch_id, service_id,
                                 awacs_backend_id, env)
VALUES (1, now(), now(), null, false, 123, 15,
        'taxi_clownductor_testing_default', 'testing'),
       (2, now(), now(), null, false, 124, 16, 'taxi_clownductor_testing',
        'unstable'),
       (3, now(), now(), null, false, 125, 16, 'taxi_clownductor_unstable',
        'unstable')
;
INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (2, 2),
       (2, 3)
;
