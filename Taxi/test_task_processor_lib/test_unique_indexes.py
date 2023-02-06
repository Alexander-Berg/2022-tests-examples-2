import pytest

from task_processor_lib import types


async def _cube_caller():
    return


@pytest.fixture
def _default_tp_init_params():
    test_provider = types.Provider(
        name='clown', id=1, cube_caller=_cube_caller,
    )
    test_cube = types.Cube(
        provider=test_provider,
        name='test_cube',
        needed_parameters=[],
        optional_parameters=[],
        output_parameters=[],
        check_input_mappings=False,
        check_output_mappings=False,
    )

    return {
        'providers': [test_provider],
        'cubes': [test_cube],
        'recipes': [],
        'raw_recipes': [
            {
                'name': 'test_recipe',
                'provider_name': test_provider.name,
                'job_vars': [],
                'stages': [
                    {
                        'name': test_cube.name,
                        'input_mapping': {},
                        'output_mapping': {},
                    },
                ],
            },
            {
                'name': 'new_recipe',
                'provider_name': test_provider.name,
                'job_vars': [],
                'stages': [
                    {
                        'name': test_cube.name,
                        'input_mapping': {},
                        'output_mapping': {},
                    },
                ],
            },
        ],
    }


async def add_job(task_processor):
    return await task_processor.start_job(
        'test_recipe',
        {},
        'deoevgen',
        change_doc_id='change_doc_1',
        idempotency_token=None,
    )


async def test_change_doc_id(library_context, task_processor):
    first_job = await add_job(task_processor)
    sec_job = await add_job(task_processor)
    assert first_job is sec_job
    assert len(task_processor.jobs) == 1
    first_job.status = types.Status.canceled
    await add_job(task_processor)
    assert len(task_processor.jobs) == 2
