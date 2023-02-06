import pytest


@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            {'old_enabled': True, 'old_disabled_filenames': []},
            id='empty_config',
        ),
        pytest.param(
            {
                'old_enabled': False,
                'old_disabled_filenames': ['file1', 'file2'],
            },
            id='filled_config_disabled',
        ),
        pytest.param(
            {
                'old_enabled': True,
                'old_disabled_filenames': ['file1', 'file2'],
            },
            id='filled_config_enabled',
        ),
    ],
)
async def test_dashboard_get_old_config(
        web_app_client, patch_get_old_config_handler, expected_response,
):
    configs_upload_handler_mock = patch_get_old_config_handler(
        expected_response, 200,
    )

    response = await web_app_client.get('v1/dashboard_configs/get_config')
    assert configs_upload_handler_mock.times_called == 1
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
