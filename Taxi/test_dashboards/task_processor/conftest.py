import pytest

from dashboards.lib import cubes


@pytest.fixture(scope='session', name='all_cubes')
def _all_cubes():
    return cubes.get_all()


@pytest.fixture(name='call_cube_client')
def _call_cube_client(taxi_dashboards_web):
    return taxi_dashboards_web
