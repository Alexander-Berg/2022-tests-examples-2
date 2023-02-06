# -*- coding: utf-8 -*-

from re import compile as re_compile

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.lazy_loader import LazyLoader
from passport.backend.social.broker.exceptions import (
    ApplicationUnknownError,
    ConsumerUnknownError,
    HostInvalidError,
    PkceCodeInvalidError,
    PkceMethodInvalidError,
    ProviderUnknownError,
    RetpathInvalidError,
    SessionInvalidError,
    UserIpInvalidError,
)
from passport.backend.social.broker.handlers.args_processor import ArgsProcessor
from passport.backend.social.broker.tests.base_broker_test_data import (
    TEST_CONSUMER,
    TEST_FRONTEND_URL,
    TEST_OAUTH_TOKEN,
    TEST_PROVIDER,
    TEST_RETPATH,
    TEST_SESSION_ID,
    TEST_TASK_ID,
    TEST_USER_IP,
    TEST_YANDEX_UID,
)
from passport.backend.social.common.provider_settings import providers
from passport.backend.social.common.providers.Facebook import Facebook
from passport.backend.social.common.test.conf import settings_context
from passport.backend.social.common.test.consts import (
    APPLICATION_SECRET1,
    EXTERNAL_APPLICATION_ID1,
    FACEBOOK_APPLICATION_NAME1,
    VKONTAKTE_APPLICATION_NAME1,
)
from passport.backend.social.common.test.test_case import TestCase
from passport.backend.social.common.useragent import Url


