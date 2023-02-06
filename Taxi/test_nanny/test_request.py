import aiohttp
import pytest


@pytest.mark.parametrize(
    'request_method, request_url, response_statuses, exp_response_data',
    [
        pytest.param(
            'get',
            '/v2/services/service_name/',
            [500, 200],
            {'data': 'some_data'},
            marks=pytest.mark.config(
                NANNY_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
            id='200 response after retry',
        ),
        pytest.param(
            'get',
            '/v2/services/service_name/',
            [500, 204],
            {},
            marks=pytest.mark.config(
                NANNY_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
            id='204 response after retry',
        ),
        pytest.param(
            'get',
            '/v2/services/service_name/',
            [500, 404],
            None,
            marks=pytest.mark.config(
                NANNY_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
            id='404 response after retry',
        ),
    ],
)
async def test_nanny_request_succ_retries(
        nanny_client,
        request_method,
        request_url,
        response_mock,
        patch_aiohttp_session,
        response_statuses,
        exp_response_data,
):
    @patch_aiohttp_session(f'base_url{request_url}', 'get')
    def patch_request_fail(*args, **kwargs):  # pylint: disable=unused-variable
        return response_mock(
            status=response_statuses[0], json={'data': 'some_fail_data'},
        )

    @patch_aiohttp_session(f'base_url{request_url}', 'get')
    def patch_request_succ(*args, **kwargs):  # pylint: disable=unused-variable
        return response_mock(
            status=response_statuses[1], json={'data': 'some_data'},
        )

    response_data = (
        await nanny_client._request(  # noqa: E501 pylint: disable=protected-access
            request_method,
            request_url,
            True,
            response_status=response_statuses[0],
        )
    )
    assert exp_response_data == response_data


@pytest.mark.parametrize(
    'request_method, request_url, response_status',
    [
        pytest.param(
            'get',
            '/v2/services/service_name/',
            500,
            marks=pytest.mark.config(
                NANNY_CLIENT_QOS={
                    '__default__': {'attempts': 2, 'timeout-ms': 1000},
                },
            ),
        ),
    ],
)
async def test_nanny_request_fail_retries(
        nanny_client,
        request_method,
        request_url,
        response_mock,
        patch_aiohttp_session,
        response_status,
):
    @patch_aiohttp_session(f'base_url{request_url}', 'get')
    def patch_request(*args, **kwargs):  # pylint: disable=unused-variable
        return response_mock(
            status=response_status, json={'data': 'some_data'},
        )

    try:
        await nanny_client._request(  # pylint: disable=protected-access
            request_method, request_url, True,
        )
        assert False
    except aiohttp.ClientResponseError as exp:
        assert str(response_status) in str(exp)
