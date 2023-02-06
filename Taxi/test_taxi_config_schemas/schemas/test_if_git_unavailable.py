import pytest

from taxi_config_schemas.repo_manager import errors


@pytest.fixture(autouse=True)
async def _fixture(patch):
    @patch('taxi_config_schemas.repo_manager.util.GitHelper._call_command')
    async def _call_command(*args, **kwargs):
        raise errors.SubprocessError('error')


@pytest.mark.usefixtures('patch_configs_by_group')
async def test_if_git_unavailable(patcher_tvm_ticket_check, web_app_client):
    patcher_tvm_ticket_check('config-schemas')
    response = await web_app_client.post(
        '/v1/schemas/actual_commit/',
        headers={'X-Ya-Service-Ticket': 'good'},
        json={'commit': 'a5c6b9d9edc2f871162ce694bd7ea21dc9c70106'},
    )
    assert response.status == 502

    response = await web_app_client.get(
        '/v1/schemas/diff/?commit=a5c6b9d9edc2f871162ce694bd7ea21dc9c70106',
        headers={'X-Ya-Service-Ticket': 'good'},
    )
    assert response.status == 502
