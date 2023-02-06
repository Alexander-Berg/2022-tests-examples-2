INSERT INTO balancers.namespaces (project_id, awacs_namespace, env, abc_quota_source, is_external)
VALUES (1, 'ns1', 'stable', 'abcstable', true),
       (1, 'ns2', 'testing', 'abctesting', false),
       (2, 'ns3', 'stable', 'abcstable', false)
;

INSERT INTO balancers.entry_points
    (id, namespace_id, awacs_upstream_id, protocol, dns_name, env)
VALUES (1, 1, 'ns1', 'http', 'fqdn.net', 'stable'),
       (2, 2, 'ns2', 'http', 'fqdn.test.net', 'testing'),
       (3, 3, 'ns3', 'https', 'fqdn2.net', 'stable')
;
