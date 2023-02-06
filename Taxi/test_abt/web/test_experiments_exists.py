import pytest

from test_abt import consts
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'get', '/v1/experiments/exists', taxi_abt_web,
    )


@pytest.mark.parametrize('experiment_type', ['experiment', 'config', None])
async def test_get_success(taxi_abt_web, abt, invoke_handler, experiment_type):
    params = {'name': consts.DEFAULT_EXPERIMENT_NAME}
    if experiment_type:
        params.update({'type': experiment_type})

    got = await invoke_handler(params=params)
    assert got['exists'] is False

    await abt.state.add_experiment(
        experiment_type=experiment_type or 'experiment',
    )

    got = await invoke_handler(params=params)
    assert got['exists'] is True
