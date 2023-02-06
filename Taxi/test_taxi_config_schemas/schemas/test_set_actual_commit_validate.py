# pylint: disable=unused-variable
import typing

import pytest

from config_schemas_lib import storage

from taxi_config_schemas.generated.cron import run_cron


CONFIGS = [
    {
        'name': 'SOME_CONFIG',
        'description': '',
        'group': 'other',
        'default': 100000000,
        'tags': ['fallback'],
        'validators': ['$integer', {'$gt': 0}],
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
        git_log = 'git_log_output_verbose.txt'

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
        return (
            'default: false\ndescription: Выключатель\n'
            'tags: []\nvalidators:\n- $boolean'
        )

    @patch('taxi_config_schemas.repo_manager.util.GitHelper.get_commits_log')
    async def _get_commits(commit_from, commit_to, *args, **kwargs):
        return load(_Args.git_log)

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
    git_log: str = 'git_log_output_verbose.txt'
    patch_send_comment_path: str = (
        'taxi_config_schemas.report_manager.comment_tickets.AddComments.'
        '_send_comment'
    )
    result: typing.List = [
        {
            'args': (
                'TAXICOMMON-2482',
                {
                    'New schema for config "(('
                    'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
                    'dev/configs/edit/CONFIG_SCHEMAS_RUNTIME_FEATURES '
                    'CONFIG_SCHEMAS_RUNTIME_FEATURES))" '
                    'was applied in admin by @serg-novikov',
                },
            ),
            'kwargs': {},
        },
    ]
    check_report: bool = True
    error_response: typing.Optional[typing.Dict] = None


@pytest.mark.parametrize(
    'config_name,'
    'status,git_log,'
    'patch_send_comment_path,result,check_report,error_response',
    [
        pytest.param(
            *Case(
                config_name='SOME_CONFIG',
                status=422,
                check_report=False,
                error_response={
                    'code': 'NEW_VALIDATOR_ERROR',
                    'message': (
                        'Can\'t change actual commit, '
                        'validation does not pass on values from db. '
                        'Details: errors occurred during validation of config '
                        'SOME_CONFIG: [\'must be a boolean\']. '
                        'See pull requests: '
                        'https://github.yandex-team.ru/taxi/'
                        'schemas/pull/9315. '
                    ),
                    'status': 'error',
                    'details': {
                        'prs': [
                            'https://github.yandex-team.ru/'
                            'taxi/schemas/pull/9315',
                        ],
                    },
                },
            ),
            id='fail_update',
        ),
        pytest.param(
            *Case(
                config_name='SOME_CONFIG',
                status=422,
                git_log='git_log_output_verbose_other_symbol.txt',
                check_report=False,
                error_response={
                    'code': 'NEW_VALIDATOR_ERROR',
                    'message': (
                        'Can\'t change actual commit, '
                        'validation does not pass on values from db. '
                        'Details: errors occurred during validation of config '
                        'SOME_CONFIG: [\'must be a boolean\']. '
                        'See pull requests: '
                        'https://github.yandex-team.ru/taxi/'
                        'schemas/pull/9315. '
                    ),
                    'status': 'error',
                    'details': {
                        'prs': [
                            'https://github.yandex-team.ru/'
                            'taxi/schemas/pull/9315',
                        ],
                    },
                },
            ),
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={'pr_symbol': '~'},
            ),
            id='fail_update_other_symbol_for_pr_selection',
        ),
        pytest.param(
            *Case(
                config_name='SOME_CONFIG',
                status=422,
                git_log='git_log_output_verbose_regexp_symbol.txt',
                check_report=False,
                error_response={
                    'code': 'NEW_VALIDATOR_ERROR',
                    'message': (
                        'Can\'t change actual commit, '
                        'validation does not pass on values from db. '
                        'Details: errors occurred during validation of config '
                        'SOME_CONFIG: [\'must be a boolean\']. '
                        'See pull requests: '
                        'https://github.yandex-team.ru/taxi/'
                        'schemas/pull/9315. '
                    ),
                    'status': 'error',
                    'details': {
                        'prs': [
                            'https://github.yandex-team.ru/'
                            'taxi/schemas/pull/9315',
                        ],
                    },
                },
            ),
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={'pr_symbol': '$'},
            ),
            id='fail_update_regexp_symbol_for_pr_selection',
        ),
        pytest.param(
            *Case(),
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={
                    'report_method': 'add_to_tickets',
                    'report_collect_ticket': '',
                    (
                        'taxi_config_schemas.crontasks.'
                        'send_alerts_for_update'
                    ): 'enabled',
                },
            ),
            id='success_update_and_add_to_tickets_report',
        ),
        pytest.param(
            *Case(
                patch_send_comment_path=(
                    'taxi_config_schemas.report_manager.collect_to_ticket.'
                    'CommentCommonTicket._send_comment'
                ),
                result=[
                    {
                        'args': (
                            'collect_ticket',
                            {
                                'New schema for config '
                                '"((https://tariff-editor-unstable.taxi.'
                                'tst.yandex-team.ru/dev/configs/edit/'
                                'CONFIG_SCHEMAS_RUNTIME_FEATURES '
                                'CONFIG_SCHEMAS_RUNTIME_FEATURES))" '
                                'was applied in admin by @serg-novikov',
                            },
                        ),
                        'kwargs': {},
                    },
                ],
            ),
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={
                    'report_method': 'add_to_one_ticket',
                    'report_collect_ticket': 'TAXICOMMON-2482',
                    (
                        'taxi_config_schemas.crontasks.'
                        'send_alerts_for_update'
                    ): 'enabled',
                },
            ),
            id='success_update_and_collect_to_ticket_report',
        ),
        pytest.param(
            *Case(
                patch_send_comment_path=(
                    'taxi_config_schemas.report_manager.collect_to_ticket.'
                    'CommentCommonTicket._send_comment'
                ),
                result=[],
                check_report=False,
            ),
            marks=pytest.mark.config(
                CONFIG_SCHEMAS_RUNTIME_FEATURES={
                    (
                        'taxi_config_schemas.crontasks.'
                        'send_alerts_for_update'
                    ): 'enabled',
                },
            ),
            id='success_update_and_no_report',
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
        git_log,
        patch_send_comment_path,
        result,
        check_report,
        error_response,
        _set_local_mocks,
):
    _set_local_mocks.config_name = config_name
    _set_local_mocks.git_log = git_log

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

    updated_before, sent_before = await get_actual_date(web_context.mongo)
    await run_cron.main(
        ['taxi_config_schemas.crontasks.send_alerts_for_update', '-t', '0'],
    )
    updated_after, sent_after = await get_actual_date(web_context.mongo)

    assert fake_send.calls == result

    if not check_report:
        return

    assert sent_before is None
    assert sent_after is not None
    assert updated_before == updated_after
    assert sent_after > updated_after
