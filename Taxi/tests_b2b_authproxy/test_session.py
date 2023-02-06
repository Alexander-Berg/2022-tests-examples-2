import pytest

from tests_b2b_authproxy import const


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_session_route_200(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        is_b2b_header_set,
        cargo_corp_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.config(CARGO_B2B_ACCESS_CONTROL_ENABLED=False)
async def test_session_route_200_if_cargo(
        b2b_authproxy_post_with_cargo_init, test_handler, mock_cargocorp,
):
    mock_cargocorp.set_ok_response(is_employee=True, is_enabled=True)
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test', json=const.DEFAULT_REQUEST, is_b2b_header_set=True,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_session_passport_500(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    async def _test(request):
        assert False

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        session='raise_500',
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_session_route_passport_timeout(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    def _test(request):
        assert False

    @mockserver.json_handler('/blackbox')
    async def _passport_timeout(request):
        raise mockserver.TimeoutError

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert response.status_code == 504
    assert response.json() == {
        'code': '504',
        'message': 'Internal error: network read timeout',
    }


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_cache_sid(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        is_b2b_header_set,
        cargo_corp_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test', json=const.DEFAULT_REQUEST,
    )
    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        blackbox_sessions=[
            {
                'session_id': 'session_1',
                'yandex_uid': '2222',
                'login': 'login2',
            },
        ],
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert test_handler.times_called == 2
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
@pytest.mark.config(B2B_AUTHPROXY_CORP_CLIENT_CUTOUT=[const.CORP_CLIENT_ID])
async def test_session_blocked_by_cutout(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        is_b2b_header_set,
        cargo_corp_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 403
    assert response.json() == {
        'code': 'access_denied',
        'message': 'Access denied',
    }
