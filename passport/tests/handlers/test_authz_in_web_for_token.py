# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from copy import copy
from datetime import timedelta
import json
import socket

from furl import furl
import mock
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_sessionid_response
from passport.backend.core.test.test_utils.utils import check_url_equals
from passport.backend.core.types.display_name import DisplayName
from passport.backend.social.broker.cookies import build_json_secure_cookie
from passport.backend.social.broker.failure_diagnostics import (
    build_failure_diagnostics_id,
    FailureDiagnostics,
    save_failure_diagnostics,
)
from passport.backend.social.broker.handlers.token import task_state
from passport.backend.social.broker.test import (
    InternalBrokerHandlerV1TestCase,
    TestCase,
)
from passport.backend.social.common import oauth2
from passport.backend.social.common._urllib3 import urllib3
from passport.backend.social.common.application import (
    Application,
    ApplicationGroupId,
)
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import (
    PLACE_QUERY,
    urllib_quote,
    urlparse_qs,
    UserParamDescriptor,
)
from passport.backend.social.common.redis_client import RedisError
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import (
    find_refresh_token_by_token_id,
    save_refresh_token,
)
from passport.backend.social.common.task import (
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_ID3,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_NAME3,
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN4,
    APPLICATION_TOKEN_TTL1,
    APPLICATION_TOKEN_TTL2,
    AUTHORIZATION_CODE1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    FRONTEND_URL1,
    RETPATH1,
    TASK_ID1,
    TASK_ID2,
    TASK_TTL1,
    UID1,
    UID2,
    UNIXTIME1,
    UNIXTIME2,
    USER_IP1,
)
from passport.backend.social.common.test.parameterized import parameterized_expand
from passport.backend.social.common.test.types import (
    DatetimeNow,
    FakeResponse,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_value_for_account,
    save_token,
)
from passport.backend.social.common.useragent import Url
from passport.backend.utils.common import deep_merge
import urllib3.exceptions


APPLICATION_DISPLAY_NAME1 = 'Супер приложение для Станции!'
TOKEN_URL1 = 'https://y.x/token'
REFRESH_TOKEN_URL1 = 'https://y.x/refresh_token'

DEFAULT_APPLICATION_CONF = dict(
    application_id=APPLICATION_ID1,
    application_name=APPLICATION_NAME1,
    display_name=APPLICATION_DISPLAY_NAME1,
    provider_client_id=EXTERNAL_APPLICATION_ID1,
    secret=APPLICATION_SECRET1,
    authorization_url='https://y.x/authorize',
    token_url=TOKEN_URL1,
    domain='social.yandex.net',
    group_id=ApplicationGroupId.station,
)

DEFAULT_SESSION_APPLICATION = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)
ERROR_RETPATH = 'https://passport.yandex.ru/auth/social/callback?status=error'
MAX_RESPONSE_LEN = 64000
MAX_TOKEN_LEN = 30000


class _TestCaseMixin(object):
    def build_settings(self):
        conf = super(_TestCaseMixin, self).build_settings()
        conf.update(
            dict(
                applications=self._build_app_settings(),
            ),
        )
        conf['social_config'].update(
            diagnostics_per_report=2,
            diagnostics_ttl=timedelta(minutes=1),
            passport_frontend_host_without_tld='passport.yandex.',
        )
        return conf

    def _build_app_settings(self):
        return [DEFAULT_APPLICATION_CONF]

    def _load_diagnostics_from_redis(self, application_name=None):
        application_name = application_name or APPLICATION_NAME1
        diagnostics = self._fake_redis.lrange(build_failure_diagnostics_id(application_name), 0, -1)
        return map(FailureDiagnostics.from_json, diagnostics)

    def _save_diagnostics_to_redis(self, diagnostics_list, application_name=None):
        application_name = application_name or APPLICATION_NAME1
        diagnostics_list = [d.to_json() for d in diagnostics_list]
        self._fake_redis.rpush(build_failure_diagnostics_id(application_name), *diagnostics_list)

    def _quick_patch(self, name):
        return mock.patch('passport.backend.social.broker.handlers.token.authz_in_web.%s' % name)

    def _assign_all_grants(self):
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web-for-token'])


