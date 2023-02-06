# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_

from .base import BaseYasmsTestCase


UID = UID_ALPHA = 4814
PHONE_NUMBER = PHONE_NUMBER_ALPHA = u'+79000000001'
CONFIRM_DATE = datetime(2000, 1, 1, 13, 0, 0)

UID_BETA = 9141
PHONE_NUMBER_BETA = u'+79000000002'

UID_GAMMA = 3816
PHONE_NUMBER_GAMMA = u'+79000000003'

MINUTE = timedelta(minutes=1)


class TestValidationsNumberOfUserPhones(BaseYasmsTestCase):
    _DEFAULT_SETTINGS = dict(
        BaseYasmsTestCase._DEFAULT_SETTINGS,
        SMS_VALIDATION_MAX_CHECKS_COUNT=3,
    )

    def test_yasms_phone_bound_just_once_by_user(self):
        """
        Телефон связан с учётной записью пользователя.
        Данные о телефонах пользователя хранятся в ЧЯ.
        Телефоны пользователя никогда не привязывались к другим учётным
        записям.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + MINUTE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': CONFIRM_DATE + MINUTE,
                u'validations_number': 1,
                u'other_accounts': 0,
            }],
        )

    def test_phone_is_being_bound_by_just_single_user(self):
        """
        Телефон привязывается к учётной записи пользователя.
        Данные о телефонах пользователя хранятся в ЧЯ.
        Телефон не привязан к другим учётным записям.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'msgsent',
                u'confirmed_date': None,
                u'validations_number': 0,
                u'other_accounts': 0,
            }],
        )

    def test_phone_bound_by_other_user(self):
        """
        Телефон связан с учётной записью пользователя.
        Телефон пользователя привязан к другой учётной записи.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + MINUTE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': CONFIRM_DATE + MINUTE,
                u'validations_number': 2,
                u'other_accounts': 1,
            }],
        )

    def test_phone_is_being_bound_by_two_users(self):
        """
        Телефон привязывается к учётной записи пользователя.
        Телефон привязывается к другой учётной записи.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'msgsent',
                u'confirmed_date': None,
                u'validations_number': 0,
                u'other_accounts': 0,
            }],
        )

    def test_phone_removed_and_bound_again(self):
        """
        Телефоны пользователя не связаны с другими учётными записями.
        Пользователь связал телефон, а потом удалил.
        Пользователь ещё раз привязал телефон со своей учётной записью.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.confirm_and_delete_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            [CONFIRM_DATE],
        )
        black_yasms.register_phone(
            UID_ALPHA, PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + 3 * MINUTE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + 4 * MINUTE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': CONFIRM_DATE + 4 * MINUTE,
                u'validations_number': 2,
                u'other_accounts': 0,
            }],
        )

    def test_phone_bound_and_old_phone_is_being_bound(self):
        """
        Телефон привязан в учётной записи пользователя.
        Телефон привязывается к учётной записи другого пользователя.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': CONFIRM_DATE,
                u'validations_number': 1,
                u'other_accounts': 0,
            }],
        )

    def test_phone_is_being_bound_and_old_phone_bound(self):
        """
        Пользователь привязывает телефон к учётной записи.
        Телефон привязан к учётной записи другого пользователя.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'msgsent',
                u'confirmed_date': None,
                u'validations_number': 1,
                u'other_accounts': 1,
            }],
        )

    def test_old_phone_bound_by_other_user(self):
        """
        Телефон связан с учётной записью пользователя.
        Телефон пользователя привязан к другой учётной записи.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + MINUTE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_BETA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': CONFIRM_DATE,
                u'validations_number': 2,
                u'other_accounts': 1,
            }],
        )

    def test_old_phone_is_being_bound_by_two_users(self):
        """
        Телефон привязывается к учётной записи пользователя.
        Телефон привязывается к другой учётной записи.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_BETA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [{
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'msgsent',
                u'confirmed_date': None,
                u'validations_number': 0,
                u'other_accounts': 0,
            }],
        )

    def test_no_bound_phones(self):
        """У пользователя нет телефонов."""
        self._init_blackbox_yasms_configurator()

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(validations_info, [])

    def test_many_phone_numbers(self):
        """
        К учётной записи Альфа привязана телефоны А, Б.
        К учётной записи Альфа привязывается телефон В.
        К учётной записи Бета привязывается телефон Б.
        К учётной записи Бета привязан телефон В.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_ALPHA,
            CONFIRM_DATE + MINUTE,
        )
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_BETA,
            CONFIRM_DATE,
        )
        black_yasms.confirm_phone(
            UID_ALPHA,
            PHONE_NUMBER_BETA,
            CONFIRM_DATE + MINUTE,
        )
        black_yasms.register_phone(
            UID_ALPHA,
            PHONE_NUMBER_GAMMA,
            CONFIRM_DATE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_BETA,
            CONFIRM_DATE + 10 * MINUTE,
        )
        black_yasms.register_phone(
            UID_BETA,
            PHONE_NUMBER_GAMMA,
            CONFIRM_DATE + 10 * MINUTE,
        )
        black_yasms.confirm_phone(
            UID_BETA,
            PHONE_NUMBER_GAMMA,
            CONFIRM_DATE + 10 * MINUTE,
        )

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(
            validations_info,
            [
                {
                    u'number': PHONE_NUMBER_ALPHA,
                    u'valid': u'valid',
                    u'confirmed_date': CONFIRM_DATE + MINUTE,
                    u'validations_number': 1,
                    u'other_accounts': 0,
                },
                {
                    u'number': PHONE_NUMBER_BETA,
                    u'valid': u'valid',
                    u'confirmed_date': CONFIRM_DATE + MINUTE,
                    u'validations_number': 1,
                    u'other_accounts': 0,
                },
                {
                    u'number': PHONE_NUMBER_GAMMA,
                    u'valid': u'msgsent',
                    u'confirmed_date': None,
                    u'validations_number': 1,
                    u'other_accounts': 1,
                },
            ],
        )

    def test_fetch_each_account_one_time(self):
        """
        Сведения о телефонах каждой учётной записи могут быть запрошены только
        раз.
        """
        black_yasms = self._init_blackbox_yasms_configurator()
        # PHONE_NUMBER_ALPHA связан с UID_ALPHA И UID_BETA
        black_yasms.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        black_yasms.confirm_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        black_yasms.register_phone(UID_BETA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        black_yasms.confirm_phone(UID_BETA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        # PHONE_NUMBER_BETA связан с UID_ALPHA И UID_BETA
        black_yasms.register_phone(UID_ALPHA, PHONE_NUMBER_BETA, CONFIRM_DATE)
        black_yasms.confirm_phone(UID_ALPHA, PHONE_NUMBER_BETA, CONFIRM_DATE)
        black_yasms.register_phone(UID_BETA, PHONE_NUMBER_BETA, CONFIRM_DATE)
        black_yasms.confirm_phone(UID_BETA, PHONE_NUMBER_BETA, CONFIRM_DATE)

        validations_info = self._yasms.validations_number_of_user_phones(
            self._get_account_by_uid(UID_ALPHA),
            self._get_account_by_uid,
        )

        eq_(len(self.env.blackbox.get_requests_by_method(u'userinfo')), 2)

        eq_(
            validations_info,
            [
                {
                    u'number': PHONE_NUMBER_ALPHA,
                    u'valid': u'valid',
                    u'confirmed_date': CONFIRM_DATE,
                    u'validations_number': 2,
                    u'other_accounts': 1,
                },
                {
                    u'number': PHONE_NUMBER_BETA,
                    u'valid': u'valid',
                    u'confirmed_date': CONFIRM_DATE,
                    u'validations_number': 2,
                    u'other_accounts': 1,
                },
            ],
        )
