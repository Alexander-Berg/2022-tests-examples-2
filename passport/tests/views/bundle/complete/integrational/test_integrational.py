# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.complete.base.base import build_headers
from passport.backend.api.tests.views.bundle.complete.base.base_test_data import (
    COOKIE_L_VALUE,
    COOKIE_LAH_VALUE,
    COOKIE_YP_VALUE,
    COOKIE_YS_VALUE,
    EXPECTED_L_COOKIE,
    EXPECTED_LAH_COOKIE,
    EXPECTED_MDA2_BEACON_COOKIE,
    EXPECTED_SESSIONID_COOKIE,
    EXPECTED_SESSIONID_SECURE_COOKIE,
    EXPECTED_YANDEX_LOGIN_COOKIE,
    EXPECTED_YP_COOKIE,
    EXPECTED_YS_COOKIE,
    FRODO_RESPONSE_OK,
    MDA2_BEACON_VALUE,
    TEST_FIRSTNAME,
    TEST_LASTNAME,
    TEST_LITE_DISPLAY_NAME,
    TEST_LITE_LOGIN,
    TEST_LOGIN,
    TEST_PASSWORD,
    TEST_PASSWORD_HASH,
    TEST_RETPATH,
    TEST_SOCIAL_DISPLAY_NAME,
    TEST_SOCIAL_LOGIN,
    TEST_UID,
)
from passport.backend.api.tests.views.bundle.test_base_data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.builders import blackbox
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_editsession_response,
    blackbox_login_response,
    blackbox_loginoccupation_response,
    blackbox_lrandoms_response,
    blackbox_sessionid_multi_response,
    blackbox_userinfo_response,
)
from passport.backend.core.builders.captcha.faker import captcha_response_check
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.common import merge_dicts


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
class CompleteIntegrationalTestCase(BaseTestViews, ProfileTestMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['complete'],
            'captcha': ['*'],
        }))
        self.track_manager = self.env.track_manager.get_manager()

        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                login=TEST_SOCIAL_LOGIN,
                aliases={
                    'social': TEST_SOCIAL_LOGIN,
                },
                have_password=False,
                display_name=TEST_SOCIAL_DISPLAY_NAME,
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )
        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.captcha_mock.set_response_value(
            'check',
            captcha_response_check(),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)
        self.env.frodo.set_response_value('confirm', '')

        self.setup_profile_responses()

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def make_submit_request(self, headers=None, retpath=TEST_RETPATH):
        data = {
            'retpath': retpath,
        }

        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/bundle/complete/submit/?consumer=dev',
            data=data,
            headers=headers,
        )

    def make_captcha_check_request(self):
        return self.env.client.post(
            '/1/captcha/check/?consumer=dev',
            data=dict(
                answer='a',
                key='b',
                track_id=self.track_id,
            ),
            headers=build_headers(),
        )

    def make_commit_request(self, headers=None, validation_method='captcha',
                            with_password=True, **kwargs):
        data = {
            'track_id': self.track_id,
            'display_language': 'ru',
            'login': TEST_LOGIN,
            # Персональные данные
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            # Язык
            'language': 'tr',
            'country': 'tr',
            'gender': 'm',
            'birthday': '1950-05-01',
            'timezone': 'Europe/Moscow',
            'validation_method': validation_method,
            # КВ/КО
            'question': 'question',
            'answer': 'answer',
        }

        if with_password:
            data['password'] = TEST_PASSWORD

        data.update(kwargs)
        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/bundle/complete/%s/?consumer=dev' % self.url_method_name,
            data=data,
            headers=headers,
        )

    def test_integrational(self):
        rv = self.make_submit_request()
        submit_response = json.loads(rv.data)
        eq_(submit_response['status'], 'ok')
        eq_(submit_response['state'], 'complete_social_with_login')
        self.track_id = submit_response['track_id']
        self.url_method_name = 'commit_social_with_login'

        resp = self.make_captcha_check_request()
        ok_(json.loads(resp.data)['status'], 'ok')

        rv = self.make_commit_request()
        commit_response = json.loads(rv.data)
        eq_(commit_response['status'], 'ok')


