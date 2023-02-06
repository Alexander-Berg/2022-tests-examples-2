# -*- coding: utf-8 -*-
import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.auth.base_test_data import *
from passport.backend.api.views.bundle.constants import X_TOKEN_OAUTH_SCOPE
from passport.backend.core import authtypes
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_oauth_response
from passport.backend.core.builders.staff import (
    StaffAuthorizationInvalidError,
    StaffEntityNotFoundError,
    StaffTemporaryError,
)
from passport.backend.core.builders.staff.faker import staff_get_user_info_response
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    settings_context,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator


eq_ = iterdiff(eq_)

TEST_RETPATH = 'https://ya.ru/foo'
TEST_OTHER_RETPATH = 'https://yadi.sk/bar'
TEST_FOREIGN_DOMAIN = 'practicum.com'
TEST_FOREIGN_RETPATH = 'https://ya.%s/abacaba' % TEST_FOREIGN_DOMAIN

TEST_OAUTH_TOKEN = 'test-x-token'
TEST_OAUTH_HEADER = 'OAuth %s' % TEST_OAUTH_TOKEN
TEST_OAUTH_SCOPE = X_TOKEN_OAUTH_SCOPE

TEST_PASSPORT_URL_TEMPLATE = 'https://passport.yandex.%(tld)s'
TEST_FOREIGN_PASSPORT_URL_TEMPLATE = 'https://passport.%(foreign_domain)s'


def build_headers(authorization=TEST_OAUTH_HEADER):
    return mock_headers(
        user_ip=TEST_IP,
        authorization=authorization,
    )


class BaseXTokenTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope=TEST_OAUTH_SCOPE,
                login_id=TEST_LOGIN_ID,
            ),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator()
        self.track_id_generator.set_return_value(self.track_id)

        self.is_yandex_ip_mock = mock.Mock(return_value=True)
        is_yandex_ip_patch = mock.patch(
            'passport.backend.api.views.bundle.auth.token.submit.is_yandex_ip',
            self.is_yandex_ip_mock,
        )
        is_yandex_server_ip_patch = mock.patch(
            'passport.backend.api.views.bundle.auth.token.submit.is_yandex_server_ip',
            self.is_yandex_ip_mock,
        )

        self.patches = [
            self.track_id_generator,
            is_yandex_ip_patch,
            is_yandex_server_ip_patch,
        ]

        for patch in self.patches:
            patch.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_by_token': ['base']}),
        )
        self.setup_statbox_templates()

    def tearDown(self):
        for patch in reversed(self.patches):
            patch.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.patches

    def query_params(self, **kwargs):
        params = {
            'type': 'x-token',
            'retpath': TEST_RETPATH,
        }
        params.update(kwargs)
        return params

    def make_request(self, data, headers):
        return self.env.client.post(
            '/1/bundle/auth/token/?consumer=dev',
            data=data,
            headers=headers,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_base(
            mode='any_auth',
            type='x-token',
            ip=TEST_IP,
            consumer='dev',
        )
        self.env.statbox.bind_entry(
            'completed',
            action='completed',
            track_id=self.track_id,
            client_id='fake_clid',
            scope='oauth:grant_xtoken',
        )

    def assert_track_ok(self, retpath=TEST_RETPATH, login=TEST_LOGIN):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(TEST_UID))
        eq_(track.login, login)
        eq_(track.retpath, retpath)
        ok_(track.allow_authorization)
        eq_(track.login_id, TEST_LOGIN_ID)
        ok_(not track.is_password_passed)
        eq_(track.auth_source, authtypes.AUTH_SOURCE_XTOKEN)

    def assert_statbox_logged_ok(self,  **kwargs):
        self.check_statbox_log_entries(
            self.env.statbox_handle_mock,
            [
                self.env.statbox.entry('completed', **kwargs),
            ],
        )


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_BASE_URL_TEMPLATE=TEST_PASSPORT_URL_TEMPLATE,
    FOREIGN_PASSPORT_BASE_URL_TEMPLATE=TEST_FOREIGN_PASSPORT_URL_TEMPLATE,
    FOREIGN_DOMAINS_WITH_PASSPORT=[TEST_FOREIGN_DOMAIN],
    IS_INTRANET=False,
)
class XTokenTestCase(BaseXTokenTestCase):

    def test_invalid_token__error(self):
        """Переданный токен не прошел проверку в ЧЯ"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                status=blackbox.BLACKBOX_OAUTH_INVALID_STATUS,
                scope=TEST_OAUTH_SCOPE,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_empty_token__error(self):
        """Передан пустой хедер - не будем даже ходить в ЧЯ"""
        rv = self.make_request(
            self.query_params(),
            build_headers(
                authorization='',
            ),
        )

        self.assert_error_response(rv, ['authorization.invalid'])
        eq_(self.env.blackbox._mock.call_count, 0)

    def test_disabled_account__error(self):
        """Аккаунт, для которого был выписан токен, заблокирован - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope=TEST_OAUTH_SCOPE,
                enabled=False,
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.disabled'])

    def test_account_is_phonish__error(self):
        """Для phonish-аккаунтов эта ручка запрещена - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login='phne-test',
                aliases={
                    'phonish': 'phne-test',
                },
                scope=TEST_OAUTH_SCOPE,
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_account_is_kolonkish__error(self):
        """Для kolonkish-аккаунтов эта ручка запрещена - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login='kolonkish-test',
                aliases={
                    'kolonkish': 'kolonkish-test',
                },
                scope=TEST_OAUTH_SCOPE,
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_account_is_mailish__error(self):
        """Для mailish-аккаунтов эта ручка запрещена - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login='admin@gmail.com',
                scope=TEST_OAUTH_SCOPE,
                aliases={
                    'mailish': 'admin@gmail.com',
                },
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['account.invalid_type'])

    def test_account_is_lite__ok(self):
        """Для lite-аккаунтов эта ручка запрещена - ошибка"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                scope=TEST_OAUTH_SCOPE,
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        self.assert_track_ok(login=TEST_LITE_LOGIN)
        self.assert_statbox_logged_ok()

    def test_wrong_scope__error(self):
        """токен с неверным скоупом вызывает ошибку"""
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                scope='test-wrong-scope',
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_error_response(rv, ['oauth_token.invalid'])

    def test_valid_token__ok(self):
        """
        Пришел валидный токен; аккаунт, для которого был выписан токен, в порядке.
        Создаём авторизационный трек.
        """
        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        self.assert_track_ok()
        self.assert_statbox_logged_ok()

    def test_custom_retpath__ok(self):
        """
        Передан retpath на бескуковом домене - соответствующего passport_tld нет
        """
        rv = self.make_request(
            self.query_params(retpath=TEST_OTHER_RETPATH),
            build_headers(),
        )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host=None,
        )
        self.assert_track_ok(retpath=TEST_OTHER_RETPATH)
        self.assert_statbox_logged_ok()

    def test_foreign_domain_retpath__ok(self):
        """
        Передан retpath на foreign домене
        """
        rv = self.make_request(self.query_params(retpath=TEST_FOREIGN_RETPATH), build_headers())

        self.assert_ok_response(rv, track_id=self.track_id, passport_host='https://passport.practicum.com')
        self.assert_track_ok(retpath=TEST_FOREIGN_RETPATH)
        self.assert_statbox_logged_ok()

    def test_custom_scope__ok(self):
        self.env.blackbox.set_blackbox_response_value(
            'oauth',
            blackbox_oauth_response(
                login=TEST_LOGIN,
                uid=TEST_UID,
                scope='yadisk:browser_sync mobile:all',
                login_id=TEST_LOGIN_ID,
            ),
        )

        rv = self.make_request(
            self.query_params(),
            build_headers(),
        )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        self.assert_track_ok()
        self.assert_statbox_logged_ok(scope='yadisk:browser_sync, mobile:all')

    def test_yateam_internal_ip__ok(self):
        with settings_context(
            IS_INTRANET=True,
            PASSPORT_BASE_URL_TEMPLATE=TEST_PASSPORT_URL_TEMPLATE,
        ):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        ok_(not self.env.staff.requests)

    def test_yateam_external_ip__ok(self):
        self.is_yandex_ip_mock.return_value = False
        self.env.staff.set_response_value(
            'get_user_info',
            staff_get_user_info_response(is_robot=False),
        )

        with settings_context(
            IS_INTRANET=True,
            PASSPORT_BASE_URL_TEMPLATE=TEST_PASSPORT_URL_TEMPLATE,
        ):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        eq_(len(self.env.staff.requests), 1)

    def test_yateam_external_ip__staff_temporary_error__ok(self):
        self.is_yandex_ip_mock.return_value = False
        self.env.staff.set_response_side_effect(
            'get_user_info',
            StaffTemporaryError,
        )

        with settings_context(
            IS_INTRANET=True,
            PASSPORT_BASE_URL_TEMPLATE=TEST_PASSPORT_URL_TEMPLATE,
            STAFF_RETRIES=3,
        ):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_ok_response(
            rv,
            track_id=self.track_id,
            passport_host='https://passport.yandex.ru',
        )
        eq_(len(self.env.staff.requests), 3)

    def test_yateam_external_ip__not_found__error(self):
        self.is_yandex_ip_mock.return_value = False
        self.env.staff.set_response_side_effect(
            'get_user_info',
            StaffEntityNotFoundError,
        )

        with settings_context(IS_INTRANET=True):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_error_response(
            rv,
            ['account.invalid_type'],
        )
        eq_(len(self.env.staff.requests), 1)

    def test_yateam_external_ip__is_robot__error(self):
        self.is_yandex_ip_mock.return_value = False
        self.env.staff.set_response_value(
            'get_user_info',
            staff_get_user_info_response(is_robot=True),
        )

        with settings_context(IS_INTRANET=True):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_error_response(
            rv,
            ['account.invalid_type'],
        )
        eq_(len(self.env.staff.requests), 1)

    def test_yateam_external_ip__authorization_invalid__error(self):
        self.is_yandex_ip_mock.return_value = False
        self.env.staff.set_response_side_effect(
            'get_user_info',
            StaffAuthorizationInvalidError,
        )

        with settings_context(IS_INTRANET=True):
            rv = self.make_request(
                self.query_params(),
                build_headers(),
            )

        self.assert_error_response(
            rv,
            ['exception.unhandled'],  # токен в секретах протух, хотим видеть эту ошибку в exception-логе
        )
        eq_(len(self.env.staff.requests), 1)
