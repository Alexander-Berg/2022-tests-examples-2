import copy
from typing import Any
from typing import Dict

import pytest


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    def make_pod(pod_id: str, state: str = 'ACTIVE'):
        return {
            'status': {
                'agent': {'iss': {'currentStates': [{'currentState': state}]}},
            },
            'meta': {'creationTime': '1628931000883990', 'id': pod_id},
        }

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        cluster = data['cluster']

        if cluster == 'MAN':
            return {
                'total': 2,
                'pods': [
                    make_pod('MAN_old_0', 'UNKNOWN'),
                    make_pod('MAN_old_1', 'UNKNOWN'),
                ],
            }
        if cluster == 'IVA':
            return {
                'total': 3,
                'pods': [
                    make_pod('IVA_old_0'),
                    make_pod('IVA_old_1'),
                    make_pod('IVA_old_2'),
                ],
            }
        if cluster == 'SAS':
            return {
                'total': 5,
                'pods': [make_pod('SAS_old_0'), make_pod('SAS_old_1')],
            }
        if cluster == 'VLA':
            return {'total': 1, 'pods': [make_pod('VLA_old_0')]}

        return {'total': 0, 'pods': []}

    return _handler


@pytest.fixture(name='nanny_yp_get_podset')
def _nanny_yp_get_podset(mockserver):
    podset_exist_dc = ['IVA', 'SAS', 'VLA', 'MAN']

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/GetPodSet/')
    def _handler(request):
        data = request.json
        if data['cluster'] in podset_exist_dc:
            return {'podsets': []}
        return mockserver.make_response(status=404)

    return _handler


@pytest.fixture(name='nanny_yp_create_podset')
def _nanny_yp_create_podset(mockserver):
    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePodSet/',
    )
    def _handler(request):
        assert request.json
        return {'podIds': ['new_pod_1']}

    return _handler


@pytest.fixture(name='nanny_yp_create_pods')
def _nanny_yp_create_pods(mockserver):
    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePods/',
    )
    def _handler(*args, **kwargs):
        data = args[0].json
        cluster = data['cluster']
        snapshots_count = data['allocationRequest']['replicas']
        return {
            'podIds': [f'{cluster}_new_{i}' for i in range(snapshots_count)],
        }

    return _handler


POD_INFO = {
    'mem': 2048,
    'network': '_TAXITESTNETS_',
    'logs_quota': 10240,
    'root_fs_quota_mb': 512,
    'root_bandwidth_guarantee_mb_per_sec': 10,
    'root_bandwidth_limit_mb_per_sec': 20,
    'root_storage_class': 'hdd',
    'cpu': 1000,
    'work_dir_quota': 512,
    'persistent_volumes': [
        {
            'diskQuotaMegabytes': 10240,
            'mountPoint': '/logs',
            'storageClass': 'hdd',
            'bandwidthGuaranteeMegabytesPerSec': 10,
            'bandwidthLimitMegabytesPerSec': 20,
        },
    ],
    'sysctl': [{'name': 'net.ipv6.icmp.ratemask', 'value': '0,3-127'}],
    'virtual_service_ids': ['elrusso-stable-8'],
    'network_band_guarantee': 0,
    'network_band_limit': 0,
    'thread_limit': 0,
    'gpus': [
        {
            'model': 'gpu_geforce_1080ti',
            'maxMemoryMegabytes': 11264,
            'minMemoryMegabytes': 11264,
            'gpuCount': 8,
        },
    ],
}


