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
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
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
    direct_link
)
values (
    1,
    'test_service_1',
    'taxi/test_service_1/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_test_service_1'
), (
    1,
    'test_service_2',
    'taxi/test_service_2/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_test_service_2'
), (
    1,
    'cool_service',
    'taxi/cool_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'taxi_cool_service'
)
;

insert into clownductor.branches (
    service_id,
    name,
    env,
    direct_link
)
values (
    1,
    'unstable_branch',
    'unstable',
    'test_service_unstable'
),(
    2,
    'unstable_branch',
    'unstable',
    'test_service_unstable'
),(
    3,
    'stable',
    'stable',
    'taxi_cool_service_stable'
),(
    3,
    'pre_stable',
    'prestable',
    'taxi_cool_service_pre_stable'
);

insert into task_manager.jobs (
    id,
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values (
    456,
    1,
    1,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'canceled'
),(
    457,
    2,
    2,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'canceled'
)
;

INSERT INTO clownductor.parameters (subsystem_name,
                                    service_id,
                                    branch_id,
                                    service_values,
                                    remote_values)
VALUES ('service_info',
        1,
        NULL,
        '{"tvm_name": "eats-launch", "release_flow": {"single_approve": true}, "wiki_path": "https://wiki.yandex-team.ru/taxi/backend/architecture/eats-launch/", "description": "launch for eda", "service_name": "eats-launch", "service_type": "uservices", "design_review": "https://st.yandex-team.ru/TAXIARCHREVIEW-205", "duty_group_id": "eda-backend-duty-eaters", "service_yaml_url": "https://github.yandex-team.ru/taxi/uservices/blob/develop/services/eats-launch/service.yaml", "clownductor_project": "eda", "deploy_callback_url": null, "yt_log_replications": null}',
        NULL),('service_info',
        2,
        NULL,
        '{"tvm_name": "eats-launch", "release_flow": {"single_approve": false}, "wiki_path": "https://wiki.yandex-team.ru/taxi/backend/architecture/eats-launch/", "description": "launch for eda", "service_name": "eats-launch", "service_type": "uservices", "design_review": "https://st.yandex-team.ru/TAXIARCHREVIEW-205", "duty_group_id": "eda-backend-duty-eaters", "service_yaml_url": "https://github.yandex-team.ru/taxi/uservices/blob/develop/services/eats-launch/service.yaml", "clownductor_project": "eda", "deploy_callback_url": null, "yt_log_replications": null}',
        NULL);
