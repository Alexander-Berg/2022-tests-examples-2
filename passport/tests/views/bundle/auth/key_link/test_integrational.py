# -*- coding: utf-8 -*-
import json
import time

import mock
from nose.tools import eq_
from passport.backend.api.test.mixins import AccountModificationNotifyTestMixin
from passport.backend.api.test.mock_objects import mock_headers
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_create_pwd_hash_response,
    blackbox_createsession_response,
    blackbox_get_track_response,
    blackbox_lrandoms_response,
    blackbox_pwdhistory_response,
    blackbox_userinfo_response,
)
from passport.backend.core.cookies import (
    cookie_l,
    cookie_lah,
    cookie_y,
)
from passport.backend.core.models.persistent_track import TRACK_TYPE_AUTH_BY_KEY_LINK
from passport.backend.core.test.data import TEST_SERIALIZED_PASSWORD
from passport.backend.core.test.test_utils.mock_objects import (
    mock_counters,
    mock_grants,
)
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.core.tracks.faker import FakeTrackIdGenerator

from .base_test_data import (
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
    MDA2_BEACON_VALUE,
    TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP,
    TEST_HOST,
    TEST_IP,
    TEST_LOGIN,
    TEST_PERSISTENT_TRACK_ID,
    TEST_PERSISTENT_TRACK_KEY,
    TEST_USER_AGENT,
    TEST_YANDEXUID_COOKIE,
)


eq_ = iterdiff(eq_)


