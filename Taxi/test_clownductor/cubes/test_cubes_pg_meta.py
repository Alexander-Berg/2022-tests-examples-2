from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres


def task_data(name='name'):
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


async def test_create_branches(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
        patch,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'CreatePostgresBranch' in text

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    project = await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateDBBranches'](
            web_context,
            task_data(),
            {
                'project_id': project['id'],
                'service_id': service['id'],
                'db_type': 'pgaas',
                'flavor_name': 's2.nano',
                'needs_unstable': False,
                'disk_size_gb': 10,
                'testing_disk_size_gb': 20,
                'new_service_ticket': 'TAXIADMIN-1',
            },
            [],
            conn,
        )

        await cube.update()

    assert cube.success
    assert len(create_comment.calls) == 1
    assert len(cube.data['payload']['job_ids']) == 2


async def test_create_branches_with_unstable(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
        patch,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'CreatePostgresBranch' in text

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    project = await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateDBBranches'](
            web_context,
            task_data(),
            {
                'project_id': project['id'],
                'service_id': service['id'],
                'db_type': 'pgaas',
                'flavor_name': 's2.nano',
                'needs_unstable': True,
                'disk_size_gb': 10,
                'testing_disk_size_gb': 20,
                'new_service_ticket': 'TAXIADMIN-1',
                'db_version': '11',
            },
            [],
            conn,
        )

        await cube.update()

    assert cube.success
    assert len(create_comment.calls) == 1
    assert len(cube.data['payload']['job_ids']) == 3


async def test_create_full_db_skip(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
):
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateFullDatabase'](
            web_context,
            task_data(),
            {
                'requester_service_id': service['id'],
                'skip': True,
                'needs_unstable': None,
                'database': None,
                'new_service_ticket': None,
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success


async def test_create_full_db(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
):
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateFullDatabase'](
            web_context,
            task_data(),
            {
                'requester_service_id': service['id'],
                'skip': False,
                'needs_unstable': False,
                'database': {
                    'db_name': 'some_db',
                    'db_type': 'pgaas',
                    'db_flavor': 's2.nano',
                    'db_disk_size_gb': 10,
                    'db_testing_disk_size_gb': 10,
                },
                'db_version': '11',
                'new_service_ticket': 'TAXIADMIN-1',
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success


async def test_create_db(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
):
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service('taxi', 'some-service')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateDBService'](
            web_context,
            task_data(),
            {'service_id': service['id'], 'db_type': 'pgaas', 'user': None},
            [],
            conn,
        )

        await cube.update()
        assert cube.success
