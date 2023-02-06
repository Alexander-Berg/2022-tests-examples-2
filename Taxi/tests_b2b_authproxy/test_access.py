import pytest


from tests_b2b_authproxy import const


HANDLER_CARGO_NO_AUTH = '/v1/cargo/proxy_401/no_auth'
HANDLER_CARGO_YA_AUTH = '/v1/cargo/proxy_401/ya_auth'
HANDLER_CARGO_PROXY_BUT_OWNER = '/v1/cargo/proxy_401/owner_only'
HANDLER_CARGO_CORP_AND_OWNER = '/v1/cargo/corp_auth/owner_only'

VARIANTS = ('', '/', '/tail')
HANDLER_UNCONFIGURED = '/v1/cargo/corp_auth/unknown/id_1'
HANDLER_CONFIGURED = '/v1/cargo/corp_auth/known/id_1'
HANDLER_SEVERAL_ARGS = '/v1/cargo/id_1/replace/id_2'


def get_handler_variants(handler):
    return (handler + variant for variant in VARIANTS)


class TestAccessControlAtWorkForCargo:
    @pytest.fixture(autouse=True)
    def init(
            self, access_control_enable, is_cargo_corp, blackbox_phone_context,
    ):
        blackbox_phone_context.is_secured = False

    @pytest.fixture
    def access_control_enable(self, taxi_config):
        taxi_config.set_values(dict(CARGO_B2B_ACCESS_CONTROL_ENABLED=True))

    @pytest.fixture
    def is_cargo_corp(self, mock_cargocorp):
        mock_cargocorp.set_ok_response(is_employee=True, is_enabled=True)

    @pytest.fixture
    def call_handler(self, b2b_authproxy_post, test_handlers):
        async def wrapper(
                handler,
                expected_code=None,
                expected_handler_times_called=None,
        ):
            test_handler = test_handlers(handler)

            response = await b2b_authproxy_post(
                handler, json=const.DEFAULT_REQUEST, is_b2b_header_set=True,
            )

            if expected_code:
                assert response.status_code == expected_code
            if expected_handler_times_called is not None:
                assert (
                    test_handler.times_called == expected_handler_times_called
                )
            return response.json()

        return wrapper

    @pytest.mark.parametrize(
        'handler_not_in_config',
        (
            const.PROXY_401_TEST_URL,
            *get_handler_variants(HANDLER_UNCONFIGURED),
        ),
    )
    async def test_url_not_in_access_config(
            self, call_handler, handler_not_in_config,
    ):
        response = await call_handler(
            handler_not_in_config,
            expected_code=403,
            expected_handler_times_called=0,
        )

        assert response == {
            'code': 'access_denied',
            'message': 'Access denied',
        }

    @pytest.mark.parametrize(
        'handler_requires_perm',
        (HANDLER_CARGO_PROXY_BUT_OWNER, HANDLER_CARGO_CORP_AND_OWNER),
    )
    async def test_no_perms(
            self, call_handler, handler_requires_perm, mock_cargo_corp_perms,
    ):
        response = await call_handler(
            handler_requires_perm,
            expected_code=403,
            expected_handler_times_called=0,
        )

        assert mock_cargo_corp_perms.times_called == 1
        assert response == {
            'code': 'no_permissions',
            'message': 'No permissions',
        }

    @pytest.mark.parametrize(
        'handler_in_access_config',
        (HANDLER_CARGO_NO_AUTH, HANDLER_CARGO_YA_AUTH),
    )
    async def test_auth_without_perms_ok(
            self,
            call_handler,
            handler_in_access_config,
            mock_cargo_corp_perms,
    ):
        response = await call_handler(
            handler_in_access_config,
            expected_code=200,
            expected_handler_times_called=1,
        )

        assert mock_cargo_corp_perms.times_called == 0
        assert response == {'id': '123'}

    @pytest.mark.parametrize(
        'is_phone_secured',
        (
            pytest.param(
                False,
                marks=pytest.mark.config(
                    CARGO_B2B_SECURED_PHONE_FOR_CORP_AUTH_REQUIRED=False,
                ),
                id='phone not secured & not required',
            ),
            pytest.param(
                True,
                marks=pytest.mark.config(
                    CARGO_B2B_SECURED_PHONE_FOR_CORP_AUTH_REQUIRED=True,
                ),
                id='phone is secured & is required',
            ),
        ),
    )
    @pytest.mark.parametrize(
        'handler_in_access_config',
        (
            HANDLER_CARGO_PROXY_BUT_OWNER,
            HANDLER_CARGO_CORP_AND_OWNER,
            *get_handler_variants(HANDLER_CONFIGURED),
            *get_handler_variants(HANDLER_SEVERAL_ARGS),
        ),
    )
    async def test_perms_ok__phone_satisfies(
            self,
            blackbox_phone_context,
            is_phone_secured,
            call_handler,
            handler_in_access_config,
            mock_cargo_corp_perms,
    ):
        blackbox_phone_context.is_secured = is_phone_secured
        mock_cargo_corp_perms.set_ok_response(
            perms=['some_other_perm', 'owner'],
        )

        response = await call_handler(
            handler_in_access_config,
            expected_code=200,
            expected_handler_times_called=1,
        )

        assert mock_cargo_corp_perms.times_called == 1
        assert response == {'id': '123'}

    @pytest.mark.config(CARGO_B2B_SECURED_PHONE_FOR_CORP_AUTH_REQUIRED=True)
    @pytest.mark.parametrize(
        'handler_in_access_config',
        (
            HANDLER_CARGO_PROXY_BUT_OWNER,
            HANDLER_CARGO_CORP_AND_OWNER,
            *get_handler_variants(HANDLER_CONFIGURED),
            *get_handler_variants(HANDLER_SEVERAL_ARGS),
        ),
    )
    async def test_perms_ok__phone_unsecured(
            self,
            call_handler,
            handler_in_access_config,
            mock_cargo_corp_perms,
    ):
        mock_cargo_corp_perms.set_ok_response(
            perms=['some_other_perm', 'owner'],
        )

        response = await call_handler(
            handler_in_access_config,
            expected_code=403,
            expected_handler_times_called=0,
        )

        assert response == {
            'code': 'no_secured_phone',
            'message': 'Access denied',
        }

    @pytest.mark.parametrize(
        'handler_requires_perm',
        (HANDLER_CARGO_PROXY_BUT_OWNER, HANDLER_CARGO_CORP_AND_OWNER),
    )
    @pytest.mark.parametrize('perms', (['owner'], ['not_owner']))
    async def test_perms_cache(
            self,
            perms,
            call_handler,
            handler_requires_perm,
            mock_cargo_corp_perms,
    ):
        mock_cargo_corp_perms.set_ok_response(perms=perms)

        for _ in range(2):
            await call_handler(handler_requires_perm)

        assert mock_cargo_corp_perms.times_called == 1


