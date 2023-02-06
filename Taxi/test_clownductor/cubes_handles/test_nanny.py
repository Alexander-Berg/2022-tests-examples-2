import pytest


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.parametrize(
    'cube_name',
    [
        'NannyCubeCreateServicePrefix',
        'CreateNannyPodSet',
        'CreateNewPodSetOrAllocateToExisted',
        'NannyCubeCreateServiceName',
        'NannyCubeCreate',
        'NannyCubeAllocatePods',
        'WaitPodsAllocateEnd',
        'NannyCubeAddPodsToDeploy',
        'NannyCubeRemovePodsFromDeploy',
        'NannyCubeCreateSnapshot',
        'NannyCubeCreateSnapshotPrestable',
        'NannyCubeOptionalDeploySnapshot',
        'NannyCubeDeploySnapshot',
        'NannyCubeWaitForDeploy',
        'NannyCubeOptionalWaitForDeploy',
        'NannyUpdateCleanupPolicy',
        'NannyGetPods',
        'NannyGetPodsInfo',
        'NannyGetPodsInfoByRegion',
        'NannyAllocateAdditionalPods',
        'NannyRemovePods',
        'NannyShutdownService',
        'NannyWaitForShutdown',
        'NannyRemoveEndpointSet',
        'NannyRemovePodSets',
        'NannyRemoveService',
        'NannyUpdateEndpointset',
        'NannyGetAllRegionsPodsInfo',
        'UnitePodIds',
        'NannyCreateAllRegionsPodSets',
    ],
)
@pytest.mark.features_on(
    'get_all_regions_pod_info_new_flow',
    'use_new_params_in_cube_unitepoids',
    'use_new_params_in_cube_addpodstodeploy',
)
async def test_post_nanny_cube_handler(
        load_json,
        nanny_mockserver,
        nanny_mock_context,
        nanny_yp_mockserver,
        add_service,
        add_nanny_branch,
        cube_name,
        call_cube_handle,
):
    if cube_name in (
            'NannyWaitForShutdown',
            'NannyRemovePodSets',
            'NannyRemoveService',
    ):
        nanny_mock_context.set_disabled_service(
            'taxi-infra_clownductor_unstable',
        )
    nanny_yp_mockserver()

    await add_service(
        project_name='taxi',
        service_name='test-service',
        direct_link='taxi_test-service',
    )
    await add_nanny_branch(service_id=1, branch_name='test-branch')

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        await call_cube_handle(cube_name, json_data)


@pytest.fixture(name='destroy_request')
def _destroy_request():
    return {
        'input_data': {
            'env': 'testing',
            'nanny_name': 'taxi_test-service_testing',
            'snapshot_id': '123',
        },
        'job_id': 1,
        'retries': 0,
        'status': 'in_progress',
        'task_id': 1,
    }


@pytest.fixture(name='list_state_changes')
async def _list_state_changes(mockserver):
    @mockserver.json_handler(
        '/client-nanny/api/repo/ListSnapshotStateChanges/',
    )
    async def _wrapper(request):
        assert request.json['snapshotId'] == '123'
        return {'total': 1, 'value': [{'targetState': {'state': 'ACTIVE'}}]}

    return _wrapper


@pytest.fixture(name='cleanup_policy')
async def _cleanup_policy(mockserver):
    @mockserver.json_handler('/client-nanny/api/repo/GetCleanupPolicy/')
    async def _wrapper(request):
        assert request.json['policy_id'] == 'taxi_test-service_testing'
        return {
            'policy': {
                'spec': {
                    'simpleCountLimit': {
                        'snapshotsCount': 1,
                        'disposableCount': 0,
                        'stalledTtl': 'PT24H',
                    },
                },
            },
        }

    return _wrapper


@pytest.fixture(name='info_attrs')
async def _info_attrs(mockserver):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/info_attrs/',
    )
    async def _wrapper(request):
        assert request.method == 'GET'
        return {
            'content': {
                'recipes': {
                    'content': [{'id': 'default'}],
                    'prepare_recipes': [{'id': 'default'}],
                },
            },
        }

    return _wrapper


@pytest.fixture(name='destroy')
async def _destroy(mockserver):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/events/',
    )
    async def _wrapper(request):
        assert request.json == {
            'type': 'SET_SNAPSHOT_STATE',
            'content': {
                'state': 'DESTROYED',
                'snapshot_id': '2ac7dee5e6efbb127339be69be3829ff94d1737f',
                'comment': (
                    'Auto destroy extra snapshot while '
                    'deploying in clownductor'
                ),
                'tracked_tickets': {'tickets': []},
                'recipe': 'default',
                'prepare_recipe': 'default',
            },
        }
        return {}

    return _wrapper


async def call_destroy_snapshot(
        call_cube_handle,
        destroy_request,
        list_state_changes,
        cleanup_policy,
        info_attrs,
        destroy,
):
    cube_name = 'NannyTryDestroyExtraSnapshots'
    json_data = {
        'data_request': destroy_request,
        'content_expected': {'sleep_duration': 10, 'status': 'in_progress'},
    }
    await call_cube_handle(cube_name, json_data)
    assert list_state_changes.times_called == 1
    assert cleanup_policy.times_called == 1
    assert info_attrs.times_called == 1
    assert destroy.times_called == 1


