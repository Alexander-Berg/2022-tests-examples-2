# pylint: disable=W0612,C0103
import json

import pytest


@pytest.mark.parametrize(
    'request_data, is_success, result_file, response_status',
    [
        (
            {
                'vendor_host': '$mockserver',
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'origin_id': 'origin_id',
                'mode': 'auth',
            },
            True,
            'test_token.json',
            200,
        ),
        (
            {
                'vendor_host': '$mockserver',
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'origin_id': 'origin_id',
                'mode': 'auth',
            },
            False,
            'test_token_error.json',
            200,
        ),
        ({}, False, '', 400),
    ],
)
async def test_check_post(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        request_data,
        is_success,
        result_file,
        response_status,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json(result_file)),
            200,
            headers={'Content-type': 'application/json'},
        )

    response = await web_app_client.post(
        '/4.0/restapp-front/api/v1/integration/shooter/partner/check-api',
        json=request_data,
    )
    assert response.status == response_status
    response_json = await response.json()
    if response.status == 200:
        assert response_json['isSuccess'] == is_success
    if response.status == 400:
        assert len(response_json['details']['errors']) == 5
