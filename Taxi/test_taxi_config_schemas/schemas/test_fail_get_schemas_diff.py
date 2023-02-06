import contextlib

import pytest

from taxi_config_schemas import config_models
from taxi_config_schemas.repo_manager import errors


@pytest.mark.parametrize(
    'commit_hash,status,before,after,expected',
    [
        ('master', 400, None, None, None),
        ('1234567890abcdef1', 400, None, None, None),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.usefixtures('patch_call_command')
async def test_fail_get_schemas_diff(
        load,
        patch,
        tmpdir,
        web_app_client,
        build_configs_by_group,
        commit_hash,
        status,
        before,
        after,
        expected,
        patcher_tvm_ticket_check,
):
    is_before_state = None

    @patch(
        'taxi_config_schemas.repo_manager.util.GitHelper.collect_from_archive',
    )
    @contextlib.asynccontextmanager
    async def _collect_from_archive(commit_or_branch):
        nonlocal is_before_state
        assert commit_or_branch in (
            'b805804d8b5ce277903492c549055f4b5a86ed0a',
            commit_hash,
        )
        if commit_or_branch == 'b805804d8b5ce277903492c549055f4b5a86ed0a':
            is_before_state = True
        elif commit_or_branch == commit_hash:
            is_before_state = False
        yield tmpdir

    @patch('taxi_config_schemas.repo_manager.RepoSession.rev_parse')
    async def _rev_parse(*args, **kwargs):
        return commit_hash

    @patch('taxi_config_schemas.repo_manager.common.is_yaml_file')
    def _is_yaml_file(file_path):
        nonlocal is_before_state
        if is_before_state:
            data = ['%s.yaml' % item['name'] for item in before]
        else:
            data = ['%s.yaml' % item['name'] for item in after]
        return file_path.split('/')[-1] in data

    @patch(
        'taxi_config_schemas.repo_manager.RepoSession.get_branches_by_commit',
    )
    async def _get_branches_by_commit(commit):
        if commit == '1234567890abcdef1':
            return []
        return ['origin/develop']

    @patch(
        'taxi_config_schemas.repo_manager.util.'
        'GitHelper.get_changed_file_names',
    )
    async def _get_changed_file_names(
            commit_before, commit_after, *args, **kwargs,
    ):
        return """schemas/configs/declarations/chatterbox/STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES.yaml
schemas/configs/declarations/devicenotify/DEVICENOTIFY_USER_TTL.yaml
schemas/configs/declarations/driver-dispatcher/DRIVER_DISPATCHER_ENABLED_REGISTERING_PIN_IN_DISPATCH.yaml
schemas/configs/declarations/branding/INCORRECT_YAML_FILE.yaml"""

    @patch('taxi_config_schemas.repo_manager.util.GitHelper.get_merge_base')
    async def _get_merge_base(*args):
        return '67f83d9'

    @patch('taxi_config_schemas.repo_manager.common.open_file')
    def _open_file(file_name):
        return ''

    @patch('taxi_config_schemas.repo_manager.common.create_config')
    def _create_config(yaml_data, config_name, config_group):
        nonlocal is_before_state
        assert is_before_state is not None
        if config_name == 'INCORRECT_YAML_FILE':
            raise errors.YamlError(yaml_data)
        configs = before if is_before_state else after
        for config in configs:
            if config.get('name') == config_name:
                return config_models.BaseConfig(
                    name=config.get('name'),
                    description=config.get('description'),
                    full_description=config.get('full-description'),
                    wiki=config.get('wiki'),
                    group=config.get('group'),
                    default=config.get('default'),
                    tags=config.get('tags'),
                    validator_declarations=config.get('validators'),
                    schema=config.get('schema'),
                    maintainers=config.get('maintainers'),
                    turn_off_immediately=config.get('turn-off-immediately'),
                )
        raise Exception('No such config in test params.')

    @patch('taxi_config_schemas.repo_manager.util.GitHelper.get_commits_log')
    async def _get_commits(commit_from, commit_to, *args):
        if commit_from == '67f83d9' and commit_to == commit_hash:
            return load('git_log_output.txt')
        return ''

    await web_app_client.app['context'].config_schemas_cache.refresh_cache()

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.get(
        f'/v1/schemas/diff/?commit={commit_hash}',
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == status
    if status == 200:
        assert await response.json() == expected
