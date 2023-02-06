import pytest


async def test_get_cubes(get_all_cubes):
    response = await get_all_cubes()
    assert response == {
        'cubes': [
            {
                'name': 'ChangeProjectForService',
                'needed_parameters': ['new_project_id', 'service_id'],
                'optional_parameters': [],
                'output_parameters': [],
            },
            {
                'name': 'Dummy',
                'needed_parameters': ['name'],
                'optional_parameters': [],
                'output_parameters': ['message'],
            },
            {
                'name': 'FindServiceForClown',
                'needed_parameters': ['clowny_service_id'],
                'optional_parameters': [],
                'output_parameters': ['service_id'],
            },
        ],
    }


async def test_cube_dummy(raw_call_cube):
    response = await raw_call_cube('Dummy', {'name': 'd1mbas'})
    data = await response.json()
    assert data['payload'] == {'message': 'Hello d1mbas'}


@pytest.mark.parametrize(
    'service_id, project_id, updated_cnt',
    [(1, 27, 3), (123, 27, 1), (666, 1, 0)],
)
@pytest.mark.pgsql('clowny_perforator', files=['test_cubes.sql'])
async def test_cube_change_project(
        raw_call_cube, web_context, service_id, project_id, updated_cnt,
):
    await raw_call_cube(
        'ChangeProjectForService',
        {'service_id': service_id, 'new_project_id': project_id},
    )

    result = await web_context.pg.primary.fetch(
        f"""
        SELECT *
        FROM perforator.services
        WHERE clown_id = {service_id} AND project_id = {project_id}
        """,
    )

    assert len(result) == updated_cnt


@pytest.mark.pgsql('clowny_perforator', files=['test_cubes.sql'])
async def test_cube_find_service(call_cube):
    data = await call_cube('FindServiceForClown', {'clowny_service_id': 123})
    assert data['payload'] == {'service_id': 1}


@pytest.mark.parametrize(
    'clowny_service_id, err_message',
    [
        (1, 'found to many 3 internal services clown_id 1'),
        (100500, 'failed to find internal service for clown_id 100500'),
    ],
)
@pytest.mark.pgsql('clowny_perforator', files=['test_cubes.sql'])
async def test_cube_find_service_fail(
        call_cube, clowny_service_id, err_message,
):
    data = await call_cube(
        'FindServiceForClown', {'clowny_service_id': clowny_service_id},
    )
    assert data['status'] == 'failed'
    assert data['error_message'] == err_message
