import pytest


@pytest.mark.usefixtures('mocks_for_service_creation')
@pytest.mark.features_on('feat_duty_group_id')
@pytest.mark.parametrize(
    'file_name, expected_group',
    [
        pytest.param('update_duty_group_id.json', 'Great'),
        pytest.param('remove_duty_group_id.json', None),
        pytest.param('no_changes.json', None),
    ],
)
async def test_update_duty_group_id(
        load_json,
        add_service,
        add_nanny_branch,
        get_remote_params,
        call_cube_handle,
        file_name,
        expected_group,
):
    service = await add_service('test-project', 'test-service')
    await add_nanny_branch(service['id'], 'test-branch', 'stable')
    await call_cube_handle('ChangeSystemInfo', load_json(file_name))
    info = await get_remote_params(1, 1, 'service_info')
    assert info.stable.duty_group_id.value == expected_group
