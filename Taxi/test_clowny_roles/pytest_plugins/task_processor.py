from typing import List
from typing import Type

import pytest

from task_processor_lib import types as tp_mock_types

from clowny_roles.internal import cubes


@pytest.fixture(name='all_cubes', scope='session')
def _all_cubes() -> List[Type[cubes.Cube]]:
    return cubes.get_all()


@pytest.fixture(name='call_cube_client')
def _call_cube_client(taxi_clowny_roles_web):
    return taxi_clowny_roles_web


@pytest.fixture(name='clown_cube_caller')
def _clown_cube_caller(mockserver):
    async def _do_it(cube, stage, request_data):
        return mockserver.make_response(
            json={**request_data, 'status': 'success'},
        )

    return _do_it


@pytest.fixture
def _default_tp_init_params(
        mockserver, call_cube, all_cubes, clown_cube_caller,
):
    async def self_cube_caller(cube, stage, request_data):
        return mockserver.make_response(
            json=await call_cube(name=cube.name, **request_data),
        )

    provider = tp_mock_types.Provider(
        name=cubes.PROVIDER_NAME, id=69, cube_caller=self_cube_caller,
    )
    clown_provider = tp_mock_types.Provider(
        name='clownductor', id=1, cube_caller=clown_cube_caller,
    )

    return {
        'providers': [provider, clown_provider],
        'cubes': [
            *(
                tp_mock_types.Cube(
                    provider=provider,
                    name=cube.name(),
                    needed_parameters=cube.needed_parameters(),
                    optional_parameters=cube.optional_parameters(),
                    output_parameters=cube.output_parameters(),
                )
                for cube in all_cubes
            ),
            tp_mock_types.Cube(
                provider=clown_provider,
                name='PermissionsAddNodesForService',
                needed_parameters=['service_id'],
            ),
            tp_mock_types.Cube(
                provider=clown_provider,
                name='PermissionsRequestRolesForNewService',
                needed_parameters=['service_id'],
            ),
        ],
        'recipes': [],
        'raw_recipes': [],
    }
