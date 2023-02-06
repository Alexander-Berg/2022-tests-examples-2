# -*- coding: utf-8 -*-
from datetime import datetime

from nose.tools import eq_
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import CheckUserView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_check_user_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.xml.test_utils import assert_xml_response_equals

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    OptionalSenderWhenGrantsAreOptionalTestMixin,
    RequiredUidWhenGrantsAreOptionalTestMixin,
)


UID = 4814
PHONE_NUMBER = u'+79000000001'
PHONE_ID = 251
BOUND_TIME = datetime(2000, 1, 2, 12, 34, 56)


@with_settings_hosts
class TestCheckUserView(BaseTestCase,
                        BlackboxCommonTestCase,
                        OptionalSenderWhenGrantsAreOptionalTestMixin,
                        RequiredUidWhenGrantsAreOptionalTestMixin):
    def make_request(self, sender=u'dev', uid=UID, headers=None):
        self.response = self.env.client.get(
            u'/yasms/checkuser',
            query_string={u'sender': sender, u'uid': uid},
            headers=headers,
        )
        return self.response

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        assert_xml_response_equals(
            self.response,
            yasms_check_user_response(uid=UID, has_current_phone=False),
        )

    def setup_blackbox_to_serve_good_response(self):
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=UID, phones=[]),
        )

    def test_has_current_phone_with_return_full_phone(self):
        """
        У потребителя есть грант RETURN_FULL_PHONE.
        У пользователя есть активный телефон.

        Возвращается ответ с активным телефоном пользователя.
        """
        self.assign_grants([grants.RETURN_FULL_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                phones=[{u'id': PHONE_ID, u'number': PHONE_NUMBER, u'bound': BOUND_TIME}],
                attributes={u'phones.default': str(PHONE_ID)}
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_check_user_response(
                uid=UID,
                has_current_phone=True,
                phone_number=PHONE_NUMBER,
                cyrillic=True,
                blocked=False,
            ),
        )

    def test_has_current_phone_without_return_full_phone(self):
        """
        У потребителя нет гранта RETURN_FULL_PHONE.
        У пользователя есть активный телефон.

        Возвращается ответ с замаскированным активным телефоном пользователя.
        """
        self.assign_grants([])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                uid=UID,
                phones=[{u'id': PHONE_ID, u'number': u'+79054433222', u'bound': BOUND_TIME}],
                attributes={u'phones.default': str(PHONE_ID)}
            ),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_check_user_response(
                uid=UID,
                has_current_phone=True,
                phone_number=u'*******3222',
                cyrillic=True,
                blocked=False,
            ),
        )

    def test_has_no_current_phone(self):
        """
        У пользователя нет телефонов.

        Возвращается ответ означающий, что у пользователя нет активного
        телефона.
        """
        self.assign_grants([grants.RETURN_FULL_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=UID, phones=[]),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        assert_xml_response_equals(
            response,
            yasms_check_user_response(uid=UID, has_current_phone=False),
        )

    def test_has_no_current_phone_when_user_not_found(self):
        """
        Пользователь с данным UID'ом не найден.

        Возвращается ответ означающий, что у пользователя нет активного
        телефона.
        """
        self.assign_grants([grants.RETURN_FULL_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        response = self.make_request()

        assert_xml_response_equals(
            response,
            yasms_check_user_response(uid=UID, has_current_phone=False),
        )

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(CheckUserView)
