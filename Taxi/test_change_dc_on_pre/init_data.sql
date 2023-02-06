insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    env_params,
    responsible_team,
    namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": ["elrusso_group"], "logins": ["elrusso"]}'::jsonb,
    '{"stable": {"domain": "taxi.yandex.net"}, "general": {"project_prefix": "taxi", "docker_image_tpl": "taxi/{{ service }}/$"}, "testing": {"domain": "taxi.tst.yandex.net"}, "unstable": {"domain": "taxi.dev.yandex.net"}}'::jsonb,
    '{"ops": ["yandex-elrusso-88005553535"], "managers": [], "developers": [], "superusers": ["elrusso"]}'::jsonb,
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
    direct_link,
    service_url
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service',
    'test-service',
    'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/services/test_service/service.yaml'
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
    'testing',
    'testing',
    'test_service_testing'
), (
    1,
    'stable',
    'stable',
    'test_service_stable'
), (
    1,
    'pre_stable',
    'prestable',
    'test_service_pre_stable'
)
;

insert into permissions.roles (role, login, project_id, service_id, is_super)
values
    ('nanny_admin_prod', 'karachevda', null, null, true),
    ('nanny_admin_prod', 'vstimchenko', null, null, true)
;