class TestArgsProcessorStart(TestCase):
    def setUp(self):
        super(TestArgsProcessorStart, self).setUp()

        providers.init()

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)

        args = {
            'retpath': TEST_RETPATH,
            'consumer': TEST_CONSUMER,
            'provider': TEST_PROVIDER['code'],
            'display': 'popup',
            'place': 'fragment',
            'token': TEST_OAUTH_TOKEN,
            'scope': 'a,b',
        }
        form = {
            'frontend_url': TEST_FRONTEND_URL,
            'yandexuid': TEST_YANDEX_UID,
            'Session_id': TEST_SESSION_ID,
            'user_ip': TEST_USER_IP,
        }

        self.p = ArgsProcessor(
            args=args,
            form=form,
            log_actions=True,
        )

    def test_process_frontend_url(self):
        del self.p.form['frontend_url']
        with self.assertRaises(SessionInvalidError):
            self.p.process_frontend_url()

        self.p.form['frontend_url'] = TEST_FRONTEND_URL
        self.p.process_frontend_url()
        eq_(self.p.processed_args['frontend_url'], TEST_FRONTEND_URL)

    def test_user_ip_missing(self):
        del self.p.form['user_ip']
        with self.assertRaises(UserIpInvalidError):
            self.p.process_user_ip()

    def test_return_brief_profile(self):
        self.p.args['return_brief_profile'] = '1'
        self.p.get_bool('return_brief_profile')
        eq_(self.p.processed_args['return_brief_profile'], True)

    def test_require_auth(self):
        self.p.args['require_auth'] = '1'
        self.p.get_bool('require_auth')
        eq_(self.p.processed_args['require_auth'], True)

    def test_scope(self):
        del self.p.args['scope']
        self.p.process_scope()
        eq_(self.p.processed_args['scope'], [])

        self.p.args['scope'] = ' ,  a,b c,valuable access,   '
        self.p.process_scope()
        eq_(self.p.processed_args['scope'], ['a', 'b', 'c', 'VALUABLE_ACCESS'])

    def test_pkce_required(self):
        with self.assertRaises(PkceCodeInvalidError):
            self.p.process_pkce()

        self.p.args.update(
            code_challenge='a' * 200,
        )
        with self.assertRaises(PkceCodeInvalidError):
            self.p.process_pkce()

        self.p.args.update(
            code_challenge='a' * 43,
            code_challenge_method='foo',
        )
        with self.assertRaises(PkceMethodInvalidError):
            self.p.process_pkce()

        self.p.args.update(
            code_challenge='a' * 43,
            code_challenge_method='s256',
        )
        self.p.process_pkce()
        eq_(self.p.processed_args['code_challenge'], 'a' * 43)
        eq_(self.p.processed_args['code_challenge_method'], 'S256')

    def test_pkce_optional(self):
        self.p.process_pkce(required=False)
        ok_(self.p.processed_args['code_challenge'] is None)
        ok_(self.p.processed_args['code_challenge_method'] is None)

        self.p.args.update(
            code_challenge='a' * 43,
            code_challenge_method='s256',
        )
        self.p.process_pkce(required=False)
        eq_(self.p.processed_args['code_challenge'], 'a' * 43)
        eq_(self.p.processed_args['code_challenge_method'], 'S256')

    def test_sid(self):
        self.p.process_sid()
        ok_(self.p.processed_args['sid'] is None)

        self.p.args['sid'] = 'abc'
        self.p.process_sid()
        ok_(self.p.processed_args['sid'] is None)

        self.p.args['sid'] = '12'
        self.p.process_sid()
        eq_(self.p.processed_args['sid'], 12)

    def test_place(self):
        self.p.args['place'] = 'abc'
        self.p.process_place()
        eq_(self.p.processed_args['place'], '')

        self.p.args['place'] = 'fragment'
        self.p.process_place()
        eq_(self.p.processed_args['place'], 'fragment')

        self.p.args['place'] = 'query'
        self.p.process_place()
        eq_(self.p.processed_args['place'], 'query')

    def test_create_retry_url(self):
        self.p.create_retry_url(TEST_FRONTEND_URL, TEST_TASK_ID)
        eq_(self.p.processed_args['retry_url'], TEST_FRONTEND_URL + '1234567890abcdef/retry')

    def test_hostname_and_tld(self):
        with self.assertRaises(HostInvalidError):
            self.p.process_hostname_and_tld(frontend_url='abc')

        with self.assertRaises(HostInvalidError):
            self.p.process_hostname_and_tld(frontend_url='http://ya.fff')

        with self.assertRaises(HostInvalidError):
            self.p.process_hostname_and_tld(frontend_url='http://a\\b@ya.ru')

        self.p.process_hostname_and_tld(frontend_url='http://ya.ru')
        eq_(self.p.processed_args['hostname'], 'ya.ru')
        eq_(self.p.processed_args['tld'], 'ru')

    def test_consumer(self):
        self.p.args['consumer'] = ''
        with self.assertRaises(ConsumerUnknownError):
            self.p.process_consumer()

        self.p.args['consumer'] = TEST_CONSUMER
        self.p.process_consumer()
        eq_(self.p.processed_args['consumer'], TEST_CONSUMER)

    def test_app_and_provider(self):
        self.p.processed_args = {}
        self.p.args['application'] = ''
        self.p.args['provider'] = ''
        with self.assertRaises(SessionInvalidError):
            self.p.process_app_and_provider(tld='ru')

        self.p.processed_args = {}
        self.p.args['provider'] = 'abc'
        with self.assertRaises(ProviderUnknownError):
            self.p.process_app_and_provider(tld='ru')

        self.p.processed_args = {}
        self.p.args['provider'] = Facebook.code
        self.p.process_app_and_provider(tld='ru')
        eq_(self.p.processed_args['provider'], TEST_PROVIDER)
        eq_(self.p.processed_args['application'].name, FACEBOOK_APPLICATION_NAME1)

        self.p.processed_args = {}
        self.p.args['provider'] = ''
        self.p.args['application'] = 'invalid_application_name'
        with self.assertRaises(ApplicationUnknownError):
            self.p.process_app_and_provider(tld='ru')

        self.p.processed_args = {}
        self.p.args['provider'] = ''
        self.p.args['application'] = FACEBOOK_APPLICATION_NAME1
        self.p.process_app_and_provider(tld='ru')
        eq_(self.p.processed_args['provider'], TEST_PROVIDER)
        eq_(self.p.processed_args['application'].name, FACEBOOK_APPLICATION_NAME1)

        # Временная функциональность. На время исправления бага в АМе
        self.p.processed_args = {}
        self.p.args['provider'] = 'fb'
        self.p.args['application'] = EXTERNAL_APPLICATION_ID1
        self.p.process_app_and_provider(tld='ru')
        eq_(self.p.processed_args['provider'], TEST_PROVIDER)
        eq_(self.p.processed_args['application'].name, FACEBOOK_APPLICATION_NAME1)

        self.p.processed_args = {}
        self.p.args['provider'] = 'fb'
        self.p.args['application'] = 'hello'
        with self.assertRaises(ApplicationUnknownError):
            self.p.process_app_and_provider(tld='ru')

    def test_app_and_profile_selection(self):
        provider_list, application_list = self._get_providers_and_applications()
        with settings_context(fake_db=self._fake_db, providers=provider_list, applications=application_list):
            for provider_code in providers.providers:
                if isinstance(provider_code, int) or unicode(provider_code).isnumeric():
                    continue
                self.p.args['provider'] = provider_code
                self.p.processed_args = {}
                self.p.process_app_and_provider(tld='ru')
                ok_(provider_code in [self.p.processed_args['provider'][key] for key in ['code', 'name']])

            self.p.args = {}
            for app in application_list:
                app_model = providers.get_application_by_name(app['application_name'])
                self.p.args['application'] = app['application_name']
                self.p.processed_args = {}
                self.p.process_app_and_provider(tld='ru')
                eq_(self.p.processed_args['provider']['name'], app_model.provider['name'])
                eq_(self.p.processed_args['application'].name, app['application_name'])

    def _get_providers_and_applications(self):
        return (
            [
                {
                    'id': 1,
                    'code': 'vk',
                    'name': 'vkontakte',
                    'timeout': 1,
                    'retries': 1,
                    'display_name': {
                        'default': 'Vkontakte',
                    },
                },
            ],
            [
                {
                    'provider_id': 1,
                    'application_id': 11,
                    'application_name': VKONTAKTE_APPLICATION_NAME1,
                    'default': '1',
                    'provider_client_id': EXTERNAL_APPLICATION_ID1,
                    'secret': APPLICATION_SECRET1,
                    'domain': 'social.yandex.net',
                },
            ],
        )

    def test_retpath(self):
        def check_retpath(retpath, should_throw):
            with settings_context(
                fake_db=self._fake_db,
                social_config=dict(
                    allowed_retpath_schemes=map(re_compile, ['^maple$', '^yandex.*']),
                    broker_retpath_grammars=[
                        """
                        domain = 'social.yandex.' yandex_tld
                        path = '/broker2'
                        """,

                        """
                        domain = 'www.kinopoisk.ru'
                        path = '/social-broker/response-receiver/'
                        """,

                        """
                        domain = 'ext.kinopoisk.ru'
                        path = '/auth' ('/' path_bit){3}
                        """,
                    ],
                ),
            ):
                self.p.args['retpath'] = retpath
                if should_throw:
                    with self.assertRaises(RetpathInvalidError):
                        self.p.process_retpath()
                else:
                    self.p.process_retpath()

        check_retpath('https://social.yandex.ru/broker2', False)
        check_retpath('maple://social.yandex.ru/broker2', False)
        check_retpath('httt://social.yandex.ru/broker2', True)

        # tld
        check_retpath('https://social.yandex.com/broker2', False)
        check_retpath('https://social.yandex.com.tr/broker2', False)

        check_retpath('://social.yandex.ru/broker2', True)
        check_retpath('//social.yandex.ru/broker2', True)
        check_retpath('maple://closer', False)
        check_retpath('maple://any_host/any_path', False)
        check_retpath('', True)

        # some random text
        check_retpath('zddfhdfhfghjx4w875y4t&^HI$*(', True)

        # invalid domain
        check_retpath('https://social.yandexx.ru/broker2', True)

        # unknown consumer
        check_retpath('httt://social.yandex.ru/broker2', True)

        # prohibited symbol
        check_retpath('https://a\\b@social.yandex.ru/broker2', True)

        check_retpath('https://my.yaa.ru/demo', True)
        check_retpath('https://my.yaa.net/demo', True)

        # PASSP-14596
        check_retpath('https://www.disney.com%2F.yandex.ru', True)

        check_retpath('yandexko://ko/ko', False)
        check_retpath('yandex://ko/ko', False)
        check_retpath('yande://ko/ko', True)
        check_retpath('andex://ko/ko', True)

        check_retpath('https://yandex.ru.xakep.ru/broker2', True)
        check_retpath('https://yandex', True)

        check_retpath('https://www.kinopoisk.ru/social-broker/response-receiver/', False)
        check_retpath('https://www.kinopoisk.ru/social-broker/response-receiver/?foo=bar', False)
        check_retpath('https://www.kinopoisk.ru/board/showthread.php', True)
        check_retpath('https://forum.kinopoisk.ru/social-closer/../showthread.php', True)
        check_retpath('https://ext.kinopoisk.ru/auth/android/3.4.1/odnoklassniki', False)
        check_retpath('https://www.kinopoisk.ru/social-broker/response-receiver/;..%2f..%2f..%2f..%2fs%5c', True)

    def test_ui_language(self):
        self.p.form['ui_language'] = 'ru'
        self.p.process_ui_language()
        eq_(self.p.processed_args['ui_language'], 'ru')

    def test_ui_language__unknown(self):
        self.p.form['ui_language'] = 'unknown'
        self.p.process_ui_language()
        eq_(self.p.processed_args['ui_language'], 'unknown')

    def test_no_ui_language(self):
        self.p.process_ui_language()
        ok_(self.p.processed_args['ui_language'] is None)

    def test_no_passthrough_errors(self):
        self.p.process_passthrough_errors()
        ok_(self.p.processed_args['passthrough_errors'] is None)

    def test_empty_passthrough_errors(self):
        self.p.args['passthrough_errors'] = ''
        self.p.process_passthrough_errors()
        ok_(self.p.processed_args['passthrough_errors'] is None)

    def test_empty_bits_passthrough_errors(self):
        self.p.args['passthrough_errors'] = ','
        self.p.process_passthrough_errors()
        ok_(self.p.processed_args['passthrough_errors'] is None)

    def test_passthrough_errors__single_word(self):
        self.p.args['passthrough_errors'] = 'Hello'
        self.p.process_passthrough_errors()
        eq_(self.p.processed_args['passthrough_errors'], ['hello'])

    def test_passthrough_errors__many_words(self):
        self.p.args['passthrough_errors'] = 'Hello,wOrLd,AgAiN'
        self.p.process_passthrough_errors()
        eq_(self.p.processed_args['passthrough_errors'], ['again', 'hello', 'world'])

    def test_passthrough_errors__duplicate_words(self):
        self.p.args['passthrough_errors'] = 'Hello,Hello,World'
        self.p.process_passthrough_errors()
        eq_(self.p.processed_args['passthrough_errors'], ['hello', 'world'])

    def test_passthrough_errors__forbidden_letters(self):
        self.p.args['passthrough_errors'] = '2H:;"e_!L@0-L\x00w1'
        self.p.process_passthrough_errors()
        eq_(self.p.processed_args['passthrough_errors'], ['2he_l0-lw1'])


