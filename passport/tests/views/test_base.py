# -*- coding: utf-8 -*-

from contextlib import contextmanager
import json
import unittest

from flask.globals import request
import mock
from nose.tools import (
    assert_is_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.adm_api.common.exceptions import (
    AccountDisabledError,
    AuthorizationHeaderError,
    HeadersEmptyError,
    OAuthTokenValidationError,
    SessionidInvalidError,
    ValidationFailedError,
)
from passport.backend.adm_api.test.mock_objects import (
    mock_grants,
    mock_headers,
)
from passport.backend.adm_api.test.utils import with_settings_hosts
from passport.backend.adm_api.test.views import ViewsTestEnvironment
from passport.backend.adm_api.tests.base.forms import TestForm
from passport.backend.adm_api.tests.views.base_test_data import TEST_UID
from passport.backend.adm_api.views.base import (
    ADM_API_OAUTH_SCOPE,
    BaseView,
)
from passport.backend.adm_api.views.headers import (
    Header,
    HEADER_CLIENT_COOKIE,
    HEADER_CLIENT_HOST,
    HEADER_CONSUMER_AUTHORIZATION,
    HEADER_CONSUMER_CLIENT_IP,
)
from passport.backend.core import validators
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_sessionid_response,
)
from passport.backend.utils.common import merge_dicts
from werkzeug.datastructures import Headers


@with_settings_hosts()
class TestApiRequiredHeaders(unittest.TestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        bundle_views = [(key, value) for key, value in self.env.client.application.view_functions.items() if 'api' in key]

        self.apis = []

        for name, view_func in bundle_views:
            rule = self.env.client.application.url_map._rules_by_endpoint.get(name)
            if rule:
                rule = rule[0]

                # удаляем методы, зачем-то добавленные flask-ом/werkzeug-ом
                if 'OPTIONS' in rule.methods:
                    rule.methods.remove('OPTIONS')
                if 'HEAD' in rule.methods:
                    rule.methods.remove('HEAD')

                # (имя бандла, view_class, url, methods)
                # имя бандла: строка
                # view_class: класс данного бандла
                # url: строка
                # methods: set из http методов
                self.apis.append(
                    (name, view_func.view_class(), rule.rule, rule.methods),
                )

    def tearDown(self):
        self.env.stop()

    def bundle_request(self, method, params):
        return getattr(self.env.client, method)(**params)

    def test_need_headers(self):
        for bundle_name, view_class, path, methods in self.apis:
            if not view_class.required_headers:
                continue
            for method in methods:
                method = method.lower()
                params = {'path': path}

                rv = self.bundle_request(method, params)
                eq_(rv.status_code, 200, [rv.data, bundle_name])
                response = json.loads(rv.data)
                eq_(
                    response['errors'],
                    HeadersEmptyError(
                        [h.code_for_error for h in view_class.required_headers],
                    ).errors,
                    [rv.data, bundle_name],
                )

    def test_need_grants(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(login='looser', attributes=[]),
        )
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(login='looser', scope=ADM_API_OAUTH_SCOPE, attributes=[]),
        )
        self.env.grants_loader.set_grants_json(mock_grants())
        for bundle_name, view_class, path, methods in self.apis:
            if not view_class.required_grants:
                continue
            for method in methods:
                method = method.lower()
                params = {
                    'path': path,
                    'headers': {
                        HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                        HEADER_CLIENT_HOST.name: 'yandex-team.ru',
                    },
                }
                if view_class.session_required:
                    params['headers'][HEADER_CLIENT_COOKIE.name] = 'Session_id=good'
                if view_class.token_required:
                    params['headers'][HEADER_CONSUMER_AUTHORIZATION.name] = 'OAuth 1234'

                rv = self.bundle_request(method, params)
                eq_(rv.status_code, 200, [rv.data, bundle_name])
                response = json.loads(rv.data)
                eq_(
                    response['errors'],
                    ['access.denied'],
                    [rv.data, bundle_name],
                )