class _BaseAuthorizationTestCase(_TestCaseMixin, InternalBrokerHandlerV1TestCase):
    def _build_session(self,
                       state=None,
                       exchange=None,
                       created=None,
                       application=DEFAULT_SESSION_APPLICATION,
                       consumer=CONSUMER1,
                       task_id=TASK_ID1,
                       retpath=RETPATH1,
                       place=PLACE_QUERY,
                       uid=UID1,
                       collect_diagnostics=None,
                       in_redis=None,
                       user_param=None):
        task = Task()
        task.state = state
        task.exchange = exchange
        task.start_args = dict(foo='bar')
        task.task_id = task_id
        task.created = created
        task.consumer = consumer
        task.application = application
        task.retpath = retpath
        task.place = place
        task.uid = uid
        task.collect_diagnostics = collect_diagnostics
        task.in_redis = in_redis
        task.user_param = user_param
        return task

    def _setup_blackbox(self, account=None):
        if account is None:
            account = self._build_account()

        kwargs = deep_merge(
            account.get('userinfo', dict()),
            account.get('sessionid', dict()),
        )
        self._fake_blackbox.set_response_side_effect(
            'sessionid',
            [
                blackbox_sessionid_response(**kwargs),
            ],
        )

    def _build_account(self, uid=UID1):
        display_name = DisplayName(name='iNSidious Joe')
        return dict(
            userinfo=dict(
                uid=uid,
                display_name=display_name.as_dict(),
            ),
        )

    def _build_invalid_sessionid(self):
        return dict(
            sessionid=dict(
                status=BLACKBOX_SESSIONID_INVALID_STATUS,
            ),
        )

    def _build_task_cookie(self, session_kwargs=dict(), expired_at=None):
        _now = now()
        expired_at = expired_at or (_now + timedelta(seconds=TASK_TTL1))
        expires_in = (expired_at - _now).total_seconds()

        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=expires_in)

        return task_cookie

    def _build_task(self,
                    application=DEFAULT_SESSION_APPLICATION,
                    uid=UID1,
                    consumer=CONSUMER1,
                    task_id=TASK_ID1,
                    finished=None,
                    token=APPLICATION_TOKEN1,
                    token_expired_at=None,
                    refresh_token=APPLICATION_TOKEN2,
                    scope=None):
        task = Task()
        task.application = application

        task.access_token = dict(
            value=token,
            expires=token_expired_at,
            scope=scope,
        )
        if refresh_token is not None:
            task.access_token.update(dict(refresh=refresh_token))

        task.created = 1.0
        task.finished = finished
        task.task_id = task_id
        task.consumer = consumer
        task.uid = uid
        task.in_redis = True
        return task

    def _assert_token_saved(self,
                            uid=UID1,
                            application_id=APPLICATION_ID1,
                            token_value=APPLICATION_TOKEN1,
                            scopes=None,
                            token_expires_in=APPLICATION_TOKEN_TTL1):
        token = find_token_by_value_for_account(uid, application_id, token_value, self._fake_db.get_engine())
        self.assertIsNotNone(token)

        self.assertIsNone(token.profile_id)
        self.assertIsNone(token.secret)

        if scopes is None:
            scopes = set([])
        self.assertEqual(token.scopes, scopes)

        if token_expires_in is not None:
            token_expires_at = DatetimeNow(timestamp=now() + timedelta(seconds=token_expires_in))
        else:
            token_expires_at = None
        self.assertEqual(token.expired, token_expires_at)

        self.assertEqual(token.created, DatetimeNow())
        self.assertEqual(token.verified, DatetimeNow())
        self.assertEqual(token.confirmed, DatetimeNow())

    def _assert_refresh_token_saved(self,
                                    uid=UID1,
                                    application_id=APPLICATION_ID1,
                                    token_value=APPLICATION_TOKEN1,
                                    refresh_token_value=APPLICATION_TOKEN2,
                                    scopes=None):
        token = find_token_by_value_for_account(uid, application_id, token_value, self._fake_db.get_engine())
        self.assertIsNotNone(token)

        refresh_token = find_refresh_token_by_token_id(token.token_id, self._fake_db.get_engine())

        self.assertEqual(refresh_token.value, refresh_token_value)

        if scopes is None:
            scopes = set([])
        self.assertEqual(refresh_token.scopes, scopes)

    def _setup_token(self,
                     uid=UID1,
                     application=DEFAULT_SESSION_APPLICATION,
                     token_value=APPLICATION_TOKEN3,
                     token_expires_in=APPLICATION_TOKEN_TTL1,
                     refresh_token_value=APPLICATION_TOKEN4):
        _now = now()
        token = Token(
            uid=uid,
            application_id=application.identifier,
            value=token_value,
            expired=_now + timedelta(seconds=token_expires_in),
            created=_now,
            verified=_now,
            confirmed=_now,
        )
        save_token(token, self._fake_db.get_engine())

        refresh_token = RefreshToken(
            token_id=token.token_id,
            value=refresh_token_value,
            expired=None,
        )
        save_refresh_token(refresh_token, self._fake_db.get_engine())

    def _setup_task(self, task):
        save_task_to_redis(self._fake_redis, task.task_id, task)

    def _assert_token_not_saved(self,
                                uid=UID1,
                                application_id=APPLICATION_ID1,
                                token_value=APPLICATION_TOKEN1):
        token = find_token_by_value_for_account(
            uid,
            application_id,
            token_value,
            self._fake_db.get_engine(),
        )
        self.assertIsNone(token)

    def _build_authorization_url(self,
                                 base_url='https://y.x/authorize',
                                 client_id=EXTERNAL_APPLICATION_ID1,
                                 extra_args=None,
                                 frontend_url=FRONTEND_URL1,
                                 scope=None):
        url = furl(base_url)
        url.args.update(
            dict(
                response_type='code',
                client_id=client_id,
            ),
        )

        if scope is not None:
            url.args['scope'] = scope

        if extra_args is not None:
            url.args.update(extra_args)

        redirect_url = 'https://social.yandex.net/broker/redirect'
        callback_url = '%s/authz_in_web/%s/callback' % (frontend_url, TASK_ID1)
        url.args.update(
            dict(
                redirect_uri=redirect_url,
                state=callback_url,
            ),
        )
        url = url.url
        return url


class _BaseStartTestCase(_BaseAuthorizationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_web/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        consumer=CONSUMER1,
        application_name=APPLICATION_NAME1,
        retpath=RETPATH1,
        place=PLACE_QUERY,
        Session_id='testsessionid',
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def _assert_start_ok_response(self, rv, location=None, session=None):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        if location is None:
            location = self._build_authorization_url()
        self._assert_response_forwards_to_url(rv, location)

        if session is None:
            session = self._build_session()
        self._assert_response_contains_session(rv, session)

    def _assert_start_error_response(self, rv, errors, retpath=Undefined):
        if retpath is Undefined:
            retpath = RETPATH1
        self._assert_error_response(rv, errors, retpath)

    def _assert_start_redirect_to_passport_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['location'],
        )

        location = self._build_passport_url()
        self._assert_response_forwards_to_url(rv, location)

    def _build_passport_url(self, retpath=RETPATH1, start_url=None):
        url = furl('https://passport.yandex.ru/auth')
        fail_retpath = self._build_fail_retpath(retpath)
        url.args.update({
            'from': 'social',
            'retpath': start_url or self._build_start_url(),
            'backpath': fail_retpath,
        })
        url = url.url
        return url

    def _build_start_url(
        self,
        application_name=APPLICATION_NAME1,
        consumer=CONSUMER1,
        retpath=RETPATH1,
        extra_args=None,
    ):
        params = dict(
            application_name=application_name,
            consumer=consumer,
            retpath=retpath,
        )
        for key in extra_args or dict():
            params.setdefault(key, extra_args[key])
        return Url('https://social.yandex.ru/broker2/authz_in_web/start', params=params)

    def _build_session(self,
                       state='authz_in_web.r_to_soc',
                       **kwargs):
        if 'created' not in kwargs:
            kwargs.update(created=now.f())
        return super(_BaseStartTestCase, self)._build_session(
            state=state,
            **kwargs
        )


