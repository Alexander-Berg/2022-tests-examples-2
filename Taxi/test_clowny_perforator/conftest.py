# pylint: disable=redefined-outer-name
from typing import Dict
from typing import Type

import pytest

import clowny_perforator.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from clowny_perforator.lib import cubes


pytest_plugins = [
    'clowny_perforator.generated.service.cte_configs.pytest_plugin',
    'clowny_perforator.generated.service.pytest_plugins',
    'plugins.puncher_api.pytest_plugin',
]


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist.update({'CTE_ROBOT_OAUTH': 'cte_robot_oauth'})
    return simple_secdist


class _CheckCubesFixture:
    def __init__(self):
        self._cubes_by_name: Dict[str, Type[cubes.base.Cube]] = {
            x.name(): x for x in cubes.get_all()
        }
        self._cubes_called = {x: 0 for x in self._cubes_by_name.keys()}

    def inc(self, name):
        self._cubes_called[name] += 1

    def check_params(self, name, response):
        cube = self._cubes_by_name[name]
        needed_parameters = set(cube.needed_parameters())
        optional_parameters = set(cube.optional_parameters())
        assert not needed_parameters.intersection(optional_parameters)

        output_parameters = cube.output_parameters()
        if output_parameters and response['status'] == 'success':
            assert set(response['payload'].keys()) == set(output_parameters)
        if not output_parameters:
            assert (
                'payload' not in response
            ), 'payload is not empty, but no output params are specified'


@pytest.fixture(scope='session')
def check_cubes():
    _fixture = _CheckCubesFixture()
    yield _fixture


@pytest.fixture
def get_all_cubes(taxi_clowny_perforator_web):
    async def _do_it():
        response = await taxi_clowny_perforator_web.get(
            '/task-processor/v1/cubes/',
        )
        assert response.status == 200
        return await response.json()

    return _do_it


@pytest.fixture(name='call_cube_client')
def _call_cube_client(taxi_clowny_perforator_web):
    return taxi_clowny_perforator_web
