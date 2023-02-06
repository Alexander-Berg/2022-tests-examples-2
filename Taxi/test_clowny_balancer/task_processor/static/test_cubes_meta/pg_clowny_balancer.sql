INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, abc_quota_source)
VALUES (2, 1, 'ns1', 'stable', 'abcstable')
;

INSERT INTO balancers.entry_points
    (id, namespace_id, awacs_upstream_id, protocol, dns_name, env, domain_id)
VALUES (2, 2, 'upstream_1', 'http', 'fqdn.net', 'stable', NULL),
       (3, 2, 'upstream_2', 'http', 'fqdn.net', 'stable', 'domain-id.net')
;

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (3, 3, 1, 'backend1', 'stable'),
       (4, 4, 1, 'backend2', 'prestable')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (2, 3),
       (2, 4)
;
