import pytest

from tests_b2b_authproxy import const


HANDLER_CARGO_CORP_AND_OWNER = '/v1/cargo/corp_auth/owner_only'


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_token_route_200(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


@pytest.mark.config(
    B2B_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/v1/cargo/'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {
                'server-hosts': ['*'],
                'passport-scopes': ['forbidden:scope'],
            },
        },
    ],
)
@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_scopes(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 401


@pytest.mark.config(
    B2B_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/v1/cargo/'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {
                'server-hosts': ['*'],
                'passport-scopes': ['forbidden:scope'],
                'alternative-passport-scopes': ['corptaxi:all'],
            },
        },
    ],
)
@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_alternative_scopes(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200


@pytest.mark.config(
    B2B_AUTHPROXY_ROUTE_RULES=[
        {
            'input': {'http-path-prefix': '/v1/cargo/'},
            'output': {'upstream': {'$mockserver': ''}, 'tvm-service': 'mock'},
            'proxy': {'server-hosts': ['*'], 'proxy-401': True},
        },
    ],
)
@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_no_token_403(
        b2b_authproxy_post_with_cargo_init, mockserver, cargo_robot_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    async def _test(request):
        return mockserver.make_response(json={'text': 'invalid'}, status=403)

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer='',
        drop_bearer=True,
        cargo_robot_code=cargo_robot_code,
    )

    assert _test.times_called == 1
    assert response.status_code == 403


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
@pytest.mark.parametrize('token', ('unknown_token', 'token_no_corp'))
async def test_bad_token(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=token,
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 401


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_token_passport_500(
        b2b_authproxy_post_with_cargo_init, mockserver, cargo_robot_code,
):
    @mockserver.json_handler('/v1/cargo/test')
    async def _test(request):
        assert False

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        headers={},
        bearer='raise_500',
        cargo_robot_code=cargo_robot_code,
    )

    assert response.status_code == 500


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_token_route_passport_timeout(
        b2b_authproxy_post_with_cargo_init,
        mockserver,
        get_default_token,
        cargo_robot_code,
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
        bearer=get_default_token,
        cargo_robot_code=cargo_robot_code,
    )

    assert response.status_code == 504
    assert response.json() == {
        'code': '504',
        'message': 'Internal error: network read timeout',
    }


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
async def test_cache_token(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test', bearer=get_default_token, json=const.DEFAULT_REQUEST,
    )
    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        blackbox_tokens=[
            {
                'token': 'token_1',
                'yandex_uid': '2222',
                'scope': 'corptaxi:all',
                'login': 'login2',
            },
        ],
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 2
    assert response.status_code == 200
    assert response.json() == {'id': '123'}


async def test_token_if_cargo_robot(
        b2b_authproxy_post_with_cargo_init,
        test_handlers,
        get_default_token,
        mock_cargo_robot_client,
        mock_cargo_corp_perms,
        mock_taxicorp,
):
    test_handler = test_handlers(HANDLER_CARGO_CORP_AND_OWNER)
    mock_cargo_corp_perms.set_ok_response(perms=['owner'])
    mock_taxicorp.set_response_by_code(404)

    response = await b2b_authproxy_post_with_cargo_init(
        HANDLER_CARGO_CORP_AND_OWNER,
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=200,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    assert mock_taxicorp.times_called == 0
    assert mock_cargo_corp_perms.times_called == 1
    assert mock_cargo_robot_client.times_called == 1


async def test_token_if_cargo_employee(
        b2b_authproxy_post_with_cargo_init,
        test_handlers,
        get_default_token,
        mock_cargo_robot_client,
        mock_cargo_corp_perms,
        mock_cargocorp,
        mock_taxicorp,
):
    test_handler = test_handlers(HANDLER_CARGO_CORP_AND_OWNER)
    mock_cargo_corp_perms.set_ok_response(perms=['owner'])
    mock_cargocorp.set_ok_response(is_employee=True, is_enabled=True)
    mock_taxicorp.set_response_by_code(404)

    response = await b2b_authproxy_post_with_cargo_init(
        HANDLER_CARGO_CORP_AND_OWNER,
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        is_b2b_header_set=True,
        cargo_corp_code=200,
        cargo_robot_code=404,
    )

    assert test_handler.times_called == 1
    assert response.status_code == 200
    assert response.json() == {'id': '123'}

    assert mock_taxicorp.times_called == 0
    assert mock_cargocorp.times_called == 1
    assert mock_cargo_corp_perms.times_called == 1
    assert mock_cargo_robot_client.times_called == 0


@pytest.mark.parametrize(
    'cargocorp_code',
    [
        pytest.param(404, id='cargo empl 404'),
        pytest.param(500, id='cargo empl 500'),
    ],
)
async def test_token_if_not_cargo_employee(
        b2b_authproxy_post_with_cargo_init,
        test_handlers,
        get_default_token,
        mock_cargo_robot_client,
        mock_cargo_corp_perms,
        cargocorp_code,
        mock_cargocorp,
        mock_taxicorp,
):
    test_handler = test_handlers(HANDLER_CARGO_CORP_AND_OWNER)
    mock_taxicorp.set_response_by_code(404)

    response = await b2b_authproxy_post_with_cargo_init(
        HANDLER_CARGO_CORP_AND_OWNER,
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        is_b2b_header_set=True,
        cargo_corp_code=cargocorp_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 403

    assert mock_taxicorp.times_called == 1
    assert mock_cargocorp.times_called == 1
    assert mock_cargo_corp_perms.times_called == 0

    assert mock_cargo_robot_client.times_called == 0


async def test_token_route_401(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        mock_cargo_robot_client,
        mock_taxicorp,
):
    mock_taxicorp.set_response_by_code(404)

    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=404,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 401


@pytest.mark.parametrize(*const.CARGO_CORP_TOKEN_CASES)
@pytest.mark.config(B2B_AUTHPROXY_CORP_CLIENT_CUTOUT=[const.CORP_CLIENT_ID])
async def test_token_blocked_by_cutout(
        b2b_authproxy_post_with_cargo_init,
        test_handler,
        get_default_token,
        cargo_robot_code,
):
    response = await b2b_authproxy_post_with_cargo_init(
        'v1/cargo/test',
        json=const.DEFAULT_REQUEST,
        bearer=get_default_token,
        cargo_robot_code=cargo_robot_code,
    )

    assert test_handler.times_called == 0
    assert response.status_code == 403
    assert response.json() == {
        'code': 'access_denied',
        'message': 'Access denied',
    }
