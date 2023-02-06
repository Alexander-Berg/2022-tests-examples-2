from typing import Optional

import pytest

import dashboards.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['dashboards.generated.service.pytest_plugins']

from task_processor_lib import (  # noqa: E501,I100 pylint: disable=C0413
    types as tp_mock_types,
)


@pytest.fixture(name='clown_cube_caller')
def _clown_cube_caller(mockserver):
    async def _do_it(cube, stage, request_data):
        if cube.name == 'StartGithubMergeDiffProposalWithoutPR':
            return mockserver.make_response(
                json={'status': 'success', 'payload': {'job_id': 15}},
            )
        if cube.name == 'MetaCubeWaitForJobCommon':
            return mockserver.make_response(json={'status': 'success'})

        return mockserver.make_response(
            json={**request_data, 'status': 'success'},
        )

    return _do_it


@pytest.fixture
async def _default_tp_init_params(
        get_all_cubes, raw_call_cube, clown_cube_caller,
):
    clown = tp_mock_types.Provider(
        name='clownductor', id=1, cube_caller=clown_cube_caller,
    )

    async def self_cube_caller(cube, stage, request_data):
        return await raw_call_cube(name=cube.name, **request_data)

    provider = tp_mock_types.Provider(
        name='dashboards', id=3, cube_caller=self_cube_caller,
    )

    return {
        'providers': [clown, provider],
        'cubes': [
            *(
                tp_mock_types.Cube(
                    provider=provider,
                    check_input_mappings=True,
                    check_output_mappings=True,
                    **x,
                )
                for x in (await get_all_cubes())['cubes']
            ),
            tp_mock_types.Cube(
                provider=clown,
                name='StartGithubMergeDiffProposalWithoutPR',
                needed_parameters=['diff_proposal'],
                optional_parameters=['st_ticket'],
                output_parameters=['job_id'],
                check_input_mappings=True,
                check_output_mappings=True,
            ),
            tp_mock_types.Cube(
                provider=clown,
                name='MetaCubeWaitForJobCommon',
                needed_parameters=['job_id'],
                optional_parameters=[],
                output_parameters=[],
                check_input_mappings=True,
                check_output_mappings=True,
            ),
        ],
        'recipes': [],
        'raw_recipes': [],
    }


@pytest.fixture
def get_dashboard_configs_count(web_context):
    async def _wrapper(
            service_branch_id: int, dashboard_name: Optional[str] = None,
    ):
        query, args = web_context.sqlt.service_branches_fetch_all_configs(
            service_branch_id=service_branch_id,
            dashboard_name=dashboard_name,
            status=None,
        )
        rows = await web_context.pg.primary.fetch(query, *args)
        return len(rows)

    return _wrapper


@pytest.fixture(name='config_service_overrides', scope='session')
def _config_service_overrides():
    return {
        'DASHBOARDS_RUN_APPLY_CONFIGS_SETTINGS': {
            'max_apply_number': 10,
            'process_config_sleep_ms': 0,
        },
        'DASHBOARDS_UPLOAD_CONFIGS_TO_REPO': {
            'github_vendor': {
                'enabled': False,
                'user': 'taxi',
                'repo': 'infra-cfg-graphs',
                'max_files_for_one_job': 20,
            },
            'arcadia_vendor': {
                'enabled': True,
                'user': 'arcadia',
                'repo': 'taxi/infra-cfg-graphs',
                'max_files_for_one_job': 50,
            },
        },
        'DASHBOARDS_FEATURES': {
            '__default__': {
                'generate_from_arc': False,
                'skip_equal_configs_merge': True,
                'sync_arc_local_cache': True,
                'sync_git_local_cache': True,
                'upload_dashboard_from_config': False,
            },
        },
    }


@pytest.fixture(name='config_service_defaults', scope='session')
def _config_service_defaults(
        config_service_defaults, config_service_overrides,
):
    defaults = {**config_service_defaults}
    defaults.update(config_service_overrides)
    return defaults
