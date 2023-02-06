import pytest

from clownductor.internal.tasks import cubes


@pytest.fixture(name='get_cube')
def _get_cube(web_context, task_data):
    def _wrapper(name, body):
        return cubes.CUBES[name](web_context, task_data(name), body, [], None)

    return _wrapper
