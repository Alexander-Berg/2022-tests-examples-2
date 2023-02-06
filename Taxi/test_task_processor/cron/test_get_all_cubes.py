from aiohttp import web
import pytest

from task_processor.internal import models

TEST_CUBE = models.Cube(
    name='testCube',
    provider_id=1,
    needed_parameters=['test'],
    optional_parameters=['optional'],
    output_parameters=['output_parameter'],
    id_=1,
)
TEST_NO_OPTIONAL_CUBE = models.Cube(
    name='CubeNoOptional',
    provider_id=1,
    needed_parameters=['test', 'token'],
    id_=2,
)
TEST_EMPTY_CUBE = models.Cube(name='EmptyCube', provider_id=1, id_=3)


@pytest.mark.parametrize(
    'data_mock, provider_id, expected_cubes, provider_status',
    [
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
            ],
            1,
            [TEST_CUBE],
            200,
        ),
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
                {
                    'name': 'CubeNoOptional',
                    'needed_parameters': ['test', 'token'],
                },
                {'name': 'EmptyCube'},
            ],
            1,
            [TEST_CUBE, TEST_NO_OPTIONAL_CUBE, TEST_EMPTY_CUBE],
            200,
        ),
        ([], 1, [], 200),
        ([], 1, [], 400),
        ([], 1, [], 500),
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
            ],
            1,
            [],
            200,
        ),
        # update cubes
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
                {
                    'name': 'CubeNoOptional',
                    'needed_parameters': ['test', 'token'],
                },
            ],
            2,
            [TEST_CUBE, TEST_NO_OPTIONAL_CUBE],
            200,
        ),
        # 2 update, 1 add
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
                {
                    'name': 'CubeNoOptional',
                    'needed_parameters': ['test', 'token'],
                },
                {'name': 'EmptyCube'},
            ],
            2,
            [TEST_CUBE, TEST_NO_OPTIONAL_CUBE, TEST_EMPTY_CUBE],
            200,
        ),
        # 1 update, 1 invalid
        (
            [
                {
                    'name': 'testCube',
                    'needed_parameters': ['test'],
                    'optional_parameters': ['optional'],
                    'output_parameters': ['output_parameter'],
                },
            ],
            2,
            [
                TEST_CUBE,
                models.Cube(
                    'CubeNoOptional',
                    2,
                    needed_parameters=['token'],
                    invalid=True,
                    id_=1,
                ),
            ],
            200,
        ),
        # all invali
        (
            [],
            2,
            [
                models.Cube(
                    name='testCube',
                    provider_id=1,
                    needed_parameters=['service_id', 'job_id'],
                    optional_parameters=['env', 'ticket'],
                    invalid=True,
                    id_=1,
                ),
                models.Cube(
                    'CubeNoOptional',
                    2,
                    needed_parameters=['token'],
                    invalid=True,
                    id_=1,
                ),
            ],
            200,
        ),
        pytest.param(
            [
                {
                    'name': 'Some',
                    'provider_id': 1,
                    'needed_parameters': ['var1', 'var2'],
                },
                {
                    'name': 'Another',
                    'provider_id': 1,
                    'needed_parameters': ['var1', 'var2'],
                },
            ],
            1,
            [
                models.Cube(
                    name='Some',
                    provider_id=1,
                    needed_parameters=['var1', 'var2'],
                    id_=1,
                ),
                models.Cube(
                    name='Another',
                    provider_id=1,
                    needed_parameters=['var1', 'var2'],
                    id_=1,
                ),
            ],
            200,
            id='cubes with same params',
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'task-processor', 'dst': 'clownductor'}],
    CRON_GET_ALL_CUBES_ENABLED=True,
)
@pytest.mark.pgsql('task_processor', files=['test_add_cubes.sql'])
async def test_cubes_add(
        cron_runner,
        mock_provider_client,
        get_cubes_by_provider_id,
        data_mock,
        provider_id,
        expected_cubes,
        provider_status,
):
    @mock_provider_client('/task-processor/v1/cubes/')
    # pylint: disable=unused-variable
    async def handler(request):
        return web.json_response({'cubes': data_mock}, status=provider_status)

    await cron_runner.get_all_cubes()

    local_cubes = await get_cubes_by_provider_id(provider_id)
    data_cubes_exp = {}
    for expected_cube in expected_cubes:
        data_cubes_exp[expected_cube.name] = expected_cube

    if expected_cubes:
        assert local_cubes, expected_cubes
    for local_cube in local_cubes:
        expected_cube = data_cubes_exp.pop(local_cube.name)
        assert local_cube == expected_cube