class TestStart(_BaseStartTestCase):
    def setUp(self):
        super(TestStart, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        self._setup_blackbox()
        rv = self._make_request()
        self._assert_start_ok_response(rv)

    def test_invalid_sessionid(self):
        self._setup_blackbox(account=self._build_invalid_sessionid())
        rv = self._make_request()
        self._assert_start_redirect_to_passport_response(rv)

    def test_consumer_unknown(self):
        self._setup_blackbox()
        rv = self._make_request(data=dict(consumer='unknown'))
        self._assert_response_contains_session(rv, self._build_session(consumer='unknown'))

    def test_no_consumer(self):
        self._setup_blackbox()
        rv = self._make_request(data=dict(consumer=None))
        self._assert_start_error_response(rv, ['ConsumerUnknownError'], retpath=None)

    def test_no_application_name(self):
        rv = self._make_request(data=dict(application_name=None))
        self._assert_start_error_response(rv, ['ApplicationUnknownError'])

    def test_unknown_application(self):
        rv = self._make_request(data=dict(application_name='unknown'))
        self._assert_start_error_response(rv, ['ApplicationUnknownError'])

    def test_no_retpath(self):
        self._setup_blackbox()
        rv = self._make_request(data=dict(retpath=None))
        self._assert_start_error_response(rv, ['RetpathInvalidError'], retpath=None)

    def test_no_user_ip(self):
        self._setup_blackbox()
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_start_error_response(rv, ['UserIpInvalidError'], retpath=RETPATH1)

    def test_no_frontend_url(self):
        self._setup_blackbox()
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_start_error_response(rv, ['SessionInvalidError'], retpath=RETPATH1)

    def test_collect_diagnostics(self):
        self._setup_blackbox()

        rv = self._make_request(data=dict(flags='collect_diagnostics'))

        session = self._build_session(collect_diagnostics=True)
        self._assert_start_ok_response(rv, session=session)


class _BaseCallbackTestCase(_BaseAuthorizationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_web/callback'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        query='code=%s' % urllib_quote(AUTHORIZATION_CODE1),
        task_id=TASK_ID1,
        Session_id='testsessionid',
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def _assert_callback_ok_response(self, rv, session=None):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        if session is None:
            session = self._build_response_session()
        self._assert_response_contains_session(rv, session)

        self._assert_response_forwards_to_url(
            rv,
            '%s/authz_in_web/%s/bind' % (FRONTEND_URL1, TASK_ID1),
        )

    def _assert_callback_form_try_again_response(
        self,
        rv,
        application_display_name=APPLICATION_DISPLAY_NAME1,
    ):
        self._assert_ok_response(
            rv,
            response={
                'status': 'form_try_again',
                'application_display_name': application_display_name,
            },
            skip=['cancel_url', 'retry_url']
        )

        data = json.loads(rv.data)

        self.assertIn('cancel_url', data)
        fail_retpath = self._build_fail_retpath(RETPATH1)
        check_url_equals(data['cancel_url'], fail_retpath)

        self.assertIn('retry_url', data)
        authorization_url = self._build_authorization_url()
        check_url_equals(data['retry_url'], authorization_url)

    def _build_session(self,
                       state='authz_in_web.r_to_soc',
                       created=1.0,
                       **kwargs):
        return super(_BaseCallbackTestCase, self)._build_session(
            state=state,
            created=created,
            **kwargs
        )

    def _build_response_session(
        self,
        state='authz_in_web.got_auth_code',
        exchange=AUTHORIZATION_CODE1,
        **kwargs
    ):
        return self._build_session(
            state=state,
            exchange=exchange,
            **kwargs
        )


class TestCallback(_BaseCallbackTestCase):
    def setUp(self):
        super(TestCallback, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_callback_ok_response(rv)

    def test_user_denied_authorization(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(
            data=dict(
                query='error=access_denied',
                track=task_cookie,
            ),
        )

        self._assert_callback_form_try_again_response(rv)

    def test_no_user_ip(self):
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_error_response(rv, ['UserIpInvalidError'], retpath=None)

    def test_no_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_no_task_id(self):
        rv = self._make_request(data=dict(task_id=None))
        self._assert_error_response(rv, ['TaskIdInvalidError'], retpath=None)

    def test_no_track(self):
        rv = self._make_request(data=dict(track=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_mismatch_task_id(self):
        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(),
                task_id=TASK_ID2
            ),
        )
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)


class TestCallbackApplicationDisplayNameUndefined(_BaseCallbackTestCase):
    def setUp(self):
        super(TestCallbackApplicationDisplayNameUndefined, self).setUp()
        self._assign_all_grants()

    def build_settings(self):
        conf = super(TestCallbackApplicationDisplayNameUndefined, self).build_settings()
        app_conf = dict(DEFAULT_APPLICATION_CONF)
        del app_conf['display_name']
        conf.update(
            dict(
                applications=[app_conf],
            ),
        )
        return conf

    def test_user_denied_authorization(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(
            data=dict(
                query='error=access_denied',
                track=task_cookie,
            ),
        )

        self._assert_callback_form_try_again_response(rv, application_display_name=APPLICATION_NAME1)


class TestCallbackOnGotAuthCode(_BaseCallbackTestCase):
    def setUp(self):
        super(TestCallbackOnGotAuthCode, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        task_cookie = self._build_task_cookie(session_kwargs=dict(state='authz_in_web.got_auth_code'))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
                'task_id': TASK_ID1,
            },
            skip=['location', 'request_id'],
        )

        self._assert_response_forwards_to_url(
            rv,
            '%s/authz_in_web/%s/bind' % (FRONTEND_URL1, TASK_ID1),
        )


class TestCallbackOnGotToken(_BaseCallbackTestCase):
    def setUp(self):
        super(TestCallbackOnGotToken, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        task_cookie = self._build_task_cookie(session_kwargs=dict(state='authz_in_web.got_token'))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
                'task_id': TASK_ID1,
            },
            skip=['location', 'request_id'],
        )

        self._assert_response_forwards_to_url(
            rv,
            '%s/authz_in_web/%s/bind' % (FRONTEND_URL1, TASK_ID1),
        )


class TestCallbackCollectDiagnostics(_BaseCallbackTestCase):
    def setUp(self):
        super(TestCallbackCollectDiagnostics, self).setUp()
        self._assign_all_grants()

    def _build_session(self, **kwargs):
        kwargs.setdefault('collect_diagnostics', True)
        return super(TestCallbackCollectDiagnostics, self)._build_session(**kwargs)

    def _assert_callback_error_redirect_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        fail_retpath = self._build_fail_retpath(RETPATH1)
        self._assert_response_forwards_to_url(rv, fail_retpath)

        self._assert_response_burns_session(rv)

    def _assert_callback_redirect_to_collect_diagnostics_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )
        self._assert_response_contains_session(
            rv,
            self._build_session(
                state='authz_in_web.got_auth_code',
                exchange=AUTHORIZATION_CODE1,
            ),
        )
        self._assert_response_forwards_to_url(
            rv,
            '%s/authz_in_web/%s/collect_diagnostics' % (FRONTEND_URL1, TASK_ID1),
        )

    def test_ok(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_callback_redirect_to_collect_diagnostics_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    authorization_error_response_queries = [
        'foo=bar&error=access_denied&bar=foo',
        'error=unknown',
    ]

    @parameterized_expand([(q,) for q in authorization_error_response_queries])
    def test_authorization_error_response(self, query):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(
            data=dict(
                query=query,
                track=task_cookie,
            ),
        )

        self._assert_callback_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        type='authorization_error_response',
                        query=mock.ANY,
                    ),
                ),
            ],
        )

        diagnostics = dict(diagnostics[0])
        self.assertEqual(urlparse_qs(diagnostics['query']), urlparse_qs(query))

    missing_authorization_code_queries = [
        'foo=bar',
        '',
    ]

    @parameterized_expand([(q,) for q in missing_authorization_code_queries])
    def test_missing_authorization_code(self, query):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(
            data=dict(
                query=query,
                track=task_cookie,
            ),
        )

        self._assert_callback_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        type='missing_authorization_code',
                        query=mock.ANY,
                    ),
                ),
            ],
        )

        diagnostics = dict(diagnostics[0])
        self.assertEqual(urlparse_qs(diagnostics['query']), urlparse_qs(query))

    def test_unknown_failure(self):
        task_cookie = self._build_task_cookie()

        with self._quick_patch('_AuthzinInWebForTokenDiagnosticCouncil.diagnose') as council_diagnose_mock:
            council_diagnose_mock.return_value = None

            rv = self._make_request(
                data=dict(
                    query='foo=bar',
                    track=task_cookie,
                ),
            )

        self._assert_error_response(rv, ['CommunicationFailedError'], retpath=ERROR_RETPATH)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_unexpected_exception_when_collect_diagnostics(self):
        task_cookie = self._build_task_cookie()

        with self._quick_patch('_AuthzinInWebForTokenDiagnosticCouncil.diagnose') as council_diagnose_mock:
            council_diagnose_mock.side_effect = Exception('test_failed_when_collect_diagnostics')

            rv = self._make_request(
                data=dict(
                    query='foo=bar',
                    track=task_cookie,
                ),
            )

        self._assert_error_response(rv, ['CommunicationFailedError'], retpath=ERROR_RETPATH)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_fail_to_save_diagnostics(self):
        task_cookie = self._build_task_cookie()

        with self._quick_patch('DiagnosticManager._save_collected_reports') as save_collected_reports_mock:
            save_collected_reports_mock.side_effect = Exception('test_fail_to_save_diagnostics')

            rv = self._make_request(
                data=dict(
                    query='foo=bar',
                    track=task_cookie,
                ),
            )

        self._assert_error_response(rv, ['CommunicationFailedError'], retpath=ERROR_RETPATH)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_unexpected_exception_when_collect_diagnostics_about_access_denied(self):
        task_cookie = self._build_task_cookie()

        with self._quick_patch('_AuthzinInWebForTokenDiagnosticCouncil.diagnose') as council_diagnose_mock:
            council_diagnose_mock.side_effect = Exception('test_failed_when_collect_diagnostics')

            rv = self._make_request(
                data=dict(
                    query='error=access_denied',
                    track=task_cookie,
                ),
            )

        self._assert_callback_form_try_again_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_fail_to_save_diagnostics_about_access_denied(self):
        task_cookie = self._build_task_cookie()

        with self._quick_patch('DiagnosticManager._save_collected_reports') as save_collected_reports_mock:
            save_collected_reports_mock.side_effect = Exception('test_fail_to_save_diagnostics')

            rv = self._make_request(
                data=dict(
                    query='error=access_denied',
                    track=task_cookie,
                ),
            )

        self._assert_callback_form_try_again_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_ok__diagnostics_collection_disabled(self):
        task_cookie = self._build_task_cookie(dict(collect_diagnostics=False))

        with self._quick_patch('DiagnosticManager._finish') as deh_finish_mock:
            rv = self._make_request(data=dict(track=task_cookie))

        session = self._build_response_session(collect_diagnostics=False)
        self._assert_callback_ok_response(rv, session=session)

        deh_finish_mock.assert_not_called()

    def test_missing_authorization_code__diagnostics_collection_disabled(self):
        task_cookie = self._build_task_cookie(dict(collect_diagnostics=False))

        with self._quick_patch('DiagnosticManager._finish') as deh_finish_mock:
            rv = self._make_request(
                data=dict(
                    query='foo=bar',
                    track=task_cookie,
                ),
            )

        self._assert_error_response(rv, ['CommunicationFailedError'], retpath=ERROR_RETPATH)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

        deh_finish_mock.assert_not_called()

    def test_authorization_error_response__diagnostics_collection_disabled(self):
        task_cookie = self._build_task_cookie(dict(collect_diagnostics=False))

        with self._quick_patch('DiagnosticManager._finish') as deh_finish_mock:
            rv = self._make_request(
                data=dict(
                    query='error=access_denied',
                    track=task_cookie,
                ),
            )

        self._assert_callback_form_try_again_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

        deh_finish_mock.assert_not_called()

    def test_old_diagnostics(self):
        diagnostics = FailureDiagnostics(
            dict(
                foo='foo1',
                bar='bar1',
            ),
        )
        save_failure_diagnostics(APPLICATION_NAME1, [diagnostics])

        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_callback_redirect_to_collect_diagnostics_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())


