INSERT INTO clownductor.namespaces (name) values ('test');

INSERT INTO
clownductor.projects (
    id,
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    namespace_id
)
VALUES (
    1,
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
)
;

INSERT INTO
clownductor.services (
    project_id,
    id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service
)
VALUES (
    1,
    1,
    'test-service1',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    1,
    2,
    'test-service2',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    1,
    3,
    'test-db1',
    'artifact_name',
    'postgres',
    'unit_test',
    'abc_service'
),
(
    1,
    4,
    'test-db2',
    'artifact_name',
    'mongo_mdb',
    'unit_test',
    'abc_service'
),
(
    1,
    5,
    'test-service3',
    'artifact_name',
    'conductor',
    'unit_test',
    'abc_service'
),
(
    1,
    6,
    'test-service3',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    1,
    7,
    'test-service3',
    'artifact_name',
    'postgres',
    'unit_test',
    'abc_service'
)
;

INSERT INTO clownductor.related_services (service_id, related_service_id) VALUES
(1, 3),
(2, 3),
(2, 4),
(5, 4);
