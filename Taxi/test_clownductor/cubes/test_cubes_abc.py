import logging

import pytest

from taxi.logs import log

from clownductor.internal.db import db_types
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


def _api_v4_usage_variants():
    conf = pytest.mark.config(
        CLOWNDUCTOR_ABC_API_V4_USAGE={
            'create_abc_service': 1,
            'service': 1,
            'service_by_id': 1,
            'services': 1,
            'add_department': 1,
            'add_member': 1,
            'delete_member': 1,
            'get_members': 1,
            'get_resources': 1,
            'get_responsibles': 1,
            'edit_abc_service': 1,
            'add_tag': 1,
            'non_official_get_tvm_secret': 1,
            'non_official_add_responsible': 1,
        },
    )
    return pytest.mark.parametrize(
        '',
        [
            pytest.param(marks=conf, id='use_api_v4'),
            pytest.param(id='use_api_v3'),
        ],
    )


pytestmark = [_api_v4_usage_variants()]  # pylint: disable=invalid-name


# pylint: disable=invalid-name
async def test_abc_cube_generate_service_name(web_context, abc_mockserver):
    abc_mockserver()

    cube = cubes.CUBES['AbcCubeGenerateServiceName'](
        web_context,
        task_data('AbcCubeGenerateServiceName'),
        {
            'project': 'taxi-infra',
            'service': 'mega_service',
            'st_task': 'TAXIADMIN-100500',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    payload = cube.data['payload']
    assert payload['slug'] == 'taxiinframegaservice'
    assert payload['name'] == 'taxi-infra/mega_service'
    assert payload['abc_name'] == {
        'en': 'taxi-infra/mega_service',
        'ru': 'taxi-infra/mega_service',
    }


# pylint: disable=invalid-name
async def test_abc_cube_generate_pg_service_name(web_context, abc_mockserver):
    abc_mockserver()

    cube = cubes.CUBES['AbcCubeGeneratePostgresName'](
        web_context,
        task_data('AbcCubeGeneratePostgresName'),
        {
            'project': 'taxi',
            'service': 'mega_service',
            'st_task': 'TAXIADMIN-100500',
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    project = 'taxi/mega_service'

    payload = cube.data['payload']
    assert payload['slug'] == 'taxipgaasmegaservice'
    assert payload['name'] == f'PGaaS storage for {project}'


@pytest.mark.parametrize(
    'db_type, slug, name',
    [
        (
            db_types.DbType.Postgres.value,
            'taxipgaasmegaservice',
            'PGaaS storage for taxi/mega_service',
        ),
        (
            db_types.DbType.Mongo.value,
            'taximongoaasmegaservice',
            'Mongo storage for taxi/mega_service',
        ),
        (
            db_types.DbType.Redis.value,
            'taxiredismegaservice',
            'Redis storage for taxi/mega_service',
        ),
    ],
)
async def test_abc_cube_generate_db_service_name(
        web_context, abc_mockserver, db_type, slug, name,
):
    abc_mockserver()

    cube = cubes.CUBES['AbcCubeGenerateDbName'](
        web_context,
        task_data('AbcCubeGenerateDbName'),
        {
            'project': 'taxi',
            'service': 'mega_service',
            'st_task': 'TAXIADMIN-100500',
            'db_type': db_type,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    payload = cube.data['payload']
    assert payload['slug'] == slug
    assert payload['name'] == name


@pytest.mark.parametrize(
    'is_production, reference_name, reference_slug, tvm_id',
    [
        (
            False,
            'TVM for taxi-infra/mega_service - testing',
            'tvmtaxiinframegaservicetesting',
            '',
        ),
        (
            True,
            'TVM for taxi-infra/mega_service - stable',
            'tvmtaxiinframegaservicestable',
            '',
        ),
        (False, '', '', '1234'),
        (True, '', '', '1234'),
    ],
)
async def test_abc_cube_generate_tvm_name(
        web_context,
        abc_mockserver,
        is_production,
        reference_name,
        reference_slug,
        tvm_id,
):
    abc_mockserver()

    cube = cubes.CUBES['AbcCubeGenerateTvmName'](
        web_context,
        task_data('AbcCubeGenerateTvmName'),
        {
            'project': 'taxi-infra',
            'service': 'mega_service',
            'is_production': is_production,
            'tvm_id': tvm_id,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success

    payload = cube.data['payload']
    assert payload['slug'] == reference_slug
    assert payload['name'] == reference_name


@pytest.mark.parametrize(
    'parent_exists, service_exists, error',
    [
        (False, False, True),  # no parent - error
        (False, True, True),  # no parent - error
        (True, False, False),  # parent exists, should be ok
        (True, True, False),  # parent exists, should be ok
    ],
)
async def test_abc_cube_create_service(
        web_context, abc_mockserver, parent_exists, service_exists, error,
):
    parent_slug = 'someparent'
    slug = 'someservice'

    existing_services = []
    if parent_exists:
        existing_services.append(parent_slug)
    if service_exists:
        existing_services.append(slug)

    abc_mockserver(services=existing_services)

    cube = cubes.CUBES['AbcCubeCreateService'](
        web_context,
        task_data('AbcCubeCreateService'),
        {'parent_slug': parent_slug, 'slug': slug, 'name': 'Some Service'},
        [],
        None,
    )

    await cube.update()

    if not error:
        assert cube.success
    else:
        assert cube.failed


@pytest.mark.parametrize(
    'service_exists, sleeping',
    [
        (False, True),  # no service - sleep a bit
        (True, False),  # service exists - ok
    ],
)
async def test_abc_cube_wait_for_service(
        web_context, abc_mockserver, service_exists, sleeping,
):
    slug = 'someservice'

    existing_services = [slug] if service_exists else []

    abc_mockserver(services=existing_services)

    cube = cubes.CUBES['AbcCubeWaitForService'](
        web_context,
        task_data('AbcCubeWaitForService'),
        {'slug': slug},
        [],
        None,
    )

    await cube.update()

    if not sleeping:
        assert cube.success
    else:
        assert cube.data['sleep_until'] != 0


async def test_abc_cube_add_team(
        web_context, abc_mockserver, staff_mockserver,
):
    slug = 'someservice'
    abc_mockserver(services=True)
    staff_mockserver()

    cube = cubes.CUBES['AbcCubeAddTeam'](
        web_context,
        task_data('AbcCubeAddTeam'),
        {
            'slug': slug,
            'tvm_manager': None,
            'tvm_ssh_user': [],
            'system_administrator': ['some_group'],
            'developer': False,
            'project_manager': 0,
            'superusers': [],
            'mdb_user': 'some_department',
        },
        [],
        None,
    )

    await cube.update()
    assert cube.success, cube.error


@pytest.mark.parametrize(
    'reference_name, reference_slug, tvm_id',
    [('some name', 'someservice', None), (None, None, '1234')],
)
async def test_abc_cube_request_tvm(
        web_context, abc_mockserver, reference_name, reference_slug, tvm_id,
):
    abc_mockserver(services=True)

    cube = cubes.CUBES['AbcCubeRequestTvm'](
        web_context,
        task_data('AbcCubeRequestTvm'),
        {'slug': reference_slug, 'name': reference_name, 'tvm_id': tvm_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success


@pytest.mark.parametrize(
    'reference_name, reference_slug, tvm_id, expected_tvm_id',
    [
        (
            'tvmtaxiservicewithtvmtesting',
            'tvmtaxiservicewithtvmtesting',
            '',
            '123456',
        ),
        (None, None, '1234', '1234'),
    ],
)
async def test_abc_cube_wait_for_tvm(
        web_context,
        abc_mockserver,
        reference_name,
        reference_slug,
        tvm_id,
        expected_tvm_id,
):
    abc_mockserver(services=True)

    cube = cubes.CUBES['AbcCubeWaitForTvm'](
        web_context,
        task_data('AbcCubeWaitForTvm'),
        {'slug': reference_slug, 'name': reference_name, 'tvm_id': tvm_id},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['tvm_id'] == expected_tvm_id


async def test_abc_cube_stash_tvm_secret(
        web_context,
        abc_mockserver,
        cookie_monster_mockserver,
        yav_mockserver,
        tvm_info_mockserver,
):
    abc_mockserver(services=True)
    cookie_monster_mockserver()
    yav_mockserver()
    tvm_info_mockserver()

    slug = 'tvmtaxiservicewithtvmtesting'

    cube = cubes.CUBES['AbcCubeStashTvmSecret'](
        web_context,
        task_data('AbcCubeStashTvmSecret'),
        {'slug': slug, 'tvm_id': '123456'},
        [],
        None,
    )

    await cube.update()

    assert cube.success
    assert cube.data['payload']['secret_id'] == 'sec-XXX'


async def test_abc_cube_add_responsibles(
        web_context,
        abc_mockserver,
        abc_nonofficial_mockserver,
        cookie_monster_mockserver,
):
    cookie_monster_mockserver()
    abc_nonofficial_mockserver()
    abc_mockserver(services=['someservice'])
    cube = cubes.CUBES['AbcCubeAddResponsibles'](
        web_context,
        task_data('AbcCubeAddResponsibles'),
        {'slug': 'someservice', 'responsibles': ['blah']},
        [],
        None,
    )

    await cube.update()
    assert cube.success


async def test_abc_cube_change_owner(
        web_context,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        add_service,
):
    login_mockserver()
    staff_mockserver()
    service = await add_service('taxi', 'some_service')
    abc_mockserver(services=['someservice'])
    cube = cubes.CUBES['AbcCubeChangeOwner'](
        web_context,
        task_data('AbcCubeCreateService'),
        {'service_id': service['id'], 'slug': 'someservice'},
        [],
        None,
    )

    await cube.update()
    assert cube.success


@pytest.mark.parametrize(
    'employees, fired_employee',
    [(['Peter Parker', 'Clark Kent'], None), (['Clark Kent'], 'Johnny Storm')],
)
async def test_abc_cube_patch_service(
        web_context,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
        add_service,
        employees,
        fired_employee,
):
    login_mockserver()
    staff_mockserver()
    cookie_monster_mockserver()
    abc_nonofficial_mockserver()
    await add_service('taxi', 'some_service')
    abc_mockserver(services=['someservice'], fired_employee=fired_employee)
    if fired_employee:
        employees.append(fired_employee)
    cube = cubes.CUBES['AbcCubeEditService'](
        web_context,
        task_data('AbcCubeCreateService'),
        {
            'slug': 'someservice',
            'name': 'new_service_name',
            'new_team_members': employees,
        },
        [],
        None,
    )
    await cube.update()
    assert cube.success


async def test_logs_for_cubes(caplog, web_context, abc_mockserver):
    log.init_logger(logger_names=['clownductor'])
    caplog.set_level(logging.INFO, logger='clownductor')

    abc_mockserver()
    cube = cubes.CUBES['AbcCubeGenerateServiceName'](
        web_context,
        task_data('AbcCubeGenerateServiceName'),
        {
            'project': 'taxi-infra',
            'service': 'mega_service',
            'st_task': 'TAXIADMIN-100500',
        },
        [],
        None,
    )

    await cube.update()
    assert cube.success

    assert len(caplog.records) == 3
    extdict = {
        'task_id': 123,
        'job_id': 456,
        'tp_task_id': 123,
        'tp_job_id': 456,
        'cube': 'AbcCubeGenerateServiceName',
    }
    msg_prefix = (
        '<AbcCubeGenerateServiceName: id 123, job 456, state in_progress>:'
    )
    expected = [
        ('Updating task', extdict),
        (
            'Generated name '
            'taxi-infra/mega_service '
            'and slug taxiinframegaservice',
            extdict,
        ),
        ('Successfully finished', extdict),
    ]
    for i, (msg, extdict) in enumerate(expected):
        assert caplog.records[i].msg == f'{msg_prefix} {msg}'
        assert caplog.records[i].extdict == extdict


async def test_abc_cube_get_info(
        web_context,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
        add_service,
):
    login_mockserver()
    staff_mockserver()
    await add_service('taxi', 'some_service')
    abc_mockserver(services=['someservice'])
    cube = cubes.CUBES['AbcCubeGetServiceInfo'](
        web_context,
        task_data('AbcCubeGetServiceInfo'),
        {'slug': 'someservice'},
        [],
        None,
    )

    await cube.update()
    assert cube.success
    assert cube.data['payload'] == {
        'description': {'en': '', 'ru': ''},
        'maintainers': ['isharov', 'nikslim'],
        'name': {
            'en': 'TVM for billing_orders service (TAXIADMIN-6231) - testing',
            'ru': 'TVM для сервиса billing_orders (TAXIADMIN-6231) - testing',
        },
    }


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'abc_add_micro_tag': True})
async def test_abc_cube_tag_micro_service(
        web_context,
        abc_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
):
    slug = 'someservice'
    abc_mockserver(services=True)
    cookie_monster_mockserver()
    abc_nonofficial_mockserver()

    cube = cubes.CUBES['AbcCubeTagMicroService'](
        web_context,
        task_data('AbcCubeTagMicroService'),
        {'slug': slug},
        [],
        None,
    )

    await cube.update()

    assert cube.success


@pytest.mark.parametrize(
    'service_slug, parent_slug, expected_move_id',
    [
        ('servicelsug', 'parentslug', 11468),
        ('servicelsug', 'someserviceabcslug', 0),
    ],
)
async def test_abc_cube_change_parent(
        web_context,
        abc_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
        add_service,
        add_project,
        login_mockserver,
        service_slug,
        parent_slug,
        expected_move_id,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()
    await add_project('old_project')
    new_project = await add_project('new_project', service_abc=parent_slug)
    service = await add_service(
        project_name='old_project',
        service_name='test_service',
        abc_service=service_slug,
    )
    abc_mockserver(services=True)
    cookie_monster_mockserver()
    abc_nonofficial_mockserver()

    cube = cubes.CUBES['AbcCubeChangeServiceParent'](
        web_context,
        task_data('AbcCubeChangeServiceParent'),
        {'service_id': service['id'], 'project_id': new_project['id']},
        [],
        None,
    )

    await cube.update()
    assert cube.success
    assert cube.data['payload'] == {'move_id': expected_move_id}


@pytest.mark.parametrize('move_id, ', [1, 0, None])
async def test_abc_cube_wait_change_parent(
        web_context,
        move_id,
        abc_mockserver,
        cookie_monster_mockserver,
        abc_nonofficial_mockserver,
):
    abc_mockserver(services=True)
    cookie_monster_mockserver()
    mock_handler = abc_nonofficial_mockserver()

    cube = cubes.CUBES['AbcCubeWaitChangeServiceParent'](
        web_context,
        task_data('AbcCubeWaitChangeServiceParent'),
        {'move_id': move_id},
        [],
        None,
    )

    await cube.update()
    assert cube.success
    if move_id:
        assert mock_handler.times_called == 1


@pytest.mark.features_on('abc_service_removal')
@pytest.mark.parametrize(
    'success,abc_slug,num_services',
    [
        pytest.param(True, None, 5, id='empty input'),
        pytest.param(
            True,
            'ifindyourlackoffaithdisturbing',
            0,
            id='non-existent slug with no services',
        ),
        pytest.param(
            False,
            'ifindyourlackoffaithdisturbing',
            1,
            id='non-existent slug with 1 service',
        ),
        pytest.param(
            False,
            'ifindyourlackoffaithdisturbing',
            2,
            id='non-existent slug with 2 services',
        ),
        pytest.param(
            False,
            'taxitvmbillingorderstesting',
            2,
            id='correct slug that has more than one service',
        ),
        pytest.param(
            True,
            'taxitvmbillingorderstesting',
            1,
            id='correct slug with only one service',
        ),
    ],
)
async def test_abc_cube_close_service(
        web_context,
        success,
        abc_slug,
        num_services,
        add_service,
        abc_mockserver,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()
    if success and num_services:
        mock_handler = abc_mockserver(services=True)
    else:
        mock_handler = abc_mockserver()

    service_id = None
    service = None

    if abc_slug and num_services:
        for i in range(num_services):
            service = await add_service(
                project_name=f'project_{i}',
                service_name=f'test_service_{i}',
                abc_service=abc_slug,
            )
        service_id = service['id']

    cube = cubes.CUBES['AbcCubeCloseService'](
        web_context,
        task_data('AbcCubeCloseService'),
        {'service_id': service_id},
        [],
        None,
    )

    await cube.update()
    assert cube.success == success

    if abc_slug and service_id and num_services <= 1:
        assert mock_handler.times_called >= 1
        if success:
            assert mock_handler.times_called == 2
    else:
        assert not mock_handler.times_called