class _BaseBindSubmitTestCase(_BaseAuthorizationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_web/bind/submit'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        task_id=TASK_ID1,
        Session_id='testsessionid',
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def _assert_bind_submit_form_bind_agreement_response(
        self,
        rv,
        application_display_name=APPLICATION_DISPLAY_NAME1,
        session=None,
    ):
        self._assert_ok_response(
            rv,
            response={
                'status': 'form_bind_agreement',
                'application_display_name': application_display_name,
                'account_display_name': {
                    'name': 'iNSidious Joe',
                    'display_name_empty': False,
                },
            },
            skip=['cookies', 'cancel_url'],
        )

        data = json.loads(rv.data)

        self.assertIn('cancel_url', data)
        fail_retpath = self._build_fail_retpath(RETPATH1)
        check_url_equals(data['cancel_url'], fail_retpath)

        self._assert_response_contains_session(
            rv,
            session or self._build_bind_submit_form_bind_agreement_session(),
        )

    def _build_bind_submit_form_bind_agreement_session(
        self,
        in_redis=True,
        state='authz_in_web.got_token',
        **kwargs
    ):
        return self._build_session(
            in_redis=in_redis,
            state=state,
            **kwargs
        )

    def _build_session(self,
                       state='authz_in_web.got_auth_code',
                       created=1.0,
                       exchange=AUTHORIZATION_CODE1,
                       **kwargs):
        return super(_BaseBindSubmitTestCase, self)._build_session(
            state=state,
            created=created,
            exchange=exchange,
            **kwargs
        )

    def _build_task(self, token_expires_in=APPLICATION_TOKEN_TTL1, **kwargs):
        if 'token_expired_at' not in kwargs:
            kwargs['token_expired_at'] = now.i() + token_expires_in
        if 'finished' not in kwargs:
            kwargs['finished'] = now.f()
        return super(_BaseBindSubmitTestCase, self)._build_task(**kwargs)

    def _setup_authorization_code_response(self):
        response = oauth2.test.oauth2_access_token_response(
            access_token=APPLICATION_TOKEN1,
            refresh_token=APPLICATION_TOKEN2,
            expires_in=APPLICATION_TOKEN_TTL1,
        )
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

    def _assert_bind_submit_ok_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        ok_retpath = self._build_ok_retpath(RETPATH1, task_id=None)
        self._assert_response_forwards_to_url(rv, ok_retpath)

        self._assert_response_contains_session(
            rv,
            self._build_session(
                in_redis=True,
                state='authz_in_web.got_token',
            ),
        )


class TestBindSubmit(_BaseBindSubmitTestCase):
    def setUp(self):
        super(TestBindSubmit, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        self._setup_authorization_code_response()
        self._setup_blackbox()
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_submit_form_bind_agreement_response(rv)

        self._assert_task_equals(TASK_ID1, self._build_task())

    def test_user_trusts_application(self):
        self._setup_authorization_code_response()
        self._setup_blackbox()
        self._setup_token(
            token_value=APPLICATION_TOKEN3,
            refresh_token_value=APPLICATION_TOKEN4,
        )
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_submit_ok_response(rv)

        self._assert_token_saved()
        self._assert_refresh_token_saved()

        self._assert_token_saved(token_value=APPLICATION_TOKEN3)
        self._assert_refresh_token_saved(
            token_value=APPLICATION_TOKEN3,
            refresh_token_value=APPLICATION_TOKEN4,
        )

        self._assert_task_equals(TASK_ID1, self._build_task())

    def test_got_token_already(self):
        self._setup_blackbox()

        task = self._build_task(token_expired_at=UNIXTIME1, finished=UNIXTIME2)
        self._setup_task(task)

        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                state='authz_in_web.got_token',
                in_redis=True,
            ),
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_submit_form_bind_agreement_response(rv)

        self._assert_task_equals(TASK_ID1, task)

    def test_no_user_ip(self):
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_error_response(rv, ['UserIpInvalidError'], retpath=None)

    def test_no_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_no_task_id(self):
        rv = self._make_request(data=dict(task_id=None))
        self._assert_error_response(rv, ['TaskIdInvalidError'], retpath=None)

    def test_no_track(self):
        rv = self._make_request(data=dict(track=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_mismatch_task_id(self):
        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(),
                task_id=TASK_ID2
            ),
        )
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_invalid_task_state(self):
        self._setup_authorization_code_response()
        self._setup_blackbox()
        task_cookie = self._build_task_cookie(
            session_kwargs={
                'state': task_state.AUTHZ_IN_WEB_R_TO_SOC,
            },
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['SessionInvalidError'], retpath=ERROR_RETPATH)

    def test_another_account_in_task(self):
        self._setup_authorization_code_response()
        self._setup_blackbox(account=self._build_account(uid=UID2))
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['SessionInvalidError'], retpath=ERROR_RETPATH)


