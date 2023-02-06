import pytest


@pytest.mark.parametrize(
    'cube_name',
    [
        'AbcCubeGenerateServiceName',
        'AbcCubeGenerateTvmName',
        'AbcCubeGenerateDbName',
        'AbcCubeGeneratePostgresName',
        'AbcCubeCreateService',
        'AbcCubeWaitForService',
        'AbcCubeAddTeam',
        'AbcCubeRequestTvm',
        'AbcCubeWaitForTvm',
        'AbcCubeStashTvmSecret',
        'AbcCubeAddResponsibles',
        'AbcCubeChangeOwner',
        'AbcCubeGetServiceInfo',
        'AbcCubeEditService',
        'AbcCubeTagMicroService',
        'AbcCubeChangeServiceParent',
        'AbcCubeWaitChangeServiceParent',
        'AbcMoveService',
    ],
)
async def test_post_abc_cube_generate_service_name(
        web_app_client,
        cube_name,
        load_json,
        abc_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
        yav_mockserver,
        add_service,
        login_mockserver,
        staff_mockserver,
        tvm_info_mockserver,
        add_project,
):
    cookie_monster_mockserver()
    abc_nonofficial_mockserver()
    yav_mockserver()
    login_mockserver()
    staff_mockserver()

    if cube_name in [
            'AbcCubeWaitForTvm',
            'AbcCubeRequestTvm',
            'AbcCubeAddTeam',
            'AbcCubeStashTvmSecret',
            'AbcCubeChangeServiceParent',
            'AbcMoveService',
    ]:
        tvm_info_mockserver()
        abc_mockserver(services=True)
    else:
        abc_mockserver(services=['parent_slug', 'someservice'])

    if cube_name == 'AbcCubeChangeServiceParent':
        await add_project('old_project')
        await add_project('new_project', service_abc='parent_slug')
        await add_service(
            project_name='old_project',
            service_name='test_service',
            abc_service='someservice',
        )

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        if cube_name in ['AbcCubeChangeOwner']:
            service = await add_service('taxi', 'some_service')
            data_request['input_data']['service_id'] = service['id']

        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']


async def test_abc_get_members(call_cube_handle, abc_mockserver):
    mock = abc_mockserver(services=['abc-service'])
    await call_cube_handle(
        'AbcGetMembers',
        {
            'content_expected': {
                'payload': {
                    'members': [
                        {'login': 'isharov', 'role_id': 8},
                        {'login': 'nikslim', 'role_id': 8},
                        {
                            'linked_department': (
                                'yandex_distproducts_'
                                'browserdev_mobile_taxi_mnt'
                            ),
                            'login': 'eatroshkin',
                            'role_id': 16,
                        },
                    ],
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {'slug': 'abc-service', 'role_ids': [8, 16]},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert mock.times_called == 1
    query = mock.next_call()['request'].query
    assert query['role__in'] == '8,16'
    assert query['service__slug'] == 'abc-service'


async def test_abc_prepare_members(call_cube_handle):
    await call_cube_handle(
        'AbcPrepareMembersToAdd',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'members': [
                        {'login': 'isharov', 'role_id': 8},
                        {'login': 'nikslim', 'role_id': 8},
                    ],
                },
            },
            'data_request': {
                'input_data': {
                    'ignore_with_departments': True,
                    'members': [
                        {'login': 'isharov', 'role_id': 8},
                        {'login': 'nikslim', 'role_id': 8},
                        {
                            'linked_department': (
                                'yandex_distproducts_'
                                'browserdev_mobile_taxi_mnt'
                            ),
                            'login': 'eatroshkin',
                            'role_id': 16,
                        },
                    ],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )


async def test_abc_add_members(call_cube_handle, abc_mockserver):
    mock = abc_mockserver(services=['abc-service'])
    await call_cube_handle(
        'AbcAddMembers',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'slug': 'abc-service',
                    'members': [{'login': 'karachevda', 'role_id': 8}],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert mock.times_called == 2
    mock.next_call()
    assert mock.next_call()['request'].json == {
        'person': 'karachevda',
        'role': 8,
        'service': 3155,
    }


async def test_abc_get_departments(call_cube_handle, abc_mockserver):
    mock = abc_mockserver(services=['abc-service'])
    await call_cube_handle(
        'AbcGetDepartments',
        {
            'content_expected': {
                'payload': {
                    'departments': [{'department_id': 9293, 'role_id': 1258}],
                },
                'status': 'success',
            },
            'data_request': {
                'input_data': {'slug': 'abc-service', 'role_ids': [1258]},
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert mock.times_called == 1
    query = mock.next_call()['request'].query
    assert query['service__slug'] == 'abc-service'


async def test_abc_prepare_departments(call_cube_handle):
    await call_cube_handle(
        'AbcPrepareDepartmentsToAdd',
        {
            'content_expected': {
                'status': 'success',
                'payload': {
                    'departments': [{'department_id': 9293, 'role_id': 1258}],
                },
            },
            'data_request': {
                'input_data': {
                    'departments': [{'department_id': 9293, 'role_id': 1258}],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )


async def test_abc_add_departments(call_cube_handle, abc_mockserver):
    mock = abc_mockserver(services=['abc-service'])
    await call_cube_handle(
        'AbcAddDepartments',
        {
            'content_expected': {'status': 'success'},
            'data_request': {
                'input_data': {
                    'slug': 'abc-service',
                    'departments': [{'department_id': 9293, 'role_id': 1258}],
                },
                'job_id': 1,
                'retries': 0,
                'status': 'in_progress',
                'task_id': 1,
            },
        },
    )

    assert mock.times_called == 2
    mock.next_call()
    assert mock.next_call()['request'].json == {
        'role': 1258,
        'service': 3155,
        'department': 9293,
    }
