from aiohttp import web
import pytest
from submodules.testsuite.testsuite.utils import http


@pytest.mark.parametrize(
    (
        'input_data',
        'ext_api_status',
        'ext_api_response',
        'expected_status',
        'expected_result',
    ),
    [
        (
            {'url': 'some url'},
            400,
            {'error': ['apple error']},
            400,
            {
                'code': 'apple_pay_token_error',
                'message': 'request to tips failed: apple error',
            },
        ),
        (
            {'url': 'some url'},
            200,
            {'key1': 1, 'key2': 2},
            200,
            {'token': {'key1': 1, 'key2': 2}},
        ),
    ],
)
async def test_apple_pay_token(
        taxi_eats_tips_payments_web,
        mock_chaevieprosto,
        input_data,
        ext_api_status,
        ext_api_response,
        expected_status,
        expected_result,
):
    @mock_chaevieprosto('/dhdghfier.html')
    async def _mock_waiter(request: http.Request):
        assert request.form['action'] == 'get-toke2'
        return web.json_response(ext_api_response, status=ext_api_status)

    response = await taxi_eats_tips_payments_web.post(
        '/v1/payments/apple-pay-token', json=input_data,
    )
    assert response.status == expected_status
    content = await response.json()
    assert content == expected_result
