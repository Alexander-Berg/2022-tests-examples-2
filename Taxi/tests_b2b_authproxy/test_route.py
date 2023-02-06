import pytest

from tests_b2b_authproxy import const


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_route_handler_timeout(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    async def _test(request):
        raise mockserver.TimeoutError

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert _test.times_called == 1
    assert response.status_code == 500


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_route_401_default(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        is_b2b_header_set,
        cargo_corp_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        blackbox_sessions=[],
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 401
    assert response.json() == {
        'code': 'unauthorized',
        'message': 'Not authorized request',
    }


async def test_route_401_if_cargo_but_disabled(
        b2b_authproxy_post_with_cargo_init, mock_cargocorp, test_handler,
):
    mock_cargocorp.set_ok_response(is_employee=True, is_enabled=False)

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test', json=const.DEFAULT_REQUEST, is_b2b_header_set=True,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 401
    assert response.json() == {
        'code': 'unauthorized',
        'message': 'Not authorized request',
    }


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
@pytest.mark.parametrize(
    'session, uid_expected',
    (
        pytest.param('unknown_session', False, id='no auth'),
        pytest.param('session_no_corp', True, id='partial auth'),
    ),
)
async def test_proxy_401_session(
        b2b_authproxy_post_with_cargo_init,
        test_proxy_401_handlers,
        session,
        uid_expected,
        is_b2b_header_set,
        cargo_corp_code,
):
    test_handler = test_proxy_401_handlers(
        const.PROXY_401_TEST_URL, uid_expected,
    )
    response = await b2b_authproxy_post_with_cargo_init(
        const.PROXY_401_TEST_URL,
        json=const.DEFAULT_REQUEST,
        session=session,
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert test_handler.times_called == 1
    assert response.json() == {'id': '123'}
    assert response.status_code == 200


@pytest.mark.parametrize(
    'token, uid_expected',
    (
        pytest.param('bad_token', False, id='no auth'),
        pytest.param('token_no_corp', True, id='partial auth'),
    ),
)
async def test_proxy_401_token(
        b2b_authproxy_post_with_cargo_init,
        test_proxy_401_handlers,
        token,
        uid_expected,
        mock_cargo_robot_client,
):
    test_handler = test_proxy_401_handlers(
        const.PROXY_401_TEST_URL, uid_expected,
    )
    response = await b2b_authproxy_post_with_cargo_init(
        const.PROXY_401_TEST_URL, json=const.DEFAULT_REQUEST, bearer=token,
    )

    assert test_handler.times_called == 1
    assert response.json() == {'id': '123'}
    assert response.status_code == 200


@pytest.mark.config(B2B_AUTHPROXY_ROUTE_RULES=[])
@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_noroute(
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
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No route for URL'}


@pytest.mark.config(
    B2B_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/v1/cargo/'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {'server-hosts': ['invalid host name']},
        },
    ],
)
@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_other_host_route(
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
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'No route for URL'}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.tvm2_ticket({1000: 'MOCK_TICKET'})
@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_route_tvm(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/tvm/test')
    def _test(request):
        assert request.headers['X-Ya-Service-Ticket'] == 'MOCK_TICKET'
        assert request.headers['X-Ya-User-Ticket'] == 'test_user_ticket'
        assert request.headers['X-Yandex-UID'] == '1111'

        return mockserver.make_response('{"text": "smth"}', status=200)

    response = await b2b_authproxy_post_with_cargo_init(
        '/v1/cargo/tvm/test',
        json={},
        is_b2b_header_set=is_b2b_header_set,
        cargo_corp_code=cargo_corp_code,
    )

    assert _test.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'text': 'smth'}


@pytest.mark.parametrize(*const.CARGO_CORP_CASES)
async def test_route_options_method(
        taxi_b2b_authproxy,
        blackbox_service,
        mockserver,
        mock_taxicorp,
        mock_cargocorp,
        get_session_headers,
        is_b2b_header_set,
        cargo_corp_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    def _test(request):
        assert request.method == 'OPTIONS'

        return {'id': '123'}

    mock_cargocorp.set_response_by_code(response_code=cargo_corp_code)
    blackbox_service.set_sessionid_info('session_1', uid='1111')

    response = await taxi_b2b_authproxy.options(
        'v1/cargo/test',
        json={},
        headers=get_session_headers(is_b2b_header_set=is_b2b_header_set),
    )

    assert response.status_code == 200
    assert response.json() == {'id': '123'}
    assert _test.times_called == 1
