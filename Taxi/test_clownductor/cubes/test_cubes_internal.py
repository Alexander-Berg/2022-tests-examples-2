import freezegun
import pytest
from ruamel import yaml

from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres


# pylint: disable=invalid-name
async def test_internal_cube_update_service(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_service,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')

    cube = cubes.CUBES['InternalCubeUpdateService'](
        web_context,
        task_data('InternalCubeUpdateService'),
        {
            'service_id': service['id'],
            'service_production_ready': True,
            'service_artifact_name': 'new-art-name',
            'service_st_task': None,
            'service_wiki_path': None,
            'service_abc_service': None,
            'tvm_testing_abc_service': None,
            'tvm_stable_abc_service': None,
            'direct_link': 'some_name',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    service = await get_service(service['id'])
    assert service['production_ready'] is True
    assert service['artifact_name'] == 'new-art-name'
    assert service['direct_link'] == 'some_name'


# pylint: disable=invalid-name
async def test_internal_cube_update_branch(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_branch,
        add_nanny_branch,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')
    branch_id = await add_nanny_branch(
        service['id'], 'new-branch', direct_link='path',
    )

    cube = cubes.CUBES['InternalCubeUpdateBranch'](
        web_context,
        task_data('InternalCubeUpdateService'),
        {
            'branch_id': branch_id,
            'branch_direct_link': 'path_to_nanny',
            'branch_artifact_version': None,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    branch = await get_branch(branch_id)
    assert branch[0]['direct_link'] == 'path_to_nanny'


async def test_internal_cube_init_balancer_alias(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        add_nanny_branch,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some-service')
    branch_id = await add_nanny_branch(service['id'], 'new-branch')
    await web_context.service_manager.hosts.upsert(
        {
            'name': 'some-host',
            'datacenter': 'some-datacenter',
            'branch_id': branch_id,
        },
    )

    cube = cubes.CUBES['InternalCubeInitBalancerAlias'](
        web_context,
        task_data('InternalCubeInitBalancerAlias'),
        {'service_id': service['id'], 'env': 'unstable'},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['host'] == 'some-host'


async def test_internal_generate_artifact_name(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')

    cube = cubes.CUBES['InternalGenerateArtifactName'](
        web_context,
        task_data('InternalGenerateArtifactName'),
        {'service_id': service['id']},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['artifact_name'] == 'taxi/some_service/$'


async def test_internal_cube_sleep(web_context, task_data):
    cube = cubes.CUBES['InternalCubeSleep'](
        web_context,
        task_data('InternalCubeSleep'),
        {'sleep_sec': 1},
        [],
        None,
    )
    with freezegun.freeze_time('2012-01-14 12:00:01'):
        await cube.update()
    assert not cube.success
    with freezegun.freeze_time('2012-01-14 12:00:03'):
        await cube.update()
    assert cube.success


async def test_internal_cube_branch_set_deleted(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_branches,
        add_nanny_branch,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')
    branch_id = await add_nanny_branch(
        service['id'], 'new-branch', direct_link='path',
    )

    cube = cubes.CUBES['InternalJobBranchSetDeleted'](
        web_context,
        task_data('InternalJobBranchSetDeleted'),
        {'branch_id': branch_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    branches = await get_branches(service['id'])
    assert not branches


async def test_internal_cube_service_set_deleted(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        get_services,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')

    cube = cubes.CUBES['InternalJobServiceSetDeleted'](
        web_context,
        task_data('InternalJobServiceSetDeleted'),
        {'service_id': service['id']},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    services = await get_services()
    assert services['projects'] == [
        {'project_id': 1, 'project_name': 'taxi', 'services': []},
    ]


@pytest.mark.parametrize(
    ['expected_delay', 'has_message'],
    (
        pytest.param(
            0,
            False,
            marks=pytest.mark.config(
                CLOWNDUCTOR_DUTY_ENFORCE_SETTINGS={'deploy_delay': 0},
            ),
        ),
        pytest.param(
            1800,
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_DUTY_ENFORCE_SETTINGS={'deploy_delay': 1800},
            ),
        ),
    ),
)
async def test_internal_cube_missing_duty_check(
        web_context,
        login_mockserver,
        staff_mockserver,
        add_service,
        expected_delay,
        has_message,
        task_data,
):
    login_mockserver()
    staff_mockserver()

    service = await add_service('taxi', 'some_service')

    cube = cubes.CUBES['InternalCubeMissingDutyCheck'](
        web_context,
        task_data('InternalCubeMissingDutyCheck'),
        {'service_id': service['id']},
        [],
        None,
    )

    await cube.update()

    assert cube.success

    assert cube.data['payload']['deploy_delay'] == expected_delay
    assert bool(cube.data['payload']['deploy_delay_message']) == has_message


@pytest.mark.parametrize(
    'service_yaml_path, service_config_path',
    [
        pytest.param(
            'service_yaml',
            'expected_service_config',
            id='service_yaml_with_empty_disk_profiles',
        ),
    ],
)
@pytest.mark.features_on('disk_profiles')
async def test_internal_service_yaml_to_parameters(
        web_context,
        login_mockserver,
        staff_mockserver,
        service_yaml_path,
        service_config_path,
        load_json,
        task_data,
):
    login_mockserver()
    staff_mockserver()
    service_yaml = load_json(f'{service_yaml_path}.json')
    service_config = load_json(f'{service_config_path}.json')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['InternalServiceYamlToParameters'](
            web_context,
            task_data('InternalServiceYamlToParameters'),
            {'service_yaml': service_yaml},
            [],
            conn,
        )
        await cube.update()

    assert cube.success
    assert service_config == cube.data['payload']['service_config']


@pytest.mark.parametrize(
    ['service_id', 'service_yaml', 'calls', 'expected_file'],
    (
        [
            (1, 'service.yaml', 1, 'service_yaml.json'),
            (2, 'service.yaml', 0, 'non_service_yaml.json'),
        ]
    ),
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_internal_cube_sync_service_yaml_in_repo(
        web_context,
        patch_github_single_file,
        service_id,
        service_yaml,
        calls,
        expected_file,
        load_json,
        task_data,
):
    get_single_file = patch_github_single_file(
        f'test_cubes_internal/{service_yaml}', service_yaml,
    )

    service_yaml_data = {'service_info': 'not_updated_service_yaml'}
    cube = cubes.CUBES['InternalCubeSyncServiceYamlInRepo'](
        web_context,
        task_data('InternalCubeSyncServiceYamlInRepo'),
        {'service_id': service_id, 'service_yaml': service_yaml_data},
        [],
        None,
    )

    await cube.update()
    assert cube.success
    assert len(get_single_file.calls) == calls
    assert cube.data['payload'] == load_json(f'expected/{expected_file}')


@pytest.mark.parametrize(
    ['service_id', 'expected_file'], ([(1, 'change_preset.yaml'), (2, None)]),
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_internal_cube_change_preset_info(
        web_context,
        load_yaml,
        service_id,
        expected_file,
        login_mockserver,
        staff_mockserver,
        patch_github_single_file,
        task_data,
):
    login_mockserver()
    staff_mockserver()
    get_single_file = patch_github_single_file(
        'test_cubes_internal/service.yaml', 'service.yaml',
    )
    cube = cubes.CUBES['InternalCubeChangePresetInfo'](
        web_context,
        task_data('InternalCubeChangePresetInfo'),
        {'service_id': service_id},
        [],
        None,
    )

    await cube.update()
    if service_id == 2:
        assert cube.failed
    else:
        assert cube.success
        yaml_mng = yaml.YAML(typ='rt')
        data = yaml_mng.load(cube.data['payload']['content'])
        assert data == load_yaml(f'expected/{expected_file}')
        assert len(get_single_file.calls) == 1
