insert into services (id, name, cluster_type, grafana_url, tvm_name) values
(139, 'hejmdal', 'nanny', 'url', 'tvm_name'),
(123456, 'not_hejmdal', 'conductor', 'url', 'tvm_name');

insert into branches (id, service_id, env) values
(1, 139, 'stable'),
(2, 139, 'testing'),
(3, 123456, 'prestable'),
(4, 123456, 'stable'),
(5, 123456, 'testing'),
(6, 123456, 'unstable');
