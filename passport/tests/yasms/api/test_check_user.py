# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.models.phones.faker import build_account

from .base import BaseYasmsTestCase


UID = 2323
PHONE_NUMBER = u'+79087766555'
PHONE_ID = 8877
TEST_BOUND_DT = datetime(2000, 1, 2, 12, 34, 56)


class TestCheckUser(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def test_user_has_no_phones(self):
        """
        У пользователя нет привязанных номеров.
        """
        account = build_account(uid=UID, phones=[])

        self._yasms.check_user(account)

        eq_(len(self.env.blackbox.requests), 0)

    def test_user_has_no_default_phone(self):
        """
        У пользователя есть привязанные номера, но нет активного.
        """
        account = build_account(
            uid=UID,
            phones=[{u'id': PHONE_ID, u'number': PHONE_NUMBER}],
            attributes={},
        )

        user_info = self._yasms.check_user(account)

        eq_(len(self.env.blackbox.requests), 0)

        eq_(
            user_info,
            {
                u'uid': UID,
                u'has_current_phone': False,
                u'number': None,
                u'cyrillic': None,
                u'blocked': None,
            },
        )

    def test_user_has_default_phone(self):
        """
        У пользователя есть активный привязанный номер.
        """
        account = build_account(
            uid=UID,
            phones=[{u'id': PHONE_ID, u'number': PHONE_NUMBER, u'bound': TEST_BOUND_DT}],
            attributes={u'phones.default': PHONE_ID},
        )

        user_info = self._yasms.check_user(account)

        eq_(len(self.env.blackbox.requests), 0)

        eq_(
            user_info,
            {
                u'uid': UID,
                u'has_current_phone': True,
                u'number': PHONE_NUMBER,
                u'cyrillic': True,
                u'blocked': False,
            },
        )
