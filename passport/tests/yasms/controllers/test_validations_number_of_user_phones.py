# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)

from nose.tools import eq_
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import ValidationsNumberOfUserPhonesView
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_validations_number_of_user_phones_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.xml.test_utils import assert_xml_response_equals

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    OptionalSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
)


UID = UID_ALPHA = 4814
PHONE_NUMBER = PHONE_NUMBER_ALPHA = u'+79000000001'
CONFIRM_DATE = datetime(2000, 1, 1, 13, 0, 0)

UID_BETA = 9141
PHONE_NUMBER_BETA = u'+79000000002'

UID_GAMMA = 3816
PHONE_NUMBER_GAMMA = u'+79000000003'

MINUTE = timedelta(minutes=1)


@with_settings_hosts(
    YASMS_URL=u'http://ya.s.ms/',
)
class TestValidationsNumberOfUserPhonesView(BaseTestCase,
                                            BlackboxCommonTestCase,
                                            OptionalSenderWhenGrantsAreRequiredTestMixin,
                                            RequiredUidWhenGrantsAreRequiredTestMixin):
    def make_request(self, sender=u'dev', uid=UID, headers=None):
        self.response = self.env.client.get(
            u'/yasms/validationsnumberofuserphones',
            query_string={u'sender': sender, u'uid': uid},
            headers=headers,
        )
        return self.response

    def assert_response_is_good_response(self):
        self.assert_response_is_ok([{
            u'validations_number': u'1',
            u'number': PHONE_NUMBER,
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE),
            u'other_accounts': u'0',
        }])

    def assert_response_is_ok(self, phones):
        eq_(self.response.status_code, 200)
        assert_xml_response_equals(
            self.response,
            yasms_validations_number_of_user_phones_response(phones),
        )

    def setup_blackbox_to_serve_good_response(self):
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.register_phone(UID_ALPHA, PHONE_NUMBER, CONFIRM_DATE)
        cfgr.confirm_phone(UID_ALPHA, PHONE_NUMBER, CONFIRM_DATE)

    def test_phone_is_confirmed(self):
        self.assign_grants([
            grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            grants.RETURN_FULL_PHONE,
        ])
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.confirm_and_delete_phone(UID_ALPHA, PHONE_NUMBER, [CONFIRM_DATE])
        cfgr.register_phone(UID_ALPHA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)
        cfgr.confirm_phone(UID_ALPHA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)
        cfgr.confirm_and_delete_phone(
            UID_BETA,
            PHONE_NUMBER,
            [CONFIRM_DATE + i * MINUTE for i in range(3)],
        )
        cfgr.register_phone(UID_GAMMA, PHONE_NUMBER, CONFIRM_DATE)
        cfgr.confirm_phone(UID_GAMMA, PHONE_NUMBER, CONFIRM_DATE)

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([{
            u'validations_number': u'6',
            u'number': PHONE_NUMBER,
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE + MINUTE),
            u'other_accounts': u'1',
        }])

        self.make_request(uid=UID_BETA)

        self.assert_response_is_ok([])

        self.make_request(uid=UID_GAMMA)

        self.assert_response_is_ok([{
            u'validations_number': u'6',
            u'number': PHONE_NUMBER,
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE),
            u'other_accounts': u'1',
        }])

    def test_phone_is_not_confirmed(self):
        self.assign_grants([
            grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            grants.RETURN_FULL_PHONE,
        ])
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.confirm_and_delete_phone(UID_ALPHA, PHONE_NUMBER, [CONFIRM_DATE])
        cfgr.register_phone(UID_BETA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)
        cfgr.confirm_phone(UID_BETA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([])

        self.make_request(uid=UID_BETA)

        self.assert_response_is_ok([{
            u'validations_number': u'2',
            u'number': PHONE_NUMBER,
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE + MINUTE),
            u'other_accounts': u'0',
        }])

    def test_phone_is_registered_but_not_confirmed(self):
        self.assign_grants([
            grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            grants.RETURN_FULL_PHONE,
        ])
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.register_phone(UID_ALPHA, PHONE_NUMBER, CONFIRM_DATE)
        cfgr.confirm_and_delete_phone(UID_BETA, PHONE_NUMBER, [CONFIRM_DATE])
        cfgr.register_phone(UID_BETA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)
        cfgr.confirm_phone(UID_BETA, PHONE_NUMBER, CONFIRM_DATE + MINUTE)
        cfgr.register_phone(UID_GAMMA, PHONE_NUMBER, CONFIRM_DATE)

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([{
            u'validations_number': u'2',
            u'number': PHONE_NUMBER,
            u'valid': u'msgsent',
            u'confirmed_date': u'',
            u'other_accounts': u'1',
        }])

        self.make_request(uid=UID_BETA)

        self.assert_response_is_ok([{
            u'validations_number': u'2',
            u'number': PHONE_NUMBER,
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE + MINUTE),
            u'other_accounts': u'0',
        }])

        self.make_request(uid=UID_GAMMA)

        self.assert_response_is_ok([{
            u'validations_number': u'2',
            u'number': PHONE_NUMBER,
            u'valid': u'msgsent',
            u'confirmed_date': u'',
            u'other_accounts': u'1',
        }])

    def test_two_confirmed_phones(self):
        self.assign_grants([
            grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            grants.RETURN_FULL_PHONE,
        ])
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.register_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        cfgr.confirm_phone(UID_ALPHA, PHONE_NUMBER_ALPHA, CONFIRM_DATE)
        cfgr.confirm_and_delete_phone(UID_ALPHA, PHONE_NUMBER_BETA, [CONFIRM_DATE])
        cfgr.register_phone(UID_ALPHA, PHONE_NUMBER_BETA, CONFIRM_DATE + MINUTE)
        cfgr.confirm_phone(UID_ALPHA, PHONE_NUMBER_BETA, CONFIRM_DATE + MINUTE)

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([
            {
                u'validations_number': u'1',
                u'number': PHONE_NUMBER_ALPHA,
                u'valid': u'valid',
                u'confirmed_date': str(CONFIRM_DATE),
                u'other_accounts': u'0',
            },
            {
                u'validations_number': u'2',
                u'number': PHONE_NUMBER_BETA,
                u'valid': u'valid',
                u'confirmed_date': str(CONFIRM_DATE + MINUTE),
                u'other_accounts': u'0',
            },
        ])

    def test_without_return_full_phone(self):
        self.assign_grants([grants.VALIDATIONS_NUMBER_OF_USER_PHONES])
        cfgr = self.init_blackbox_yasms_configurator()
        cfgr.register_phone(UID_ALPHA, u'+79000000001', CONFIRM_DATE)
        cfgr.confirm_phone(UID_ALPHA, u'+79000000001', CONFIRM_DATE)

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([{
            u'validations_number': u'1',
            u'number': u'*******0001',
            u'valid': u'valid',
            u'confirmed_date': str(CONFIRM_DATE),
            u'other_accounts': u'0',
        }])

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(
            ValidationsNumberOfUserPhonesView,
        )

    def test_no_phones_when_uid_does_not_exist(self):
        """Пользователь с данным uid не находится в ЧЯ."""
        self.assign_grants([
            grants.VALIDATIONS_NUMBER_OF_USER_PHONES,
            grants.RETURN_FULL_PHONE,
        ])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        self.make_request(uid=UID_ALPHA)

        self.assert_response_is_ok([])

    def test_blackbox_builder_requests_phone_data(self):
        """
        Проверим, что blackbox_builder вызывает ручки ЧЯ с правильными
        параметрами.
        """
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        self.make_request()

        # Собираем данные о телефонах пользователя
        eq_(len(self.env.blackbox.requests), 2)
        self.env.blackbox.requests[0].assert_post_data_contains({
            u'method': u'userinfo',
            u'getphones': u'all',
            u'getphoneoperations': u'1',
            u'getphonebindings': u'all',
        })

        # Собираем данные о связках телефонов
        self.env.blackbox.requests[1].assert_query_contains({
            u'method': u'phone_bindings',
        })
