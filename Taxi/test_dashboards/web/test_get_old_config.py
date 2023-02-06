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
            marks=pytest.mark.config(
                DASHBOARDS_GENERATOR_SETTINGS={
                    'old_enabled': False,
                    'old_disabled_filenames': ['file1', 'file2'],
                },
            ),
            id='filled_config_disabled',
        ),
        pytest.param(
            {
                'old_enabled': True,
                'old_disabled_filenames': ['file1', 'file2'],
            },
            marks=pytest.mark.config(
                DASHBOARDS_GENERATOR_SETTINGS={
                    'old_enabled': True,
                    'old_disabled_filenames': ['file1', 'file2'],
                },
            ),
            id='filled_config_enabled',
        ),
    ],
)
async def test_get_old_config_handle(web_app_client, expected_response):
    response = await web_app_client.get('/v1/configs/get_config')
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