DISABLE_NANNY_SNAPSHOT_ACTIVATE = {
    '__default__': {},
    'test_project': {
        'test_service': {'disable_nanny_snapshot_activate': True},
        '__default__': {},
    },
}


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'remove_extra_snapshots': True})
@pytest.mark.parametrize(
    'add_service_info, expected_current_state_times_called',
    [
        pytest.param(
            True,
            1,
            id=(
                'service_name/project_name present, '
                'disable_nanny_snaphot_activate=false, '
                'cube passes feature check'
            ),
        ),
        pytest.param(
            False,
            1,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE=(
                    DISABLE_NANNY_SNAPSHOT_ACTIVATE
                ),
            ),
            id=(
                'service_name/project_name absent, '
                'disable_nanny_snaphot_activate=true, '
                'cube passes feature check'
            ),
        ),
        pytest.param(
            True,
            0,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE=(
                    DISABLE_NANNY_SNAPSHOT_ACTIVATE
                ),
            ),
            id=(
                'service_name/project_name present, '
                'disable_nanny_snaphot_activate=true, '
                'cube exits without performing any actions'
            ),
        ),
    ],
)
async def test_destroy_snapshot_disabled(
        call_cube_handle,
        destroy_request,
        mockserver,
        list_state_changes,
        cleanup_policy,
        add_service_info,
        expected_current_state_times_called,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/current_state/',
    )
    async def _current_state(request):
        assert request.method == 'GET'
        return {
            '_id': '',
            'entered': 1568716247920,
            'content': {
                'active_snapshots': [
                    {
                        'state': 'GENERATING',
                        'snapshot_id': '123',
                        'entered': 1601582768405,
                    },
                ],
            },
        }

    if add_service_info:
        destroy_request['input_data']['project_name'] = 'test_project'
        destroy_request['input_data']['service_name'] = 'test_service'

    cube_name = 'NannyTryDestroyExtraSnapshots'
    json_data = {
        'data_request': destroy_request,
        'content_expected': {'status': 'success'},
    }
    await call_cube_handle(cube_name, json_data)

    assert _current_state.times_called == expected_current_state_times_called


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'remove_extra_snapshots': True})
@pytest.mark.parametrize('use_destroy_snapshots', [True, False])
async def test_not_destroy_snapshot(
        call_cube_handle,
        mockserver,
        list_state_changes,
        cleanup_policy,
        destroy_request,
        use_destroy_snapshots,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/current_state/',
    )
    async def _current_state(request):
        assert request.method == 'GET'
        active_snapshots = [
            {
                'state': 'GENERATING',
                'snapshot_id': '123',
                'entered': 1601582768405,
            },
            {
                'state': 'DEACTIVATE_PENDING',
                'snapshot_id': '18381d2d99c86d85c21798962c7a43a90954db63',
                'entered': 1601582768307,
            },
            {
                'state': 'DEACTIVATE_PENDING',
                'snapshot_id': '3ee42adcfcb833b4c6341094f7f9c681b67360d1',
                'entered': 1601564746515,
            },
        ]
        if use_destroy_snapshots:
            active_snapshots.extend(
                [
                    {
                        'state': 'DEACTIVATING',
                        'snapshot_id': '0001',
                        'entered': 1601582768406,
                    },
                    {
                        'state': 'DESTROYING',
                        'snapshot_id': '0002',
                        'entered': 1601582768407,
                    },
                    {
                        'state': 'REMOVING',
                        'snapshot_id': '0003',
                        'entered': 1601582768408,
                    },
                ],
            )
        return {
            '_id': '',
            'entered': 1568716247920,
            'content': {'active_snapshots': active_snapshots},
        }

    cube_name = 'NannyTryDestroyExtraSnapshots'
    json_data = {
        'data_request': destroy_request,
        'content_expected': {'status': 'success'},
    }
    await call_cube_handle(cube_name, json_data)
    assert list_state_changes.times_called == 1
    assert _current_state.times_called == 1
    assert cleanup_policy.times_called == 1


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'remove_extra_snapshots': True})
async def test_safe_destroy_extra_snapshot(
        call_cube_handle,
        destroy_request,
        mockserver,
        list_state_changes,
        cleanup_policy,
        info_attrs,
        destroy,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/current_state/',
    )
    async def _current_state(request):
        assert request.method == 'GET'
        return {
            '_id': '',
            'entered': 1568716247920,
            'content': {
                'active_snapshots': [
                    {
                        'state': 'GENERATING',
                        'snapshot_id': '123',
                        'entered': 1601582768405,
                    },
                    {
                        'state': 'DEACTIVATE_PENDING',
                        'snapshot_id': (
                            '18381d2d99c86d85c21798962c7a43a90954db63'
                        ),
                        'entered': 1601582768307,
                    },
                    {
                        'state': 'PREPARED',
                        'snapshot_id': (
                            '2ac7dee5e6efbb127339be69be3829ff94d1737f'
                        ),
                        'entered': 1601564840526,
                    },
                    {
                        'state': 'DEACTIVATE_PENDING',
                        'snapshot_id': (
                            '3ee42adcfcb833b4c6341094f7f9c681b67360d1'
                        ),
                        'entered': 1601564746515,
                    },
                ],
            },
        }

    await call_destroy_snapshot(
        call_cube_handle,
        destroy_request,
        list_state_changes,
        cleanup_policy,
        info_attrs,
        destroy,
    )
    assert _current_state.times_called == 1


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'remove_extra_snapshots': True})
async def test_not_safe_destroy_extra_snapshot(
        call_cube_handle,
        destroy_request,
        mockserver,
        list_state_changes,
        cleanup_policy,
        info_attrs,
        destroy,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/taxi_test-service_testing/current_state/',
    )
    async def _current_state(request):
        assert request.method == 'GET'
        return {
            '_id': '',
            'entered': 1568716247920,
            'content': {
                'active_snapshots': [
                    {
                        'state': 'GENERATING',
                        'snapshot_id': '123',
                        'entered': 1601582768405,
                    },
                    {
                        'state': 'DEACTIVATE_PENDING',
                        'snapshot_id': (
                            '2ac7dee5e6efbb127339be69be3829ff94d1737f'
                        ),
                        'entered': 1601582768307,
                    },
                    {
                        'state': 'DEACTIVATE_PENDING',
                        'snapshot_id': (
                            '18381d2d99c86d85c21798962c7a43a90954db63'
                        ),
                        'entered': 1601564840526,
                    },
                    {
                        'state': 'DEACTIVATE_PENDING',
                        'snapshot_id': (
                            '3ee42adcfcb833b4c6341094f7f9c681b67360d1'
                        ),
                        'entered': 1601564746515,
                    },
                ],
            },
        }

    @mockserver.json_handler(
        '/client-nanny/v2/history/services/runtime_attrs/', prefix=True,
    )
    async def _runtime_attrs(request):
        assert request.method == 'GET'
        return {
            'change_info': {
                'comment': '-',
                'ctime': 1595425007940,
                'author': 'robot-taxi-clown',
            },
            'parent_id': 'ac0d82834302977753329c3993f5a5d470e9e5ee',
            '_id': '1d4d26263a2d8d58c81eb40a596a51b94c961cfc',
            'content': {
                'instances': {
                    'yp_pod_ids': {
                        'pods': [
                            {'cluster': 'VLA', 'pod_id': 'pod1'},
                            {'cluster': 'MAN', 'pod_id': 'pod2'},
                            {'cluster': 'MAN', 'pod_id': 'pod3'},
                        ],
                    },
                },
            },
        }

    @mockserver.json_handler(
        '/client-nanny-yp/api/yplite/pod-sets/ListPodConfigurationInstances/',
    )
    async def _configuration_instances(request):
        assert request.json['service_id'] == 'taxi_test-service_testing'
        return {'podConfigurationInstances': [{'current_state': 'ACTIVE'}]}

    await call_destroy_snapshot(
        call_cube_handle,
        destroy_request,
        list_state_changes,
        cleanup_policy,
        info_attrs,
        destroy,
    )
    assert _current_state.times_called == 1
    _assert_runtime_attrs(_runtime_attrs)
    _assert_configuration_instances(_configuration_instances)


