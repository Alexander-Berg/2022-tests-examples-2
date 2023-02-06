INSERT INTO clownductor.namespaces (name) values ('taxi'), ('eda');

INSERT INTO clownductor.projects
    (id, name, network_stable, network_testing, service_abc, yp_quota_abc, tvm_root_abc, namespace_id)
VALUES
(
    1,
    'taxi',
    'TAXI',
    'TAXIT',
    'abc-srv',
    'yp-abc-quota',
    'tvm-root-abc',
    1
),
(
    2,
    'eda',
    'EDA',
    'EDAT',
    'abc-srv',
    'yp-abc-quota',
    'tvm-root-abc',
    2
)
;
