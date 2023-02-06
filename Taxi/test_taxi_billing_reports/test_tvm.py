import pytest

from . import conftest

_NO_TVM = ['/ping']


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    'headers,expected_response,assert_message',
    [
        ({}, 403, 'doesn\'t require TVM token'),
        (conftest.get_request_headers(), 400, 'returns unexpected response'),
    ],
)
async def test_tvm(
        taxi_billing_reports_app,
        taxi_billing_reports_client,
        headers,
        expected_response,
        assert_message,
        patched_tvm_ticket_check,
):
    app_routes = taxi_billing_reports_app.router.routes()
    for route in app_routes:
        path = route.get_info()['path']
        method = route.method
        if path not in _NO_TVM:
            response = None
            if method == 'POST':
                response = await taxi_billing_reports_client.post(
                    path, json={}, headers=headers,
                )
            elif method == 'GET':
                response = await taxi_billing_reports_client.get(
                    path, headers=headers,
                )
            assert (
                response and response.status == expected_response
            ), f'{path} {assert_message}'
