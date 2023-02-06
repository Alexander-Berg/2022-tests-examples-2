# -*- coding: utf-8 -*-
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_AUTH_HEADER,
    TEST_EMPTY_SESSION_COOKIE,
    TEST_USER_COOKIE,
)
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response


class GetAccountBySessionOrTokenMixin(object):
    """
    Миксин для тестирования общих кейсов при получении аккаунта по сессии или токену.
    Классу, который будет наследоваться от него, необходимы следующие методы:
        * make_request(self, headers=None, ...)
        * build_headers(self, **headers) - только для тесткейсов, не использующих BaseBundleTestViews:make_request
        * set_blackbox_response(self, scope=TEST_OAUTH_SCOPE, ...)
    С дефолтными параметрами тестируемая ручка должна работать по сессии или токену (не по уиду!)
    """
    def _headers(self, **kwargs):
        # Костыль: есть новые тесткейсы, юзающие BaseBundleTestViews:make_request,
        # есть старые с самописными make_request. Мы должны отработать в обоих случаях.
        if hasattr(self, 'build_headers'):
            return self.build_headers(**kwargs)
        else:
            return kwargs

    def test_by_oauth_token_missing_header(self):
        response = self.make_request(
            headers=self._headers(
                cookie=None,
                authorization=None,
            ),
        )
        self.assert_error_response(response, ['request.credentials_all_missing'], check_content=False)

    def test_by_oauth_token_missing_scope(self):
        self.set_blackbox_response(
            scope='',
        )
        response = self.make_request(
            headers=self._headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        self.assert_error_response(response, ['oauth_token.invalid'], check_content=False)

    def test_session_and_token_in_request_error(self):
        response = self.make_request(
            headers=self._headers(
                cookie=TEST_USER_COOKIE,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        self.assert_error_response(response, ['request.credentials_several_present'], check_content=False)

    def test_empty_session_cookie_and_oauth_token_present(self):
        response = self.make_request(
            headers=self._headers(
                cookie=TEST_EMPTY_SESSION_COOKIE,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        self.assert_error_response(response, ['request.credentials_several_present'], check_content=False)

    def test_empty_session_cookie_and_no_oauth_token(self):
        response = self.make_request(
            headers=self._headers(
                cookie=TEST_EMPTY_SESSION_COOKIE,
                authorization=None,
            ),
        )
        self.assert_error_response(response, ['sessionid.invalid'], check_content=False)

    def test_auth_header_invalid(self):
        for header in ('', ' ', 'Oauth', 'Oauth  ', 'auth'):
            response = self.make_request(
                headers=self._headers(
                    cookie=None,
                    authorization=header,
                ),
            )
            self.assert_error_response(response, ['authorization.invalid'], check_content=False)

    def test_bb_response_invalid(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
            ),
        )
        response = self.make_request(
            headers=self._headers(
                cookie=None,
                authorization=TEST_AUTH_HEADER,
            ),
        )
        self.assert_error_response(response, ['oauth_token.invalid'], check_content=False)
