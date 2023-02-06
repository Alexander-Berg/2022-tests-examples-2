from typing import Optional

import pytest

ROUTE_RULES = [
    {
        'input': {'http-path-prefix': '/v1/payment/status'},
        'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
    },
]

DISABLE_IP_WHITELIST = {'vtb': {'enabled': False, 'whitelist': []}}
IP_WHITELIST_CLIENT_WITHOUT_IP = {'vtb': {'enabled': True, 'whitelist': []}}
IP_WHITELIST_CLIENT_WITH_OTHER_IP = {
    'vtb': {'enabled': True, 'whitelist': ['198.12.0.2']},
}
IP_WHITELIST_CLIENT_WITH_IP = {
    'vtb': {'enabled': True, 'whitelist': ['192.68.0.5']},
}


@pytest.mark.config(
    MAAS_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    MAAS_AUTHPROXY_IP_WHITELIST=DISABLE_IP_WHITELIST,
)
@pytest.mark.parametrize(
    'maas_status',
    (
        pytest.param(200, id='Success response from maas service'),
        pytest.param(500, id='Fail response from maas service'),
    ),
)
async def test_success_proxy(
        uapi_keys_ok, maas, make_request, metrics_checker, maas_status: int,
):
    maas_mock = maas(maas_status)
    response = await make_request()

    assert response.status == maas_status
    if maas_status == 200:
        expected_body = {}
    else:
        expected_body = {'code': 'some_maas_problem'}
    assert response.json() == expected_body
    assert uapi_keys_ok.has_calls
    assert maas_mock.has_calls
    await metrics_checker.check_metrics(expected_approves=1)


@pytest.mark.config(
    MAAS_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    MAAS_AUTHPROXY_IP_WHITELIST=DISABLE_IP_WHITELIST,
)
@pytest.mark.parametrize(
    'uapi_key_status',
    (
        pytest.param(403, id='Wrong api key'),
        pytest.param(456, id='Fail response from uapi-keys'),
    ),
)
async def test_uapi_keys_problem(
        uapi_keys_fail,
        maas_ok,
        make_request,
        metrics_checker,
        uapi_key_status: int,
):
    uapi_keys_mock = uapi_keys_fail(uapi_key_status)
    response = await make_request()

    assert uapi_keys_mock.has_calls
    assert not maas_ok.has_calls
    if uapi_key_status == 403:
        assert response.status == 401
        await metrics_checker.check_metrics(expected_rejects=1)
    else:
        assert response.status == 500
        await metrics_checker.check_metrics()


@pytest.mark.config(
    MAAS_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    MAAS_AUTHPROXY_IP_WHITELIST=DISABLE_IP_WHITELIST,
)
@pytest.mark.parametrize(
    'x_api_key',
    (
        pytest.param(None, id='No auth header'),
        pytest.param('', id='Empty auth header'),
        pytest.param('admin', id='Auth header without colon'),
        pytest.param(':', id='Auth with only colon'),
        pytest.param(':api-key', id='Only api-key'),
        pytest.param('vtb:', id='Only client_id'),
    ),
)
async def test_auth_header_parsing(
        uapi_keys_ok,
        maas_ok,
        make_request,
        metrics_checker,
        x_api_key: Optional[str],
):
    response = await make_request(
        x_api_key=x_api_key, has_auth_header=(x_api_key is not None),
    )

    assert not uapi_keys_ok.has_calls
    assert not maas_ok.has_calls
    assert response.status == 401
    await metrics_checker.check_metrics(expected_rejects=1)


@pytest.mark.config(
    MAAS_AUTHPROXY_ROUTE_RULES=ROUTE_RULES,
    MAAS_AUTHPROXY_IP_WHITELIST=DISABLE_IP_WHITELIST,
)
async def test_path_with_colon(
        uapi_keys_ok, maas_ok, make_request, metrics_checker,
):
    response = await make_request(url='/v1/payment/status/with/colon:')

    assert not uapi_keys_ok.has_calls
    assert not maas_ok.has_calls
    assert response.status == 400


@pytest.mark.config(MAAS_AUTHPROXY_ROUTE_RULES=ROUTE_RULES)
@pytest.mark.parametrize(
    'has_auth_header, expected_status',
    (
        pytest.param(False, 401, id='No auth params'),
        pytest.param(True, 401, id='No clients in ip whitelist'),
        pytest.param(
            True,
            401,
            marks=pytest.mark.config(
                MAAS_AUTHPROXY_IP_WHITELIST=IP_WHITELIST_CLIENT_WITHOUT_IP,
            ),
            id='Client has empty whitelist',
        ),
        pytest.param(
            True,
            401,
            marks=pytest.mark.config(
                MAAS_AUTHPROXY_IP_WHITELIST=IP_WHITELIST_CLIENT_WITH_OTHER_IP,
            ),
            id='IP not in whitelist',
        ),
        pytest.param(
            True,
            200,
            marks=pytest.mark.config(
                MAAS_AUTHPROXY_IP_WHITELIST=IP_WHITELIST_CLIENT_WITH_IP,
            ),
            id='Success auth',
        ),
    ),
)
async def test_ip_whitelist(
        uapi_keys_ok,
        maas_ok,
        make_request,
        has_auth_header: bool,
        expected_status: int,
):
    response = await make_request(has_auth_header=has_auth_header)

    assert response.status == expected_status
    if expected_status == 200:
        assert maas_ok.has_calls
    else:
        assert not maas_ok.has_calls
