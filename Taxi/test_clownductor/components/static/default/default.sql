insert into clownductor.namespaces (name) values ('taxi'), ('eda');

insert into
    clownductor.projects (
        name,
        network_testing,
        network_stable,
        service_abc,
        yp_quota_abc,
        tvm_root_abc,
        namespace_id,
        env_params
    )
values (
    'taxi-devops',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1,
    '{"general": {"project_prefix": "taxi"}}'
), (
    'eda',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    2,
    '{"general": {"project_prefix": "eda"}}'
)
;

insert into
    clownductor.services (
        project_id,
        name,
        artifact_name,
        cluster_type,
        requester,
        abc_service
    )
values (
    1,
    'nanny-1',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service1'
),
(
    1,
    'nanny-2',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service2'
),
(
    1,
    'conductor-3',
    'artifact_name',
    'conductor',
    'unit_test',
    'abc_service3'
),
(
    1,
    'pg_4',
    'artifact_name',
    'postgres',
    'unit_test',
    'abc_service4'
), (
    2,
    'nanny-5',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service1'
)
;

insert into
    clownductor.branches (
        service_id,
        name,
        env,
        direct_link
    )
values (
    1,
    'stable',
    'stable',
    'taxi_nanny-1_stable'
),
(
    1,
    'pre_stable',
    'prestable',
    'taxi_nanny-1_pre_stable'
),
(
    1,
    'testing',
    'testing',
    'taxi_nanny-1_testing'
),
(
    1,
    'unstable',
    'prestable',
    'taxi_nanny-1_unstable'
),
(
    2,
    'stable',
    'stable',
    'taxi_nanny-2_stable'
),
(
    2,
    'pre_stable',
    'prestable',
    'taxi_nanny-2_pre_stable'
),
(
    3,
    'stable',
    'stable',
    'taxi_conductor-3'
),
(
    4,
    'stable',
    'stable',
    'pg-direct-link-4'
),
(
    5,
    'stable',
    'stable',
    'eda_nanny-5_stable'
),
(
    5,
    'testing',
    'testing',
    'eda_nanny-5_testing'
)
;

