# -*- coding: utf-8 -*-

from contextlib import contextmanager
import json

import mock
from nose.tools import eq_
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.exceptions import (
    AccountDisabledError,
    AccountNotFoundError,
    ValidationFailedError,
)
from passport.backend.api.views.bundle.otp.base import BaseBundleAppView
from passport.backend.core.builders.blackbox.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.builders.yasms import YaSmsTemporaryError
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.redis_manager.redis_manager import RedisError
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.exceptions import TrackNotFoundError
from passport.backend.utils.common import merge_dicts
from werkzeug.datastructures import Headers


@with_settings_hosts(BLACKBOX_URL='localhost')
class BaseBundleAppViewTestCase(BaseTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        headers = mock_headers(
            host='pass.ya.ru',
            user_ip='3.3.3.3',
            authorization='OAuth 123',
            other={
                'some_empty_header': '',
            },
        )
        self.headers = Headers(headers.items())
        self.base_params = {
            'headers': self.headers,
            'environ_overrides': {'REMOTE_ADDR': '127.0.0.1'},
        }

        self.default_url = '/1/test/'
        self.default_params = {'path': self.default_url, 'method': 'GET'}

    def tearDown(self):
        self.env.stop()
        del self.env

    @contextmanager
    def create_base_bundle(self, params):
        """
        @param params: это dict, с параметрами для werkzeug.EnvironBuilder
        """
        params = merge_dicts(self.base_params, params)

        with self.env.client.application.test_request_context(**params):
            # выполняю подготовку запроса, то есть выполняю функции из before_request_funcs
            self.env.client.application.preprocess_request()

            # создаю каждый раз, потому что именно так работает as_view,
            # он инстанцирует класс View на каждый запрос
            yield BaseBundleAppView()

    def test_process_request(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.process_request()
            eq_(bundle.response_values['server_time'], TimeNow())

    def test_respond_error(self):
        with self.create_base_bundle(self.default_params) as bundle:
            # ошибки аккаунта
            for error, slug in [
                (AccountDisabledError(), 'disabled'),
                (AccountNotFoundError(), 'not_found'),
            ]:
                error_response = bundle.respond_error(error)
                eq_(error_response.status_code, 200)
                eq_(
                    json.loads(error_response.data),
                    {
                        u'status': u'error',
                        u'errors': [u'account.%s' % slug],
                    }
                )

            # ValidationFailedError
            error_mock = mock.Mock()
            error_mock.error_dict = {
                'field': mock.Mock(),
            }
            error_mock.error_dict['field'].error_dict = {}
            error_mock.error_dict['field'].error_list = []
            error_mock.error_list = []
            error_response = bundle.respond_error(
                ValidationFailedError.from_invalid(error_mock),
            )
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'field.invalid'],
                }
            )

            # TrackNotFoundError
            error_response = bundle.respond_error(TrackNotFoundError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'track.not_found'],
                }
            )

            # BlackboxTemporaryError, YaSmsTemporaryError, DBError, RedisError
            # будут отдаваться как 'internal.temporary'
            errors = [
                BlackboxTemporaryError,
                YaSmsTemporaryError,
                DBError,
                RedisError,
                OAuthTemporaryError,
            ]
            for error in errors:
                error_response = bundle.respond_error(error())
                eq_(error_response.status_code, 200)
                eq_(
                    json.loads(error_response.data),
                    {
                        u'status': u'error',
                        u'errors': [u'internal.temporary'],
                    }
                )

            # InternalError
            error_response = bundle.respond_error(ValueError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'internal.permanent'],
                }
            )