class TestBindSubmitApplicationDisplayNameUndefined(_BaseBindSubmitTestCase):
    def setUp(self):
        super(TestBindSubmitApplicationDisplayNameUndefined, self).setUp()
        self._assign_all_grants()

    def build_settings(self):
        conf = super(TestBindSubmitApplicationDisplayNameUndefined, self).build_settings()
        app_conf = dict(DEFAULT_APPLICATION_CONF)
        del app_conf['display_name']
        conf.update(
            dict(
                applications=[app_conf],
            ),
        )
        return conf

    def test_ok(self):
        self._setup_authorization_code_response()
        self._setup_blackbox()
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_submit_form_bind_agreement_response(rv, application_display_name=APPLICATION_NAME1)

        self._assert_task_equals(TASK_ID1, self._build_task())


class _BaseBindCommitTestCase(_BaseAuthorizationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_web/bind/commit'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        task_id=TASK_ID1,
        Session_id='testsessionid',
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def _assert_bind_commit_ok_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        ok_retpath = self._build_ok_retpath(RETPATH1, task_id=None)
        self._assert_response_forwards_to_url(rv, ok_retpath)

        self._assert_response_contains_session(rv, self._build_session())

    def _build_session(self,
                       state='authz_in_web.got_token',
                       created=1.0,
                       exchange=AUTHORIZATION_CODE1,
                       in_redis=True,
                       **kwargs):
        return super(_BaseBindCommitTestCase, self)._build_session(
            state=state,
            created=created,
            exchange=exchange,
            in_redis=in_redis,
            **kwargs
        )

    def _build_task(self, token_expires_in=APPLICATION_TOKEN_TTL1, **kwargs):
        if 'token_expired_at' not in kwargs:
            kwargs['token_expired_at'] = now.f() + token_expires_in
        return super(_BaseBindCommitTestCase, self)._build_task(**kwargs)


class TestBindCommit(_BaseBindCommitTestCase):
    def setUp(self):
        super(TestBindCommit, self).setUp()
        self._assign_all_grants()

    def test_ok(self):
        self._setup_blackbox()
        self._setup_task(self._build_task())
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_commit_ok_response(rv)
        self._assert_token_saved()
        self._assert_refresh_token_saved()

    def test_provider_repeats_token(self):
        self._setup_token(
            token_value=APPLICATION_TOKEN1,
            refresh_token_value=APPLICATION_TOKEN2,
            token_expires_in=APPLICATION_TOKEN_TTL1,
        )
        self._setup_blackbox()
        self._setup_task(self._build_task(token_expires_in=APPLICATION_TOKEN_TTL2))
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_bind_commit_ok_response(rv)
        self._assert_token_saved(token_expires_in=APPLICATION_TOKEN_TTL2)
        self._assert_refresh_token_saved()

    def test_another_account_in_task(self):
        self._setup_blackbox(self._build_account(uid=UID2))
        self._setup_task(self._build_task())
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['SessionInvalidError'], RETPATH1)

        self._assert_token_not_saved(uid=UID1)
        self._assert_token_not_saved(uid=UID2)

    def test_no_user_ip(self):
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_error_response(rv, ['UserIpInvalidError'], retpath=None)

    def test_no_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_no_task_id(self):
        rv = self._make_request(data=dict(task_id=None))
        self._assert_error_response(rv, ['TaskIdInvalidError'], retpath=None)

    def test_no_track(self):
        rv = self._make_request(data=dict(track=None))
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_mismatch_task_id(self):
        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(),
                task_id=TASK_ID2
            ),
        )
        self._assert_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_invalid_task_state(self):
        self._setup_blackbox()
        self._setup_task(self._build_task())
        task_cookie = self._build_task_cookie(
            session_kwargs={
                'state': task_state.AUTHZ_IN_WEB_R_TO_SOC,
            },
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['SessionInvalidError'], retpath=ERROR_RETPATH)

    def test_invalid_sessionid(self):
        self._setup_blackbox(account=self._build_invalid_sessionid())
        self._setup_task(self._build_task())
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['AuthorizationRequiredError'], retpath=ERROR_RETPATH)

    def test_task_not_found_error(self):
        self._setup_blackbox()
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_error_response(rv, ['TaskNotFoundError'], retpath=None)


