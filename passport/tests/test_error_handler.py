# -*- coding: utf-8 -*-

from nose.tools import eq_
from passport.backend.social.common import exception as common_exceptions
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.proxy2.error_handler import ErrorHandler
from passport.backend.social.proxy2.exception import (
    InvalidParametersError,
    ProfileNotFoundError,
    ProxyMethodNotImplementedError,
    TokensNotFoundError,
)


class TestErrorHandler(TestCase):
    def _tst_result(self, ex, type_='external', code=None):
        try:
            raise ex
        except Exception as ex:
            data = ErrorHandler(ex).exception_to_response()

        eq_(data['state'], 'failure')
        if code is not None:
            eq_(data['reason']['code'], code)
            eq_(data['reason']['type'], type_)

    def test_basic(self):
        self._tst_result(ProxyMethodNotImplementedError(), code='not_implemented_error')
        self._tst_result(ProfileNotFoundError(), code='profile_not_found')
        self._tst_result(TokensNotFoundError(), code='no_tokens_found')

        self._tst_result(common_exceptions.ProviderCommunicationProxylibError(), code='api_error')
        self._tst_result(common_exceptions.InvalidTokenProxylibError(), code='invalid_token')
        self._tst_result(common_exceptions.PermissionProxylibError(), code='permission_error')
        self._tst_result(InvalidParametersError(), code='invalid_parameters')
        self._tst_result(common_exceptions.ProviderRateLimitExceededProxylibError(), code='rate_limit_exceeded')
        self._tst_result(common_exceptions.SocialUserDisabledProxylibError(), code='user_disabled')
        self._tst_result(common_exceptions.AlbumNotExistsProxylibError(), code='album_not_exists')
        self._tst_result(common_exceptions.DatabaseError(), code='internal_error', type_='internal')

    def test_internal_proxylib_error(self):
        self.assertTrue(ErrorHandler(common_exceptions.InternalProxylibError()).exception_to_response() is None)

    def test_key_error(self):
        self.assertTrue(ErrorHandler(KeyError()).exception_to_response() is None)
