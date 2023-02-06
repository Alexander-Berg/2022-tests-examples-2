insert into clownductor.namespaces (id, name) values (1, 'taxi');

insert into clownductor.projects (
    id,
    name,
    yp_quota_abc,
    network_stable,
    network_testing,
    tvm_root_abc,
    service_abc,
    namespace_id
)
values (
    150,
    'taxi-devops',
    'quotastaxiinfrastructure',
    '_TAXI_INFRA_NETS_',
    '_TAXITESTNETS_',
    'taxitvmaccess',
    'quotastaxiinfrastructure',
    1
)
;

insert into clownductor.services (
    id,
    name,
    project_id,
    artifact_name,
    cluster_type
)
values (
    1,
    'clownductor',
    150,
    'taxi/clownductor/$',
    'nanny'
)
;

insert into task_manager.jobs (
    id,
    service_id,
    name,
    initiator,
    status
)
values (
    1,
    1,
    'CreateNannyBranch',
    'clownductor',
    'in_progress'
)
;

insert into task_manager.tasks (
    id,
    job_id,
    name,
    input_mapping,
    output_mapping,
    retries,
    status
)
values (
    1,
    1,
    'GenerateJugglerDiffProposal',
    '{"project_name": "project", "service_name": "service", "env": "env", "branch_name": "branch"}',
    '{}',
    0,
    'in_progress'
)
;

insert into task_manager.job_variables (
    job_id,
    variables
)
values (
    1,
    '{"project": "taxi-devops", "service": "geotracks-admin", "env": "stable", "branch": "stable"}'
)
;
