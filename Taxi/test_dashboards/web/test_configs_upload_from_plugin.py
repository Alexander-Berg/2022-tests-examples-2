import pytest


@pytest.mark.parametrize(
    'request_data_filepath, expected_config_filepath',
    [
        pytest.param(
            'generated_requests/request_dashboards_config.json',
            'expected/dashboard_config.json',
        ),
    ],
)
@pytest.mark.pgsql('dashboards', files=['init_data.sql'])
async def test_upload_config_from_plugin(
        web_app_client,
        load_json,
        request_data_filepath,
        expected_config_filepath,
):
    request_data = load_json(request_data_filepath)
    expected_config = load_json(expected_config_filepath)

    response = await web_app_client.post(
        '/v1/configs/upload',
        params=request_data['params'],
        json=request_data['body'],
    )
    assert response.status == 200

    content = await response.json()
    assert content['is_created']
    assert content['config'] == expected_config, str(content)