@with_settings_hosts(
    BLACKBOX_URL='http://localhost',
    PASSPORT_SUBDOMAIN='passport-test',
    LITE_ACCOUNTS_ENFORCED_COMPLETION_DENOMINATOR=1,
    CLEAN_WEB_API_ENABLED=False,
)
class CompleteAuthIntegrationalTestCase(BaseBundleTestViews, ProfileTestMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={
            'account': ['complete'],
            'auth_password': ['base'],
        }))
        self.track_manager = self.env.track_manager.get_manager()
        self.env.blackbox.set_blackbox_response_value(
            'login',
            blackbox_login_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                aliases={
                    'lite': TEST_LITE_LOGIN,
                },
                crypt_password=TEST_PASSWORD_HASH,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LITE_LOGIN,
                aliases={'lite': TEST_LITE_LOGIN},
                crypt_password=TEST_PASSWORD_HASH,
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                status=blackbox.BLACKBOX_SESSIONID_VALID_STATUS,
                have_password=True,
                crypt_password=TEST_PASSWORD_HASH,
                ttl=5,
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'editsession',
            blackbox_editsession_response(),
        )

        self.env.blackbox.set_blackbox_lrandoms_response_value(blackbox_lrandoms_response())
        self.env.blackbox.set_blackbox_response_value(
            'loginoccupation',
            blackbox_loginoccupation_response({TEST_LOGIN: 'free'}),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)

        self.cookies_patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
            ),
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch.object(
                cookie_y.SessionCookieY,
                'pack',
                self._cookie_ys_pack,
            ),
            mock.patch.object(
                cookie_y.PermanentCookieY,
                'pack',
                self._cookie_yp_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]
        for patch in self.cookies_patches:
            patch.start()

        self.env.frodo.set_response_value('check', FRODO_RESPONSE_OK)
        self.env.frodo.set_response_value('confirm', '')
        self.setup_profile_responses()

    def tearDown(self):
        for patch in reversed(self.cookies_patches):
            patch.stop()

        self.env.stop()
        del self.env
        del self.track_manager
        del self.cookies_patches
        del self._cookie_l_pack
        del self._cookie_lah_pack
        del self._cookie_yp_pack
        del self._cookie_ys_pack

    def make_auth_request(self):
        data = {
            'login': TEST_LITE_LOGIN,
            'password': TEST_PASSWORD,
            'retpath': TEST_RETPATH,
        }
        return self.env.client.post(
            '/1/bundle/auth/password/submit/?consumer=dev',
            data=data,
            headers=build_headers(),
        )

    def make_commit_request(self, headers=None, validation_method='captcha', **kwargs):
        data = {
            'track_id': self.track_id,
            'display_language': 'ru',
            'login': TEST_LOGIN,
            'validation_method': validation_method,
            # Персональные данные
            'firstname': TEST_FIRSTNAME,
            'lastname': TEST_LASTNAME,
            'language': 'tr',
            'country': 'tr',
            'gender': 'm',
            'birthday': '1950-05-01',
            'timezone': 'Europe/Moscow',
            'eula_accepted': 'true',
            # КВ/КО
            'question': 'question',
            'answer': 'answer',
        }

        data.update(kwargs)
        headers = build_headers() if headers is None else headers
        return self.env.client.post(
            '/1/bundle/complete/force_commit_lite/?consumer=dev',
            data=data,
            headers=headers,
        )

    def get_expected_response(self):
        account_info = {
            'display_login': TEST_LITE_LOGIN,
            'display_name': TEST_LITE_DISPLAY_NAME,
            'uid': TEST_UID,
            'login': TEST_LOGIN,
        }
        return {
            'status': 'ok',
            'track_id': self.track_id,
            'retpath': TEST_RETPATH,
            'account': merge_dicts(
                {
                    'person': {
                        'firstname': TEST_FIRSTNAME,
                        'lastname': TEST_LASTNAME,
                        'language': 'tr',
                        'country': 'tr',
                        'gender': 1,
                        'birthday': '1950-05-01',
                    },
                },
                account_info,
            ),
            'accounts': [account_info],
            'cookies': [
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE % TEST_LOGIN,
                EXPECTED_LAH_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            'default_uid': TEST_UID,
        }

    def test_auth_lite_integrational(self):
        rv = self.make_auth_request()

        self.assert_ok_response(rv, check_all=False, state='force_complete_lite')
        auth_response = json.loads(rv.data)
        self.track_id = auth_response['track_id']

        track = self.track_manager.read(self.track_id)
        ok_(track.is_force_complete_lite)
        ok_(not track.session)
        ok_(track.is_password_passed)
        ok_(track.password_hash)
        with self.track_manager.transaction(self.track_id).commit_on_error() as track:
            track.is_captcha_checked = True
            track.is_captcha_recognized = True

        rv = self.make_commit_request()
        self.assert_ok_response(rv, **self.get_expected_response())


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class CompleteIntegrationalTestCaseNoBlackboxHash(CompleteIntegrationalTestCase):
    pass
