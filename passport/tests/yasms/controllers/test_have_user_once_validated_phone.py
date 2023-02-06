# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import HaveUserOnceValidatedPhoneView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_have_user_once_validated_phone_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.xml.test_utils import assert_xml_response_equals

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    OptionalSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
)


TEST_UID_ALPHA = 4814
TEST_UID_BETA = 7778

TEST_PHONE_NUMBER = u'+79000000001'
TEST_CONFIRM_DATE = datetime(2000, 1, 1, 13, 0, 0)

MINUTE = timedelta(minutes=1)


@with_settings_hosts
class TestHaveUserOnceValidatedPhoneView(BaseTestCase,
                                         BlackboxCommonTestCase,
                                         OptionalSenderWhenGrantsAreRequiredTestMixin,
                                         RequiredUidWhenGrantsAreRequiredTestMixin):
    def setUp(self):
        super(TestHaveUserOnceValidatedPhoneView, self).setUp()
        black = self.init_blackbox_yasms_configurator()
        black.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        black.confirm_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

    def make_request(self, sender=u'dev', uid=TEST_UID_ALPHA, headers=None):
        self.response = self.env.client.get(
            u'/yasms/haveuseroncevalidatedphone',
            query_string={u'sender': sender, u'uid': uid},
            headers=headers,
        )
        return self.response

    def assert_response_is(self, value, reason):
        eq_(self.response.status_code, 200)
        assert_xml_response_equals(
            self.response,
            yasms_have_user_once_validated_phone_response(value, reason),
        )

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        assert_xml_response_equals(
            self.response,
            yasms_have_user_once_validated_phone_response(u'1', u'ok'),
        )

    def test_ok(self):
        self.assign_all_grants()
        yasms_configurator = self.init_blackbox_yasms_configurator()
        yasms_configurator.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        yasms_configurator.confirm_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

        self.make_request()

        self.assert_response_is(u'1', u'ok')

    def test_no_phone(self):
        self.assign_all_grants()
        self.init_blackbox_yasms_configurator()

        self.make_request()

        self.assert_response_is(u'0', u'no-phone')

    def test_no_confirmed_phone(self):
        self.assign_all_grants()
        yasms_configurator = self.init_blackbox_yasms_configurator()
        yasms_configurator.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

        self.make_request()

        self.assert_response_is(u'0', u'no-confirmed-phone')

    def test_no_quality_confirmed_phone(self):
        self.assign_all_grants()
        yasms_configurator = self.init_blackbox_yasms_configurator()
        yasms_configurator.confirm_and_delete_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, [TEST_CONFIRM_DATE])
        yasms_configurator.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE + MINUTE)
        yasms_configurator.confirm_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE + MINUTE)

        self.make_request()

        self.assert_response_is(u'0', u'no-quality-confirmed-phone')

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(
            HaveUserOnceValidatedPhoneView,
        )

    def test_account_not_found(self):
        self.assign_grants([grants.HAVE_USER_ONCE_VALIDATED_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        self.make_request()

        self.assert_response_is(u'0', u'no-phone')
