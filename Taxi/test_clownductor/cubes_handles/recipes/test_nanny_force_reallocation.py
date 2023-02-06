import pytest


CURRENT_STATE = {
    'content': {
        'active_snapshots': [
            {
                'prepared': {
                    'status': 'True',
                    'last_transition_time': 1618331412060,
                },
                'state': 'ACTIVE',
                'conf_id': 'karachevda-service-1618331338102',
                'snapshot_id': '765195c0d2ed88439dadb9a85c9800fa596fa812',
                'taskgroup_id': 'deploy-0000090995',
                'entered': 1618331534343,
                'taskgroup_started': {
                    'status': 'true',
                    'reason': '',
                    'message': '',
                    'last_transition_time': 1618331414337,
                },
            },
        ],
    },
    'entered': 1600112573571,
    '_id': '',
    'reallocation': {
        'taskgroup_id': 'deploy-0000091037',
        'state': {
            'status': 'Idle',
            'reason': '',
            'entered': 1618931302449,
            'message': 'DONE',
        },
        'id': 'tuxuyawpnyh7qxmqnhvznnz7',
    },
}


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        assert data['cluster'] in ['MAN', 'VLA', 'SAS']
        if data['cluster'] == 'MAN':
            return {
                'total': 1,
                'pods': [
                    {
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
                    'meta': {
                        'creationTime': '1610977634417595',
                        'id': 'karachevda-service-3',
                    },
                },
                {
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


@pytest.fixture(name='nanny_state_stable')
def _nanny_state_stable(mockserver):
    @mockserver.json_handler('/client-nanny/v2/services/test_service_stable/')
    def _handler(request):
        assert request.method == 'GET'
        return {'current_state': CURRENT_STATE}

    return _handler


@pytest.fixture(name='nanny_state_pre_stable')
def _nanny_state_pre_stable(mockserver):
    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_pre_stable/',
    )
    def _handler(request):
        assert request.method == 'GET'
        return {'current_state': CURRENT_STATE}

    return _handler


@pytest.fixture(name='nanny_current_state_stable')
def _nanny_current_state_stable(mockserver):
    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_stable/current_state/',
    )
    def _handler(request):
        assert request.method == 'GET'
        return CURRENT_STATE

    return _handler


@pytest.fixture(name='nanny_current_state_pre_stable')
def _nanny_current_state_pre_stable(mockserver):
    @mockserver.json_handler(
        '/client-nanny/v2/services/test_service_pre_stable/current_state/',
    )
    def _handler(request):
        assert request.method == 'GET'
        return CURRENT_STATE

    return _handler


@pytest.fixture(name='st_get_comments_value')
def _st_get_comments_value():
    def _wrapper(*args, **kwargs):
        return [
            {
                'id': 2,
                'self': 'url_to_comment',
                'createdBy': {'id': 'karachevda'},
                'createdAt': '2000-06-28T15:27:25.359+0000',
                'updatedAt': '2000-06-28T15:27:25.359+0000',
                'text': 'Rollback reallocation',
            },
        ]

    return _wrapper


@pytest.mark.usefixtures(
    'nanny_yp_list_pods',
    'nanny_yp_list_pods_groups',
    'nanny_state_stable',
    'nanny_yp_pod_reallocation_spec',
    'nanny_yp_start_pod_reallocation',
    'st_get_myself',
    'st_create_comment',
    'st_create_ticket',
    'nanny_current_state_stable',
    'st_get_comments',
    'nanny_state_pre_stable',
    'nanny_current_state_pre_stable',
    'st_execute_transaction',
    'st_get_ticket',
)
@pytest.mark.config(
    CLOWNDUCTOR_APPROVERS_CHECKER={
        '__default__': {'use_conductor': False, 'use_idm': True},
    },
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_nanny_force_reallocation_recipe(
        mockserver, load_yaml, task_processor, run_job_common, yp_mockserver,
):
    yp_mockserver()
    recipe = task_processor.load_recipe(
        load_yaml('recipes/NannyForceReallocation.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_service_stable',
            'reallocation_coefficient': 1.5,
            'user': 'karachevda',
            'branch_id': 2,
            'service_id': 1,
            'role_to_check': 'nanny_admin_prod',
        },
        initiator='clownductor',
    )
    await run_job_common(job)

    assert job.job_vars == {
        'branch_id': 2,
        'comment_props': {'summonees': ['karachevda']},
        'end_comment': 'tickets.nanny_force_reallocation_end_comment',
        'key_phrase': 'Rollback reallocation',
        'nanny_name': 'test_service_stable',
        'new_ticket': 'TAXIADMIN-1',
        'newest_pod_id': 'karachevda-service-4',
        'original_allocation_request': {
            'annotations': [],
            'anonymousMemoryLimitMegabytes': 0,
            'enableInternet': False,
            'gpus': [],
            'labels': [],
            'memoryGuaranteeMegabytes': 2048,
            'networkBandwidthGuaranteeMegabytesPerSec': 0,
            'networkBandwidthLimitMegabytesPerSec': 0,
            'networkMacro': '_TAXI_CLOWNDUCTOR_TEST_NETS_',
            'persistentVolumes': [
                {
                    'bandwidthGuaranteeMegabytesPerSec': 12,
                    'bandwidthLimitMegabytesPerSec': 30,
                    'diskQuotaGigabytes': 0,
                    'diskQuotaMegabytes': 20480,
                    'mountPoint': '/cores',
                    'storageClass': 'hdd',
                    'storageProvisioner': 'SHARED',
                    'virtualDiskId': '',
                },
            ],
            'podNamingMode': 'RANDOM',
            'replicas': 0,
            'resourceCaches': [],
            'rootBandwidthGuaranteeMegabytesPerSec': 5,
            'rootBandwidthLimitMegabytesPerSec': 10,
            'rootFsQuotaGigabytes': 0,
            'rootFsQuotaMegabytes': 20480,
            'rootVolumeStorageClass': 'hdd',
            'snapshotsCount': 3,
            'sysctlProperties': [],
            'threadLimit': 0,
            'vcpuGuarantee': 900,
            'vcpuLimit': 1000,
            'virtualDisks': [],
            'virtualServiceIds': [],
            'workDirQuotaGigabytes': 0,
            'workDirQuotaMegabytes': 512,
        },
        'pre_end_comment': 'tickets.nanny_force_reallocation_end_comment',
        'pre_reallocation_id': 'tuxuyawpnyh7qxmqnhvznnz7',
        'pre_rollback_end_comment': (
            'tickets.nanny_force_reallocation_end_comment'
        ),
        'pre_rollback_reallocation_id': 'tuxuyawpnyh7qxmqnhvznnz7',
        'pre_rollback_start_comment': (
            'tickets.nanny_force_reallocation_start_comment'
        ),
        'pre_start_comment': 'tickets.nanny_force_reallocation_start_comment',
        'rollback_comment': (
            'tickets.nanny_force_reallocation_rollback_comment'
        ),
        'prepared_allocation_request': {
            'annotations': [],
            'anonymousMemoryLimitMegabytes': 0,
            'enableInternet': False,
            'gpus': [],
            'labels': [],
            'memoryGuaranteeMegabytes': 3072,
            'networkBandwidthGuaranteeMegabytesPerSec': 0,
            'networkBandwidthLimitMegabytesPerSec': 0,
            'networkMacro': '_TAXI_CLOWNDUCTOR_TEST_NETS_',
            'persistentVolumes': [
                {
                    'bandwidthGuaranteeMegabytesPerSec': 18,
                    'bandwidthLimitMegabytesPerSec': 45,
                    'diskQuotaGigabytes': 0,
                    'diskQuotaMegabytes': 30720,
                    'mountPoint': '/cores',
                    'storageClass': 'hdd',
                    'storageProvisioner': 'SHARED',
                    'virtualDiskId': '',
                },
            ],
            'podNamingMode': 'RANDOM',
            'replicas': 0,
            'resourceCaches': [],
            'rootBandwidthGuaranteeMegabytesPerSec': 8,
            'rootBandwidthLimitMegabytesPerSec': 15,
            'rootFsQuotaGigabytes': 0,
            'rootFsQuotaMegabytes': 30720,
            'rootVolumeStorageClass': 'hdd',
            'snapshotsCount': 3,
            'sysctlProperties': [],
            'threadLimit': 0,
            'vcpuGuarantee': 1350,
            'vcpuLimit': 1500,
            'virtualDisks': [],
            'virtualServiceIds': [],
            'workDirQuotaGigabytes': 0,
            'workDirQuotaMegabytes': 768,
        },
        'prestable_nanny_name': 'test_service_pre_stable',
        'reallocation_coefficient': 1.5,
        'reallocation_id': 'tuxuyawpnyh7qxmqnhvznnz7',
        'region': 'MAN',
        'role_to_check': 'nanny_admin_prod',
        'rollback_end_comment': 'tickets.nanny_force_reallocation_end_comment',
        'rollback_reallocation_id': 'tuxuyawpnyh7qxmqnhvznnz7',
        'rollback_start_comment': (
            'tickets.nanny_force_reallocation_start_comment'
        ),
        'service_id': 1,
        'start_comment': 'tickets.nanny_force_reallocation_start_comment',
        'ticket_description': 'tickets.nanny_force_reallocation_description',
        'ticket_summary': 'tickets.nanny_force_reallocation_summary',
        'user': 'karachevda',
    }
