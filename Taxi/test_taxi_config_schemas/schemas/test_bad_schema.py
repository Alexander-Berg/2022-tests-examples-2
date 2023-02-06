# pylint: disable=unused-variable
import typing

import pytest

from config_schemas_lib import storage


CONFIGS = [
    {
        'name': 'TIYE',
        'description': '',
        'group': 'other',
        'default': {
            'buffer_size': 1000,
            'concurency_count': 20,
            'millis_per_quant': 50,
            'quants_per_frame': 20,
            'queries_per_frame': 1000,
        },
        'tags': ['fallback'],
        'validators': [
            {
                '$keyset': [
                    'buffer_size',
                    'queries_per_frame',
                    'quants_per_frame',
                    'millis_per_quant',
                    'concurency_count',
                ],
                '$conditions': [
                    'isinstance(queries_per_frame, int)',
                    'queries_per_frame >= 10',
                    'isinstance(quants_per_frame, int)',
                    'quants_per_frame >= 10',
                    'isinstance(millis_per_quant, int)',
                    'millis_per_quant >= 10',
                    'isinstance(buffer_size, int)',
                    'buffer_size > quants_per_frame * 10',
                    'isinstance(concurency_count, int)',
                    'concurency_count >= 1',
                    'concurency_count < 100000',
                ],
            },
        ],
    },
]


@pytest.fixture
def patch_configs_by_group(patch, build_configs_by_group):
    @patch(
        'taxi_config_schemas.repo_manager.RepoSession.'
        '_collect_configs_by_group',
    )
    def _collect_configs_by_group(*args, **kwargs):
        return build_configs_by_group(CONFIGS)


@pytest.fixture
def _set_local_mocks(patch, load, patcher_tvm_ticket_check):
    class _Args:
        config_name = ''

    @patch('taxi_config_schemas.repo_manager.RepoSession.cat_file')
    async def cat_file(*args, **kwargs):
        return

    @patch('taxi_config_schemas.repo_manager.RepoSession.rev_parse')
    async def rev_parse(*args, **kwargs):
        return 'some_commit'

    @patch(
        'taxi_config_schemas.repo_manager.util.'
        'GitHelper.get_changed_file_names',
    )
    async def get_changed_file_names(*args, **kwargs):
        return 'schemas/configs/declarations/group/{}.yaml'.format(
            _Args.config_name,
        )

    @patch(
        'taxi_config_schemas.repo_manager.RepoSession.get_branches_by_commit',
    )
    async def get_branches_by_commit(commit):
        if commit == '1234567':
            return []
        return ['origin/develop']

    @patch(
        'taxi_config_schemas.repo_manager.util.GitHelper.get_file_for_commit',
    )
    async def get_file_for_commit(*args, **kwargs):
        return """default:
  buffer_size: 1000
  concurency_count: 20
  millis_per_quant: 50
  quants_per_frame: 20
  queries_per_frame: 1000
description: Параметры ограничения потока запросов CheckChangesHandler
tags: []
validators:
- $keyset:
  - buffer_size
  - queries_per_frame
  - quants_per_frame
  - millis_per_quant
  - concurency_count
- $conditions:
  - isinstance(queries_per_frame, int)
  - queries_per_frame >= 10
  - isinstance(quants_per_frame, int)
  - quants_per_frame >= 10
  - isinstance(millis_per_quant, int)
  - millis_per_quant >= 10
  - isinstance(buffer_size, int)
  - buffer_size > quants_per_frame * 10
  - isinstance(concurency_count, int)
  - concurency_count >= 1
  - concurency_count < 100000
"""

    @patch('taxi_config_schemas.repo_manager.util.GitHelper.get_commits_log')
    async def _get_commits(commit_from, commit_to, *args, **kwargs):
        return load('git_log_output_verbose.txt')

    @patch('os.path.exists')
    def exists(file_name):
        return True

    patcher_tvm_ticket_check('config-schemas')

    yield _Args


async def get_actual_date(db) -> typing.Optional[typing.Tuple]:
    meta = await db.secondary.configs_meta.find_one(
        {'_id': storage.CONFIG_SCHEMAS_META_ID},
    )
    if not meta:
        return None
    return (
        meta.get(storage.META_FIELDS.UPDATED),
        meta.get(storage.META_FIELDS.SENT),
    )


class Case(typing.NamedTuple):
    config_name: str = 'CONFIG_SCHEMAS_RUNTIME_FEATURES'
    status: int = 200
    patch_send_comment_path: str = (
        'taxi_config_schemas.report_manager.comment_tickets.AddComments.'
        '_send_comment'
    )
    result: typing.List = [
        {
            'args': (
                'TAXICOMMON-2482',
                {
                    'New schema for config '
                    '"CONFIG_SCHEMAS_RUNTIME_FEATURES" '
                    'was applied in admin by serg-novikov',
                },
            ),
            'kwargs': {},
        },
    ]
    check_report: bool = True
    error_response: typing.Optional[typing.Dict] = None


@pytest.mark.parametrize(
    'config_name,'
    'status,patch_send_comment_path,result,check_report,error_response',
    [
        pytest.param(
            *Case(
                config_name='TIYE',
                status=422,
                check_report=False,
                error_response={
                    'code': 'NEW_VALIDATOR_ERROR',
                    'message': (
                        'Can\'t change actual commit, validation does '
                        'not pass on values from db. Details: '
                        'errors occurred during validation of config TIYE: '
                        'Unknown validator name: conditions. '
                        'See pull requests: '
                        'https://github.yandex-team.ru/taxi/'
                        'schemas/pull/7315. '
                    ),
                    'status': 'error',
                    'details': {
                        'prs': [
                            'https://github.yandex-team.ru/'
                            'taxi/schemas/pull/7315',
                        ],
                    },
                },
            ),
            id='fail_update',
        ),
    ],
)
@pytest.mark.usefixtures(
    'patch_configs_by_group', 'patch_call_command', 'update_schemas_cache',
)
async def test_set_actual_commit_validate(
        patch,
        web_context,
        web_app_client,
        config_name,
        status,
        patch_send_comment_path,
        result,
        check_report,
        error_response,
        _set_local_mocks,
):
    _set_local_mocks.config_name = config_name

    @patch(patch_send_comment_path)
    async def fake_send(*args, **kwargs):
        pass

    response = await web_app_client.post(
        '/v1/schemas/actual_commit/',
        headers={
            'X-Ya-Service-Ticket': 'good',
            'X-Yandex-Login': 'serg-novikov',
        },
        json={'commit': 'a5c6b9d9edc2f871162ce694bd7ea21dc9c70106'},
    )
    assert response.status == status
    if status != 200:
        assert await response.json() == error_response
        return