@with_settings_hosts(
    BLACKBOX_URL='localhost',
    FRODO_URL='http://localhost/',
    PASSPORT_SUBDOMAIN='passport-test',
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=1,
    **mock_counters(
        ACCOUNT_MODIFICATION_PER_UID_COUNTER_TEMPLATE={'push:changed_password': 5},
    )
)
class Integrational(
    AccountModificationNotifyTestMixin,
    BaseBundleTestViews,
):
    track_type = 'authorize'

    def setUp(self):
        TEST_UID = '1'

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value(
            mock_grants(grants={'auth_key': ['base']}),
        )

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid(self.track_type)
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.env.grants.set_grants_return_value(
            mock_grants(
                grants={
                    'auth_key': ['base'],
                    'auth_password': ['base'],
                },
            ),
        )

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                login=TEST_LOGIN,
                dbfields={
                    'subscription.login_rule.100': 1,
                    'subscription.suid.100': 1,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_PERSISTENT_TRACK_ID,
                created=TEST_AUTH_BY_KEY_LINK_CREATE_TIMESTAMP,
                expired=int(time.time() + 60),
                content={
                    'type': TRACK_TYPE_AUTH_BY_KEY_LINK,
                },
            ),
        )
        self.env.blackbox.set_blackbox_response_value(
            'pwdhistory',
            blackbox_pwdhistory_response(found=False),
        )
        self.env.blackbox.set_blackbox_lrandoms_response_value(
            blackbox_lrandoms_response(),
        )

        self.env.blackbox.set_blackbox_response_value(
            'createsession',
            blackbox_createsession_response(),
        )

        self.env.blackbox.set_blackbox_response_value(
            'create_pwd_hash',
            blackbox_create_pwd_hash_response(password_hash=TEST_SERIALIZED_PASSWORD),
        )

        self.env.shakur.set_response_value(
            'check_password',
            json.dumps({'found': False, 'passwords': []}),
        )

        self.env.frodo.set_response_value('check', '<spamlist></spamlist>')

        self._cookie_l_pack = mock.Mock(return_value=COOKIE_L_VALUE)
        self._cookie_ys_pack = mock.Mock(return_value=COOKIE_YS_VALUE)
        self._cookie_yp_pack = mock.Mock(return_value=COOKIE_YP_VALUE)
        self._cookie_lah_pack = mock.Mock(return_value=COOKIE_LAH_VALUE)
        self.cookies_patches = [
            mock.patch.object(
                cookie_l.CookieL,
                'pack',
                self._cookie_l_pack,
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
            mock.patch.object(
                cookie_lah.CookieLAH,
                'pack',
                self._cookie_lah_pack,
            ),
            mock.patch(
                'passport.backend.api.common.authorization.generate_cookie_mda2_beacon_value',
                return_value=MDA2_BEACON_VALUE,
            ),
        ]

        for patch in self.cookies_patches:
            patch.start()

        self.setup_kolmogor()
        self.start_account_modification_notify_mocks(ip=TEST_IP)

    def tearDown(self):
        self.stop_account_modification_notify_mocks()
        self.env.stop()
        for patch in reversed(self.cookies_patches):
            patch.stop()
        self.track_id_generator.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator
        del self.cookies_patches
        del self._cookie_yp_pack
        del self._cookie_ys_pack
        del self._cookie_l_pack
        del self._cookie_lah_pack

    def setup_kolmogor(self, rate=4):
        self.env.kolmogor.set_response_side_effect(
            'get',
            [
                str(rate),
            ],
        )
        self.env.kolmogor.set_response_side_effect('inc', ['OK'])

    def test_integrational(self):
        TEST_UID = '1'

        response = self.env.client.post(
            '/1/bundle/auth/key_link/submit/?consumer=dev',
            headers=mock_headers(
                host=TEST_HOST,
                user_agent=TEST_USER_AGENT,
                cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE,
                user_ip=TEST_IP,
            ),
            data=dict(secret_key=TEST_PERSISTENT_TRACK_KEY),
        )

        expected = {
            'status': 'ok',
            'state': 'complete_autoregistered',
            'track_id': self.track_id,
        }
        self.assert_ok_response(response, **expected)

        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.is_captcha_recognized = True
            track.is_captcha_checked = True

        response = self.env.client.post(
            '/2/bundle/auth/password/complete_autoregistered/?consumer=dev',
            data={
                'track_id': self.track_id,
                'password': 'aaaa1bbbbccc',
                'eula_accepted': '1',
                'validation_method': 'captcha',
                'display_language': 'ru',
                'question': 'question',
                'answer': 'lala',
            },
            headers=mock_headers(
                host=TEST_HOST,
                user_agent=TEST_USER_AGENT,
                cookie='yandexuid=%s' % TEST_YANDEXUID_COOKIE,
                user_ip=TEST_IP,
            ),
        )

        self.assert_ok_response(
            response,
            ignore_order_for=['cookies'],
            cookies=[
                EXPECTED_SESSIONID_COOKIE,
                EXPECTED_SESSIONID_SECURE_COOKIE,
                EXPECTED_YP_COOKIE,
                EXPECTED_YS_COOKIE,
                EXPECTED_L_COOKIE,
                EXPECTED_YANDEX_LOGIN_COOKIE,
                EXPECTED_LAH_COOKIE,
                EXPECTED_MDA2_BEACON_COOKIE,
            ],
            default_uid=int(TEST_UID),
            account={
                'uid': int(TEST_UID, 16),
                'login': TEST_LOGIN,
                'display_login': TEST_LOGIN,
            },
            accounts=[
                {
                    'uid': int(TEST_UID, 16),
                    'login': TEST_LOGIN,
                    'display_login': TEST_LOGIN,
                    'display_name': {
                        'name': '',
                        'default_avatar': '',
                    },
                },
            ],
        )

        self.check_account_modification_push_sent(
            ip=TEST_IP,
            event_name='changed_password',
            uid=TEST_UID,
            title='Пароль в аккаунте {} успешно изменён'.format(TEST_LOGIN),
            body='Если это вы, всё в порядке. Если нет, нажмите здесь',
            track_id=self.track_id,
        )


@with_settings_hosts(
    BLACKBOX_MD5_ARGON_HASH_DENOMINATOR=0,
)
class IntegrationalNoBlackboxHash(Integrational):
    pass
