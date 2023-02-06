# -*- coding: utf-8 -*-
from contextlib import contextmanager
import json

from flask import request
import mock
from nose.tools import (
    assert_is_none,
    assert_is_not_none,
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.api.common.processes import PROCESS_RESTORE
from passport.backend.api.forms import LoginValidation
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.views.bundle.base import BaseBundleView
from passport.backend.api.views.bundle.exceptions import (
    AccountDisabledError,
    AuthorizationHeaderError,
    HeadersEmptyError,
    InvalidTrackStateError,
    ValidationFailedError,
)
from passport.backend.api.views.bundle.headers import (
    Header,
    HEADER_CLIENT_HOST,
    HEADER_CONSUMER_CLIENT_IP,
)
from passport.backend.core.builders.blackbox.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_loginoccupation_response
from passport.backend.core.builders.oauth import OAuthTemporaryError
from passport.backend.core.builders.yasms import YaSmsTemporaryError
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.grants import MissingGrantsError
from passport.backend.core.redis_manager.redis_manager import RedisError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.tracks.exceptions import TrackNotFoundError
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_CLIENT_ID_2,
    TEST_INVALID_TICKET,
    TEST_TICKET,
)
from passport.backend.core.types.file import File
from passport.backend.core.ydb.exceptions import YdbTemporaryError
from passport.backend.utils.common import merge_dicts
from six import StringIO
from werkzeug.datastructures import Headers


@with_settings_hosts(BLACKBOX_URL='localhost')
class BaseBundleViewTestCase(BaseTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID): {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        headers = mock_headers(
            host='pass.ya.ru',
            user_ip='3.3.3.3',
            authorization='OAuth My_token-123',
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

        self.no_grants_error = MissingGrantsError('missing_grant', '127.0.0.1', 'passport', TEST_CLIENT_ID)

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid()

        self.env.grants.set_grants_return_value(mock_grants(grants={'account': ['phone']}))

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.env.stop()
        del self.fake_tvm_credentials_manager
        del self.env
        del self.track_manager

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
            yield BaseBundleView()

    def test_empty_init_static_variables(self):
        with self.create_base_bundle({}) as bundle:
            assert_is_none(bundle.consumer)
            eq_(bundle.form_values, {})
            eq_(bundle.path_values, {})
            eq_(bundle.response_values, {})
            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            assert_is_none(bundle.basic_form)
            ok_(not bundle.require_track)
            assert_is_none(bundle.required_headers)
            assert_is_none(bundle.required_grants)
            ok_(not bundle.require_process)
            assert_is_none(bundle.process_name)
            assert_is_none(bundle.allowed_processes)

    def test_empty_empty_context(self):
        params = []
        for m in ['GET', 'POST', 'PUT', 'DELETE']:
            params.append({'path': self.default_url, 'method': m})

        for p in params:
            with self.create_base_bundle(p) as bundle:
                eq_(bundle.all_values, {}, [bundle.all_values, p])
                eq_(bundle.request_values, {}, [bundle.request_values, p])
                eq_(bundle.request_files, {}, [bundle.request_files, p])
                assert_is_not_none(bundle.track_manager)
                eq_(bundle.request, request)
                for h in self.headers.keys():
                    eq_(bundle.headers.get(h), self.headers.get(h))
                eq_(str(bundle.consumer_ip), '127.0.0.1')
                eq_(str(bundle.client_ip), '3.3.3.3')
                eq_(bundle.host, 'pass.ya.ru')
                eq_(bundle.authorization, 'OAuth My_token-123')
                eq_(bundle.oauth_token, 'My_token-123')

    def test_with_simple_context_cached_property_property(self):
        params = [
            ({'path': '/1/questions/?consumer=dev&track_id=1234', 'method': 'GET'},
             {'consumer': 'dev', 'track_id': '1234'},
             {}),
            ({'path': '/1/questions/', 'method': 'GET',
              'query_string': 'consumer=dev'},
             {'consumer': 'dev'},
             {}),
            ({'path': '/1/questions/', 'method': 'GET',
              'data': {'consumer': 'dev', 'test': 'test', 'file': (StringIO(''), 'hw.txt')}},
             {},
             {}),
            ({'path': '/1/account/?consumer=dev', 'method': 'POST'},
             {'consumer': 'dev'},
             {}),
            ({'path': '/1/account/', 'method': 'POST', 'query_string': 'consumer=dev'},
             {'consumer': 'dev'},
             {}),
            ({'path': '/1/account/', 'method': 'POST', 'data': {'consumer': 'dev'}},
             {},
             {}),
            ({'path': '/1/account/?consumer=dev', 'method': 'POST',
              'data': {'consumer': 'mail'}},
             {'consumer': 'dev'},
             {}),
            ({'path': '/1/questions/', 'method': 'DELETE',
              'data': {'consumer': 'dev', 'test': 'test'},
              'query_string': 'test2=test2'},
             {'test2': 'test2'},
             {}),
            ({'method': 'POST',
              'data': {'file': (StringIO('hello world'), 'hw.txt')}},
             {},
             {'file': (File('hw.txt', StringIO('hello world')),)}),
        ]

        for p, result, files in params:
            with self.create_base_bundle(p) as bundle:
                eq_(bundle.all_values, result, [bundle.all_values, result, p])
                eq_(bundle.request_values, result, [bundle.request_values, result, p])
                eq_(bundle.request_files, files, [bundle.request_files, files, p])
                assert_is_not_none(bundle.track_manager)
                eq_(bundle.request, request)
                for h in self.headers.keys():
                    eq_(bundle.headers.get(h), self.headers.get(h))
                eq_(str(bundle.consumer_ip), '127.0.0.1')
                eq_(str(bundle.client_ip), '3.3.3.3')
                eq_(bundle.host, 'pass.ya.ru')
                eq_(bundle.authorization, 'OAuth My_token-123')
                eq_(bundle.oauth_token, 'My_token-123')

    def test_property_oauth_token_invalid(self):
        headers = mock_headers(host='pass.ya.ru', user_ip='3.3.3.3', authorization='Invalid authorization')
        self.base_params['headers'] = Headers(headers.items())
        with self.assertRaises(AuthorizationHeaderError):
            with self.create_base_bundle({}) as bundle:
                bundle.oauth_token

    def test_dispatch_request_with_respond_success(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET'}
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'ok', u'test_param': 1})

