insert into clownductor.namespaces (name) values ('taxi');

insert into clownductor.projects (
    name,
    network_testing,
    network_stable,
    service_abc,
    yp_quota_abc,
    tvm_root_abc,
    owners,
    namespace_id
)
values (
    'test_project',
    '_TAXITESTNETS_',
    '_HWTAXINETS_',
    'taxiservicesdeploymanagement',
    'taxiquotaypdefault',
    'taxitvmaccess',
    '{"groups": [], "logins": []}'::jsonb,
    1
)
;

insert into clownductor.services (
    project_id,
    name,
    artifact_name,
    cluster_type,
    requester,
    abc_service
)
values (
    1,
    'test_service',
    'taxi/test_service/$',
    'nanny',
    'unit_test',
    'abc_service'
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
), (
    1,
    'testing_branch',
    'testing',
    'test_service_testing'
), (
    1,
    'tank-branch',
    'testing',
    'tank_service_testing'
);

insert into task_manager.jobs (
    service_id,
    branch_id,
    name,
    initiator,
    status
)
values (
    1,
    1,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'success'
), (
    1,
    3,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'success'
), (
    1,
    3,
    'DeployNannyServiceNoApprove',
    'deoevgen',
    'success'
)
;

insert into task_manager.job_variables (job_id, variables)
values (
    2,
    '{
  "image": "taxi/real-service/testing:latest",
  "comment": "Automatically created release",
  "changelog": null,
  "nanny_name": "taxi_yaga-adjust_stable",
  "environment": "testing",
  "snapshot_id": "1a309f488210c85a1d2d02887a104c3dfd5455bf",
  "job_branch_id": 294774,
  "job_service_id": 354389,
  "link_to_changelog": "https://tariff-editor.taxi.yandex-team.ru/services/38/edit/354179/jobs?jobId=624685&isClownJob=true",
  "sandbox_resources": [
    {
      "task_id": "984739487",
      "task_type": "TAXI_GRAPH_DO_UPLOAD_TASK",
      "is_dynamic": false,
      "local_path": "leptidea",
      "resource_id": "2198429773",
      "resource_type": "TAXI_GRAPH_LEPTIDEA_RESOURCE"
    },
    {
      "task_id": "984739487",
      "task_type": "TAXI_GRAPH_DO_UPLOAD_TASK",
      "is_dynamic": false,
      "local_path": "road-graph",
      "resource_id": "2198429502",
      "resource_type": "TAXI_GRAPH_ROAD_GRAPH_RESOURCE"
    },
    {
      "task_id": "984739487",
      "task_type": "TAXI_GRAPH_DO_UPLOAD_TASK",
      "is_dynamic": false,
      "local_path": "persistent-index",
      "resource_id": "2198429682",
      "resource_type": "TAXI_GRAPH_PERSISTENT_INDEX_RESOURCE"
    }
  ]
}'
), (
    3,
    '{
  "name": "taxi_cargo-c2c_stable",
  "prestable_name": "taxi_cargo-c2c_pre_stable",
  "image": "taxi/cargo-c2c/production:0.0.77",
  "comment": "Automatically created release",
  "aliases": [],
  "release_ticket_st": "TAXIREL-34886",
  "prestable_aliases": [],
  "sandbox_resources": null,
  "lock_names": [
    "Deploy.taxi_cargo-c2c_stable"
  ],
  "configs_info": [
    {
      "name": "ADMIN_IMAGES_CLIENT_QOS",
      "libraries": [
        "image-tag-cache"
      ],
      "plugins": [
        "client-admin-images"
      ],
      "is_service_yaml": false
    },
    {
      "name": "ADMIN_IMAGES_INTERNAL_LIST_LIMIT",
      "libraries": [
        "image-tag-cache"
      ],
      "plugins": [],
      "is_service_yaml": false
    },
    {
      "name": "VGW_API_CLIENT_QOS",
      "libraries": [],
      "plugins": [
        "client-vgw-api"
      ],
      "is_service_yaml": false
    }
  ],
  "configs_branch_ids": [
    295293
  ],
  "project_names": [
    "cargo"
  ],
  "changelog": "* antonyzhilin | fix all: fix build",
  "is_rollback": false,
  "job_service_id": 354870,
  "job_branch_id": 295293,
  "sync_job_ids": [],
  "current_diff_job_id": null,
  "current_diff_aliases_jobs": [],
  "current_diff_comment": null,
  "current_diff_skip": true,
  "approving_managers": [
    "mbruzha",
    "bruno",
    "f-damir",
    "perishkova",
    "demyanna",
    "romario"
  ],
  "approving_developers": [
    "ivankolosov",
    "fmobster",
    "seanchaidh",
    "akocherov",
    "plurye"
  ],
  "diff_config": null,
  "diff_comment": null,
  "diff_resolve_id": null,
  "diff_skip": true,
  "ok_diff_phrase": null,
  "reject_diff_phrase": null,
  "skip_closure": true
}'
)
;


insert into clownductor.configs (
    branch_id,
    name,
    plugins,
    libraries,
    is_service_yaml
)
values (
    1, 'EXIST_CONFIG', '{plugin}', '{lib}', True
),
(
    1, 'DELETED_CONFIG', '{plugin}', '{lib}', True
);
