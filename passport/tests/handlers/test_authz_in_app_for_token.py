# -*- coding: utf-8 -*-

from datetime import timedelta
import json

from furl import furl
from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.social.broker.cookies import build_json_secure_cookie
from passport.backend.social.broker.misc import generate_retpath
from passport.backend.social.broker.test import InternalBrokerHandlerV1TestCase
from passport.backend.social.common.application import Application
from passport.backend.social.common.builders.blackbox import BlackboxTemporaryError
from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import (
    PLACE_FRAGMENT,
    PLACE_QUERY,
    urlencode,
    X_TOKEN_SCOPE,
)
from passport.backend.social.common.oauth2.test import build_error as oauth2_build_error
from passport.backend.social.common.pkce import (
    PKCE_METHOD_PLAIN,
    PKCE_METHOD_S256,
    s256,
)
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import (
    find_refresh_token_by_token_id,
    save_refresh_token,
)
from passport.backend.social.common.task import (
    save_task_to_redis,
    Task,
)
from passport.backend.social.common.test.conf import settings_context
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_ID3,
    APPLICATION_NAME1,
    APPLICATION_SECRET1,
    APPLICATION_SECRET2,
    APPLICATION_SECRET3,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN_TTL1,
    APPLICATION_TOKEN_TTL2,
    AUTHORIZATION_CODE1,
    AUTHORIZATION_CODE2,
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    EXTERNAL_APPLICATION_ID3,
    FRONTEND_URL1,
    FRONTEND_URL2,
    PKCE_CODE_CHALLENGE1,
    PKCE_CODE_CHALLENGE2,
    PKCE_CODE_VERIFIER1,
    REQUEST_ID1,
    RETPATH1,
    RETPATH2,
    TASK_ID1,
    TASK_ID2,
    TASK_TTL1,
    UID1,
    UID2,
    USER_IP1,
    USER_IP2,
    YANDEX_TOKEN1,
    YANDEX_TOKEN2,
)
from passport.backend.social.common.test.types import (
    DatetimeNow,
    FakeResponse,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_value_for_account,
    save_token,
)
from passport.backend.social.common.useragent import RequestError as UserAgentRequestError


CONF_APPLICATIONS = [
    dict(
        application_id=APPLICATION_ID1,
        application_name=APPLICATION_NAME1,
        provider_client_id=EXTERNAL_APPLICATION_ID1,
        secret=APPLICATION_SECRET1,
        authorization_url='https://y.x/authorize',
        token_url='https://y.x/token',
        domain='social.yandex.net',
        request_from_intranet_allowed='1',
    ),
    dict(
        application_id=APPLICATION_ID2,
        application_name='app_without_provider',
        provider_client_id=EXTERNAL_APPLICATION_ID2,
        secret=APPLICATION_SECRET2,
        authorization_url='https://z.x/authz',
        token_url='https://z.x/token',
        domain='social.yandex.net',
        request_from_intranet_allowed='1',
    ),
    dict(
        application_id=APPLICATION_ID3,
        application_name='app_with_provider',
        provider_client_id=EXTERNAL_APPLICATION_ID3,
        secret=APPLICATION_SECRET3,
        domain='social.yandex.net',
        provider_id=Vkontakte.id,
        request_from_intranet_allowed='1',
    ),
]


