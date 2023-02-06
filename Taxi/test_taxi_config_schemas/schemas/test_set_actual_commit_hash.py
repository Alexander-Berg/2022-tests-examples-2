import pytest

from config_schemas_lib import storage


@pytest.mark.parametrize(
    'commit_hash,status',
    [('123456', 200), ('develop', 400), ('1234567', 400)],
)
@pytest.mark.usefixtures('patch_configs_by_group', 'patch_call_command')
async def test_set_actual_commit_hash(
        patch,
        web_context,
        patcher_tvm_ticket_check,
        web_app_client,
        commit_hash,
        status,
):
    @patch('taxi_config_schemas.repo_manager.RepoSession.cat_file')
    async def _cat_file(*args, **kwargs):
        return

    @patch(
        'taxi_config_schemas.repo_manager.RepoSession.get_branches_by_commit',
    )
    async def _get_branches_by_commit(commit):
        if commit == '1234567':
            return []
        return ['origin/develop']

    @patch(
        'taxi_config_schemas.repo_manager.util.'
        'GitHelper.get_changed_file_names',
    )
    async def _get_changed_file_names(*args, **kwargs):
        return ''

    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/schemas/actual_commit/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json={'commit': commit_hash},
    )
    assert response.status == status
    if status == 200:
        doc = await web_context.mongo.configs_meta.find_one(
            {'_id': storage.CONFIG_SCHEMAS_META_ID},
        )
        assert doc['hash'] == commit_hash
