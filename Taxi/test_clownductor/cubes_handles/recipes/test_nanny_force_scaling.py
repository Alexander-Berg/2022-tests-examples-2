import pytest


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        assert data['cluster'] in ['MAN', 'VLA', 'SAS', 'IVA', 'MYT']
        if data['cluster'] == 'MAN':
            return {
                'total': 1,
                'pods': [
                    {
                        'status': {
                            'agent': {
                                'iss': {
                                    'currentStates': [
                                        {'currentState': 'ACTIVE'},
                                    ],
                                },
                            },
                        },
                        'meta': {
                            'creationTime': '1628931000883990',
                            'id': 'karachevda-service-4',
                        },
                    },
                ],
            }
        return {
            'total': 2,
            'pods': [
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1610977634417595',
                        'id': 'karachevda-service-3',
                    },
                },
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1618931000883990',
                        'id': 'karachevda-service-4',
                    },
                },
            ],
        }

    return _handler


@pytest.fixture(name='nanny_yp_list_pods_groups')
def _nanny_yp_list_pods_groups(mockserver):
    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/ListPodsGroups/',
    )
    def _handler(request):
        data = request.json
        assert set(data.keys()) == {'cluster', 'pod_filter', 'service_id'}
        return {
            'podsGroups': [
                {
                    'allocationRequest': {
                        'vcpuGuarantee': 900,
                        'labels': [],
                        'virtualDisks': [],
                        'networkMacro': '_TAXI_CLOWNDUCTOR_TEST_NETS_',
                        'sysctlProperties': [],
                        'rootBandwidthGuaranteeMegabytesPerSec': 5,
                        'workDirQuotaGigabytes': 0,
                        'rootFsQuotaMegabytes': 20480,
                        'rootFsQuotaGigabytes': 0,
                        'virtualServiceIds': [],
                        'annotations': [],
                        'podNamingMode': 'RANDOM',
                        'vcpuLimit': 1000,
                        'replicas': 0,
                        'persistentVolumes': [
                            {
                                'diskQuotaMegabytes': 20480,
                                'virtualDiskId': '',
                                'storageProvisioner': 'SHARED',
                                'storageClass': 'hdd',
                                'bandwidthLimitMegabytesPerSec': 30,
                                'diskQuotaGigabytes': 0,
                                'mountPoint': '/cores',
                                'bandwidthGuaranteeMegabytesPerSec': 12,
                            },
                        ],
                        'enableInternet': False,
                        'networkBandwidthLimitMegabytesPerSec': 0,
                        'gpus': [],
                        'networkBandwidthGuaranteeMegabytesPerSec': 0,
                        'anonymousMemoryLimitMegabytes': 0,
                        'memoryGuaranteeMegabytes': 2048,
                        'rootBandwidthLimitMegabytesPerSec': 10,
                        'snapshotsCount': 3,
                        'workDirQuotaMegabytes': 512,
                        'rootVolumeStorageClass': 'hdd',
                        'resourceCaches': [],
                        'threadLimit': 0,
                    },
                },
            ],
        }

    return _handler


@pytest.fixture(name='st_get_comments_value')
def _st_get_comments_value():
    def _wrapper(*args, **kwargs):
        return [
            {
                'id': 2,
                'self': 'url_to_comment',
                'createdBy': {'id': 'vstimchenko'},
                'createdAt': '2000-06-28T15:27:25.359+0000',
                'updatedAt': '2000-06-28T15:27:25.359+0000',
                'text': 'Rollback scaling',
            },
        ]

    return _wrapper


@pytest.mark.features_on('enable_ratelimit_mask_change')
@pytest.mark.usefixtures(
    'nanny_yp_list_pods',
    'nanny_yp_list_pods_groups',
    'nanny_yp_pod_reallocation_spec',
    'nanny_yp_start_pod_reallocation',
    'st_get_myself',
    'st_create_comment',
    'st_create_ticket',
    'st_get_comments',
    'st_execute_transaction',
    'st_get_ticket',
)
@pytest.mark.config(
    CLOWNDUCTOR_APPROVERS_CHECKER={
        '__default__': {'use_conductor': False, 'use_idm': True},
    },
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_nanny_force_scaling_recipe(
        mockserver,
        load_yaml,
        task_processor,
        run_job_common,
        add_external_cubes,
        nanny_mockserver,
        nanny_yp_mockserver,
        load_json,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/test_nanny_service/current_state/',
        prefix=True,
    )
    async def _handler_test_nanny_service(request):
        return load_json('nanny_service_current_state.json')

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_stable/current_state/',
        prefix=True,
    )
    async def _handler_test_service_stable(request):
        return load_json('nanny_service_current_state.json')

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_pre_stable/runtime_attrs/',
    )  # pylint: disable=unused-variable
    def handler_pre(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs_pre.json')
        return None

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_stable/runtime_attrs/',
    )  # pylint: disable=unused-variable
    def handler(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs.json')
        if request.method == 'PUT':
            return load_json('nanny_service_runtime_attrs_response.json')
        return None

    add_external_cubes()
    nanny_yp_mockserver()
    recipe = task_processor.load_recipe(
        load_yaml('recipes/NannyForceScaling.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_service_stable',
            'new_pod_count': 4,
            'user': 'vstimchenko',
            'branch_id': 2,
            'service_id': 1,
            'role_to_check': 'nanny_admin_prod',
            'pod_naming_mode': 'ENUMERATE',
            'yp_quota_abc': 'abc_service',
            'regions': [],  # use all regions
            'use_append_pods': True,
            'comment': 'Testing automated pod scaling',
            'branch_ids': [2],
            'use_active': True,
            'datacenters_count': 3,
        },
        initiator='clownductor',
    )
    await run_job_common(job)
    expected = load_json('expected_data.json')
    assert job.job_vars == expected