class TestAccessControlIfNoOrYaAuthRequired:
    @pytest.fixture(autouse=True)
    def init(self, access_control_enable, mock_cargocorp):
        pass

    @pytest.fixture
    def access_control_enable(self, taxi_config):
        taxi_config.set_values(dict(CARGO_B2B_ACCESS_CONTROL_ENABLED=True))

    @pytest.fixture
    def call_handler(self, b2b_authproxy_post, test_proxy_401_handlers):
        async def wrapper(
                handler,
                expected_code,
                expected_handler_times_called,
                session=None,
                expected_b2b_header=None,
        ):
            test_handler = test_proxy_401_handlers(
                handler, expected_b2b_header=expected_b2b_header,
            )

            response = await b2b_authproxy_post(
                handler,
                json=const.DEFAULT_REQUEST,
                session=session,
                is_b2b_header_set=True,
            )

            assert response.status_code == expected_code
            assert test_handler.times_called == expected_handler_times_called
            return response.json()

        return wrapper

    @pytest.fixture
    def assert_call_no_auth_ok(self, call_handler):
        async def wrapper(session=None, expected_b2b_header=None):
            response = await call_handler(
                HANDLER_CARGO_NO_AUTH,
                expected_code=200,
                expected_handler_times_called=1,
                session=session,
                expected_b2b_header=expected_b2b_header,
            )

            assert response == {'id': '123'}

        return wrapper

    async def test_no_auth_at_all(self, assert_call_no_auth_ok):
        await assert_call_no_auth_ok(session='unknown_session')

    @pytest.mark.parametrize(
        'is_employee_enabled, expected_b2b_header',
        ((True, const.CORP_CLIENT_ID), (False, None)),
    )
    async def test_no_auth_required(
            self,
            mock_cargocorp,
            assert_call_no_auth_ok,
            is_employee_enabled,
            expected_b2b_header,
    ):
        mock_cargocorp.set_ok_response(
            is_employee=True, is_enabled=is_employee_enabled,
        )

        await assert_call_no_auth_ok(expected_b2b_header=expected_b2b_header)

    async def test_ya_auth_required(self, call_handler):
        response = await call_handler(
            HANDLER_CARGO_YA_AUTH,
            expected_code=401,
            expected_handler_times_called=0,
            session='unknown_session',
        )

        assert response == {'code': 'unauthorized', 'message': 'Access denied'}


