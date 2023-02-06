import pytest

from clownductor.internal.tasks.cubes import cube


PROVIDERS = {
    '__default__': {
        'cubes': {
            '__default__': {
                'min_retries_amount': 1,
                'max_sleep_duration_sec': 1,
            },
            'CubeTest': {'min_retries_amount': 1, 'max_sleep_duration_sec': 1},
        },
    },
    'clownductor': {
        'cubes': {
            '__default__': {
                'min_retries_amount': 2,
                'max_sleep_duration_sec': 2,
            },
            'CubeTestWithMaxRetries': {
                'min_retries_amount': 4,
                'max_sleep_duration_sec': 40,
            },
            'CubeTest': {
                'min_retries_amount': 5,
                'max_sleep_duration_sec': 50,
            },
        },
    },
}


class CubeTestWithMaxRetries(cube.TaskCube):
    @classmethod
    def infinite_retries(cls):
        return False

    @classmethod
    def needed_parameters(cls):
        return []

    @classmethod
    def max_retries(cls):
        return 10

    @classmethod
    def fail_on_max_retries(cls) -> bool:
        return False

    async def _update(self, input_data):
        self.sleep(10)
        self._data['sleep_until'] = 0


class CubeTest(cube.TaskCube):
    @classmethod
    def infinite_retries(cls):
        return True

    @classmethod
    def needed_parameters(cls):
        return []

    async def _update(self, input_data):
        self.sleep(10)
        self._data['sleep_until'] = 0


class CubeTestWithError(cube.TaskCube):
    @classmethod
    def infinite_retries(cls):
        return True

    @classmethod
    def needed_parameters(cls):
        return []

    async def _update(self, input_data):
        raise Exception()


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


@pytest.mark.config(
    TASK_PROCESSOR_CUBES_INC_SLEEP={'enabled': True, 'providers': PROVIDERS},
    CLOWNDUCTOR_FEATURES={'use_infinite_retries': True},
)
async def test_inc_sleep_on_max_retries(web_context):
    cube_test = CubeTestWithMaxRetries(
        web_context, task_data('CubeTestWithMaxRetries'), {}, [], None,
    )
    durations = [10, 10, 10, 10, 10, 11, 12, 13, 14, 15]
    await _test_durations(cube_test, durations)

    await cube_test.update()
    assert cube_test.success


@pytest.mark.config(
    TASK_PROCESSOR_CUBES_INC_SLEEP={'enabled': True, 'providers': PROVIDERS},
    CLOWNDUCTOR_FEATURES={'use_infinite_retries': True},
)
async def test_inc_sleep_on(web_context):
    cube_test = CubeTest(web_context, task_data('CubeTest'), {}, [], None)
    durations = [10, 10, 10, 10, 10, 10]
    sleep = 10
    while len(durations) < 100:
        if sleep < 50:
            sleep += 1
        durations.append(sleep)
    await _test_durations(cube_test, durations)


@pytest.mark.config(
    TASK_PROCESSOR_CUBES_INC_SLEEP={'enabled': False, 'providers': PROVIDERS},
    CLOWNDUCTOR_FEATURES={'use_infinite_retries': True},
)
async def test_error_inc_retries(web_context):
    cube_test = CubeTestWithError(
        web_context, task_data('CubeTestWithError'), {}, [], None,
    )
    await cube_test.update()
    assert cube_test.sleep_duration == 10
    assert cube_test.data['retries'] == 1


async def _test_durations(cube_test, durations):
    for retry, duration in enumerate(durations):
        await cube_test.update()
        assert cube_test.sleep_duration == duration
        assert cube_test.status == 'in_progress'
        assert cube_test.data['retries'] == retry + 1