def _assert_configuration_instances(_configuration_instances):
    assert _configuration_instances.times_called == 6
    ids = {
        ('2ac7dee5e6efbb127339be69be3829ff94d1737f', 'VLA'),
        ('2ac7dee5e6efbb127339be69be3829ff94d1737f', 'MAN'),
        ('18381d2d99c86d85c21798962c7a43a90954db63', 'VLA'),
        ('18381d2d99c86d85c21798962c7a43a90954db63', 'MAN'),
        ('3ee42adcfcb833b4c6341094f7f9c681b67360d1', 'VLA'),
        ('3ee42adcfcb833b4c6341094f7f9c681b67360d1', 'MAN'),
    }
    while _configuration_instances.has_calls:
        request = _configuration_instances.next_call()['request']
        ids.remove((request.json['snapshot_id'], request.json['cluster']))
    assert not ids


def _assert_runtime_attrs(_runtime_attrs):
    assert _runtime_attrs.times_called == 3
    prefix = '/client-nanny/v2/history/services/runtime_attrs/'
    ids = {
        f'{prefix}2ac7dee5e6efbb127339be69be3829ff94d1737f/',
        f'{prefix}18381d2d99c86d85c21798962c7a43a90954db63/',
        f'{prefix}3ee42adcfcb833b4c6341094f7f9c681b67360d1/',
    }
    while _runtime_attrs.has_calls:
        request = _runtime_attrs.next_call()
        ids.remove(request['request'].path)
    assert not ids
