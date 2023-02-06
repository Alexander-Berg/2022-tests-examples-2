import pytest


@pytest.mark.usefixtures('clown_cube_caller')
async def test_recipe(
        load_yaml,
        task_processor,
        run_job_common,
        mockserver,
        mock_clownductor,
):

    task_processor.load_recipe(load_yaml('CreateAwacsBalancer.yaml')['data'])
