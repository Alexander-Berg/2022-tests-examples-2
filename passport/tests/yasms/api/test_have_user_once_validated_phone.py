# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_

from .base import BaseYasmsTestCase


TEST_UID_ALPHA = 4814
TEST_UID_BETA = 7778

TEST_PHONE_NUMBER = u'+79000000001'
TEST_CONFIRM_DATE = datetime(2000, 1, 1, 13, 0, 0)

MINUTE = timedelta(minutes=1)


class TestHaveUserOnceValidatedPhone(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        YASMS_CLEAN_PHONE_NUMBER_BINDINGS_LIMIT=1,
        SMS_VALIDATION_MAX_CHECKS_COUNT=3,
    )

    def test_ok(self):
        """
        Телефон привязан к учётной записи пользователя.
        Телефон не привязан к учётным записям других пользователей.
        """
        blackbox_yasms = self._init_blackbox_yasms_configurator()
        blackbox_yasms.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        blackbox_yasms.confirm_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

        account = self._get_account_by_uid(TEST_UID_ALPHA)
        user_info = self._yasms.have_user_once_validated_phone(account)

        eq_(
            user_info,
            {
                u'have_user_once_validated_phone': True,
                u'reason': u'ok',
            },
        )

    def test_no_phone(self):
        """К учётной записи не привязано номеров."""
        self._init_blackbox_yasms_configurator()

        account = self._get_account_by_uid(TEST_UID_ALPHA)
        user_info = self._yasms.have_user_once_validated_phone(account)

        eq_(
            user_info,
            {
                u'have_user_once_validated_phone': False,
                u'reason': u'no-phone',
            },
        )

    def test_no_confirmed_phone(self):
        """
        Телефон привязывается к учётной записи пользователя.
        Телефон не привязан к учётным записям других пользователей.
        """
        blackbox_yasms = self._init_blackbox_yasms_configurator()
        blackbox_yasms.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

        account = self._get_account_by_uid(TEST_UID_ALPHA)
        user_info = self._yasms.have_user_once_validated_phone(account)

        eq_(
            user_info,
            {
                u'have_user_once_validated_phone': False,
                u'reason': u'no-confirmed-phone',
            },
        )

    def test_no_quality_confirmed_phone(self):
        """
        Телефон привязан к учётной записи пользователя.
        Телефон уже был привязан к учётной записи этого же пользователя.
        Телефон не привязан к учётным записям других пользователей.
        """
        blackbox_yasms = self._init_blackbox_yasms_configurator()
        # Подтверждаем связь, а затем удаляем
        blackbox_yasms.confirm_and_delete_phone(
            TEST_UID_ALPHA,
            TEST_PHONE_NUMBER,
            [TEST_CONFIRM_DATE],
        )
        # Подтверждаем связь
        blackbox_yasms.register_phone(
            TEST_UID_ALPHA,
            TEST_PHONE_NUMBER,
            TEST_CONFIRM_DATE + MINUTE,
        )
        blackbox_yasms.confirm_phone(
            TEST_UID_ALPHA,
            TEST_PHONE_NUMBER,
            TEST_CONFIRM_DATE + MINUTE,
        )

        account = self._get_account_by_uid(TEST_UID_ALPHA)
        user_info = self._yasms.have_user_once_validated_phone(account)

        eq_(
            user_info,
            {
                u'have_user_once_validated_phone': False,
                u'reason': u'no-quality-confirmed-phone',
            },
        )

    def test_no_quality_confirmed_phone_with_binding(self):
        """
        Телефон привязан к учётной записи пользователя.
        Телефон привязан к учётной записи другого пользователя.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        black_yasms.confirm_phone(TEST_UID_ALPHA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        black_yasms.register_phone(TEST_UID_BETA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)
        black_yasms.confirm_phone(TEST_UID_BETA, TEST_PHONE_NUMBER, TEST_CONFIRM_DATE)

        account = self._get_account_by_uid(TEST_UID_ALPHA)
        user_info = self._yasms.have_user_once_validated_phone(account)

        eq_(
            user_info,
            {
                u'have_user_once_validated_phone': False,
                u'reason': u'no-quality-confirmed-phone',
            },
        )
