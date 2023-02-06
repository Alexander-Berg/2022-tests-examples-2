INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, is_shared, is_external, abc_quota_source)
VALUES (1, 1, 'ns-1', 'stable'::balancers.namespace_env_t, FALSE, TRUE, 'taxi_abc_service')
;

INSERT INTO balancers.entry_points (id, namespace_id, awacs_upstream_id, is_external, protocol, dns_name, env, domain_id)
VALUES (1, 1, 'default', FALSE, 'http'::balancers.entry_point_protocol_t, 'fqdn.net', 'stable'::balancers.entry_point_env_t, 'd-1')
;

INSERT INTO balancers.upstreams (id, service_id, branch_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'b-1', 'stable'::balancers.upstream_env_t),
       (2, 1, 2, 'b-2', 'prestable'::balancers.upstream_env_t)
;

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (1, 2)
;
