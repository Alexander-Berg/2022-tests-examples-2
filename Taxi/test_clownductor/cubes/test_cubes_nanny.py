import freezegun
import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
    return {
        'id': 123,
        'job_id': 456,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


async def test_nanny_create_service_name(
        nanny_mockserver,
        nanny_yp_mockserver,
        staff_mockserver,
        web_context,
        add_service,
        add_nanny_branch,
        login_mockserver,
):
    login_mockserver()
    nanny_yp_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'kitty', direct_link='taxi_kitty')
    branch_id = await add_nanny_branch(service['id'], 'unstable')

    cube = cubes.CUBES['NannyCubeCreateServiceName'](
        web_context,
        task_data('NannyCubeCreateServiceName'),
        {'branch_id': branch_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['name'] == 'taxi_kitty_unstable'


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    ['branch_id', 'branch_direct_link', 'endpointsets', 'expected'],
    [
        (
            1,
            'taxi_elrusso_stable',
            [
                {
                    'meta': {
                        'id': 'rtc_elrusso_test_sas',
                        'ownership': 'SYSTEM',
                        'serviceId': 'rtc_elrusso-test_sas',
                        'version': 'd940b1b7-77b9-450d-9704-3ae45bd93d51',
                    },
                    'spec': {
                        'description': 'Created by awacs',
                        'podFilter': '',
                        'port': 80,
                        'protocol': 'TCP',
                    },
                },
            ],
            [
                {
                    'id': 'rtc_elrusso_test_sas',
                    'regions': ['VLA', 'MAN', 'SAS', 'IVA', 'MYT'],
                },
            ],
        ),
    ],
)
async def test_nanny_cube_update_endpointset(
        mockserver,
        nanny_mockserver,
        web_context,
        branch_id,
        pgsql,
        branch_direct_link,
        endpointsets,
        expected,
):
    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/endpoint-sets/ListEndpointSets/',
        prefix=True,
    )
    def handler(_):
        return {'endpointSets': endpointsets}

    cube = cubes.CUBES['NannyUpdateEndpointset'](
        web_context,
        task_data('NannyUpdateEndpointset'),
        {'branch_id': branch_id, 'branch_direct_link': branch_direct_link},
        [],
        None,
    )
    await cube.update()
    assert cube.status == 'success'
    assert cube.payload['endpointsets'] == expected
    assert handler.times_called == 5


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'tc_deploy_changelog': True})
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.features_on('enable_sent_project_id_to_nanny')
async def test_nanny_cube_create_snapshot(
        nanny_mockserver,
        nanny_yp_mockserver,
        web_context,
        mockserver,
        load_json,
):
    nanny_yp_mockserver()
    expected = load_json('nanny_service_runtime_attrs_expected.json')

    @mockserver.json_handler(
        'client-nanny/v2/services/taxi_kitty_unstable/runtime_attrs/',
    )
    def handler(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs.json')

        if request.method == 'PUT':
            data = request.json
            assert expected['content'] == data['content']
            return expected
        return None

    task_info = task_data('NannyCubeCreateSnapshot')
    task_info['job_id'] = 1

    cube = cubes.CUBES['NannyCubeCreateSnapshot'](
        web_context,
        task_info,
        {
            'name': 'taxi_kitty_unstable',
            'image': 'kitty-service:0.0.1',
            'changelog': 'test',
            'project_id': 1,
            'service_id': 1,
        },
        [],
        None,
    )
    with freezegun.freeze_time('2012-01-14 12:00:01'):
        await cube.update()

    assert cube.success

    snap_id = '5c26609053b7c34a9ad5a283f48ae03c79853d58'
    assert cube.data['payload']['snapshot_id'] == snap_id
    assert handler.times_called == 2


async def test_nanny_unite_ids(
        nanny_mockserver, nanny_yp_mockserver, web_context,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['UnitePodIds'](
        web_context,
        task_data('UnitePodIds'),
        {
            'first_man_ids': ['a1', 'a2'],
            'second_man_ids': ['b2', 'b3'],
            'first_sas_ids': ['a3', 'a4'],
            'second_sas_ids': None,
            'first_vla_ids': None,
            'second_vla_ids': None,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.payload == {
        'united_man_ids': ['a1', 'a2', 'b2', 'b3'],
        'united_sas_ids': ['a3', 'a4'],
        'united_vla_ids': [],
        'pod_ids_by_region': {},
    }


async def test_nanny_create_pod_set(
        nanny_mockserver, nanny_yp_mockserver, web_context, abc_mockserver,
):
    nanny_yp_mockserver()
    abc_mockserver()

    cube = cubes.CUBES['CreateNannyPodSet'](
        web_context,
        task_data('CreateNannyPodSet'),
        {
            'nanny_name': 'test_nanny_service',
            'region': 'SAS',
            'pod_info': {
                'network': '_TEST_',
                'root_fs_quota_mb': 2048,
                'persistent_volumes': [],
                'cpu': 1000,
                'mem': 2048,
                'work_dir_quota': 256,
            },
            'pod_naming_mode': 'ENUMERATE',
            'instances': 2,
            'yp_quota_abc': 'abc_test',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.payload == {'pod_ids': ['taxi-clownductor-stable-4']}


async def test_nanny_create_all_regions_pod_sets(
        patch, mockserver, nanny_mockserver, web_context, abc_mockserver,
):
    abc_mockserver()

    @patch('clownductor.internal.tasks.cubes.cube.TaskCube.sleep')
    def _sleep(duration, error=False):
        pass

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/GetPodSet/')
    def handler_get_podsets(request):
        data = request.json
        assert data['cluster'] != 'VLA'
        if data['cluster'] == 'SAS':
            return {'podsets': []}
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def handler_list_pods(request):
        data = request.json
        assert data['cluster'] == 'SAS'
        return {'pods': [{'meta': {'id': 'pod_sas_1'}}]}

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/CreatePodSet/',
    )
    def handler_create_podset(request):
        data = request.json
        assert data['cluster'] == 'MAN'
        return {'podIds': ['new_pod_man_1']}

    cube = cubes.CUBES['NannyCreateAllRegionsPodSets'](
        web_context,
        task_data('NannyCreateAllRegionsPodSets'),
        {
            'nanny_name': 'test_nanny_service',
            'pod_info': {
                'network': '_TEST_',
                'root_fs_quota_mb': 2048,
                'persistent_volumes': [],
                'cpu': 1000,
                'mem': 2048,
                'work_dir_quota': 256,
            },
            'pod_naming_mode': 'ENUMERATE',
            'yp_quota_abc': 'abc_test',
            'allocate_pod_set_by_region': {
                'vla': True,
                'sas': False,
                'man': False,
            },
            'instances_by_region': {'vla': 1, 'man': 1, 'sas': 2},
        },
        [],
        None,
    )

    await cube.update()
    assert cube.in_progress
    assert cube.payload == {
        'pod_ids_by_region': {'vla': [], 'man': ['new_pod_man_1']},
    }

    await cube.update()
    assert cube.in_progress
    assert cube.payload == {
        'pod_ids_by_region': {
            'sas': ['pod_sas_1'],
            'vla': [],
            'man': ['new_pod_man_1'],
        },
    }

    await cube.update()
    assert cube.success
    assert cube.payload == {
        'pod_ids_by_region': {
            'sas': ['pod_sas_1'],
            'vla': [],
            'man': ['new_pod_man_1'],
            'iva': [],
            'myt': [],
        },
    }

    assert handler_get_podsets.times_called == 2
    assert handler_list_pods.times_called == 1
    assert handler_create_podset.times_called == 1


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES_PER_SERVICE={
        '__default__': {},
        'test_project': {
            '__default__': {'resize_instances_recipe_new_flow': True},
        },
    },
)
@pytest.mark.parametrize(
    'project_name, expected_create, expected_allocate',
    [(None, False, True), ('test_project', True, True)],
)
async def test_nanny_create_or_allocate(
        nanny_mockserver,
        nanny_yp_mockserver,
        web_context,
        project_name,
        expected_create,
        expected_allocate,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['CreateNewPodSetOrAllocateToExisted'](
        web_context,
        task_data('CreateNewPodSetOrAllocateToExisted'),
        {'nanny_name': 'test_nanny_service', 'project_name': project_name},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.payload == {
        'allocate_man_to_existed': expected_allocate,
        'allocate_sas_to_existed': expected_allocate,
        'allocate_vla_to_existed': expected_allocate,
        'allocate_pod_set_by_region': {
            'iva': True,
            'man': True,
            'myt': True,
            'sas': True,
            'vla': True,
        },
        'create_man_pod_set': expected_create,
        'create_sas_pod_set': expected_create,
        'create_vla_pod_set': expected_create,
        'create_pod_set_by_region': {
            'iva': False,
            'man': False,
            'myt': False,
            'sas': False,
            'vla': False,
        },
    }


async def test_nanny_runtime_attrs(
        nanny_mockserver, nanny_yp_mockserver, web_context,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyGetRuntimeAttrsInfo'](
        web_context,
        task_data('NannyGetRuntimeAttrsInfo'),
        {'nanny_name': 'taxi_kitty_unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.payload == {
        'instances_by_region': {'VLA': ['qqbyrftajycoh7q2']},
    }


async def test_nanny_cube_wait_for_deploy(
        nanny_mockserver, nanny_yp_mockserver, web_context,
):
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyCubeWaitForDeploy'](
        web_context,
        task_data('NannyCubeWaitForDeploy'),
        {
            'name': 'taxi_kitty_unstable',
            'snapshot_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_cube_add_owners(
        nanny_mockserver, nanny_yp_mockserver, staff_mockserver, web_context,
):
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyCubeAddOwners'](
        web_context,
        task_data('NannyCubeAddOwners'),
        {
            'name': 'taxi_kitty_unstable',
            'comment': 'some useful comment',
            'owners': ['svc_vopstaxi'],
            'owner_logins': ['karachevda'],
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_update_cleanup_policy(nanny_mockserver, web_context):
    cube = cubes.CUBES['NannyUpdateCleanupPolicy'](
        web_context,
        task_data('NannyUpdateCleanupPolicy'),
        {'nanny_name': 'taxi-infra_clownductor_unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={'nanny_set_l7_monitoring_settings': True},
)
@pytest.mark.parametrize(
    ['env', 'project_name'],
    [
        ('unstable', 'taxi'),
        ('testing', 'taxi'),
        ('prestable', 'taxi'),
        ('stable', 'taxi'),
        ('stable', 'eda'),
    ],
)
async def test_nanny_set_l7_monitoring_settings(
        nanny_mockserver,
        login_mockserver,
        staff_mockserver,
        project_name,
        env,
        web_context,
        add_service,
        add_nanny_branch,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service(
        project_name, 'kitty', direct_link='taxi_kitty',
    )
    await add_nanny_branch(
        service['id'], env if env != 'prestable' else 'pre_stable', env,
    )
    cube = cubes.CUBES['NannySetL7MonitoringSettings'](
        web_context,
        task_data('NannySetL7MonitoringSettings'),
        {
            'service_id': service['id'],
            'env': env,
            'nanny_service': 'rtc_balancer_whatever_name',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_shutdown_service(nanny_mockserver, web_context):
    cube = cubes.CUBES['NannyShutdownService'](
        web_context,
        task_data('NannyShutdownService'),
        {'nanny_name': 'taxi-infra_clownductor_unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_remove_endpointset(
        nanny_mockserver,
        nanny_mock_context,
        nanny_yp_mockserver,
        staff_mockserver,
        web_context,
):
    nanny_name = 'taxi-infra_clownductor_unstable'
    nanny_mock_context.set_disabled_service(nanny_name)
    nanny_yp_mockserver()
    staff_mockserver()

    cube = cubes.CUBES['NannyRemoveEndpointSet'](
        web_context,
        task_data('NannyRemoveEndpointSet'),
        {'nanny_name': 'taxi-infra_clownductor_unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_remove_podset(
        nanny_mockserver, nanny_mock_context, nanny_yp_mockserver, web_context,
):
    nanny_name = 'taxi-infra_clownductor_unstable'
    nanny_mock_context.set_disabled_service(nanny_name)
    nanny_yp_mockserver()

    cube = cubes.CUBES['NannyRemovePodSets'](
        web_context,
        task_data('NannyRemovePodSets'),
        {'nanny_name': 'taxi-infra_clownductor_unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success


async def test_nanny_start_deploy_services(
        web_context,
        add_service,
        add_nanny_branch,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()
    service = await add_service('taxi', 'test_nanny')
    await add_nanny_branch(service['id'], 'testing')

    service = await add_service('taxi', 'test_nanny_2')
    await add_nanny_branch(service['id'], 'testing')

    cube = cubes.CUBES['MetaStartDeployNannyServices'](
        web_context,
        task_data('MetaStartDeployNannyServices'),
        {
            'service_id': 1,
            'branch_id': 1,
            'image': 'test_image',
            'nanny_name': 'test_nanny',
            'aliases': [
                {
                    'branch_id': 2,
                    'service_id': 2,
                    'nanny_name': 'test_nanny_2',
                    'image': 'test_image_2',
                },
            ],
            'comment': 'test_comment',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert len(cube.payload['job_ids']) == 2


async def test_nanny_remove_service(
        nanny_mockserver, nanny_mock_context, web_context,
):
    nanny_name = 'taxi-infra_clownductor_unstable'
    nanny_mock_context.set_disabled_service(nanny_name)

    cube = cubes.CUBES['NannyRemoveService'](
        web_context,
        task_data('NannyRemoveService'),
        {'nanny_name': nanny_name},
        [],
        None,
    )

    await cube.update()

    assert cube.success