class BaseStartTestCase(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_app/start'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = dict(
        retpath=RETPATH1,
        place=PLACE_QUERY,
        application_name=APPLICATION_NAME1,
        code_challenge=PKCE_CODE_CHALLENGE1,
        code_challenge_method=PKCE_METHOD_PLAIN,
        consumer=CONSUMER1,
    )
    REQUEST_DATA = dict(
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def setUp(self):
        super(BaseStartTestCase, self).setUp()
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-app'])

    def build_settings(self):
        conf = super(BaseStartTestCase, self).build_settings()
        conf.update(
            dict(
                applications=CONF_APPLICATIONS,
            ),
        )
        return conf

    DEFAULT_SESSION_APPLICATION = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)

    def _build_session(self,
                       application=DEFAULT_SESSION_APPLICATION,
                       code_challenge=PKCE_CODE_CHALLENGE1,
                       code_challenge_method=PKCE_METHOD_PLAIN,
                       consumer=CONSUMER1,
                       task_id=TASK_ID1,
                       retpath=RETPATH1,
                       place=PLACE_QUERY,
                       provider=None,
                       state='authz_in_app.r_to_soc',
                       uid=None,
                       yandexuid=None,
                       passthrough_errors=None):
        task = Task()
        task.state = state
        task.start_args = dict(foo='bar')
        task.task_id = task_id
        task.created = now.f()
        task.code_challenge = code_challenge
        task.code_challenge_method = code_challenge_method
        task.consumer = consumer
        task.application = application
        task.provider = provider
        task.retpath = retpath
        task.place = place
        task.uid = uid
        task.yandexuid = yandexuid
        task.passthrough_errors = passthrough_errors or []
        return task

    def _assert_start_error_response(self, rv, errors, retpath=Undefined):
        if retpath is Undefined:
            retpath = RETPATH1
        self._assert_error_response(rv, errors, retpath)

    def _build_redirect_url(self,
                            base_url='https://y.x/authorize',
                            yandex_auth_code=None,
                            client_id=EXTERNAL_APPLICATION_ID1,
                            extra_args=None,
                            provider_allows_args_in_redirect_url=False,
                            display=None,
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

        if yandex_auth_code is not None:
            url.args['yandex_auth_code'] = yandex_auth_code

        if display is not None:
            url.args['display'] = display

        if extra_args is not None:
            url.args.update(extra_args)

        redirect_url = 'https://social.yandex.net/broker/redirect'
        callback_url = '%s/authz_in_app/%s/callback' % (frontend_url, TASK_ID1)
        if provider_allows_args_in_redirect_url:
            redirect_url = redirect_url + '?' + urlencode(dict(url=callback_url))
            url = url.url + '&' + urlencode(dict(redirect_uri=redirect_url))
        else:
            url.args.update(
                dict(
                    redirect_uri=redirect_url,
                    state=callback_url,
                ),
            )
            url = url.url
        return url

    def _assert_start_ok_response(self, rv, expected=None):
        expected = expected or dict()
        self.assertEqual(rv.status_code, 200)
        self._assert_response_forwards_to_url(
            rv,
            expected.get('location', self._build_redirect_url()),
        )


class TestStart(BaseStartTestCase):
    def test_code_challenge(self):
        rv = self._make_request(query=dict(code_challenge=PKCE_CODE_CHALLENGE2))
        self._assert_response_contains_session(rv, self._build_session(code_challenge=PKCE_CODE_CHALLENGE2))

    def test_no_code_challenge(self):
        rv = self._make_request(query=dict(code_challenge=None))
        self._assert_start_error_response(rv, ['PkceCodeInvalidError'])

    def test_code_challenge_too_short(self):
        rv = self._make_request(query=dict(code_challenge='1' * 42))
        self._assert_start_error_response(rv, ['PkceCodeInvalidError'])

    def test_code_challenge_too_long(self):
        rv = self._make_request(query=dict(code_challenge='1' * 129))
        self._assert_start_error_response(rv, ['PkceCodeInvalidError'])

    def test_code_challenge_method_plain(self):
        rv = self._make_request(query=dict(code_challenge_method='plain'))
        self._assert_response_contains_session(rv, self._build_session(code_challenge_method=PKCE_METHOD_PLAIN))

    def test_code_challenge_S256_in_upper_case(self):
        rv = self._make_request(query=dict(code_challenge_method='S256'))
        self._assert_response_contains_session(rv, self._build_session(code_challenge_method=PKCE_METHOD_S256))

    def test_code_challenge_method_S256_in_lower_case(self):
        rv = self._make_request(query=dict(code_challenge_method='s256'))
        self._assert_response_contains_session(rv, self._build_session(code_challenge_method=PKCE_METHOD_S256))

    def test_no_code_challenge_method(self):
        rv = self._make_request(query=dict(code_challenge_method=None))
        self._assert_response_contains_session(rv, self._build_session(code_challenge_method=PKCE_METHOD_PLAIN))

    def test_invalid_code_challenge_method(self):
        rv = self._make_request(query=dict(code_challenge_method='Y256'))
        self._assert_start_error_response(rv, ['PkceMethodInvalidError'])

    def test_yandex_auth_code(self):
        rv = self._make_request(query=dict(yandex_auth_code='yandex_auth_code1'))

        expected_redirect_url = self._build_redirect_url(yandex_auth_code='yandex_auth_code1')
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

    def test_no_yandex_auth_code(self):
        rv = self._make_request(query=dict(yandex_auth_code=None))

        expected_redirect_url = self._build_redirect_url(yandex_auth_code=None)
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

    def test_no_application_name(self):
        rv = self._make_request(query=dict(application_name=None))
        self._assert_start_error_response(rv, ['ApplicationUnknownError'])

    def test_unknown_application(self):
        rv = self._make_request(query=dict(application_name='unknown'))
        self._assert_start_error_response(rv, ['ApplicationUnknownError'])

    def test_application_without_provider(self):
        rv = self._make_request(query=dict(application_name='app_without_provider'))

        expected_redirect_url = self._build_redirect_url(base_url='https://z.x/authz', client_id=EXTERNAL_APPLICATION_ID2)
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

        expected_app = Application(identifier=APPLICATION_ID2, name='app_without_provider')
        self._assert_response_contains_session(rv, self._build_session(provider=None, application=expected_app))

    def test_application_with_provider(self):
        rv = self._make_request(query=dict(application_name='app_with_provider'))

        expected_redirect_url = self._build_redirect_url(
            base_url='https://oauth.vk.com/authorize',
            client_id=EXTERNAL_APPLICATION_ID3,
            extra_args=dict(v='5.131'),
            provider_allows_args_in_redirect_url=True,
            scope='email,offline',
        )
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

        expected_app = Application(identifier=APPLICATION_ID3, name='app_with_provider')
        self._assert_response_contains_session(
            rv,
            self._build_session(
                provider=dict(id=1, code='vk', name='vkontakte'),
                application=expected_app,
            ),
        )

    def test_retpath(self):
        rv = self._make_request(query=dict(retpath=RETPATH2))
        self._assert_response_contains_session(rv, self._build_session(retpath=RETPATH2))

    def test_no_retpath(self):
        rv = self._make_request(query=dict(retpath=None))
        self._assert_start_error_response(rv, ['RetpathInvalidError'], retpath=None)

    def test_place_fragment(self):
        rv = self._make_request(query=dict(place=PLACE_FRAGMENT))
        self._assert_response_contains_session(rv, self._build_session(place=PLACE_FRAGMENT))

    def test_place_query(self):
        rv = self._make_request(query=dict(place=PLACE_QUERY))
        self._assert_response_contains_session(rv, self._build_session(place=PLACE_QUERY))

    def test_no_place(self):
        rv = self._make_request(query=dict(place=None))
        self._assert_response_contains_session(rv, self._build_session(place=PLACE_QUERY))

    def test_invalid_display(self):
        rv = self._make_request(query=dict(display='viewsonic'))

        self._assert_start_error_response(rv, ['DisplayInvalidError'])

    def test_consumer(self):
        rv = self._make_request(query=dict(consumer=CONSUMER2))
        self._assert_response_contains_session(rv, self._build_session(consumer=CONSUMER2))

    def test_consumer_unknown(self):
        rv = self._make_request(query=dict(consumer='unknown'))
        self._assert_response_contains_session(rv, self._build_session(consumer='unknown'))

    def test_no_consumer(self):
        rv = self._make_request(query=dict(consumer=None))
        self._assert_start_error_response(rv, ['ConsumerUnknownError'], retpath=None)

    def test_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=FRONTEND_URL2))

        expected_redirect_url = self._build_redirect_url(frontend_url=FRONTEND_URL2)
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

    def test_no_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_start_error_response(rv, ['SessionInvalidError'])

    def test_no_user_ip(self):
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_start_error_response(rv, ['UserIpInvalidError'])

    def test_session_service_data(self):
        self._fake_generate_task_id.set_retval(TASK_ID2)

        rv = self._make_request()

        self._assert_response_contains_session(
            rv,
            self._build_session(
                task_id=TASK_ID2,
                state='authz_in_app.r_to_soc',

                uid=None,
                yandexuid=None,
            ),
        )

    def test_authorize_url_contains_query(self):
        with settings_context(
            fake_db=self._fake_db,
            applications=[
                dict(
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    secret=APPLICATION_SECRET1,
                    authorization_url='https://y.x/authorize?hello=yello',
                    token_url='https://y.x/token',
                    domain='social.yandex.net',
                ),
            ],
        ):
            rv = self._make_request()

        expected_redirect_url = self._build_redirect_url(extra_args=dict(hello='yello'))
        self._assert_start_ok_response(rv, dict(location=expected_redirect_url))

    def test_passthrough_errors(self):
        rv = self._make_request(query={'passthrough_errors': 'the_error'})

        self._assert_start_ok_response(rv)
        self._assert_response_contains_session(
            rv,
            self._build_session(passthrough_errors=['the_error']),
        )