@pytest.mark.parametrize(
    'instances,pods_to_remove,united_pods,new_pod_ids_existed,allocated_pods',
    [
        pytest.param(
            2,
            {
                'iva': ['IVA_old_0'],
                'man': ['MAN_old_0', 'MAN_old_1'],
                'sas': [],
            },
            {
                'iva': [],
                'man': [],
                'myt': ['new_pod_1'],
                'sas': [],
                'vla': ['VLA_new_0'],
            },
            {'vla': ['VLA_new_0']},
            1,
            id='order 2 instances',
        ),
        pytest.param(
            3,
            {'iva': [], 'man': ['MAN_old_0', 'MAN_old_1']},
            {
                'iva': [],
                'man': [],
                'myt': ['new_pod_1'],
                'sas': ['SAS_new_0'],
                'vla': ['VLA_new_0', 'VLA_new_1'],
            },
            {'sas': ['SAS_new_0'], 'vla': ['VLA_new_0', 'VLA_new_1']},
            2,
            id='order 3 instances',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on(
    'enable_ratelimit_mask_change',
    'change_resources_by_name_new_flow',
    'get_all_regions_pod_info_new_flow',
    'resize_instances_recipe_new_flow',
    'use_cube_allocate_all_additional_pods',
    'use_new_params_in_cube_unitepoids',
    'use_new_params_in_cube_addpodstodeploy',
    'remove_pods_from_deploy_new_flow',
    'delete_unknown_pods_from_snapshot',
)
async def test_resize_instances_one_nanny_service_recipe(
        load_yaml,
        task_processor,
        run_job_with_meta,
        nanny_mockserver,
        nanny_yp_mockserver,
        add_external_cubes,
        instances,
        pods_to_remove,
        united_pods,
        new_pod_ids_existed,
        allocated_pods,
        nanny_yp_list_pods,
        nanny_yp_get_podset,
        nanny_yp_create_podset,
        nanny_yp_create_pods,
        abc_mockserver,
):
    nanny_yp_mockserver()
    abc_mockserver()
    add_external_cubes()
    recipe = task_processor.load_recipe(
        load_yaml('recipes/ResizeInstancesOneNannyService.yaml')['data'],
    )

    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_nanny_service_pods',
            'pod_naming_mode': 'RANDOM',
            'yp_quota_abc': 'abc_service',
            'regions': [],
            'comment': 'Robot said to do this',
            'use_append_pods': True,
            'service_id': 1,
            'branch_ids': [1],
            'service_name': 'test_service',
            'project_name': 'test_project',
            'instances_by_region': {
                'iva': instances,
                'man': 0,
                'myt': instances,
                'sas': instances,
                'vla': instances,
            },
            'pod_ids_by_region': {
                'iva': ['IVA_old_0', 'IVA_old_1', 'IVA_old_2'],
                'man': ['MAN_old_0', 'MAN_old_1'],
                'myt': [],
                'sas': ['SAS_old_0', 'SAS_old_1'],
                'vla': ['VLA_old_0'],
            },
            'environment': 'stable',
        },
        initiator='clownductor',
        idempotency_token='ony_one_job',
    )

    await run_job_with_meta(job, continue_on_sleep=False)
    expected_vars: Dict[Any] = {
        'nanny_name': 'test_nanny_service_pods',
        'pod_naming_mode': 'RANDOM',
        'yp_quota_abc': 'abc_service',
        'regions': [],
        'comment': 'Robot said to do this',
        'use_append_pods': True,
        'service_id': 1,
        'namespace_ids': ['namespace_id_1'],
        'branch_ids': [1],
        'pod_info': copy.deepcopy(POD_INFO),
        'create_pod_set_by_region': {
            'iva': False,
            'man': False,
            'myt': True,
            'sas': False,
            'vla': False,
        },
        'allocate_pod_set_by_region': {
            'iva': True,
            'man': True,
            'myt': False,
            'sas': True,
            'vla': True,
        },
        'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        'service_name': 'test_service',
        'project_name': 'test_project',
        'instances_by_region': {
            'iva': instances,
            'man': 0,
            'myt': instances,
            'sas': instances,
            'vla': instances,
        },
        'pod_ids_by_region': {
            'iva': ['IVA_old_0', 'IVA_old_1', 'IVA_old_2'],
            'man': ['MAN_old_0', 'MAN_old_1'],
            'myt': [],
            'sas': ['SAS_old_0', 'SAS_old_1'],
            'vla': ['VLA_old_0'],
        },
        'success_after_sleep': False,
        'pods_to_remove_by_region': pods_to_remove,
        'new_pod_ids_create_pod_set_by_region': {
            'iva': [],
            'man': [],
            'myt': ['new_pod_1'],
            'sas': [],
            'vla': [],
        },
        'new_pod_ids_existed_pod_by_region': new_pod_ids_existed,
        'completed_regions': ['iva', 'man', 'sas', 'vla'],
        'active_snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        'united_pods_ids_by_region': united_pods,
        'environment': 'stable',
    }
    if allocated_pods > 0:
        expected_vars['pod_info']['replicas'] = allocated_pods

    assert job.job_vars == expected_vars


@pytest.mark.parametrize('instances', [1])
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on(
    'enable_ratelimit_mask_change',
    'change_resources_by_name_new_flow',
    'get_all_regions_pod_info_new_flow',
    'resize_instances_recipe_new_flow',
    'use_cube_allocate_all_additional_pods',
    'use_new_params_in_cube_unitepoids',
    'use_new_params_in_cube_addpodstodeploy',
    'remove_pods_from_deploy_new_flow',
    'delete_unknown_pods_from_snapshot',
)
async def test_resize_instances_downsize(
        mockserver,
        load_yaml,
        task_processor,
        run_job_with_meta,
        nanny_mockserver,
        nanny_yp_mockserver,
        add_external_cubes,
        instances,
        nanny_yp_list_pods,
        nanny_yp_get_podset,
        nanny_yp_create_podset,
        nanny_yp_create_pods,
        abc_mockserver,
):
    abc_mockserver()
    nanny_yp_mockserver()
    add_external_cubes()
    recipe = task_processor.load_recipe(
        load_yaml('recipes/ResizeInstancesOneNannyService.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'nanny_name': 'test_nanny_service_pods',
            'pod_naming_mode': 'RANDOM',
            'yp_quota_abc': 'abc_service',
            'regions': [],
            'comment': 'Robot said to do this',
            'use_append_pods': True,
            'service_id': 1,
            'branch_ids': [1],
            'service_name': 'test_service',
            'project_name': 'test_project',
            'instances_by_region': {
                'iva': instances,
                'man': 0,
                'myt': 0,
                'sas': instances,
                'vla': instances,
            },
            'pod_ids_by_region': {
                'iva': ['IVA_old_0', 'IVA_old_1', 'IVA_old_2'],
                'man': ['MAN_old_0', 'MAN_old_1'],
                'myt': [],
                'sas': ['SAS_old_0', 'SAS_old_1'],
                'vla': ['VLA_old_0'],
            },
            'environment': 'unstable',
        },
        initiator='clownductor',
        idempotency_token='ony_one_job',
    )
    await run_job_with_meta(job, continue_on_sleep=False)
    expected_vars: Dict[Any] = {
        'nanny_name': 'test_nanny_service_pods',
        'pod_naming_mode': 'RANDOM',
        'yp_quota_abc': 'abc_service',
        'regions': [],
        'comment': 'Robot said to do this',
        'use_append_pods': True,
        'service_id': 1,
        'namespace_ids': ['namespace_id_1'],
        'branch_ids': [1],
        'pod_info': copy.deepcopy(POD_INFO),
        'create_pod_set_by_region': {
            'iva': False,
            'man': False,
            'myt': True,
            'sas': False,
            'vla': False,
        },
        'allocate_pod_set_by_region': {
            'iva': True,
            'man': True,
            'myt': False,
            'sas': True,
            'vla': True,
        },
        'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        'service_name': 'test_service',
        'project_name': 'test_project',
        'instances_by_region': {
            'iva': 1,
            'man': 0,
            'myt': 0,
            'sas': 1,
            'vla': 1,
        },
        'pod_ids_by_region': {
            'iva': ['IVA_old_0', 'IVA_old_1', 'IVA_old_2'],
            'man': ['MAN_old_0', 'MAN_old_1'],
            'myt': [],
            'sas': ['SAS_old_0', 'SAS_old_1'],
            'vla': ['VLA_old_0'],
        },
        'success_after_sleep': False,
        'pods_to_remove_by_region': {
            'iva': ['IVA_old_0', 'IVA_old_1'],
            'man': ['MAN_old_0', 'MAN_old_1'],
            'sas': ['SAS_old_0'],
            'vla': [],
        },
        'new_pod_ids_create_pod_set_by_region': {
            'iva': [],
            'man': [],
            'myt': [],
            'sas': [],
            'vla': [],
        },
        'new_pod_ids_existed_pod_by_region': {},
        'completed_regions': ['iva', 'man', 'sas', 'vla'],
        'active_snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        'united_pods_ids_by_region': {
            'iva': [],
            'man': [],
            'myt': [],
            'sas': [],
            'vla': [],
        },
        'environment': 'unstable',
    }

    assert job.job_vars == expected_vars
