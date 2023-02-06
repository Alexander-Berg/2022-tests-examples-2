insert into clownductor.namespaces (name) values ('taxi');

insert into
    clownductor.projects (
        name,
        network_testing,
        network_stable,
        service_abc,
        yp_quota_abc,
        tvm_root_abc,
        namespace_id
    )
values (
    'blah',
    '_taxitestnets_',
    '_hwtaxinets_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
),
(
    '__NO_CONFIG_PROJECT',
    '_taxitestnets_',
    '_hwtaxinets_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    1
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
    'blah',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
),
(
    2,
    '__NO_CONF_PROJECT_SERVICE',
    'artifact_name',
    'nanny',
    'unit_test',
    'abc_service'
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
    'blah',
    'stable',
    'blah'
),
(
    2,
    '_NO_CONF_PR_BRANCH',
    'stable',
    'conf_link'
)
;

INSERT INTO
    clownductor.hosts (
        name,
        branch_id,
        datacenter
    )
VALUES(
    'host1',
    1,
    'man'
),
(
    'host2',
    1,
    'man'
)
;
