INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, is_shared, is_external, abc_quota_source)
VALUES (1, 1, 'awacs-ns-1', 'stable'::balancers.namespace_env_t, FALSE, TRUE, 'taxi_abc_service');

INSERT INTO balancers.entry_points (id, namespace_id, awacs_upstream_id, is_external, protocol, dns_name, env, domain_id, can_share_namespace)
VALUES (1, 1, 'default', FALSE, 'https'::balancers.entry_point_protocol_t, 'service-fqdn.net', 'stable'::balancers.entry_point_env_t, 'awacs-domain-1', TRUE);

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'some', 'stable'),
       (2, 2, 1, 'some', 'prestable')
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2)
;
