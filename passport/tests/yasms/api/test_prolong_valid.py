# -*- coding: utf-8 -*-

from datetime import datetime

from nose.tools import eq_
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.time_utils.time_utils import DatetimeNow

from .base import BaseYasmsTestCase


UID = 1
PHONE_ID_ALPHA = 101
PHONE_NUMBER_ALPHA = u'+79019988777'
PHONE_NUMBER_BETA = u'+79027766555'
TEST_DATE = datetime(2012, 2, 1, 10, 20, 30)


class ProlongValidTestCase(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
    )

    def test_ok(self):
        """
        Проверим ответ.

        Телефон привязн к учётной записи.
        Телефон подтверждён.
        """
        account = build_account(
            uid=UID,
            phones=[{
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'created': TEST_DATE,
                u'bound': TEST_DATE,
                u'confirmed': TEST_DATE,
            }],
        )

        response = self._yasms.prolong_valid(account, PHONE_NUMBER_ALPHA)

        eq_(response, {u'status': u'ok', u'uid': UID})

    def test_admitted_updated(self):
        """
        Проверим, что дата признания пользователем номера обновляется.

        Телефон привязн к учётной записи.
        Телефон подтверждён.
        """
        account = build_account(
            uid=UID,
            phones=[{
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'created': TEST_DATE,
                u'bound': TEST_DATE,
                u'confirmed': TEST_DATE,
            }],
        )

        self._yasms.prolong_valid(account, PHONE_NUMBER_ALPHA)

        eq_(account.phones.by_number(PHONE_NUMBER_ALPHA).admitted, DatetimeNow())

    def test_no_phone_number(self):
        """
        Телефона нет среди телефонов учётной записи.
        """
        account = build_account(
            uid=UID,
            phones=[{
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'created': TEST_DATE,
                u'bound': TEST_DATE,
                u'confirmed': TEST_DATE,
            }],
        )

        response = self._yasms.prolong_valid(account, PHONE_NUMBER_BETA)

        eq_(response, {u'status': u'nophone', u'uid': UID})

    def test_user_has_no_phones(self):
        """
        У пользователя нет телефонов.
        """
        account = build_account(
            uid=UID,
            phones=[],
        )

        response = self._yasms.prolong_valid(account, PHONE_NUMBER_BETA)

        eq_(response, {u'status': u'nophone', u'uid': UID})

    def test_phone_number_confirmed_only(self):
        """
        Данный номер подтверждён, но отвязан.
        """
        account = build_account(
            uid=UID,
            phones=[{
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'created': TEST_DATE,
                u'bound': None,
                u'confirmed': TEST_DATE,
            }],
        )

        response = self._yasms.prolong_valid(account, PHONE_NUMBER_ALPHA)

        eq_(response, {u'status': u'nophone', u'uid': UID})

    def test_any_operation_on_phone_number(self):
        """
        Никакая операция над телефоном не может помешать работе подпрограммы.

        Телефон привязн к учётной записи.
        Телефон подтверждён.
        """
        account = build_account(
            uid=UID,
            phones=[{
                u'id': PHONE_ID_ALPHA,
                u'number': PHONE_NUMBER_ALPHA,
                u'created': TEST_DATE,
                u'bound': TEST_DATE,
                u'confirmed': TEST_DATE,
            }],
            phone_operations=[{
                u'phone_id': PHONE_ID_ALPHA,
                u'phone_number': PHONE_NUMBER_ALPHA,
                u'type': u'remove',
            }],
        )

        response = self._yasms.prolong_valid(account, PHONE_NUMBER_ALPHA)

        eq_(response, {u'status': u'ok', u'uid': UID})