class _BaseCollectDiagnostics(_BaseAuthorizationTestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_web/collect_diagnostics'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        task_id=TASK_ID1,
        Session_id='testsessionid',
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def build_settings(self):
        conf = super(_BaseCollectDiagnostics, self).build_settings()
        conf['social_config'].update(
            diagnostics_recommended_token_ttl=3600,
        )
        return conf

    def _build_app_settings(self):
        app = copy(DEFAULT_APPLICATION_CONF)
        app.update(refresh_token_url=REFRESH_TOKEN_URL1)
        return [app]

    def _assert_collect_oauth_server_diagnostics_ok_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        ok_retpath = self._build_ok_retpath(RETPATH1, task_id=None)
        self._assert_response_forwards_to_url(rv, ok_retpath)

        self._assert_response_burns_session(rv)

    def _assert_collect_oauth_server_diagnostics_error_redirect_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'status': 'redirect',
            },
            skip=['cookies', 'location'],
        )

        fail_retpath = self._build_fail_retpath(RETPATH1)
        self._assert_response_forwards_to_url(rv, fail_retpath)

        self._assert_response_burns_session(rv)

    def _build_session(self,
                       state='authz_in_web.got_auth_code',
                       created=1.0,
                       exchange=AUTHORIZATION_CODE1,
                       **kwargs):
        return super(_BaseCollectDiagnostics, self)._build_session(
            state=state,
            created=created,
            exchange=exchange,
            **kwargs
        )

    def _get_default_request_data(self):
        data = dict(self.REQUEST_DATA)
        data.update(track=self._build_task_cookie())
        return data

    def _build_dns_failure_proxy_error(self):
        return urllib3.exceptions.ProxyError(
            'Cannot connect to proxy.',
            socket.error('Tunnel connection failed: 502 resolving failed'),
        )

    def _build_ssl_certificate_untrusted_zora_response(self):
        return FakeResponse(
            '',
            status_code=599,
            headers={
                'X-Yandex-GoZora-Error-Code': '1000',
                'X-Yandex-Gozora-Error-Description': 'the remote host certificate verification failed',
            },
        )


class TestCollectDiagnostics(_BaseCollectDiagnostics):
    def setUp(self):
        super(TestCollectDiagnostics, self).setUp()
        self._assign_all_grants()

    def test_no_problems(self):
        token_response = oauth2.test.oauth2_access_token_response(
            expires_in=3600,
            refresh_token=APPLICATION_TOKEN2,
        )
        refresh_token_response_on_invalid_token = oauth2.test.build_error('invalid_grant')
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                token_response.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        self._setup_blackbox()

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_unknown_failure(self):
        response = FakeResponse('Internal server error', status_code=500)
        self._fake_zora_useragent.set_response_value(response)
        self._setup_blackbox()

        with self._quick_patch('_AuthzinInWebForTokenDiagnosticCouncil.diagnose') as council_diagnose_mock:
            council_diagnose_mock.return_value = None

            rv = self._make_request()

        self._assert_error_response(rv, ['CommunicationFailedError'], retpath=ERROR_RETPATH)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    def test_old_diagnostics(self):
        old_diagnostics = FailureDiagnostics(
            dict(
                foo='foo1',
                bar='bar1',
            ),
        )
        save_failure_diagnostics(APPLICATION_NAME1, [old_diagnostics])

        exc = urllib3.exceptions.ReadTimeoutError(None, None, None)
        self._fake_zora_useragent.set_response_value(exc)

        self._setup_blackbox()

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                old_diagnostics,
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='useragent_request_timeout',
                        duration=0,
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )


class TestCollectDiagnosticsGetAccessToken(_BaseCollectDiagnostics):
    def setUp(self):
        super(TestCollectDiagnosticsGetAccessToken, self).setUp()
        self._assign_all_grants()
        self._setup_blackbox()

    error_codes = [
        'invalid_client',
        'invalid_grant',
        'unknown',
    ]

    @parameterized_expand([(e,) for e in error_codes])
    def test_error_response(self, error):
        response = oauth2.test.build_error(error)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_error',
                        error=error,
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_dns_failed(self):
        self._fake_zora_useragent.set_response_value(self._build_dns_failure_proxy_error())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='dns_failed',
                        hostname=Url(TOKEN_URL1).hostname,
                    ),
                ),
            ],
        )

    def test_read_timeout(self):
        self._fake_zora_useragent.set_response_value(urllib3.exceptions.ReadTimeoutError(None, None, None))

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='useragent_request_timeout',
                        duration=0,
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_ssl_failed(self):
        response = self._build_ssl_certificate_untrusted_zora_response()
        self._fake_zora_useragent.set_response_value(response)

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='ssl_failed',
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_http_status_500(self):
        response = FakeResponse('Internal server error', status_code=500)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='bad_http_status',
                        http_status='500',
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_too_long(self):
        response = oauth2.test.oauth2_access_token_response(access_token='Too long' + 'x' * MAX_RESPONSE_LEN)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_too_long',
                        http_status='200',
                        max_response_length=MAX_RESPONSE_LEN,
                        response_length=len(response.content),
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_not_json(self):
        token_response = FakeResponse('<html>Kekeke</html>', status_code=200)
        self._fake_zora_useragent.set_response_value(token_response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_not_json',
                        http_status='200',
                        url=TOKEN_URL1,
                    ),
                ),
            ],
        )

    invalid_access_tokens = [
        'x' * (MAX_TOKEN_LEN + 1),
        '',

        # Нет значения
        None,
    ]

    @parameterized_expand([(t,) for t in invalid_access_tokens])
    def test_invalid_access_token(self, access_token):
        response = oauth2.test.oauth2_access_token_response(access_token=access_token)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_invalid_access_token',
                        max_length=MAX_TOKEN_LEN,
                        min_length=1,
                    ),
                ),
            ],
        )

    invalid_refresh_tokens = [
        'x' * (MAX_TOKEN_LEN + 1),
    ]

    @parameterized_expand([(t,) for t in invalid_refresh_tokens])
    def test_invalid_refresh_token(self, refresh_token):
        response = oauth2.test.oauth2_access_token_response(refresh_token=refresh_token)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_invalid_refresh_token',
                        max_length=MAX_TOKEN_LEN,
                        min_length=1,
                    ),
                ),
            ],
        )

    invalid_expires_in = [
        -1,
        'a',
    ]

    @parameterized_expand([(e,) for e in invalid_expires_in])
    def test_invalid_expires_in(self, expires_in):
        response = oauth2.test.oauth2_access_token_response(expires_in=expires_in)
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='get_access_token',
                        type='token_response_invalid_expires_in',
                    ),
                ),
            ],
        )

    def test_expires_in_low(self):
        token_response = oauth2.test.oauth2_access_token_response(
            expires_in=3595,
            refresh_token=APPLICATION_TOKEN2,
        )
        refresh_token_response = oauth2.test.oauth2_access_token_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        type='token_expires_in_low',
                    ),
                ),
            ],
        )

    def test_token_expirable_but_no_refresh_token(self):
        token_response = oauth2.test.oauth2_access_token_response(expires_in=3600)
        invalid_refresh_token_response = oauth2.test.build_error('invalid_grant')
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                invalid_refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        type='token_expirable_but_no_refresh_token',
                    ),
                ),
            ],
        )


class TestCollectDiagnosticsTokenExpirableButNoRefreshTokenUrl(_BaseCollectDiagnostics):
    def setUp(self):
        super(TestCollectDiagnosticsTokenExpirableButNoRefreshTokenUrl, self).setUp()
        self._assign_all_grants()
        self._setup_blackbox()

    def _build_app_settings(self):
        return [DEFAULT_APPLICATION_CONF]

    def test(self):
        response = oauth2.test.oauth2_access_token_response(
            expires_in=3600,
            refresh_token=APPLICATION_TOKEN2,
        )
        self._fake_zora_useragent.set_response_value(response.to_zora_response())

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        type='token_expirable_but_no_refresh_token_url',
                    ),
                ),
            ],
        )


