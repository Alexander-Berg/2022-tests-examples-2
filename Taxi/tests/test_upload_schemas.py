import dataclasses
from typing import Any
from typing import Dict
from typing import List
from typing import Sequence
from typing import Tuple

import pytest
import yaml

import arc_checkout
from taxi_buildagent.tools.vcs import arc_repo
from tests.utils import pytest_wraps
from tests.utils.examples import arcadia
import update_config_schemas

DEFINITIONS_PATH = 'schemas/configs/definitions/'
DECLARATIONS_PATH = 'schemas/configs/declarations/'

DEFINITION_YAML = 'definitions/test_definition.yaml'
DECLARATION_YAML = 'abt/TEST_DECLARATION.yaml'

DEFINITION = {
    'Value': {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'value': {'type': 'string'}},
    },
}


SCHEMA = {
    'description': 'Settings for client',
    'default': {'value': '123'},
    'maintainers': ['szmship'],
    'tags': ['notfallback'],
    'schema': {
        'type': 'object',
        'additionalProperties': False,
        'properties': {'value': {'type': 'string'}},
    },
}


@dataclasses.dataclass
class ArcadiaCommit:
    message: str
    data: Sequence[Tuple[str, Dict]]  # path to file and schema


@dataclasses.dataclass
class Params(pytest_wraps.Params):
    commits: Sequence[ArcadiaCommit]
    expected_history: str
    mock_configs_admin_data: List[str]
    ignore_schemas: List[str] = dataclasses.field(default_factory=list)
    update_only_group_schemas: List[str] = dataclasses.field(
        default_factory=list,
    )
    tc_report_problems_calls: Sequence[Dict[str, Any]] = dataclasses.field(
        default_factory=list,
    )
    tc_report_test_problems_calls: Sequence[
        Dict[str, Any]
    ] = dataclasses.field(default_factory=list)
    configs_admin_token: str = 'cool-token'


