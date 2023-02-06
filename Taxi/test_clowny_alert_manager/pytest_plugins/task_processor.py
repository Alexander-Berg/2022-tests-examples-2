from typing import List
from typing import Type

import pytest

from task_processor_lib import types as tp_mock_types

from clowny_alert_manager import cubes


@pytest.fixture(name='clown_cube_caller')
def _clown_cube_caller(mockserver):
    async def _do_it(cube, stage, request_data):
        return mockserver.make_response(
            json={**request_data, 'status': 'success'},
        )

    return _do_it


@pytest.fixture(name='all_cubes', scope='session')
def _all_cubes() -> List[Type[cubes.Cube]]:
    return cubes.get_all()


@pytest.fixture(name='call_cube_client')
def _call_cube_client(taxi_clowny_alert_manager_web):
    return taxi_clowny_alert_manager_web


@pytest.fixture
async def _default_tp_init_params(
        mockserver, call_cube, all_cubes, clown_cube_caller,
):
    async def self_cube_caller(cube, stage, request_data):
        return mockserver.make_response(
            json=await call_cube(name=cube.name, **request_data),
        )

    provider = tp_mock_types.Provider(
        name='clowny-alert-manager', id=69, cube_caller=self_cube_caller,
    )
    clown = tp_mock_types.Provider(
        name='clownductor', id=1, cube_caller=clown_cube_caller,
    )
    return {
        'providers': [clown, provider],
        'cubes': [
            *(
                tp_mock_types.Cube(
                    provider=provider,
                    name=x.name(),
                    needed_parameters=x.needed_parameters(),
                    optional_parameters=x.optional_parameters(),
                    output_parameters=x.output_parameters(),
                )
                for x in all_cubes
            ),
            tp_mock_types.Cube(
                provider=clown,
                name='StartGithubMergeDiffProposalWithoutPR',
                needed_parameters=['diff_proposal'],
                optional_parameters=['st_ticket', 'initiator'],
                output_parameters=['job_id'],
            ),
            tp_mock_types.Cube(
                provider=clown,
                name='MetaCubeWaitForJobCommon',
                needed_parameters=['job_id'],
                optional_parameters=['wait_delay'],
                output_parameters=[],
            ),
        ],
        'recipes': [],
        'raw_recipes': [],
    }
