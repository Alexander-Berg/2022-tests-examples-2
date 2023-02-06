# -*- coding: utf-8 -*-
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.utils.common import merge_dicts

from .base_test_data import (
    TEST_LOGIN,
    TEST_PDD_CORRECTED_RETPATH,
    TEST_PDD_DOMAIN,
    TEST_PDD_LOGIN,
    TEST_PDD_RETPATH,
    TEST_PDD_UID,
    TEST_RETPATH,
    TEST_UID,
)
from .test_base import (
    BaseOtpMigrateTestCase,
    OtpMigrateCommonTests,
)


class OtpMigrateSubmitTestCase(BaseOtpMigrateTestCase, OtpMigrateCommonTests):

    url = '/1/bundle/otp/migrate/submit/?consumer=dev'
    with_check_cookies = True

    def assert_ok_response(self, resp,
                           domain=None, uid=TEST_UID, login=TEST_LOGIN,
                           display_login=TEST_LOGIN, **kwargs):
        base_response_kwargs = {
            'track_id': self.track_id,
            'account': {
                'person': {
                    'firstname': u'\\u0414',
                    'language': u'ru',
                    'gender': 1,
                    'birthday': u'1963-05-15',
                    'lastname': u'\\u0424',
                    'country': u'ru',
                },
                'display_name': {u'default_avatar': u'', u'name': u''},
                'login': login,
                'uid': int(uid),
                'display_login': display_login,
            },
        }
        if domain:
            base_response_kwargs['account']['domain'] = domain
        response_kwargs = merge_dicts(base_response_kwargs, kwargs)

        super(OtpMigrateSubmitTestCase, self).assert_ok_response(resp, **response_kwargs)

    def test_ok(self):
        rv = self.make_request(retpath=TEST_RETPATH)
        self.assert_ok_response(rv)
        self.assert_statbox_logged(with_check_cookies=True, action='submitted')

        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, TEST_RETPATH)
        ok_(track.is_it_otp_enable)

    def test_ok_for_pdd(self):
        self.setup_blackbox(alias_type='pdd', uid=TEST_PDD_UID, login=TEST_PDD_LOGIN, domain=TEST_PDD_DOMAIN)
        with self.track_manager.transaction(self.track_id).rollback_on_error() as track:
            track.uid = TEST_PDD_UID

        rv = self.make_request(retpath=TEST_PDD_RETPATH)
        self.assert_ok_response(
            rv,
            uid=TEST_PDD_UID,
            login=TEST_PDD_LOGIN,
            domain={'punycode': TEST_PDD_DOMAIN, 'unicode': TEST_PDD_DOMAIN},
            display_login=TEST_PDD_LOGIN,
        )
        self.assert_statbox_logged(with_check_cookies=True, action='submitted', uid=str(TEST_PDD_UID))

        track = self.track_manager.read(self.track_id)
        eq_(track.retpath, TEST_PDD_CORRECTED_RETPATH)
        ok_(track.is_it_otp_enable)