@pytest.mark.arc
@pytest_wraps.parametrize(
    [
        Params(
            pytest_id='success_only_definitions_in_taxi_schemas',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__definitions_only.json',
            ],
            expected_history='history_success_only_definitions.json',
        ),
        Params(
            pytest_id='success_only_definitions_in_psp_schemas',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'psp/platform/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__definitions_only.json',
            ],
            expected_history='history_success_only_definitions.json',
        ),
        Params(
            pytest_id='success_only_schemas_from_taxi',
            commits=[
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__empty_definitions.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_only_schemas.json',
        ),
        Params(
            pytest_id='ignore_schemas',
            ignore_schemas=[
                'ONE_MORE_TEST_DECLARATION',
                'ANOTHER_TEST_DECLARATION',
            ],
            commits=[
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}'
                            f'abt/ONE_MORE_TEST_DECLARATION.yaml',
                            SCHEMA,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}'
                            f'abt/ANOTHER_TEST_DECLARATION.yaml',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__empty_definitions.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_only_schemas.json',
        ),
        Params(
            pytest_id='update_only_group_schemas',
            update_only_group_schemas=['abt'],
            commits=[
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}'
                            f'aaa/ONE_MORE_TEST_DECLARATION.yaml',
                            SCHEMA,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}'
                            f'aaa/ANOTHER_TEST_DECLARATION.yaml',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__empty_definitions.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_only_schemas.json',
        ),
        Params(
            pytest_id='group_name_with_dot',
            commits=[
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}'
                            f'add/subdir/TEST_DECLARATION.yaml',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__empty_definitions.json',
                'mock_configs_admin__group_name_with_dot.json',
            ],
            expected_history='history_success_schemas_with_dot_in_name.json',
        ),
        Params(
            pytest_id='success_only_schemas_from_psp',
            commits=[
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'psp/platform/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__empty_definitions.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_only_schemas.json',
        ),
        Params(
            pytest_id='success_definitions_and_schemas',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__definitions_only.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_definitions_and_schemas.json',
        ),
        Params(
            pytest_id='success_definitions_and_schemas_psp',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'psp/platform/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'psp/platform/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__definitions_only.json',
                'mock_configs_admin__schemas_only.json',
            ],
            expected_history='history_success_definitions_and_schemas.json',
        ),
        Params(
            pytest_id='definitions_and_schemas__fail_definitions',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__failed_definitions.json',
            ],
            expected_history=(
                'history_definitions_and_schemas__fail_definitions.json'
            ),
            tc_report_problems_calls=[
                {
                    'description': 'Error while sending definitions: error',
                    'identity': (
                        'definitions: [\'definitions/test_definition.yaml\']'
                    ),
                },
            ],
        ),
        Params(
            pytest_id='definitions_and_schemas__fail_schemas',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            mock_configs_admin_data=[
                'mock_configs_admin__definitions_only.json',
                'mock_configs_admin__failed_schemas.json',
            ],
            expected_history=(
                'history_definitions_and_schemas__fail_schemas.json'
            ),
            tc_report_problems_calls=[
                {
                    'description': (
                        'Some schemas were sent successfully but 1 '
                        'errors occurred. '
                        'See details below.'
                    ),
                    'identity': 'Schemas upload partially succeeded',
                },
            ],
            tc_report_test_problems_calls=[
                {
                    'problem_message': 'Error while updating group abt: error',
                    'test_name': 'Uploading schemas of group abt failed',
                },
            ],
        ),
        Params(
            pytest_id='fail_by_bad_apikey',
            configs_admin_token='bad-token',
            commits=[
                ArcadiaCommit(
                    message='cc schemas.definitions: add definition',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DEFINITIONS_PATH}{DEFINITION_YAML}',
                            DEFINITION,
                        ),
                    ],
                ),
                ArcadiaCommit(
                    message='cc schemas: add Schema',
                    data=[
                        (
                            f'taxi/schemas/'
                            f'{DECLARATIONS_PATH}{DECLARATION_YAML}',
                            SCHEMA,
                        ),
                    ],
                ),
            ],
            expected_history='history_bad_apikey.json',
            mock_configs_admin_data=[],
            tc_report_problems_calls=[
                {
                    'description': 'Error while sending definitions: error',
                    'identity': (
                        'definitions: [\'definitions/test_definition.yaml\']'
                    ),
                },
            ],
        ),
    ],
)
def test_upload_schemas(
        params: Params,
        tmp_path,
        monkeypatch,
        arcadia_builder,
        configs_admin_mock,
        load_json,
        teamcity_report_problems,
        teamcity_report_test_problem,
):
    arcadia_path = tmp_path / 'arcadia'
    arcadia_path.mkdir()
    monkeypatch.chdir(arcadia_path)

    monkeypatch.setenv('ARCADIA_TOKEN', 'cool-token')
    monkeypatch.setenv('CONFIGS_ADMIN_TOKEN', params.configs_admin_token)
    monkeypatch.setenv('ARC_STORE_PATH', str(arcadia_path))
    monkeypatch.setattr(
        'taxi_buildagent.clients.configs_admin.API_URL',
        'http://configs-admin.taxi.yandex.net',
    )

    with arcadia_builder:
        arcadia.init_arcadia_base(arcadia_builder)

    arc_checkout.main([str(arcadia_path), '--branch', 'trunk'])
    repo = arc_repo.Repo(arcadia_path, from_root=True)
    master_branch = repo.stable_branch_prefix + 'schemas/configs'
    repo.checkout_new_branch(master_branch, 'trunk')

    # fill branch
    for commit in params.commits:
        for file_path, data in commit.data:
            full_file_path = arcadia_path / file_path
            full_file_path.parent.mkdir(parents=True, exist_ok=True)
            full_file_path.write_text(yaml.dump(data))
        repo.add_paths_to_index(['.'])
        repo.commit(commit.message)
    repo.arc.push('--force', '--set-upstream', master_branch)

    repo.checkout(master_branch)

    # fill mock
    for file_name in params.mock_configs_admin_data:
        configs_admin_mock.update_from_json(load_json(file_name))
    cmd = ['--branch', master_branch]

    if params.ignore_schemas:
        cmd.append('--ignore-schemas')
        cmd.extend(params.ignore_schemas)

    if params.update_only_group_schemas:
        cmd.append('--update-only-group-schemas')
        cmd.extend(params.update_only_group_schemas)

    # run script
    update_config_schemas.main(cmd)

    # check results
    assert params.tc_report_problems_calls == teamcity_report_problems.calls
    assert (
        params.tc_report_test_problems_calls
        == teamcity_report_test_problem.calls
    )
    assert load_json(params.expected_history) == configs_admin_mock.history
