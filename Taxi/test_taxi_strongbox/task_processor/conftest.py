import pytest

from taxi_strongbox.lib import cubes

from task_processor_lib import (  # noqa: E501,I100 pylint: disable=wrong-import-position
    types as tp_mock_types,
)


@pytest.fixture(scope='session', name='all_cubes')
def _all_cubes():
    return cubes.get_all()


@pytest.fixture(name='call_cube_client')
def _call_cube_client(web_app_client):
    return web_app_client


@pytest.fixture(name='tp_mock')
def _tp_mock(mockserver):
    def _wrapper():
        @mockserver.json_handler('/task-processor/v1/jobs/retrieve/')
        async def _responsibles(request):
            data = request.json
            job_id = data.get('job_id')
            if job_id == 12:
                return {
                    'job_info': {
                        'id': 12,
                        'recipe_id': 13,
                        'name': 'ArcadiaMergeDiffProposalWithPR',
                        'status': 'success',
                        'created_at': 1642948794,
                        'job_vars': {
                            'pull_request_url': 'mocked_pull_request_url',
                        },
                    },
                    'tasks': [],
                }
            return {
                'job_info': {
                    'id': 11,
                    'recipe_id': 12,
                    'name': 'SecretsAutoMerge',
                    'status': 'success',
                    'created_at': 1642948794,
                    'job_vars': {'merge_sha': 'test_merge_sha'},
                },
                'tasks': [],
            }

        return _responsibles

    return _wrapper


@pytest.fixture
def _external_raw_recipes():
    return [
        {
            'name': 'ArcadiaMergeDiffProposalWithPR',
            'provider_name': 'clownductor',
            'job_vars': ['diff_proposal', 'st_ticket', 'automerge'],
            'stages': [],
        },
        {
            'name': 'GithubMergeDiffProposalWithPR',
            'provider_name': 'clownductor',
            'job_vars': ['diff_proposal', 'st_ticket', 'automerge'],
            'stages': [],
        },
    ]


@pytest.fixture(name='external_call_cube')
def _external_call_cube(mockserver, call_cube_client):
    async def _do_it(cube, stage, request_data):
        if cube.name == 'MetaStartDiffProposalWithPR':
            return mockserver.make_response(
                json={'status': 'success', 'payload': {'job_id': 1}},
            )
        if cube.name == 'MetaCubeWaitForJobCommon':
            return mockserver.make_response(json={'status': 'success'})

        return mockserver.make_response(
            json={**request_data, 'status': 'success'},
        )

    return _do_it


@pytest.fixture
async def _default_tp_init_params(
        external_call_cube, _external_raw_recipes, raw_call_cube,
):
    async def self_cube_caller(cube, stage, request_data):
        return await raw_call_cube(name=cube.name, **request_data)

    clown = tp_mock_types.Provider(
        name='clownductor', id=1, cube_caller=external_call_cube,
    )
    strongbox = tp_mock_types.Provider(
        name='taxi-strongbox', id=2, cube_caller=self_cube_caller,
    )

    clown_cubes = [
        tp_mock_types.Cube(
            provider=clown,
            name='MetaCubeWaitForJobCompletion',
            needed_parameters=[],
            optional_parameters=['job_id'],
            output_parameters=[],
        ),
        tp_mock_types.Cube(
            provider=clown,
            name='MetaStartDiffProposalWithPR',
            needed_parameters=['st_ticket'],
            optional_parameters=[
                'diff_proposal',
                'automerge',
                'initiator',
                'reviewers',
                'approve_required',
                'with_pr',
            ],
            output_parameters=['job_id'],
        ),
    ]

    return {
        'providers': [clown, strongbox],
        'cubes': [
            tp_mock_types.Cube(
                provider=strongbox,
                name=name,
                needed_parameters=cube.needed_parameters(),
                optional_parameters=(
                    cube.optional_parameters()
                    if hasattr(cube, 'optional_parameters')
                    else []
                ),
                output_parameters=(
                    cube.output_parameters()
                    if hasattr(cube, 'output_parameters')
                    else []
                ),
                check_input_mappings=True,
                check_output_mappings=True,
            )
            for name, cube in cubes.CUBES.items()
        ] + clown_cubes,
        'recipes': [],
        'raw_recipes': _external_raw_recipes,
    }
