insert into clownductor.namespaces (name) values ('taxi');

INSERT INTO clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    namespace_id
)
VALUES (
    'taxi-devops',
    '_TAXITESTNETS_',
    '_TAXI_INFRA_NETS_',
    'quotastaxiinfrastructure',
    'quotastaxiinfrastructure',
    'taxitvmaccess',
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service,
    service_url,
    new_service_ticket
)
values (
    1,
    'clownductor',
    'taxi/clownductor/$',
    'nanny',
    'antonvasyuk',
    'taxiinfraclownductor',
    'https://a.yandex-team.ru/arc_vcs/taxi/backend-py3/services/clownductor/service.yaml',
    'TICKET-1'
    )
;

insert into clownductor.branches (
    service_id,
    name,
    direct_link,
    env
)
values
(
    1,
    'testing',
    'taxi_clownductor_testing',
    'testing'
)
;