class TestCollectDiagnosticsRefreshValidToken(_BaseCollectDiagnostics):
    def setUp(self):
        super(TestCollectDiagnosticsRefreshValidToken, self).setUp()
        self._assign_all_grants()
        self._setup_blackbox()

    def _build_token_response(self):
        return oauth2.test.oauth2_access_token_response(
            expires_in=3600,
            refresh_token=APPLICATION_TOKEN2,
        )

    error_codes = [
        'invalid_client',
        'invalid_grant',
        'unknown',
    ]

    @parameterized_expand([(e,) for e in error_codes])
    def test_error_response(self, error):
        token_response = self._build_token_response()
        refresh_token_response = oauth2.test.build_error(error)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_error',
                        error=error,
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_dns_failed(self):
        token_response = self._build_token_response()
        refresh_token_response = self._build_dns_failure_proxy_error()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response,
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='dns_failed',
                        hostname=Url(REFRESH_TOKEN_URL1).hostname,
                    ),
                ),
            ],
        )

    def test_read_timeout(self):
        token_response = self._build_token_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                urllib3.exceptions.ReadTimeoutError(None, None, None),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='useragent_request_timeout',
                        duration=0,
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_ssl_failed(self):
        token_response = self._build_token_response()
        refresh_token_response = self._build_ssl_certificate_untrusted_zora_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response,
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='ssl_failed',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_http_status_500(self):
        token_response = self._build_token_response()
        refresh_token_response = FakeResponse('Internal server error', status_code=500)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_not_json',
                        http_status='500',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_too_long(self):
        token_response = self._build_token_response()
        refresh_token_response = oauth2.test.oauth2_access_token_response(
            access_token='Too long' + 'x' * MAX_RESPONSE_LEN,
        )

        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_too_long',
                        http_status='200',
                        max_response_length=MAX_RESPONSE_LEN,
                        response_length=len(refresh_token_response.content),
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_not_json(self):
        token_response = self._build_token_response()
        refresh_token_response = FakeResponse('<html>Kekeke</html>', status_code=200)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_not_json',
                        http_status='200',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    invalid_access_tokens = [
        'x' * (MAX_TOKEN_LEN + 1),
        '',

        # Нет значения
        None,
    ]

    @parameterized_expand([(t,) for t in invalid_access_tokens])
    def test_invalid_access_token(self, access_token):
        token_response = self._build_token_response()
        refresh_token_response = oauth2.test.oauth2_access_token_response(access_token=access_token)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_invalid_access_token',
                        max_length=MAX_TOKEN_LEN,
                        min_length=1,
                    ),
                ),
            ],
        )

    invalid_refresh_tokens = [
        'x' * (MAX_TOKEN_LEN + 1),
    ]

    @parameterized_expand([(t,) for t in invalid_refresh_tokens])
    def test_invalid_refresh_token(self, refresh_token):
        token_response = self._build_token_response()
        refresh_token_response = oauth2.test.oauth2_access_token_response(refresh_token=refresh_token)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_invalid_refresh_token',
                        max_length=MAX_TOKEN_LEN,
                        min_length=1,
                    ),
                ),
            ],
        )

    invalid_expires_in = [
        -1,
        'a',
    ]

    @parameterized_expand([(e,) for e in invalid_expires_in])
    def test_invalid_expires_in(self, expires_in):
        token_response = self._build_token_response()
        refresh_token_response = oauth2.test.oauth2_access_token_response(expires_in=expires_in)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_valid_token',
                        type='token_response_invalid_expires_in',
                    ),
                ),
            ],
        )


