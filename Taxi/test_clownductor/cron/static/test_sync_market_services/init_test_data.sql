insert into clownductor.namespaces (name) values ('market'), ('taxi');

insert into
clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    approving_managers,
    approving_devs,
    env_params,
    responsible_team,
    yt_topic,
    namespace_id
)
values (
    'market-project-known',
    '_DUMMY_NETWORK',
    '_DUMMY_NETWORK',
    'market_project_known',
    'market_project_known',
    'market_project_known',
    '{"logins": [], "groups": []}',
    '{"logins": [], "cgroups": []}',
    '{"logins": [], "cgroups": []}',
    '{"general": {"project_prefix": "taxi", "docker_image_tpl": "market/{{ service }}/$"}, "stable": {"domain": "", "juggler_folder": ""}, "testing": {"domain": "", "juggler_folder": ""}, "unstable": {"domain": "", "juggler_folder": ""}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "", "permissions": [""]}',
    1
), (
    'to-delete',
    '_DUMMY_NETWORK',
    '_DUMMY_NETWORK',
    'to-delete',
    'to-delete',
    'to-delete',
    '{"logins": [], "groups": []}',
    '{"logins": [], "cgroups": []}',
    '{"logins": [], "cgroups": []}',
    '{"general": {"project_prefix": "taxi", "docker_image_tpl": "market/{{ service }}/$"}, "stable": {"domain": "", "juggler_folder": ""}, "testing": {"domain": "", "juggler_folder": ""}, "unstable": {"domain": "", "juggler_folder": ""}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "", "permissions": [""]}',
    1
), (
    'taxi-project',
    '_DUMMY_NETWORK',
    '_DUMMY_NETWORK',
    'no-delete',
    'no-delete',
    'no-delete',
    '{"logins": [], "groups": []}',
    '{"logins": [], "cgroups": []}',
    '{"logins": [], "cgroups": []}',
    '{"general": {"project_prefix": "taxi", "docker_image_tpl": "taxi/{{ service }}/$"}, "stable": {"domain": "", "juggler_folder": ""}, "testing": {"domain": "", "juggler_folder": ""}, "unstable": {"domain": "", "juggler_folder": ""}}',
    '{"ops": [], "developers": [], "managers": [], "superusers": []}',
    '{"path": "", "permissions": [""]}',
    2
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
    'market-service-known-1',
    'DUMMY_ARTIFACT_NAME',
    'market_service',
    'unit_test',
    'market_service_known_1'
), (
    1,
    'nanny-service-known-1',
    'DUMMY_ARTIFACT_NAME',
    'nanny',
    'unit_test',
    'nanny_service_known_1'
), (
    1,
    'market-service-moved-1',
    'DUMMY_ARTIFACT_NAME',
    'market_service',
    'unit_test',
    'market_service_moved_1'
)
;
