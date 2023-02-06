import pytest


@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        pytest.param(
            {'app_version': '0.0.0'},
            {'needs_update': True, 'text': 'test_text', 'url': 'test_url'},
            id='needs_update is True',
        ),
        pytest.param(
            {'app_version': '0.0.1'},
            {'needs_update': False},
            id='needs_update is False',
        ),
    ],
)
@pytest.mark.client_experiments3(
    consumer='eats-tips-admin/application-status',
    config_name='eats_tips_admin_application_status',
    args=[{'name': 'app_version', 'type': 'string', 'value': '0.0.0'}],
    value={'needs_update': True, 'text': 'test_text', 'url': 'test_url'},
)
async def test_application_status_post(
        taxi_eats_tips_admin_web,
        mock_eats_tips_partners,
        mock_eats_tips_payments,
        # params
        request_body,
        expected_response,
):
    response = await taxi_eats_tips_admin_web.post(
        '/v1/application/status', json=request_body,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected_response