class TestCollectDiagnosticsRefreshInvalidToken(_BaseCollectDiagnostics):
    def setUp(self):
        super(TestCollectDiagnosticsRefreshInvalidToken, self).setUp()
        self._assign_all_grants()
        self._setup_blackbox()

    def _build_token_response(self):
        return oauth2.test.oauth2_access_token_response(
            expires_in=3600,
            refresh_token=APPLICATION_TOKEN2,
        )

    error_codes = [
        'invalid_client',
        'invalid_grant',
        'invalid_request',
    ]

    @parameterized_expand([(e,) for e in error_codes])
    def test_invalid_token_response(self, error):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = oauth2.test.build_error(error)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())

    error_codes = [
        'unknown',
    ]

    @parameterized_expand([(e,) for e in error_codes])
    def test_error_response(self, error):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = oauth2.test.build_error(error)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='token_response_error',
                        error=error,
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_dns_failed(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = self._build_dns_failure_proxy_error()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token,
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='dns_failed',
                        hostname=Url(REFRESH_TOKEN_URL1).hostname,
                    ),
                ),
            ],
        )

    def test_read_timeout(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                urllib3.exceptions.ReadTimeoutError(None, None, None),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='useragent_request_timeout',
                        duration=0,
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_ssl_failed(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = self._build_ssl_certificate_untrusted_zora_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token,
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='ssl_failed',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_http_status_500(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = FakeResponse('Internal server error', status_code=500)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='token_response_not_json',
                        http_status='500',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_too_long(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = oauth2.test.oauth2_access_token_response(
            access_token='Too long' + 'x' * MAX_RESPONSE_LEN,
        )
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='token_response_too_long',
                        http_status='200',
                        max_response_length=MAX_RESPONSE_LEN,
                        response_length=len(refresh_token_response_on_invalid_token.content),
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_response_not_json(self):
        token_response = self._build_token_response()
        refresh_token_response_on_valid_token = self._build_token_response()
        refresh_token_response_on_invalid_token = FakeResponse('<html>Kekeke</html>', status_code=200)
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                refresh_token_response_on_valid_token.to_zora_response(),
                refresh_token_response_on_invalid_token.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_error_redirect_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(
            diagnostics,
            [
                FailureDiagnostics(
                    dict(
                        context='refresh_invalid_token',
                        type='token_response_not_json',
                        http_status='200',
                        url=REFRESH_TOKEN_URL1,
                    ),
                ),
            ],
        )

    def test_manage_to_refresh_invalid_token(self):
        token_response = self._build_token_response()
        self._fake_zora_useragent.set_response_values(
            [
                token_response.to_zora_response(),
                token_response.to_zora_response(),
                token_response.to_zora_response(),
            ],
        )

        rv = self._make_request()

        self._assert_collect_oauth_server_diagnostics_ok_response(rv)

        diagnostics = self._load_diagnostics_from_redis()
        self.assertEqual(diagnostics, list())


class _BaseReadDiagnosticsTestCase(_TestCaseMixin, TestCase):
    REQUEST_HTTP_METHOD = 'GET'
    REQUEST_URL = '/authz_in_web/read_diagnostics'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_QUERY = dict(
        consumer=CONSUMER1,
        application_name=APPLICATION_NAME1,
    )


class TestReadDiagnostics(_BaseReadDiagnosticsTestCase):
    def setUp(self):
        super(TestReadDiagnostics, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web-for-token-read-diagnostics'])

    def test_ok(self):
        diagnostics = [
            dict(
                foo='foo1',
                bar='bar1',
            ),
            dict(
                foo='foo2',
                bar='bar2',
            ),
        ]
        save_failure_diagnostics(APPLICATION_NAME1, map(FailureDiagnostics, diagnostics))

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response=dict(
                diagnostics=diagnostics,
            ),
        )

    def test_no_diagnostics(self):
        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response=dict(diagnostics=list()),
        )

    def test_too_much_diagnostics(self):
        diagnostics_dicts = [
            dict(
                foo='foo1',
                bar='bar1',
            ),
            dict(
                foo='foo2',
                bar='bar2',
            ),
            dict(
                foo='foo3',
                bar='bar3',
            ),
        ]
        diagnostics = map(FailureDiagnostics, diagnostics_dicts)
        self._save_diagnostics_to_redis(diagnostics)

        rv = self._make_request()

        self._assert_ok_response(
            rv,
            response=dict(
                diagnostics=diagnostics_dicts[-2:],
            ),
        )
        self.assertEqual(self._load_diagnostics_from_redis(), diagnostics)

    def test_redis_failed(self):
        with mock.patch.object(self._fake_redis, 'lrange') as fake_lrange:
            fake_lrange.side_effect = RedisError()

            rv = self._make_request()

        self._assert_error_response(rv, ['internal_error'])


class TestReadDiagnosticsPassportApplication(_BaseReadDiagnosticsTestCase):
    def setUp(self):
        super(TestReadDiagnosticsPassportApplication, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-web-for-token-read-diagnostics'])

    def _build_app_settings(self):
        app_conf = dict(DEFAULT_APPLICATION_CONF)
        app_conf.update(group_id=ApplicationGroupId.passport)
        return [app_conf]

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['application.unknown'])


class TestSaveFailureDiagnostics(_TestCaseMixin, TestCase):
    def test_ring_buffer(self):
        saved_diagnostics = [FailureDiagnostics(dict(idx=idx)) for idx in range(3)]
        app_name = 'x'

        for diag in saved_diagnostics:
            save_failure_diagnostics(app_name, [diag])

        loaded_diagnostics = self._load_diagnostics_from_redis(application_name=app_name)
        self.assertEqual(loaded_diagnostics, saved_diagnostics[-2:])

    def test_diagnostics_id(self):
        save_failure_diagnostics('foo', [FailureDiagnostics(dict())])

        # Неправильное безпрефиксное имя
        self.assertFalse(self._fake_redis.lrange('foo', 0, -1))

        # Праивлильное имя с префиксом
        self.assertTrue(self._fake_redis.lrange(':fd:foo', 0, -1))


class TestStartUserParam(_BaseStartTestCase):
    REQUEST_DATA = deep_merge(_BaseStartTestCase.REQUEST_DATA, dict(user_param='hello'))

    def setUp(self):
        super(TestStartUserParam, self).setUp()
        self._assign_all_grants()

    def _build_app_settings(self):
        return [deep_merge(
            DEFAULT_APPLICATION_CONF,
            dict(authorize_user_param=str(UserParamDescriptor(name='user_param'))),
        )]

    def _build_authorization_url(self, extra_args=None, **kwargs):
        if extra_args is None:
            extra_args = dict()
        extra_args.setdefault('user_param', 'hello')
        return super(TestStartUserParam, self)._build_authorization_url(extra_args=extra_args, **kwargs)

    def _build_start_url(self, extra_args=None, **kwargs):
        if extra_args is None:
            extra_args = dict()
        extra_args.setdefault('user_param', 'hello')
        return super(TestStartUserParam, self)._build_start_url(extra_args=extra_args, **kwargs)

    def _build_session(self, user_param='hello', **kwargs):
        return super(TestStartUserParam, self)._build_session(user_param=user_param, **kwargs)

    def test_ok(self):
        self._setup_blackbox()
        rv = self._make_request()
        self._assert_start_ok_response(rv)


class TestBindSubmitUserParam(_BaseBindSubmitTestCase):
    def setUp(self):
        super(TestBindSubmitUserParam, self).setUp()
        self._assign_all_grants()

    def _build_app_settings(self):
        return [
            deep_merge(
                DEFAULT_APPLICATION_CONF,
                dict(
                    token_user_param=str(UserParamDescriptor(
                        name='user_param',
                        type=UserParamDescriptor.TYPE_HEADER,
                    )),
                ),
            ),
            deep_merge(
                DEFAULT_APPLICATION_CONF,
                dict(
                    application_id=APPLICATION_ID2,
                    application_name=APPLICATION_NAME2,
                    token_user_param=str(UserParamDescriptor(
                        name='user_param',
                        type=UserParamDescriptor.TYPE_DATA,
                    )),
                ),
            ),
            deep_merge(
                DEFAULT_APPLICATION_CONF,
                dict(
                    application_id=APPLICATION_ID3,
                    application_name=APPLICATION_NAME3,
                    token_user_param=str(UserParamDescriptor(name='user_param')),
                ),
            ),
        ]

    def _build_session(self, user_param='hello', **kwargs):
        return super(TestBindSubmitUserParam, self)._build_session(user_param=user_param, **kwargs)

    def setup_environment(self):
        self._setup_authorization_code_response()
        self._setup_blackbox()

    def test_header(self):
        self.setup_environment()

        rv = self._make_request(data=dict(track=self._build_task_cookie()))

        self._assert_bind_submit_form_bind_agreement_response(rv)

        assert len(self._fake_zora_useragent.requests) == 1
        assert self._fake_zora_useragent.requests[0].headers.get('user_param') == 'hello'

    def test_data(self):
        self.setup_environment()
        app = Application(identifier=APPLICATION_ID2, name=APPLICATION_NAME2)

        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(session_kwargs=dict(application=app)),
            ),
        )

        self._assert_bind_submit_form_bind_agreement_response(
            rv,
            session=self._build_bind_submit_form_bind_agreement_session(application=app),
        )

        assert len(self._fake_zora_useragent.requests) == 1
        assert self._fake_zora_useragent.requests[0].data.get('user_param') == 'hello'

    def test_data_default(self):
        self.setup_environment()
        app = Application(identifier=APPLICATION_ID3, name=APPLICATION_NAME3)

        rv = self._make_request(
            data=dict(
                track=self._build_task_cookie(session_kwargs=dict(application=app)),
            ),
        )

        self._assert_bind_submit_form_bind_agreement_response(
            rv,
            session=self._build_bind_submit_form_bind_agreement_session(application=app),
        )

        assert len(self._fake_zora_useragent.requests) == 1
        assert self._fake_zora_useragent.requests[0].data.get('user_param') == 'hello'
