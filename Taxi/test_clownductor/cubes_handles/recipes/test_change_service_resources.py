import pytest

TRANSLATIONS = {
    'tickets.approved_change_service_resources': {'ru': 'Approved'},
}


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
@pytest.mark.features_on(
    'enable_ratelimit_mask_change',
    'disable_default_instances_and_dc',
    'change_resources_by_name_new_flow',
    'get_all_regions_pod_info_new_flow',
    'resize_instances_recipe_new_flow',
    'use_cube_allocate_all_additional_pods',
    'use_new_params_in_cube_unitepoids',
    'use_new_params_in_cube_addpodstodeploy',
    'remove_pods_from_deploy_new_flow',
    'delete_unknown_pods_from_snapshot',
)
@pytest.mark.parametrize(
    'env, branch_id, expected_main_vars, expected_secondary_vars,'
    'st_get_myself_calls, '
    'st_create_comment_calls, nanny_yp_list_pods_groups_calls, '
    'nanny_yp_pod_reallocation_spec_calls, '
    'nanny_yp_start_pod_reallocation_calls',
    [
        pytest.param(
            'testing',
            1,
            'custom_expected_vars.json',
            'custom_expected_secondary_vars.json',
            2,
            2,
            1,
            1,
            1,
        ),
        pytest.param(
            'stable',
            2,
            'stable_expected_vars.json',
            'stable_expected_secondary_vars.json',
            4,
            4,
            2,
            2,
            2,
        ),
    ],
)
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_change_service_resources(
        mockserver,
        load_yaml,
        load_json,
        task_processor,
        run_job_with_meta,
        nanny_mockserver,
        nanny_yp_mockserver,
        call_cube_handle,
        patch,
        staff_mockserver,
        nanny_yp_list_pods_groups,
        nanny_yp_pod_reallocation_spec,
        nanny_yp_start_pod_reallocation,
        st_get_myself,
        st_create_comment,
        st_execute_transaction,
        env,
        branch_id,
        expected_main_vars,
        expected_secondary_vars,
        st_get_myself_calls,
        st_create_comment_calls,
        nanny_yp_list_pods_groups_calls,
        nanny_yp_pod_reallocation_spec_calls,
        nanny_yp_start_pod_reallocation_calls,
        add_external_cubes,
        yp_mockserver,
):
    nanny_yp_mockserver()
    staff_mockserver()
    add_external_cubes()
    yp_mockserver()

    task_processor.load_recipe(
        load_yaml('recipes/ChangeServiceResources.yaml')['data'],
    )
    task_processor.load_recipe(
        load_yaml('recipes/ResizeInstancesOneNannyService.yaml')['data'],
    )
    task_processor.load_recipe(
        load_yaml('recipes/ReallocateOneNannyService.yaml')['data'],
    )

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
        '/client-nanny/v2/services/test_nanny_service/runtime_attrs/',
    )  # pylint: disable=unused-variable
    def handler_pre(request):
        if request.method == 'GET':
            return load_json('nanny_service_runtime_attrs_pre.json')
        if request.method == 'PUT':
            return load_json('nanny_service_runtime_attrs_response_pre.json')
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

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        comments = [
            {
                'login': 'some-developer1',
                'time': '2000-06-28T15:27:25.361+0000',
                'text': 'OK for release:456',
            },
            {
                'login': 'robot-taxi-clown',
                'time': '2000-06-28T15:25:25.361+0000',
                'text': 'OK for release:456',
            },
        ]
        if 'short_id' in kwargs and kwargs['short_id'] is not None:
            return []
        return [
            {
                'id': id(entry),
                'text': entry['text'],
                'createdBy': {'id': entry['login']},
                'createdAt': entry['time'],
            }
            for entry in comments
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_field_history')
    async def _get_field_history(*args, **kwargs):
        history = [
            {
                'login': 'some-manager1',
                'time': '2001-06-28T15:27:25.361+0000',
                'to': 'readyForRelease',
            },
        ]
        return [
            {
                'fields': [{'to': {'key': entry['to']}}],
                'updatedBy': {'id': entry['login']},
                'updatedAt': entry['time'],
            }
            for entry in history
        ]

    @patch('taxi.clients.startrack.StartrackAPIClient.get_ticket')
    async def _get_ticket(ticket):
        return {
            'status': {'key': 'open', 'id': '4'},
            'assignee': {'id': 'deoevgen'},
            'createdBy': {'id': 'd1mbas'},
            'key': 'SOMEONE-1',
            'id': '5fdcc3fc88238040f8b861a3',
            'followers': [],
        }

    @patch(
        'clownductor.generated.service.conductor_api.'
        'plugin.ConductorClient.get_approvers',
    )
    async def _get_approvers(*args, **kwargs):
        return [str(arg) for arg in args if arg is not None]

    service_id = 1
    await call_cube_handle(
        'StartChangeNannySubsystem',
        {
            'content_expected': {
                'payload': {
                    'nanny_job_id': 1,
                    'st_comment': (
                        'Starting job ((/services/1/edit/1/jobs?jobId=1&'
                        'isClownJob=true ChangeServiceResources))'
                    ),
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {
                    'subsystems_info': {
                        'nanny': {
                            'cpu': {'new': 1000, 'old': 500},
                            'datacenters_count': {'new': 3, 'old': 1},
                            'instances': {'new': 3, 'old': 1},
                            'persistent_volumes': {
                                'new': [
                                    {
                                        'bandwidth_guarantee_mb_per_sec': 3,
                                        'bandwidth_limit_mb_per_sec': 6,
                                        'path': '/logs',
                                        'size': 10240,
                                        'type': 'hdd',
                                    },
                                ],
                                'old': None,
                            },
                            'ram': {'new': 1000, 'old': 500},
                            'root_size': {'new': 10240, 'old': 5120},
                            'root_storage_class': {'new': 'ssd', 'old': 'hdd'},
                            'work_dir': {'new': 256, 'old': 4096},
                        },
                    },
                    'service_id': service_id,
                    'branch_id': branch_id,  # 1- testing, 2 - stable
                    'environment': env,
                    'nanny_name': 'test_service_stable',
                    'ticket': 'SOMEONE-1',
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )
    change_doc_id = f'{service_id}_{branch_id}_StartChangeNannySubsystem'
    main_job = task_processor.get_active_job(change_doc_id)
    await run_job_with_meta(main_job, continue_on_sleep=False)
    assert main_job.job_vars == load_json(expected_main_vars)
    secondary_expected_data = load_json(expected_secondary_vars)
    assert len(task_processor.jobs) - 1 == len(secondary_expected_data)
    for expected_data in secondary_expected_data:
        job = task_processor.find_job(expected_data['job_id'])
        assert job
        assert job.recipe.name == expected_data['job_name']
        assert job.job_vars == expected_data['job_vars']

    assert len(st_get_myself.calls) == st_get_myself_calls
    assert len(st_create_comment.calls) == st_create_comment_calls
    assert len(st_execute_transaction.calls) == 1
    assert (
        nanny_yp_list_pods_groups.times_called
        == nanny_yp_list_pods_groups_calls
    )
    assert (
        nanny_yp_pod_reallocation_spec.times_called
        == nanny_yp_pod_reallocation_spec_calls
    )
    assert (
        nanny_yp_start_pod_reallocation.times_called
        == nanny_yp_start_pod_reallocation_calls
    )
