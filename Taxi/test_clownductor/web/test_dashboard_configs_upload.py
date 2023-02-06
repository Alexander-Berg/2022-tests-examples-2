import pytest


ERROR_MOCK = {'code': 'ERR_CODE', 'message': 'Err msg'}


@pytest.mark.parametrize(
    'auth_token, external_request, expected_code, expected_error',
    [
        pytest.param(
            'invalid_token',
            False,
            403,
            {'code': 'UNAUTHORIZED', 'message': 'Unsuccessful authorization'},
            id='invalid_token',
        ),
        pytest.param(
            'valid_teamcity_token', True, 200, None, id='external_request_200',
        ),
        pytest.param(
            'valid_teamcity_token',
            True,
            400,
            ERROR_MOCK,
            id='external_request_400',
        ),
        pytest.param(
            'valid_teamcity_token',
            True,
            404,
            ERROR_MOCK,
            id='external_request_404',
        ),
        pytest.param(
            'valid_teamcity_token',
            True,
            409,
            ERROR_MOCK,
            id='external_request_409',
        ),
    ],
)
async def test_dashboard_proxy_upload(
        web_app_client,
        patch_configs_upload_handler,
        load_json,
        auth_token,
        expected_code,
        external_request,
        expected_error,
):
    dashboard_config = load_json('dashboard_config.json')
    request_data = {'config': dashboard_config, 'is_created': True}
    configs_upload_handler_mock = patch_configs_upload_handler(
        response=request_data if not expected_error else expected_error,
        status=expected_code,
    )

    response = await web_app_client.post(
        'v1/dashboard_configs/upload',
        params={
            'project_name': 'test-project',
            'service_name': 'test-service',
            'branch_name': 'stable',
            'service_type': 'nanny',
            'suffix': 'suffix',
        },
        json=dashboard_config,
        headers={'X-YaTaxi-Api-Key': auth_token},
    )
    assert response.status == expected_code

    if response.status in {200, 201}:
        assert await response.json() == request_data
    elif 400 <= response.status < 500:
        assert await response.json() == expected_error

    assert configs_upload_handler_mock.times_called == (
        1 if external_request else 0
    )
    if external_request:
        request = configs_upload_handler_mock.next_call()['request']
        assert request.json == dashboard_config
        assert not configs_upload_handler_mock.has_calls