class TestAccessControlDoesNotEffectCases:
    ACCESS_CONTROL_CASES = [
        pytest.param(
            flg,
            marks=pytest.mark.config(CARGO_B2B_ACCESS_CONTROL_ENABLED=flg),
        )
        for flg in (True, False)
    ]

    PROXY_ROUTE_HANDLERS = [
        'v1/cargo/test',
        const.PROXY_401_TEST_URL,
        HANDLER_CARGO_NO_AUTH,
        HANDLER_CARGO_YA_AUTH,
        HANDLER_CARGO_PROXY_BUT_OWNER,
        HANDLER_CARGO_CORP_AND_OWNER,
        'v1/cargo/not_in_access_config',
    ]

    @pytest.fixture
    def assert_call_ok(
            self, b2b_authproxy_post_with_cargo_init, test_handlers,
    ):
        async def wrapper(handler, kwargs):
            test_handler = test_handlers(handler)

            response = await b2b_authproxy_post_with_cargo_init(
                handler, json=const.DEFAULT_REQUEST, **kwargs,
            )

            assert response.status_code == 200
            assert test_handler.times_called == 1
            assert response.json() == {'id': '123'}

        return wrapper

    @pytest.mark.parametrize(*const.CARGO_CORP_CASES)
    @pytest.mark.parametrize('ac_enabled', ACCESS_CONTROL_CASES)
    @pytest.mark.parametrize('handler', PROXY_ROUTE_HANDLERS)
    async def test_taxi_session(
            self,
            assert_call_ok,
            ac_enabled,
            handler,
            is_b2b_header_set,
            cargo_corp_code,
    ):
        await assert_call_ok(
            handler,
            dict(
                is_b2b_header_set=is_b2b_header_set,
                cargo_corp_code=cargo_corp_code,
            ),
        )

    @pytest.mark.parametrize('cargo_corp_code', (200, 500))
    @pytest.mark.parametrize('ac_enabled', ACCESS_CONTROL_CASES)
    @pytest.mark.parametrize('handler', PROXY_ROUTE_HANDLERS)
    async def test_taxi_token(
            self,
            assert_call_ok,
            ac_enabled,
            handler,
            get_default_token,
            cargo_corp_code,
    ):
        await assert_call_ok(
            handler,
            dict(bearer=get_default_token, cargo_corp_code=cargo_corp_code),
        )

    @pytest.mark.config(CARGO_B2B_ACCESS_CONTROL_ENABLED=False)
    @pytest.mark.parametrize('handler', PROXY_ROUTE_HANDLERS)
    async def test_cargo_session_ac_disabled(
            self, mock_cargocorp, assert_call_ok, handler,
    ):
        mock_cargocorp.set_ok_response(is_employee=True, is_enabled=True)

        await assert_call_ok(
            handler, dict(is_b2b_header_set=True, cargo_corp_code=200),
        )
