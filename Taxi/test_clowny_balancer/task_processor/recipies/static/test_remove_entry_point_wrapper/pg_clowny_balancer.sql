INSERT INTO balancers.namespaces (id, project_id, awacs_namespace, env, is_shared, is_external, abc_quota_source)
VALUES (1, 1, 'ns-1', 'stable'::balancers.namespace_env_t, FALSE, TRUE, 'taxi_abc_service_1'),
       (2, 1, 'ns-2', 'stable'::balancers.namespace_env_t, FALSE, TRUE, 'taxi_abc_service_2');

INSERT INTO balancers.entry_points (id, namespace_id, awacs_upstream_id, is_external, protocol, dns_name, env, domain_id, can_share_namespace)
VALUES (1, 1, 'default', FALSE, 'https'::balancers.entry_point_protocol_t, 'service-fqdn-1.net', 'stable'::balancers.entry_point_env_t, 'd-1', TRUE),
       (2, 2, 'default', FALSE, 'https'::balancers.entry_point_protocol_t, 'service-fqdn-2.net', 'stable'::balancers.entry_point_env_t, 'd-2', TRUE),
       (3, 2, 'some_other', FALSE, 'https'::balancers.entry_point_protocol_t, 'service-fqdn-3.net', 'stable'::balancers.entry_point_env_t, 'd-3', TRUE);

INSERT INTO balancers.upstreams (id, branch_id, service_id, awacs_backend_id, env)
VALUES (1, 1, 1, 'b-1', 'stable'),
       (2, 2, 2, 'b-2', 'stable'),
       (3, 3, 2, 'b-3', 'stable');

INSERT INTO balancers.entry_points_upstreams (entry_point_id, upstream_id)
VALUES (1, 1),
       (2, 2),
       (2, 3),
       (3, 3);