class TestArgsProcessorFixMordaRetpath(TestCase):
    def setUp(self):
        super(TestArgsProcessorFixMordaRetpath, self).setUp()

        providers.init()

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)

        self.p = ArgsProcessor(
            args=dict(),
            form=dict(),
            log_actions=True,
        )

    def build_settings(self):
        settings = super(TestArgsProcessorFixMordaRetpath, self).build_settings()
        settings['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = domain_bit '.' domain | domain_bit '.' yandex_tld
                    """,
                ],
            ),
        )
        return settings

    def test_yandex_ru(self):
        self.p.args['retpath'] = 'https://www.yandex.ru/'
        self.p.process_retpath()
        self.p.fix_morda_retpath()
        self.assertEqual(self.p.processed_args['retpath'], 'https://www.yandex.ru/')

    def test_yandex_com(self):
        self.p.args['retpath'] = 'https://www.yandex.com/?foo=bar'
        self.p.process_retpath()
        self.p.fix_morda_retpath()
        self.assertEqual(
            self.p.processed_args['retpath'],
            'https://www.yandex.com/?foo=bar&redirect=0',
        )

    def test_yandex_com_case_insensetive(self):
        self.p.args['retpath'] = 'https://yAnDeX.com/'
        self.p.process_retpath()
        self.p.fix_morda_retpath()
        self.assertEqual(
            self.p.processed_args['retpath'],
            'https://yAnDeX.com/?redirect=0',
        )


class TestArgsProcessorSsoPassportRetpath(TestCase):
    def setUp(self):
        super(TestArgsProcessorSsoPassportRetpath, self).setUp()

        providers.init()

        LazyLoader.register('slave_db_engine', self._fake_db.get_engine)

        self.p = ArgsProcessor(
            args=dict(),
            form=dict(),
            log_actions=True,
        )

    def build_settings(self):
        settings = super(TestArgsProcessorSsoPassportRetpath, self).build_settings()
        settings['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = 'beru.ru'
                    """,
                ],
            ),
        )
        return settings

    def test_valid_retpath(self):
        self.p.args['retpath'] = str(
            Url(
                'https://sso.passport.yandex.ru/push',
                {
                    'retpath': 'https://beru.ru/?foo=bar',
                },
            ),
        )
        self.p.process_retpath()
        self.assertEqual(self.p.processed_args['retpath'], 'https://beru.ru/?foo=bar')

    def test_invalid_retpath(self):
        self.p.args['retpath'] = str(
            Url(
                'https://sso.passport.yandex.ru/push',
                {
                    'retpath': 'https://neberu.ru/',
                },
            ),
        )

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.p.process_retpath()

        self.assertEqual(str(assertion.exception), 'Invalid netloc or path: "https://neberu.ru/"')

    def test_no_retpath(self):
        self.p.args['retpath'] = 'https://sso.passport.yandex.ru/push?foo=bar'

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.p.process_retpath()

        self.assertEqual(str(assertion.exception), 'Invalid netloc: "https://sso.passport.yandex.ru/push?foo=bar"')

    def test_empty_retpath(self):
        self.p.args['retpath'] = 'https://sso.passport.yandex.ru/push?retpath='

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.p.process_retpath()

        self.assertEqual(str(assertion.exception), 'Invalid netloc: "https://sso.passport.yandex.ru/push?retpath="')

    def test_not_push(self):
        self.p.args['retpath'] = str(
            Url(
                'https://sso.passport.yandex.ru/pop',
                {
                    'retpath': 'https://beru.ru/?foo=bar',
                },
            ),
        )

        with self.assertRaises(RetpathInvalidError) as assertion:
            self.p.process_retpath()

        self.assertEqual(
            str(assertion.exception),
            'Invalid netloc or path: "https://sso.passport.yandex.ru/pop?retpath=https%3A%2F%2Fberu.ru%2F%3Ffoo%3Dbar"',
        )