    def test_dispatch_request_with_required_empty_host_header_error(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET',
                  'headers': {HEADER_CLIENT_HOST.name: '   '}}
        with self.create_base_bundle(params) as bundle:
            bundle.required_headers = [HEADER_CLIENT_HOST]
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {'status': 'error', 'errors': ['host.empty']})

    def test_dispatch_request_with_required_headers_success(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET',
                  'headers': {HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40'}}
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP]
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'ok', u'test_param': 1})

    def test_dispatch_request_with_required_headers_error(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET',
                  'headers': {HEADER_CONSUMER_CLIENT_IP.name: '100.200.30.40'}}
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_headers = [HEADER_CONSUMER_CLIENT_IP, HEADER_CLIENT_HOST]
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {'status': 'error', 'errors': ['host.empty']})

    def test_dispatch_request_with_respond_error(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET'}
        with self.create_base_bundle(params) as bundle:
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data), {u'status': u'error', u'errors': [u'exception.unhandled']})

    def test_dispatch_request_with_required_grants_error(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET'}
        self.env.grants.set_grants_return_value(mock_grants(grants={}))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_grants = ['grant1', 'grant2']
            bundle.consumer = 'dev'
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            response = json.loads(r.data)
            eq_(response['errors'], [u'access.denied'])
            eq_(
                response['error_message'],
                'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None. Required grants: %r' % bundle.required_grants,
            )

    def test_dispatch_request_with_required_grants_success(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET'}
        self.env.grants.set_grants_return_value(mock_grants(grants={}))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: bundle.response_values.update({'test_param': 1})

            bundle.required_grants = ['grant1']
            bundle.consumer = 'dev'
            r = bundle.dispatch_request(uid=1234)
            eq_(bundle.path_values, {'uid': 1234})
            eq_(json.loads(r.data)['errors'], [u'access.denied'])

    def test_process_request(self):
        with self.create_base_bundle(self.default_params) as bundle:
            assert_raises(NotImplementedError, bundle.process_request)

    def test_respond_forbidden(self):
        with self.create_base_bundle(self.default_params) as bundle:
            missing_grants_error = bundle.respond_grants_forbidden(self.no_grants_error)

            eq_(missing_grants_error.status_code, 403)
            eq_(
                json.loads(missing_grants_error.data),
                {
                    u'status': u'error',
                    u'errors': ['access.denied'],
                    u'error_message': u'Access denied for ip: 127.0.0.1; consumer: passport; tvm_client_id: %s. Required grants: missing_grant' % TEST_CLIENT_ID,
                },
            )

    def test_respond_success(self):
        with self.create_base_bundle(self.default_params) as bundle:

            eq_(bundle.response_values, {})
            success_response = bundle.respond_success()

            eq_(success_response.status_code, 200)
            eq_(json.loads(success_response.data), {u'status': u'ok'})

    def test_respond_error(self):
        with self.create_base_bundle(self.default_params) as bundle:

            # GrantsError
            error_response = bundle.respond_error(self.no_grants_error)
            eq_(error_response.status_code, 403)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': ['access.denied'],
                    u'error_message': u'Access denied for ip: 127.0.0.1; consumer: passport; tvm_client_id: %s. Required grants: missing_grant' % TEST_CLIENT_ID,
                },
            )

            # BaseBundleError
            error_response = bundle.respond_error(AccountDisabledError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'account.disabled'],
                },
            )

            # InternalError
            error_response = bundle.respond_error(ValueError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'exception.unhandled'],
                },
            )

            # TrackNotFoundError
            error_response = bundle.respond_error(TrackNotFoundError())
            eq_(error_response.status_code, 200)
            eq_(
                json.loads(error_response.data),
                {
                    u'status': u'error',
                    u'errors': [u'track.not_found'],
                },
            )

            # BlackboxTemporaryError, YaSmsTemporaryError, DBError, RedisError
            # будут отдаваться как 'backend.%s_failed'
            errors = [
                (BlackboxTemporaryError, 'blackbox'),
                (YaSmsTemporaryError, 'yasms'),
                (DBError, 'database'),
                (RedisError, 'redis'),
                (OAuthTemporaryError, 'oauth'),
                (YdbTemporaryError, 'ydb'),
            ]
            for error, slug in errors:
                error_response = bundle.respond_error(error())
                eq_(error_response.status_code, 200)
                eq_(
                    json.loads(error_response.data),
                    {
                        u'status': u'error',
                        u'errors': [u'backend.%s_failed' % slug],
                    },
                )

    def test_read_or_create_track__create_track(self):
        with self.create_base_bundle(self.default_params) as bundle:

            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            bundle.consumer = 'dev'
            bundle.read_or_create_track('register')
            ok_(bundle.track_id)
            ok_(bundle.track)
            track = bundle.track_manager.read(bundle.track_id)
            eq_(
                track._data,
                {
                    'track_type': 'register',
                    'consumer': 'dev',
                    'created': TimeNow(),
                },
            )

    def test_read_or_create_track__create_track_with_process_name(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.consumer = 'dev'
            bundle.read_or_create_track('register', process_name=PROCESS_RESTORE)
            track = bundle.track_manager.read(bundle.track_id)
            eq_(
                track._data,
                {
                    'track_type': 'register',
                    'consumer': 'dev',
                    'created': TimeNow(),
                    'process_name': PROCESS_RESTORE,
                },
            )

    def test_read_or_create_track__read_track(self):
        with self.create_base_bundle(self.default_params) as bundle:

            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            bundle.track_id = self.track_id
            bundle.read_or_create_track('register')
            ok_(bundle.track_id)
            ok_(bundle.track)
            track = bundle.track_manager.read(bundle.track_id)
            eq_(
                track._data,
                {
                    'track_type': 'register',
                    'consumer': 'dev',
                    'created': TimeNow(),
                },
            )

    def test_read_or_create_track__read_track__process_name_present_and_allowed(self):
        """Имя процесса задано в треке, View допускает указанный процесс"""
        with self.track_manager.transaction(track_id=self.track_id).commit_on_error() as track:
            track.process_name = PROCESS_RESTORE
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.process_name = PROCESS_RESTORE
            bundle.track_id = self.track_id
            bundle.read_or_create_track('restore')
            ok_(bundle.track)

    def test_read_or_create_track__read_track__process_name_required_and_not_present(self):
        """Имя процесса не задано в треке, View требует наличие процесса"""
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.require_process = True
            bundle.track_id = self.track_id
            self.assertRaises(InvalidTrackStateError, bundle.read_or_create_track, 'register')

    def test_read_or_create_track__read_track__process_name_present_and_invalid(self):
        """Имя процесса задано в треке, View не допускает заданный в треке процесс"""
        with self.track_manager.transaction(track_id=self.track_id).commit_on_error() as track:
            track.process_name = 'some-process'
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.allowed_processes = [PROCESS_RESTORE]
            bundle.track_id = self.track_id
            self.assertRaises(InvalidTrackStateError, bundle.read_or_create_track, 'restore')

    def test_create_track(self):
        with self.create_base_bundle(self.default_params) as bundle:
            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            bundle.track_id = self.track_id
            bundle.consumer = 'dev'
            bundle.create_track('register')
            ok_(bundle.track_id)
            ok_(bundle.track)
            track = bundle.track_manager.read(bundle.track_id)
            eq_(
                track._data,
                {
                    'track_type': 'register',
                    'consumer': 'dev',
                    'created': TimeNow(),
                },
            )
            ok_(bundle.track_id)

    def test_read_track(self):
        with self.create_base_bundle(self.default_params) as bundle:

            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            bundle.track_id = self.track_id
            bundle.read_track()
            ok_(bundle.track_id)
            ok_(bundle.track)
            track = bundle.track_manager.read(bundle.track_id)
            eq_(
                track._data,
                {
                    'track_type': 'register',
                    'consumer': 'dev',
                    'created': TimeNow(),
                },
            )

    def test_read_track__process_name_required_present_and_allowed(self):
        """Имя процесса задано в треке, View требует наличия процесса и допускает заданный в треке процесс"""
        with self.track_manager.transaction(track_id=self.track_id).commit_on_error() as track:
            track.process_name = PROCESS_RESTORE
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.require_process = True
            bundle.allowed_processes = [PROCESS_RESTORE]
            bundle.track_id = self.track_id
            bundle.read_track()
            ok_(bundle.track)

    def test_read_track__process_name_required_and_not_present(self):
        """Имя процесса не задано в треке, View требует наличия процесса"""
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.require_process = True
            bundle.track_id = self.track_id
            self.assertRaises(InvalidTrackStateError, bundle.read_track)

    def test_read_track__process_name_present_with_no_allowed_process_names(self):
        """Имя процесса задано в треке, но View не содержит указаний о допустимых процессах"""
        with self.track_manager.transaction(track_id=self.track_id).commit_on_error() as track:
            track.process_name = 'some-process'
        with self.create_base_bundle(self.default_params) as bundle:

            bundle.track_id = self.track_id
            self.assertRaises(InvalidTrackStateError, bundle.read_track)

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

    def test_check_grant(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.consumer = 'dev'
            assert_is_none(bundle.check_grant('account.phone'))
            with self.assertRaises(MissingGrantsError):
                bundle.check_grant('account.phone1')

    def test_error_check_grant_for_account_type_without_any(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.consumer = 'dev'
            bundle.grants_for_account_type = dict(pdd='grant.fake')
            with self.assertRaises(ValueError):
                bundle.check_grants_for_account_type()

    def test_error_check_grant_for_account_type_without_grants_at_all(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.consumer = 'dev'
            bundle.grants_for_account_type = None
            with self.assertRaises(ValueError):
                bundle.check_grants_for_account_type()

    def test_process_form(self):
        params = {'path': '/1/test/?consumer=dev&login=test', 'method': 'GET'}

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        with self.create_base_bundle(params) as bundle:
            eq_(
                bundle.process_form(LoginValidation, bundle.all_values),
                {'login': u'test', 'ignore_stoplist': False},
            )

    def test_process_form_with_exception(self):
        login = '1aaa.-bb&b1' * 100
        params = {'path': '/1/test/?consumer=dev&login=%s' % login, 'method': 'GET'}

        with self.create_base_bundle(params) as bundle:
            with self.assertRaises(ValidationFailedError):
                bundle.process_form(LoginValidation, bundle.all_values)

    def test_process_basic_form(self):
        params = {'path': '/1/test/?consumer=dev&login=test', 'method': 'GET'}

        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({'test': 'free'}),
        )

        with self.create_base_bundle(params) as bundle:
            assert_is_none(bundle.basic_form)
            eq_(bundle.form_values, {})
            BaseBundleView.basic_form = LoginValidation

            bundle.process_basic_form()
            eq_(bundle.form_values, {'login': u'test', 'ignore_stoplist': False})

    def test_process_root_form(self):
        params = {'path': '/1/test/?consumer=dev', 'method': 'GET'}

        with self.create_base_bundle(params) as bundle:
            assert_is_none(bundle.consumer)
            ok_(not bundle.require_track)

            bundle.process_root_form()
            eq_(bundle.consumer, 'dev')
            assert_is_none(bundle.track)

    def test_process_root_form_with_require_track(self):
        params = {'path': '/1/test/?consumer=dev&track_id=%s' % self.track_id, 'method': 'GET'}

        with self.create_base_bundle(params) as bundle:
            assert_is_none(bundle.consumer)
            assert_is_none(bundle.track)

            bundle.require_track = True

            bundle.process_root_form()
            eq_(bundle.consumer, 'dev')
            eq_(bundle.track_id, str(self.track_id))

    def test_track_transaction(self):
        with self.create_base_bundle(self.default_params) as bundle:
            bundle.track_id = self.track_id
            bundle.track = self.track_manager.read(self.track_id)

            ok_(bundle.track_transaction)
            assert_is_none(bundle.track.origin)

            with bundle.track_transaction.commit_on_error():
                bundle.track.origin = 'bla'

            eq_(bundle.track.origin, 'bla')

    def test_with_service_ticket(self):
        params = {
            'path': '/1/test/?consumer=dev', 'method': 'GET',
            'headers': {'X-Ya-Service-Ticket': TEST_TICKET},
        }
        self.env.grants.set_grants_return_value(mock_grants(client_id=TEST_CLIENT_ID_2))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_grants = ['karma', 'account']

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {u'status': u'ok'})

    def test_ticket_with_wrong_source_id(self):
        params = {
            'path': '/1/test/?consumer=dev', 'method': 'GET',
            'headers': {'X-Ya-Service-Ticket': TEST_TICKET},
        }
        self.env.grants.set_grants_return_value(mock_grants(client_id=TEST_CLIENT_ID))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_grants = ['grant1', 'grant2']

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {
                u'status': u'error',
                u'error_message': u'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: %s' % TEST_CLIENT_ID_2,
                u'errors': [u'access.denied'],
            })

    def test_grants_without_client_id(self):
        params = {
            'path': '/1/test/?consumer=dev', 'method': 'GET',
            'headers': {'X-Ya-Service-Ticket': TEST_TICKET},
        }
        self.env.grants.set_grants_return_value(mock_grants(client_id=None))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_grants = ['grant1', 'grant2']

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {
                u'status': u'error',
                u'error_message': u"Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: %s. Required grants: ['grant1', 'grant2']" % TEST_CLIENT_ID_2,
                u'errors': [u'access.denied'],
            })

    def test_with_invalid_service_ticket(self):
        params = {
            'path': '/1/test/?consumer=dev', 'method': 'GET',
            'headers': {'X-Ya-Service-Ticket': TEST_INVALID_TICKET},
        }
        self.env.grants.set_grants_return_value(mock_grants(client_id=TEST_CLIENT_ID_2))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_grants = ['grant1', 'grant2']

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {
                u'status': u'error',
                u'error_message': u'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None',
                u'errors': [u'access.denied'],
            })

    def test_with_empty_service_ticket(self):
        params = {
            'path': '/1/test/?consumer=dev', 'method': 'GET',
            'headers': {'X-Ya-Service-Ticket': ''},
        }
        self.env.grants.set_grants_return_value(mock_grants(client_id=TEST_CLIENT_ID_2))
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_grants = ['grant1', 'grant2']

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {
                u'status': u'error',
                u'error_message': u'Access denied for ip: 127.0.0.1; consumer: dev; tvm_client_id: None',
                u'errors': [u'access.denied'],
            })

    def test_as_view(self):
        params = merge_dicts(
            self.base_params,
            {'path': '/1/test/', 'method': 'GET'},
        )

        process_request_mock = mock.Mock()
        process_request_mock.return_value = True

        bundle = BaseBundleView.as_view()

        with mock.patch.object(BaseBundleView, 'process_request', process_request_mock), \
                self.env.client.application.test_request_context(**params):
            self.env.client.application.preprocess_request()

            bundle = bundle.view_class()

            assert_is_none(bundle.consumer)
            eq_(bundle.form_values, {})
            eq_(bundle.path_values, {})
            eq_(bundle.response_values, {})
            assert_is_none(bundle.track)
            assert_is_none(bundle.track_id)

            assert_is_none(bundle.basic_form)
            ok_(not bundle.require_track)

    def test_empty_ip(self):
        params = {
            'path': '/1/test/?consumer=dev',
            'method': 'GET',
            'headers': {'Ya-Consumer-Client-Ip': ''},
        }
        with self.create_base_bundle(params) as bundle:
            bundle.process_request = lambda: None
            bundle.required_headers = (HEADER_CONSUMER_CLIENT_IP,)

            r = bundle.dispatch_request()
            eq_(json.loads(r.data), {
                u'status': u'error',
                u'errors': [u'ip.empty'],
            })
