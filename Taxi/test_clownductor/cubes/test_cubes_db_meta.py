import pytest

from clownductor.internal import services as services_module
from clownductor.internal.db import db_types
from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres

CLUSTER_TYPE_MAP = {
    db_types.DbType.Postgres: services_module.ClusterType.POSTGRES,
    db_types.DbType.Mongo: services_module.ClusterType.MONGO_MDB,
    db_types.DbType.Redis: services_module.ClusterType.REDIS_MDB,
}


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
        'user': 'elrusso',
    }


@pytest.mark.parametrize(
    'db_type, create_branch_job',
    [
        (db_types.DbType.Postgres, 'CreatePostgresBranch'),
        (db_types.DbType.Mongo, 'CreateDBBranch'),
        (db_types.DbType.Redis, 'CreateDBBranch'),
    ],
)
@pytest.mark.parametrize('needs_unstable, job_count', [(True, 3), (False, 2)])
async def test_create_branches(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
        patch,
        db_type,
        needs_unstable,
        job_count,
        create_branch_job,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert create_branch_job in text

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    project = await add_project('taxi')
    service = await add_service(
        'taxi', 'some-service', type_=CLUSTER_TYPE_MAP[db_type].value,
    )

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateDBBranches'](
            web_context,
            task_data(),
            {
                'project_id': project['id'],
                'service_id': service['id'],
                'db_type': db_type.value,
                'flavor_name': 's2.nano',
                'needs_unstable': needs_unstable,
                'disk_size_gb': 10,
                'testing_disk_size_gb': 20,
                'new_service_ticket': 'TAXIADMIN-1',
                'user': 'elrusso',
            },
            [],
            conn,
        )

        await cube.update()

    assert cube.success
    assert len(create_comment.calls) == 1
    assert len(cube.data['payload']['job_ids']) == job_count


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


@pytest.mark.parametrize(
    'db_type',
    [db_types.DbType.Postgres, db_types.DbType.Mongo, db_types.DbType.Redis],
)
async def test_create_full_db(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
        db_type,
):
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service(
        'taxi', 'some-service', type_=CLUSTER_TYPE_MAP[db_type].value,
    )

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
                    'db_type': db_type.value,
                    'db_flavor': 's2.nano',
                    'db_disk_size_gb': 10,
                    'db_testing_disk_size_gb': 10,
                },
                'new_service_ticket': 'TAXIADMIN-1',
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success


@pytest.mark.parametrize('new_service_ticket', ['TAXIADMIN-1', None])
@pytest.mark.parametrize(
    'db_type, create_service_job',
    [
        (db_types.DbType.Postgres, 'CreatePostgresService'),
        (db_types.DbType.Mongo, 'CreateDBService'),
        (db_types.DbType.Redis, 'CreateDBService'),
    ],
)
async def test_create_db(
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        web_context,
        patch,
        db_type,
        create_service_job,
        new_service_ticket,
):
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service(
        'taxi', 'some-service', type_=CLUSTER_TYPE_MAP[db_type].value,
    )

    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text):
        assert ticket == new_service_ticket
        assert create_service_job in text

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateDBService'](
            web_context,
            task_data(),
            {
                'service_id': service['id'],
                'db_type': db_type.value,
                'user': None,
                'new_service_ticket': new_service_ticket,
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success

    assert len(_create_comment.calls) == (1 if new_service_ticket else 0)