class TestStartMordaRetpath(BaseStartTestCase):
    def build_settings(self):
        conf = super(TestStartMordaRetpath, self).build_settings()
        conf.update(
            dict(
                applications=CONF_APPLICATIONS,
            ),
        )
        conf['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = 'yandex.' yandex_tld | 'www.yandex.' yandex_tld
                    """,
                ],
            ),
        )
        return conf

    def test_retpath_yandex_ru(self):
        rv = self._make_request(query=dict(retpath='https://www.yandex.ru/'))
        self._assert_response_contains_session(rv, self._build_session(retpath='https://www.yandex.ru/'))

    def test_retpath_yandex_com(self):
        rv = self._make_request(query=dict(retpath='https://www.yandex.com/'))
        self._assert_response_contains_session(rv, self._build_session(retpath='https://www.yandex.com/?redirect=0'))


class TestContinue(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_app/%s/continue' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }

    def setUp(self):
        super(TestContinue, self).setUp()

        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
                token_type='Bearer',
            ),
        )
        response = FakeResponse(value=response, status_code=200)
        self._fake_useragent.set_response_value(response)

        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-app'])

    def build_settings(self):
        conf = super(TestContinue, self).build_settings()
        conf.update(dict(applications=CONF_APPLICATIONS))
        return conf

    def _get_default_request_data(self):
        return dict(
            frontend_url=FRONTEND_URL1,
            user_ip=USER_IP1,
            track=self._build_task_cookie(),
        )

    def _build_task_cookie(self, session_kwargs=dict(), expired_at=None):
        _now = now()
        expired_at = expired_at or (_now + timedelta(seconds=TASK_TTL1))
        expires_in = (expired_at - _now).total_seconds()

        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=expires_in)

        return task_cookie

    DEFAULT_SESSION_APPLICATION = Application(
        identifier=APPLICATION_ID1,
        name=APPLICATION_NAME1,
        is_third_party=False,
    )

    def _build_session(self,
                       application=DEFAULT_SESSION_APPLICATION,
                       code_challenge=PKCE_CODE_CHALLENGE1,
                       code_challenge_method=PKCE_METHOD_PLAIN,
                       consumer=CONSUMER1,
                       task_id=TASK_ID1,
                       retpath=RETPATH1,
                       place=PLACE_QUERY,
                       provider=None,
                       state='authz_in_app.r_to_cont',
                       uid=None,
                       yandexuid=None,
                       created=1.0,
                       exchange=AUTHORIZATION_CODE1,
                       in_redis=None):
        task = Task()
        task.application = application
        task.code_challenge = code_challenge
        task.code_challenge_method = code_challenge_method
        task.consumer = consumer
        task.created = created
        task.exchange = exchange
        task.in_redis = in_redis
        task.place = place
        task.provider = provider
        task.retpath = retpath
        task.start_args = dict(foo='bar')
        task.state = state
        task.task_id = task_id
        task.uid = uid
        task.yandexuid = yandexuid
        return task

    def _build_response_session(self, **kwargs):
        kwargs.setdefault('in_redis', True)
        return self._build_session(**kwargs)

    def _build_task(self,
                    application=DEFAULT_SESSION_APPLICATION,
                    task_id=TASK_ID1,
                    code_challenge=PKCE_CODE_CHALLENGE1,
                    code_challenge_method=PKCE_METHOD_PLAIN,
                    consumer=CONSUMER1,
                    provider=None,
                    token=APPLICATION_TOKEN1,
                    token_expires_in=APPLICATION_TOKEN_TTL1,
                    profile=None,
                    refresh_token=None,
                    scope=None,
                    token_expired_at=None,
                    finished=None):
        task = Task()
        task.application = application

        if token_expired_at is None:
            token_expired_at = now.i() + token_expires_in
        task.access_token = dict(
            value=token,
            expires=token_expired_at,
            scope=scope,
        )
        if refresh_token is not None:
            task.access_token.update(dict(refresh=refresh_token))

        task.created = 1.0

        if finished is None:
            task.finished = now.f()
        else:
            task.finished = finished

        task.in_redis = True
        task.task_id = task_id
        task.consumer = consumer
        task.code_challenge = code_challenge
        task.code_challenge_method = code_challenge_method
        task.provider = provider
        task.profile = profile or dict()
        return task

    def _setup_task(self, task):
        save_task_to_redis(self._fake_redis, task.task_id, task)

    def _assert_continue_error_response(self, rv, errors, retpath=Undefined):
        if retpath is Undefined:
            retpath = RETPATH1
        self._assert_error_response(rv, errors, retpath)

    def _assert_continue_ok_response(self, rv, expected=None, session=None):
        expected = expected or dict()

        if session is None:
            session = self._build_response_session()

        self.assertEqual(rv.status_code, 200)
        self._assert_response_contains_session(rv, session)
        self._assert_response_forwards_to_url(
            rv,
            expected.get('location', self._build_ok_retpath(url=RETPATH1, task_id=TASK_ID1)),
        )

    def _assert_continue_task_equals(self, task):
        self._assert_task_equals(TASK_ID1, task)

    def _build_reverse_redirect_uri(self):
        redirect_url = 'https://social.yandex.net/broker/redirect'
        callback_url = '%s/authz_in_app/%s/callback' % (FRONTEND_URL1, TASK_ID1)
        return redirect_url + '?' + urlencode(dict(url=callback_url))

    def test_no_frontend_url(self):
        rv = self._make_request(data=dict(frontend_url=None))
        self._assert_continue_error_response(rv, ['SessionInvalidError'])

    def test_no_user_ip(self):
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_continue_error_response(rv, ['UserIpInvalidError'])

    def test_no_session(self):
        rv = self._make_request(data=dict(track=None))
        self._assert_continue_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_session_corrupted(self):
        rv = self._make_request(data=dict(track='corrupted'))
        self._assert_continue_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_unexpected_state(self):
        task_cookie = self._build_task_cookie(dict(state='r_to_cont'))
        rv = self._make_request(data=dict(track=task_cookie))
        self._assert_continue_error_response(rv, ['SessionInvalidError'])

    def test_state_r_to_cont(self):
        task_cookie = self._build_task_cookie(dict(state='authz_in_app.r_to_cont'))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(rv)
        self._assert_continue_task_equals(self._build_task())

    def test_session_task_id_matches_task_id(self):
        task_cookie = self._build_task_cookie(dict(task_id=TASK_ID1))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(rv)
        self._assert_continue_task_equals(self._build_task(task_id=TASK_ID1))

    def test_session_task_id_not_match_task_id(self):
        task_cookie = self._build_task_cookie(dict(task_id=TASK_ID2))
        rv = self._make_request(data=dict(track=task_cookie))
        self._assert_continue_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_session_too_old(self):
        task_cookie = self._build_task_cookie(expired_at=now())
        rv = self._make_request(data=dict(track=task_cookie))
        self._assert_continue_error_response(rv, ['SessionInvalidError'], retpath=None)

    def test_session_alive(self):
        task_cookie = self._build_task_cookie(expired_at=now() + timedelta(minutes=5))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(rv)
        self._assert_continue_task_equals(self._build_task())

    def test_code_challenge(self):
        task_cookie = self._build_task_cookie(dict(code_challenge=PKCE_CODE_CHALLENGE2))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            session=self._build_response_session(code_challenge=PKCE_CODE_CHALLENGE2),
        )
        self._assert_continue_task_equals(self._build_task(code_challenge=PKCE_CODE_CHALLENGE2))

    def test_code_challenge_method_s256(self):
        task_cookie = self._build_task_cookie(dict(code_challenge_method=PKCE_METHOD_S256))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            session=self._build_response_session(code_challenge_method=PKCE_METHOD_S256),
        )
        self._assert_continue_task_equals(self._build_task(code_challenge_method=PKCE_METHOD_S256))

    def test_code_challenge_method_plain(self):
        task_cookie = self._build_task_cookie(dict(code_challenge_method=PKCE_METHOD_PLAIN))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(rv)
        self._assert_continue_task_equals(self._build_task(code_challenge_method=PKCE_METHOD_PLAIN))

    def test_consumer(self):
        task_cookie = self._build_task_cookie(dict(consumer=CONSUMER2))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            session=self._build_response_session(consumer=CONSUMER2),
        )
        self._assert_continue_task_equals(self._build_task(consumer=CONSUMER2))

    def test_application_without_provider(self):
        app = Application(
            identifier=APPLICATION_ID2,
            name='app_without_provider',
            is_third_party=False,
        )
        task_cookie = self._build_task_cookie(dict(application=app))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            session=self._build_response_session(application=app),
        )
        self._assert_continue_task_equals(self._build_task(application=app))

        request = self._fake_useragent.requests[0]
        self.assertEqual(request.url, 'https://z.x/token')
        self.assertEqual(request.data['client_id'], EXTERNAL_APPLICATION_ID2)
        self.assertEqual(request.data['client_secret'], APPLICATION_SECRET2)

    def test_application_with_provider(self):
        app = Application(
            identifier=APPLICATION_ID3,
            name='app_with_provider',
            is_third_party=False,
        )
        task_cookie = self._build_task_cookie(
            dict(
                provider=dict(id=1, code='vk', name='vkontakte'),
                application=app,
            ),
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            session=self._build_response_session(
                provider=dict(id=1, code='vk', name='vkontakte'),
                application=app,
            ),
        )

        provider = dict(code='vk', id=1, name='vkontakte')
        self._assert_continue_task_equals(
            self._build_task(
                application=app,
                provider=provider,
                scope='email,offline',
                # Профиль не создаётся!
                profile=None,
            ),
        )

        request = self._fake_useragent.requests[0]
        self.assertEqual(request.url, 'https://oauth.vk.com/access_token')
        self.assertEqual(request.query['client_id'], EXTERNAL_APPLICATION_ID3)
        self.assertEqual(request.query['client_secret'], APPLICATION_SECRET3)

    def test_authz_code(self):
        task_cookie = self._build_task_cookie(dict(exchange=AUTHORIZATION_CODE2))

        self._make_request(data=dict(track=task_cookie))

        request = self._fake_useragent.requests[0]
        self.assertEqual(request.data['code'], AUTHORIZATION_CODE2)

    def test_reverse_redirect_uri_without_provider(self):
        self._make_request()

        request = self._fake_useragent.requests[0]
        self.assertEqual(request.data['redirect_uri'], 'https://social.yandex.net/broker/redirect')

    def test_reverse_redirect_uri_with_provider_allows_args_in_redirect_url(self):
        app = Application(identifier=APPLICATION_ID3, name='app_with_provider')
        task_cookie = self._build_task_cookie(
            dict(
                provider=dict(id=1, code='vk', name='vkontakte'),
                application=app,
                task_id=TASK_ID1,
            ),
        )

        self._make_request(data=dict(track=task_cookie))

        request = self._fake_useragent.requests[0]
        self.assertEqual(
            request.query['redirect_uri'],
            self._build_reverse_redirect_uri(),
        )

    def test_retpath(self):
        task_cookie = self._build_task_cookie(dict(retpath=RETPATH2))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(
            rv,
            dict(location=generate_retpath(RETPATH2, PLACE_QUERY, status='ok', task_id=TASK_ID1)),
            self._build_response_session(retpath=RETPATH2),
        )

    def test_place_query(self):
        task_cookie = self._build_task_cookie(dict(place=PLACE_QUERY))

        rv = self._make_request(data=dict(track=task_cookie))

        retpath = generate_retpath(RETPATH1, PLACE_QUERY, status='ok', task_id=TASK_ID1)
        self._assert_continue_ok_response(rv, dict(location=retpath))

    def test_place_fragment(self):
        task_cookie = self._build_task_cookie(dict(place=PLACE_FRAGMENT))

        rv = self._make_request(data=dict(track=task_cookie))

        retpath = generate_retpath(RETPATH1, PLACE_FRAGMENT, status='ok', task_id=TASK_ID1)
        self._assert_continue_ok_response(
            rv,
            dict(location=retpath),
            self._build_response_session(place=PLACE_FRAGMENT),
        )

    def test_token(self):
        response = json.dumps(
            dict(
                access_token='token',
                expires_in=APPLICATION_TOKEN_TTL2,
                token_type='Bearer',
            ),
        )
        response = FakeResponse(value=response, status_code=200)
        self._fake_useragent.set_response_value(response)

        self._make_request()

        self._assert_continue_task_equals(self._build_task(token='token', token_expires_in=APPLICATION_TOKEN_TTL2))

    def test_refresh_token(self):
        response = json.dumps(
            dict(
                access_token=APPLICATION_TOKEN1,
                expires_in=APPLICATION_TOKEN_TTL1,
                token_type='Bearer',
                refresh_token=APPLICATION_TOKEN2,
            ),
        )
        response = FakeResponse(value=response, status_code=200)
        self._fake_useragent.set_response_value(response)

        self._make_request()

        self._assert_continue_task_equals(self._build_task(refresh_token=APPLICATION_TOKEN2))

    def test_authz_code_rejected(self):
        self._fake_useragent.set_response_value(oauth2_build_error('invalid_grant'))

        rv = self._make_request()

        self._assert_continue_error_response(rv, ['CommunicationFailedError'])

    def test_timeout_when_getting_token(self):
        self._fake_useragent.set_response_value(UserAgentRequestError())

        rv = self._make_request()

        self._assert_continue_error_response(rv, ['CommunicationFailedError'])

    def test_got_token(self):
        self._setup_task(
            self._build_task(
                finished=now.f(),
                token=APPLICATION_TOKEN2,
                token_expired_at=now.i() + APPLICATION_TOKEN_TTL1,
            ),
        )
        task_cookie = self._build_task_cookie(dict(in_redis=True))

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_continue_ok_response(rv)
        self._assert_continue_task_equals(
            self._build_task(
                token=APPLICATION_TOKEN2,
            ),
        )


class TestEntrustToAccount(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_app/entrust_to_account'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_DATA = dict(
        task_id=TASK_ID1,
        token=YANDEX_TOKEN1,
        user_ip=USER_IP1,
        code_verifier=PKCE_CODE_VERIFIER1,
    )

    def setUp(self):
        super(TestEntrustToAccount, self).setUp()

        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=UID1, scope=X_TOKEN_SCOPE),
        )
        self._fake_grants_config.add_consumer(CONSUMER1, [CONSUMER_IP1], ['authz-in-app-entrust-to-account'])

    def build_settings(self):
        conf = super(TestEntrustToAccount, self).build_settings()
        conf.update(
            dict(
                applications=CONF_APPLICATIONS,
            ),
        )
        return conf

    DEFAULT_TASK_APPLICATION = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)

    def _build_task(self,
                    application=DEFAULT_TASK_APPLICATION,
                    task_id=TASK_ID1,
                    code_challenge=PKCE_CODE_CHALLENGE1,
                    code_challenge_method=PKCE_METHOD_PLAIN,
                    consumer=CONSUMER1,
                    provider=None,
                    token=APPLICATION_TOKEN1,
                    token_expires_in=APPLICATION_TOKEN_TTL1,
                    profile=None,
                    refresh_token=None,
                    scope=None):
        task = Task()
        task.application = application

        if token_expires_in is not None:
            token_expired_at = now.i() + token_expires_in
        else:
            token_expired_at = None

        task.access_token = dict(
            value=token,
            expires=token_expired_at,
            scope=scope,
        )
        if refresh_token is not None:
            task.access_token.update(dict(refresh=refresh_token))

        task.created = 1.0
        task.finished = now.f()
        task.task_id = task_id
        task.consumer = consumer
        task.code_challenge = code_challenge
        task.code_challenge_method = code_challenge_method
        task.provider = provider
        task.profile = profile or dict()
        return task

    def _setup_task(self, task):
        save_task_to_redis(self._fake_redis, task.task_id, task)

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
            token_expires_at = now() + timedelta(seconds=token_expires_in)
            token_expires_at = DatetimeNow(timestamp=token_expires_at)
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

    def _assert_refresh_token_not_saved(self,
                                        uid=UID1,
                                        application_id=APPLICATION_ID1,
                                        token_value=APPLICATION_TOKEN1):
        token = find_token_by_value_for_account(uid, application_id, token_value, self._fake_db.get_engine())
        self.assertIsNotNone(token)

        refresh_token = find_refresh_token_by_token_id(token.token_id, self._fake_db.get_engine())
        self.assertIsNone(refresh_token)

    def _assert_yandex_token_exchanged_for_userinfo(self, token=YANDEX_TOKEN1, user_ip=USER_IP1):
        request = self._fake_blackbox.requests[0]
        request.assert_url_starts_with('http://black.yandex.ru/blackbox/')
        request.assert_query_equals(
            dict(
                method='oauth',
                oauth_token=token,
                userip=user_ip,
                regname='yes',
                aliases='all',
                format='json',
                is_display_name_empty='yes',
            ),
        )

    def _assert_entrust_to_account_ok_response(self, rv):
        self._assert_ok_response(rv, {'status': 'ok'})

    def _assert_entrust_to_account_error_response(self, rv, expected):
        self._assert_error_response(rv, expected, retpath=None)

    def test_no_task_id(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(task_id=None))
        self._assert_entrust_to_account_error_response(rv, ['TaskIdInvalidError'])

    def test_task_id_too_long(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(task_id='00' * 33))
        self._assert_entrust_to_account_error_response(rv, ['TaskIdInvalidError'])

    def test_task_not_found(self):
        rv = self._make_request(data=dict(task_id=TASK_ID2))
        self._assert_entrust_to_account_error_response(rv, ['TaskNotFoundError'])

    def test_task_found(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(task_id=TASK_ID1))
        self._assert_entrust_to_account_ok_response(rv)

    def test_no_yandex_token(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(token=None))
        self._assert_entrust_to_account_error_response(rv, ['AuthorizationRequiredError'])

    def test_yandex_token_invalid(self):
        self._setup_task(self._build_task())
        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(status=BLACKBOX_OAUTH_INVALID_STATUS, error='expired_token'),
        )

        rv = self._make_request()

        self._assert_entrust_to_account_error_response(rv, ['AuthorizationRequiredError'])

    def test_exchange_yandex_token_network_failed(self):
        self._setup_task(self._build_task())
        self._fake_blackbox.set_response_side_effect('oauth', BlackboxTemporaryError())

        rv = self._make_request()

        self._assert_entrust_to_account_error_response(rv, ['CommunicationFailedError'])

    def test_yandex_token_is_valid(self):
        self._setup_task(self._build_task())
        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=UID2, scope=X_TOKEN_SCOPE),
        )

        rv = self._make_request(data=dict(token=YANDEX_TOKEN2))

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_yandex_token_exchanged_for_userinfo(token=YANDEX_TOKEN2)
        self._assert_token_saved(uid=UID2)

    def test_no_user_ip(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(user_ip=None))
        self._assert_entrust_to_account_error_response(rv, ['UserIpInvalidError'])

    def test_user_ip(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(user_ip=USER_IP2))

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_yandex_token_exchanged_for_userinfo(user_ip=USER_IP2)

    def test_no_code_verifier(self):
        self._setup_task(self._build_task())
        rv = self._make_request(data=dict(code_verifier=None))
        self._assert_entrust_to_account_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_too_long(self):
        self._setup_task(
            self._build_task(
                code_challenge='1' * 129,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(data=dict(code_verifier='1' * 129))

        self._assert_entrust_to_account_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_plain_invalid(self):
        self._setup_task(
            self._build_task(
                code_challenge=PKCE_CODE_CHALLENGE1,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(data=dict(code_verifier=PKCE_CODE_CHALLENGE2))

        self._assert_entrust_to_account_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_plain_valid(self):
        self._setup_task(
            self._build_task(
                code_challenge=PKCE_CODE_CHALLENGE1,
                code_challenge_method=PKCE_METHOD_PLAIN,
            ),
        )

        rv = self._make_request(data=dict(code_verifier=PKCE_CODE_CHALLENGE1))

        self._assert_entrust_to_account_ok_response(rv)

    def test_code_verifier_s256_invalid(self):
        self._setup_task(
            self._build_task(
                code_challenge=s256(PKCE_CODE_CHALLENGE2),
                code_challenge_method=PKCE_METHOD_S256,
            ),
        )

        rv = self._make_request(data=dict(code_verifier=PKCE_CODE_CHALLENGE1))

        self._assert_entrust_to_account_error_response(rv, ['PkceVerifierInvalidError'])

    def test_code_verifier_s256_valid(self):
        self._setup_task(
            self._build_task(
                code_challenge=s256(PKCE_CODE_CHALLENGE2),
                code_challenge_method=PKCE_METHOD_S256,
            ),
        )

        rv = self._make_request(data=dict(code_verifier=PKCE_CODE_CHALLENGE2))

        self._assert_entrust_to_account_ok_response(rv)

    def test_yandex_token_has_no_xtoken_scope(self):
        self._setup_task(self._build_task())
        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=UID1, scope='oauth:grant_y'),
        )

        rv = self._make_request()

        self._assert_entrust_to_account_error_response(rv, ['AuthorizationRequiredError'])

    def test_yandex_token_has_xtoken_scope(self):
        self._setup_task(self._build_task())
        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=UID1, scope=X_TOKEN_SCOPE),
        )

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)

    def test_provider_token_has_no_scopes(self):
        self._setup_task(self._build_task(scope=None))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(scopes=set([]))

    def test_provider_token_has_some_scopes(self):
        self._setup_task(self._build_task(scope='hello yello'))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(scopes=set(['hello', 'yello']))

    def test_provider_token_of_unknown_application(self):
        application = Application(identifier=100500, name='max100500')
        self._setup_task(self._build_task(application=application))

        rv = self._make_request()

        self._assert_entrust_to_account_error_response(rv, ['ApplicationUnknownError'])

    def test_provider_token_of_valid_application(self):
        application = Application(identifier=APPLICATION_ID2, name='app_without_provider')
        self._setup_task(self._build_task(application=application))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(application_id=APPLICATION_ID2)

    def test_provider_token_not_expire(self):
        self._setup_task(self._build_task(token_expires_in=None))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(token_expires_in=None)

    def test_provider_token_expires(self):
        self._setup_task(self._build_task(token_expires_in=APPLICATION_TOKEN_TTL2))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(token_expires_in=APPLICATION_TOKEN_TTL2)

    def test_no_refresh_token(self):
        self._setup_task(self._build_task(refresh_token=None))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved()
        self._assert_refresh_token_not_saved()

    def test_refresh_token(self):
        self._setup_task(self._build_task(refresh_token=APPLICATION_TOKEN2))

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved()
        self._assert_refresh_token_saved()

    def test_token_and_refresh_token_already_exist(self):
        token = Token(
            uid=UID1,
            profile_id=None,
            application_id=APPLICATION_ID1,
            value=APPLICATION_TOKEN1,
            secret=None,
            scopes=set(['hello']),
            expired=now() + timedelta(hours=1),
            created=now(),
            verified=now(),
            confirmed=now(),
        )
        save_token(token, self._fake_db.get_engine())

        refresh_token = RefreshToken(
            token_id=token.token_id,
            value=APPLICATION_TOKEN2,
            expired=None,
            scopes=set(['hello']),
        )
        save_refresh_token(refresh_token, self._fake_db.get_engine())

        application = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)

        self._setup_task(
            self._build_task(
                application=application,
                token=APPLICATION_TOKEN1,
                scope='yello',
                refresh_token=APPLICATION_TOKEN2,
                token_expires_in=APPLICATION_TOKEN_TTL2,
            ),
        )

        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(uid=UID1, scope=X_TOKEN_SCOPE),
        )

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_token_saved(
            uid=UID1,
            application_id=APPLICATION_ID1,
            token_value=APPLICATION_TOKEN1,
            scopes=set(['hello', 'yello']),
            token_expires_in=APPLICATION_TOKEN_TTL2,
        )
        self._assert_refresh_token_saved(
            uid=UID1,
            application_id=APPLICATION_ID1,
            token_value=APPLICATION_TOKEN1,
            refresh_token_value=APPLICATION_TOKEN2,
            scopes=set(['hello', 'yello']),
        )

    def test_ok(self):
        self._setup_task(self._build_task())

        rv = self._make_request()

        self._assert_entrust_to_account_ok_response(rv)
        self._assert_yandex_token_exchanged_for_userinfo()
        self._assert_token_saved()


class TestCallback(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/authz_in_app/%s/callback' % TASK_ID1
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
        'Ya-Consumerid': CONSUMER1,
    }
    REQUEST_QUERY = dict(
        code=AUTHORIZATION_CODE1,
    )
    REQUEST_DATA = dict(
        frontend_url=FRONTEND_URL1,
        user_ip=USER_IP1,
    )

    def setUp(self):
        super(TestCallback, self).setUp()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['authz-in-app'],
        )

    def build_settings(self):
        conf = super(TestCallback, self).build_settings()
        conf.update(dict(applications=CONF_APPLICATIONS))
        return conf

    def _build_task_cookie(self, session_kwargs=dict(), expired_at=None):
        _now = now()
        expired_at = expired_at or (_now + timedelta(seconds=TASK_TTL1))
        expires_in = (expired_at - _now).total_seconds()

        task = self._build_session(**session_kwargs)
        task_json = task.dump_session_data()
        task_cookie = build_json_secure_cookie(value=task_json, expires_in=expires_in)

        return task_cookie

    DEFAULT_SESSION_APPLICATION = Application(identifier=APPLICATION_ID1, name=APPLICATION_NAME1)

    def _build_session(self,
                       application=DEFAULT_SESSION_APPLICATION,
                       task_id=TASK_ID1,
                       state='authz_in_app.r_to_soc',
                       created=1.0,
                       exchange=None,
                       retpath=RETPATH1,
                       passthrough_errors=None):
        task = Task()
        task.state = state
        task.start_args = dict(foo='bar')
        task.task_id = task_id
        task.created = created
        task.application = application
        task.exchange = exchange
        task.retpath = retpath
        task.passthrough_errors = passthrough_errors or []
        return task

    def _build_continue_url(self):
        return '%s/authz_in_app/%s/continue' % (FRONTEND_URL1, TASK_ID1)

    def _assert_callback_ok_response(self, rv):
        self._assert_ok_response(
            rv,
            response={
                'task_id': TASK_ID1,
                'request_id': REQUEST_ID1,
            },
            skip=['cookies', 'location'],
        )
        self._assert_response_contains_session(
            rv,
            self._build_session(
                state='authz_in_app.r_to_cont',
                exchange=AUTHORIZATION_CODE1,
            ),
        )
        self._assert_response_forwards_to_url(rv, self._build_continue_url())

    def _assert_callback_error_response(self, rv, error, passthrough_error=False):
        kwargs = dict()
        if passthrough_error:
            kwargs.update(
                dict(
                    retpath_kwargs=dict(
                        additional_args={
                            'code': error,
                            'request_id': REQUEST_ID1,
                        },
                    ),
                    response={'passthrough': True},
                ),
            )
        self._assert_error_response(rv, [error], RETPATH1, **kwargs)

    def test_ok(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_callback_ok_response(rv)

    def test_access_denied_error(self):
        task_cookie = self._build_task_cookie()

        rv = self._make_request(
            query={'error': 'access_denied'},
            exclude_query=['code'],
            data=dict(track=task_cookie),
        )

        self._assert_callback_error_response(rv, 'UserDeniedError')

    def test_access_denied_error__passthrough_errors(self):
        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                passthrough_errors=['userdeniederror'],
            ),
        )

        rv = self._make_request(
            query={'error': 'access_denied'},
            exclude_query=['code'],
            data=dict(track=task_cookie),
        )

        self._assert_callback_error_response(rv, 'UserDeniedError', passthrough_error=True)

    def test_access_denied_error__passthrough_other_errors(self):
        task_cookie = self._build_task_cookie(
            session_kwargs=dict(
                passthrough_errors=['othererror'],
            ),
        )

        rv = self._make_request(
            query={'error': 'access_denied'},
            exclude_query=['code'],
            data=dict(track=task_cookie),
        )

        self._assert_callback_error_response(rv, 'UserDeniedError')

    def test_state_token_r_to_cont(self):
        task_cookie = self._build_task_cookie(
            dict(
                exchange=AUTHORIZATION_CODE1,
                state='authz_in_app.r_to_cont',
            ),
        )

        rv = self._make_request(data=dict(track=task_cookie))

        self._assert_response_forwards_to_url(rv, self._build_continue_url())
