import pytest

import nanny_yp.components


ERRORS = {500: nanny_yp.components.Server5xxError()}


@pytest.mark.parametrize(
    'request_method, request_url, response_statuses, exp_response_data',
    [
        pytest.param(
            'get',
            '/v2/services/service_name/',
            [500, 200],
            {'data': 'some_data'},
            marks=pytest.mark.config(
                NANNY_YP_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
        ),
    ],
)
async def test_nanny_yp_request_succ_retries(
        nanny_yp_client,
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
            status=response_statuses[0], json={'data': 'som_fail_data'},
        )

    @patch_aiohttp_session(f'base_url{request_url}', 'get')
    def patch_request_succ(*args, **kwargs):  # pylint: disable=unused-variable
        return response_mock(
            status=response_statuses[1], json={'data': 'some_data'},
        )

    response_data = (
        await nanny_yp_client._request(  # pylint: disable=protected-access
            request_method, request_url,
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
                NANNY_YP_CLIENT_QOS={
                    '__default__': {'attempts': 3, 'timeout-ms': 1000},
                },
            ),
        ),
    ],
)
async def test_nanny_yp_request_fail_retries(
        nanny_yp_client,
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
        await nanny_yp_client._request(  # pylint: disable=protected-access
            request_method, request_url,
        )
        assert False
    except Exception as exp:  # pylint: disable=broad-except
        assert isinstance(exp, type(ERRORS[response_status]))
