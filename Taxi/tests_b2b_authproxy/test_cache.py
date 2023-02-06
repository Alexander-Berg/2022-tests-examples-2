import pytest

from tests_b2b_authproxy import const


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
@pytest.mark.parametrize(
    'mock_taxicorp_code, expected_code, expected_times_called',
    ((200, 200, 1), (404, 401, 2), (500, 500, 6)),
)
async def test_cache(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        mock_taxicorp,
        mock_taxicorp_code,
        expected_code,
        expected_times_called,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/cache/test')
    def _test(request):
        return mockserver.make_response(json={'text': 'smth'}, status=200)

    mock_taxicorp.set_response_by_code(mock_taxicorp_code)

    for _ in range(2):
        response = await b2b_authproxy_post_with_cargo_init(
            '/v1/cargo/cache/test',
            json={},
            is_b2b_header_set=is_b2b_header_set,
            cargo_corp_code=cargo_corp_code,
        )
        assert response.status_code == expected_code

    assert mock_taxicorp.times_called == expected_times_called


async def test_cache_skip_caching(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        mock_taxicorp,
        mock_cargocorp,
):
    @mockserver.json_handler('/v1/cargo/cache/test')
    def _test(request):
        return mockserver.make_response(json={'text': 'smth'}, status=200)

    mock_taxicorp.set_response(
        200, {'corp_client_id': const.OTHER_CORP_CLIENT_ID},
    )

    for _ in range(2):
        response = await b2b_authproxy_post_with_cargo_init(
            '/v1/cargo/cache/test',
            json={},
            is_b2b_header_set=True,  # const.CORP_CLIENT_ID
            cargo_corp_code=404,
        )
        assert response.status_code == 401

    assert mock_taxicorp.times_called == 2
    assert mock_cargocorp.times_called == 2


@pytest.mark.config(CARGO_B2B_ACCESS_CONTROL_ENABLED=False)
@pytest.mark.parametrize(
    'is_cargo_employee_enabled, expected_b2b_header',
    ((True, const.CORP_CLIENT_ID), (False, None)),
)
async def test_calls_if_cargo(
        b2b_authproxy_post_with_cargo_init,
        test_proxy_401_handlers,
        mock_cargocorp,
        mock_taxicorp,
        is_cargo_employee_enabled,
        expected_b2b_header,
):
    test_handler = test_proxy_401_handlers(
        const.PROXY_401_TEST_URL,
        uid_expected=True,
        expected_b2b_header=expected_b2b_header,
    )
    mock_cargocorp.set_ok_response(
        is_employee=True, is_enabled=is_cargo_employee_enabled,
    )

    for _ in range(2):
        response = await b2b_authproxy_post_with_cargo_init(
            '/v1/cargo/proxy_401/cache/test',
            json=const.DEFAULT_REQUEST,
            is_b2b_header_set=True,
        )
        assert response.status_code == 200

    assert test_handler.times_called == 2
    assert mock_cargocorp.times_called == 1
    assert mock_taxicorp.times_called == 0
