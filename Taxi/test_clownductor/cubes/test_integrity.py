import pytest

from clownductor.internal.tasks import cubes
from clownductor.internal.tasks.cubes import cube


ALL_CUBES = [
    (cube_name, cube_cls) for cube_name, cube_cls in cubes.CUBES.items()
]


class MockCubeDefault(cube.TaskCube):
    @classmethod
    def infinite_retries(cls):
        return False

    @classmethod
    def needed_parameters(cls):
        return []

    async def _update(self, input_data):
        raise Exception()

    def sleep(self, duration):
        self._data['retries'] += 1


class MockCubeRetries(cube.TaskCube):
    @classmethod
    def infinite_retries(cls):
        return False

    @classmethod
    def max_retries(cls):
        return 3

    @classmethod
    def needed_parameters(cls):
        return []

    async def _update(self, input_data):
        raise Exception()

    def sleep(self, duration):
        self._data['retries'] += 1


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


def test_max_retries_count_definition():
    for cube_name, cube_cls in ALL_CUBES:
        infinite_retries = _get_is_inifinite_retries(cube_name, cube_cls)

        if not infinite_retries:
            _check_max_retries(cube_name, cube_cls)


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'use_infinite_retries': True})
async def test_cube_default(web_context):
    cube_default = MockCubeDefault(
        web_context, task_data('MockCubeDefault'), {}, [], None,
    )

    await cube_default.update()
    assert cube_default.status == 'in_progress'

    await cube_default.update()
    assert cube_default.status == 'failed'
    assert (
        cube_default.data['error_message']
        == 'Max retries count was reached: "1"'
    )


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'use_infinite_retries': True})
async def test_cube_retries(web_context):
    good_cube = MockCubeRetries(
        web_context, task_data('MockCubeRetries'), {}, [], None,
    )
    for i in range(3):
        await good_cube.update()
        assert good_cube.status == 'in_progress'
        assert good_cube.data['retries'] == i + 1

    await good_cube.update()
    assert good_cube.status == 'failed'
    assert (
        good_cube.data['error_message'] == 'Max retries count was reached: "3"'
    )


def _check_max_retries(cube_name, cube_cls):
    max_retries = cube_cls.max_retries()
    if max_retries is None:
        raise AssertionError(
            f'You must specify "max_retries" ' f'method in cube "{cube_name}"',
        )
    if max_retries < 1:
        raise AssertionError('"max_retries" must be greater or equal 1')


def _get_is_inifinite_retries(cube_name, cube_cls):
    try:
        is_infinite_rertries = cube_cls.infinite_retries()
    except NotImplementedError:
        raise AssertionError(
            f'You must specify "infinite_retries" '
            f'method in cube "{cube_name}"',
        )
    return is_infinite_rertries