class TestBaseView(unittest.TestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        headers = mock_headers(
            host='pass.ya.ru',
            user_ip='3.3.3.3',
            cookie='Session_id=invalid',
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

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(attributes=[]),
        )
        self.env.grants_loader.set_grants_json(mock_grants())

    def tearDown(self):
        self.env.stop()

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
            yield BaseView()


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    HTTPS_ONLY=False,
)
class TestBaseViewHttpsOnlyFalse(TestBaseView):

    def test_empty_init_static_variables(self):
        with self.create_base_bundle({}) as bundle:
            eq_(bundle.form_values, {})
            eq_(bundle.path_values, {})
            eq_(bundle.response_values, {})

            eq_(bundle.required_headers, [HEADER_CONSUMER_CLIENT_IP, HEADER_CLIENT_COOKIE, HEADER_CLIENT_HOST])
            assert_is_none(bundle.basic_form)
            assert_is_none(bundle.required_grants)

    def test_empty_empty_context(self):
        params = []
        for m in ['GET', 'POST', 'PUT', 'DELETE']:
            params.append({'path': self.default_url, 'method': m})

        for p in params:
            with self.create_base_bundle(p) as bundle:
                eq_(bundle.all_values, {}, [bundle.all_values, p])
                eq_(bundle.request_values, {}, [bundle.request_values, p])
                eq_(bundle.request, request)
                for h in self.headers.keys():
                    eq_(bundle.headers.get(h), self.headers.get(h))
                eq_(str(bundle.consumer_ip), '127.0.0.1')
                eq_(str(bundle.client_ip), '3.3.3.3')
                eq_(bundle.host, 'pass.ya.ru')
                eq_(bundle.user_agent, None)
                eq_(bundle.required_headers, [HEADER_CONSUMER_CLIENT_IP, HEADER_CLIENT_COOKIE, HEADER_CLIENT_HOST])

    def test_with_simple_context_cached_property_property(self):
        params = [
            ({'path': '/1/questions/', 'method': 'GET',
              'query_string': 'field=10'},
             {'field': '10'}),
            ({'path': '/1/account/', 'method': 'POST', 'data': {'field': '20'}},
             {'field': '20'}),
            ({'path': '/1/questions/', 'method': 'DELETE',
              'data': {'field': '20', 'test': 'test'},
              'query_string': 'test2=test2'},
             {'test2': 'test2'}),
        ]

        for i, (p, result) in enumerate(params):
            with self.create_base_bundle(p) as bundle:
                eq_(bundle.all_values, result, [i, bundle.all_values, result, p])
                eq_(bundle.request_values, result, [i, bundle.request_values, result, p])
                eq_(bundle.request, request)
                for h in self.headers.keys():
                    eq_(bundle.headers.get(h), self.headers.get(h))
                eq_(str(bundle.consumer_ip), '127.0.0.1')
                eq_(str(bundle.client_ip), '3.3.3.3')
                eq_(bundle.host, 'pass.ya.ru')

    def test_dispatch_request_with_respond_success(self):
        params = {
            'path': '/1/test/?field=10',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CLIENT_HOST.name: 'yandex-team.ru',
                HEADER_CLIENT_COOKIE.name: 'Session_id=invalid',
            },
        }
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'ok', u'test_param': 1})

    def test_dispatch_request_with_required_headers_success(self):
        params = {'path': '/1/test/?field=20', 'method': 'GET',
                  'headers': {HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40'}}
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP]
            bundle.session_required = False
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'ok', u'test_param': 1})

    def test_dispatch_request_with_required_headers_error(self):
        params = {'path': '/1/test/?field=20', 'method': 'GET',
                  'headers': {HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40'}}
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP, HEADER_CLIENT_HOST]
            bundle.session_required = False
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {'status': 'error', 'errors': ['host.empty']})

    def test_dispatch_request_with_required_grants_success(self):
        params = {'path': '/1/test/?field=20', 'method': 'GET',
                  'headers': {
                      HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                      HEADER_CLIENT_COOKIE.name: 'Session_id=valid;sessionid2=secure',
                  }}
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(login='lite_support', attributes=[]),
        )
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP]
            bundle.required_grants = ['allow_search']
            bundle.session_required = True

            r = bundle.dispatch_request(uid=1234)
            eq_(json.loads(r.data), {u'status': u'ok', u'test_param': 1})
            ok_(bundle.is_grant_available('allow_search'))
            ok_(not bundle.is_grant_available('show_history'))
            self.env.blackbox.requests[0].assert_query_contains(dict(aliases='all'))

    def test_dispatch_request_with_required_grants_error(self):
        params = {'path': '/1/test/?field=20', 'method': 'GET',
                  'headers': {
                      HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                      HEADER_CLIENT_COOKIE.name: 'Session_id=valid;sessionid2=secure',
                  }}
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(login='lite_support', attributes=[]),
        )
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP]
            bundle.required_grants = ['allow_search', 'show_history']
            bundle.session_required = True

            r = bundle.dispatch_request(uid=1234)
            eq_(json.loads(r.data), {u'status': u'error', u'errors': [u'access.denied']})

    def test_dispatch_request_with_respond_error(self):
        params = {'path': '/1/test/?field=20', 'method': 'GET'}
        with self.create_base_bundle(params) as bundle:
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'error', u'errors': [u'exception.unhandled']})

    def test_process_request(self):
        with self.create_base_bundle(self.default_params) as bundle:
            assert_raises(NotImplementedError, bundle.process_request)

    def test_respond_success(self):
        with self.create_base_bundle(self.default_params) as bundle:

            eq_(bundle.response_values, {})
            success_response = bundle.respond_success()

            eq_(success_response.status_code, 200)
            eq_(json.loads(success_response.data), {u'status': u'ok'})

    def test_respond_error(self):
        with self.create_base_bundle(self.default_params) as bundle:

            # BaseBundleError
            error_response = bundle.respond_error(HeadersEmptyError(['ip']))
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'ip.empty'],
                }
            )

            # InternalError
            error_response = bundle.respond_error(ValueError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'exception.unhandled'],
                }
            )

            # BlackboxTemporaryError, YaSmsTemporaryError, DBError, RedisError
            # будут отдаваться как 'backend.%s_failed'
            errors = [
                (blackbox.BlackboxTemporaryError, 'blackbox'),
            ]
            for error, slug in errors:
                error_response = bundle.respond_error(error())
                eq_(error_response.status_code, 200)
                eq_(
                    json.loads(error_response.data),
                    {
                        u'status': u'error',
                        u'errors': [u'backend.%s_failed' % slug],
                    }
                )

    def test_check_headers(self):
        with self.create_base_bundle(self.default_params) as bundle:
            assert_is_none(bundle.check_headers([Header(h, h, True) for h in self.headers.keys()]))
            with self.assertRaises(HeadersEmptyError) as e:
                bundle.check_headers([Header('test-header', 'test-alias', True)])

            exc = e.exception
            eq_(exc.errors, ['test-alias.empty'])

    def test_check_header(self):
        with self.create_base_bundle(self.default_params) as bundle:
            for h in self.headers.keys():
                assert_is_none(bundle.check_header(Header(h, h, True)))
            with self.assertRaises(HeadersEmptyError) as e:
                bundle.check_header(Header('test-header', 'test-alias', True))

            exc = e.exception
            eq_(exc.errors, ['test-alias.empty'])

    def test_check_header_with_empty_value(self):
        with self.create_base_bundle(self.default_params) as bundle:
            assert_is_none(bundle.check_header(Header('some_empty_header', 'test-alias', True)))
            with self.assertRaises(HeadersEmptyError) as e:
                bundle.check_header(Header('some_empty_header', 'test-alias', False))

            exc = e.exception
            eq_(exc.errors, ['test-alias.empty'])

    def test_check_session_empty_session_id(self):
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CLIENT_HOST.name: 'yandex-team.ru',
                HEADER_CLIENT_COOKIE.name: 'Session_id=',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(SessionidInvalidError):
                bundle.check_session()

    def test_check_session_ssl_session_id_not_required(self):
        params = {
            'base_url': 'https://localhost/',
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CLIENT_HOST.name: 'yandex-team.ru',
                HEADER_CLIENT_COOKIE.name: 'Session_id=123;sessionid2=',
            },
        }
        with self.create_base_bundle(params) as bundle:
            bundle.check_session()
            eq_(bundle.support_account.uid, TEST_UID)

    def test_check_session_invalid_session_id(self):
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CLIENT_HOST.name: 'yandex-team.ru',
                HEADER_CLIENT_COOKIE.name: 'Session_id=invalid',
            },
        }
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_response(
                status=blackbox.BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(SessionidInvalidError):
                bundle.check_session()

    def test_check_oauth_token_header_invalid(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            blackbox.BlackboxTemporaryError,
        )
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CONSUMER_AUTHORIZATION.name: 'oaut 1234',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(AuthorizationHeaderError):
                bundle.check_oauth_token()

    def test_check_oauth_token_blackbox_error(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'oauth',
            blackbox.BlackboxTemporaryError,
        )
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CONSUMER_AUTHORIZATION.name: 'oauth 1234',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(blackbox.BlackboxTemporaryError):
                bundle.check_oauth_token()

    def test_check_oauth_token_account_disabled(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_DISABLED_STATUS, attributes=[]),
        )
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CONSUMER_AUTHORIZATION.name: 'oauth 1234',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(AccountDisabledError):
                bundle.check_oauth_token()

    def test_check_oauth_token_invalid(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS, attributes=[]),
        )
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CONSUMER_AUTHORIZATION.name: 'oauth 1234',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(OAuthTokenValidationError):
                bundle.check_oauth_token()

    def test_check_oauth_token_no_scope(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(scope='some_irrelevant_scope', attributes=[]),
        )
        params = {
            'path': '/1/test/?field=20',
            'method': 'GET',
            'headers': {
                HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40',
                HEADER_CONSUMER_AUTHORIZATION.name: 'oauth 1234',
            },
        }
        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(OAuthTokenValidationError):
                bundle.check_oauth_token()

    def test_process_basic_form(self):
        params = {'path': '/1/test/?field=5', 'method': 'GET'}

        with self.create_base_bundle(params) as bundle:
            bundle.basic_form = TestForm
            eq_(bundle.all_values, {'field': '5'})
            bundle.process_basic_form()
            eq_(bundle.form_values, {'field': 5})

    def test_process_form_with_exception(self):
        params = {'path': '/1/test/?field=100500', 'method': 'GET'}

        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(ValidationFailedError):
                bundle.process_form(TestForm, bundle.all_values)

    def test_as_view(self):
        params = merge_dicts(
            self.base_params,
            {'path': '/1/test/', 'method': 'GET'},
        )

        process_request_mock = mock.Mock()
        process_request_mock.return_value = True

        bundle = BaseView.as_view()

        with mock.patch.object(BaseView, 'process_request', process_request_mock), \
                self.env.client.application.test_request_context(**params):
            self.env.client.application.preprocess_request()

            bundle = bundle.view_class()

            eq_(bundle.form_values, {})
            eq_(bundle.path_values, {})
            eq_(bundle.response_values, {})

            assert_is_none(bundle.basic_form)
