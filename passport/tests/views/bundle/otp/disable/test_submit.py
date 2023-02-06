# -*- coding: utf-8 -*-
import json

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_url_contains_params
from passport.backend.core.builders.blackbox.constants import BLACKBOX_SESSIONID_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_hosted_domains_response,
    blackbox_sessionid_multi_response,
)
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.utils.common import merge_dicts

from .test_base import (
    get_headers,
    TEST_IP,
    TEST_LOGIN,
    TEST_ORIGIN,
    TEST_PDD_LOGIN,
    TEST_PDD_UID,
    TEST_UID,
)


@with_settings_hosts()
class SubmitTestCase(BaseBundleTestViews):

    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(grants={'otp': ['edit']}))

        self.default_headers = get_headers()

        self.track_manager, self.track_id = self.env.track_manager.get_manager_and_trackid('authorize')
        self.track_id_generator = FakeTrackIdGenerator().start()
        self.track_id_generator.set_return_value(self.track_id)

        self.setup_blackbox()
        self.setup_statbox_templates()

    def tearDown(self):
        self.track_id_generator.stop()
        self.env.stop()
        del self.env
        del self.track_manager
        del self.track_id_generator

    def setup_blackbox(self, uid=TEST_UID, login=TEST_LOGIN):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=uid,
                login=login,
                attributes={'account.2fa_on': '1'},
            ),
        )

    def make_request(self, headers=None, **kwargs):
        if not headers:
            headers = self.default_headers
        return self.env.client.post(
            '/1/bundle/otp/disable/submit/?consumer=dev',
            data=kwargs,
            headers=headers,
        )

    def assert_track_ok(self, retpath=None, uid=TEST_UID, origin=None):
        track = self.track_manager.read(self.track_id)
        eq_(track.uid, str(uid))
        ok_(track.is_it_otp_disable)
        ok_(track.is_allow_otp_magic)
        eq_(track.retpath, retpath)
        eq_(track.origin, origin)

    def assert_blackbox_sessionid_called(self, callnum=0):
        assert_builder_url_contains_params(
            self.env.blackbox,
            {
                'full_info': 'yes',
                'method': 'sessionid',
                'sessionid': '0:old-session',
                'sslsessionid': '0:old-sslsession',
            },
            callnum=callnum,
        )

    def setup_statbox_templates(self):
        self.env.statbox.bind_entry(
            'submitted',
            mode='disable_otp',
            action='submitted',
            track_id=self.track_id,
            ip=TEST_IP,
            yandexuid='testyandexuid',
            user_agent='curl',
            uid=str(TEST_UID),
            consumer='dev',
        )

    def assert_ok_response(self, resp,
                           domain=None, uid=TEST_UID, login=TEST_LOGIN,
                           display_login=TEST_LOGIN, is_strong_password_policy_required=False, **kwargs):
        base_response = {
            'status': 'ok',
            'track_id': self.track_id,
            'account': {
                'person': {
                    'firstname': u'\\u0414',
                    'language': u'ru',
                    'gender': 1,
                    'birthday': u'1963-05-15',
                    'lastname': u'\\u0424',
                    'country': u'ru'
                },
                'display_name': {u'default_avatar': u'', u'name': u''},
                'login': login,
                'uid': int(uid),
                'display_login': display_login,
            },
            'revokers': {
                'default': {
                    'tokens': True,
                    'web_sessions': True,
                    'app_passwords': True,
                },
                'allow_select': not is_strong_password_policy_required,
            },
        }
        if domain:
            base_response['account']['domain'] = domain
        eq_(resp.status_code, 200)
        eq_(
            json.loads(resp.data),
            merge_dicts(base_response, kwargs)
        )

    def test_empty_cookies_error(self):
        resp = self.make_request(headers=get_headers(cookie=''))
        self.assert_error_response(resp, ['sessionid.invalid'])

    def test_bad_cookies_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(status=BLACKBOX_SESSIONID_INVALID_STATUS),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['sessionid.invalid'])

    def test_account_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(uid=TEST_UID, enabled=False),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled'])

    def test_account_disabled_on_deletion_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
                enabled=False,
                attributes={
                    'account.is_disabled': '2',
                }
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['account.disabled_on_deletion'])

    def test_account_otp_already_disabled_error(self):
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_UID,
            ),
        )
        resp = self.make_request()
        self.assert_error_response(resp, ['action.not_required'])

    def test_ok(self):
        resp = self.make_request()
        self.assert_ok_response(resp)
        self.assert_track_ok()
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry('submitted'),
        ])

    def test_ok_with_retpath(self):
        """
        Протестируем, что переданный ретпас сохраняем в трек
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1'),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                crypt_password='1:crypt',
                attributes={'account.2fa_on': '1'},
            ),
        )
        resp = self.make_request(retpath='http://yandex.ru')
        self.assert_ok_response(
            resp,
            domain={'punycode': 'okna.ru', 'unicode': 'okna.ru'},
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            display_login=TEST_PDD_LOGIN,
        )
        self.assert_track_ok(
            uid=str(TEST_PDD_UID),
            retpath='http://yandex.ru',
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                uid=str(TEST_PDD_UID),
            ),
        ])

    def test_ok_with_retpath_fix_for_pdd(self):
        """
        Убираем "/for/..." из retpath ПДДшника
        """
        self.env.blackbox.set_blackbox_response_value(
            'hosted_domains',
            blackbox_hosted_domains_response(count=1, can_users_change_password='1'),
        )
        self.env.blackbox.set_blackbox_response_value(
            'sessionid',
            blackbox_sessionid_multi_response(
                uid=TEST_PDD_UID,
                login=TEST_PDD_LOGIN,
                aliases={
                    'pdd': TEST_PDD_LOGIN,
                },
                crypt_password='1:crypt',
                attributes={'account.2fa_on': '1'},
            ),
        )
        resp = self.make_request(retpath='http://mail.yandex.ru/for/okna.ru')
        self.assert_ok_response(
            resp,
            domain={'punycode': 'okna.ru', 'unicode': 'okna.ru'},
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            display_login=TEST_PDD_LOGIN,
        )
        self.assert_track_ok(
            uid=str(TEST_PDD_UID),
            retpath='http://mail.yandex.ru',
        )
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                uid=str(TEST_PDD_UID),
            ),
        ])

    def test_ok_with_origin(self):
        resp = self.make_request(origin=TEST_ORIGIN)
        self.assert_ok_response(resp)
        self.assert_track_ok(origin=TEST_ORIGIN)
        self.assert_blackbox_sessionid_called()
        self.env.statbox.assert_has_written([
            self.env.statbox.entry('check_cookies', host='passport.yandex.ru'),
            self.env.statbox.entry(
                'submitted',
                origin=TEST_ORIGIN,
            ),
        ])
