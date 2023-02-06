# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import eq_
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import UserPhonesView
from passport.backend.api.yasms.utils import old_mask_phone_number
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.builders.yasms.faker import yasms_multi_userphones_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.types.phone_number.phone_number import mask_phone_number
from passport.backend.core.xml.test_utils import assert_xml_response_equals

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    OptionalSenderWhenGrantsAreRequiredTestMixin,
    RequiredUidWhenGrantsAreRequiredTestMixin,
    TEST_PROXY_IP,
)


TEST_UID = 4814
TEST_DATE = datetime(2000, 10, 22, 4)

TEST_PHONE_NUMBER_FROM_YASMS = u'+79046655444'
TEST_PHONE_ID_FROM_YASMS = 7755
TEST_PHONE_NUMBER_FROM_BLACKBOX = u'+79035544333'
TEST_PHONE_ID_FROM_BLACKBOX = 3322


@with_settings_hosts
class TestUserPhonesView(BaseTestCase,
                         BlackboxCommonTestCase,
                         OptionalSenderWhenGrantsAreRequiredTestMixin,
                         RequiredUidWhenGrantsAreRequiredTestMixin):
    def make_request(self, sender=u'dev', uid=TEST_UID, format=None, headers=None):
        self.response = self.env.client.get(
            u'/yasms/userphones',
            query_string={u'sender': sender, u'uid': uid, u'format': format},
            headers=headers,
        )
        return self.response

    def setup_blackbox_to_serve_good_response(self):
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(
                TEST_UID,
                phones=[{
                    u'id': TEST_PHONE_ID_FROM_BLACKBOX,
                    u'number': TEST_PHONE_NUMBER_FROM_BLACKBOX,
                    u'created': TEST_DATE,
                    u'bound': TEST_DATE,
                    u'confirmed': TEST_DATE,
                }],
                attributes={
                    u'phones.default': TEST_PHONE_ID_FROM_BLACKBOX,
                },
            ),
        )

    def assert_response_is_good_response_of_blackbox(self, is_masked=False):
        eq_(self.response.status_code, 200)
        expected = {
            u'id': TEST_PHONE_ID_FROM_BLACKBOX,
            u'active': True,
            u'secure': False,
            u'cyrillic': True,
            u'valid': u'valid',
            u'validation_date': TEST_DATE,
            u'validations_left': 0,
            u'autoblocked': False,
            u'permblocked': False,
            u'blocked': False,
        }
        if is_masked:
            expected[u'number'] = old_mask_phone_number(TEST_PHONE_NUMBER_FROM_BLACKBOX)
        else:
            expected[u'number'] = TEST_PHONE_NUMBER_FROM_BLACKBOX
            expected[u'masked_number'] = mask_phone_number(TEST_PHONE_NUMBER_FROM_BLACKBOX)
        assert_xml_response_equals(
            self.response,
            yasms_multi_userphones_response(
                TEST_UID,
                [expected],
                encoding=u'utf-8',
            ),
        )

    def setup_blackbox_to_serve_empty_response(self):
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(),
        )

    def assert_response_is_empty_response(self):
        eq_(self.response.status_code, 200)
        assert_xml_response_equals(
            self.response,
            yasms_multi_userphones_response(
                TEST_UID,
                [],
                encoding=u'utf-8',
            ),
        )

    def assert_blackbox_was_not_called(self):
        eq_(len(self.env.blackbox.requests), 0)

    def test_has_phones(self):
        self.assign_grants([grants.USER_PHONES, grants.RETURN_FULL_PHONE])
        self.setup_blackbox_to_serve_good_response()

        self.make_request()

        self.assert_response_is_good_response_of_blackbox()

    def test_no_phones(self):
        self.assign_grants([grants.USER_PHONES, grants.RETURN_FULL_PHONE])
        self.setup_blackbox_to_serve_empty_response()

        self.make_request()

        self.assert_response_is_empty_response()

    def test_no_phones_when_uid_does_not_exist(self):
        self.assign_grants([grants.USER_PHONES, grants.RETURN_FULL_PHONE])
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response(uid=None),
        )

        self.make_request()

        self.assert_response_is_empty_response()

    def test_phones_without_return_full_phone_grant(self):
        self.assign_grants([grants.USER_PHONES])
        self.setup_blackbox_to_serve_good_response()

        self.make_request()

        self.assert_response_is_good_response_of_blackbox(is_masked=True)

    def test_blackbox_builder_requests_phone_data(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_empty_response()

        self.make_request()

        self.env.blackbox.requests[0].assert_post_data_contains({
            u'method': u'userinfo',
            u'getphones': u'all',
            u'getphoneoperations': u'1',
            u'getphonebindings': u'all',
        })

    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(UserPhonesView)

    def test_phones__json_format(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_good_response()

        response = self.make_request(format=u'json')

        self.assert_json_responses_equal(
            response,
            json.dumps({
                u'phones': [
                    {
                        u'secure': False,
                        u'cyrillic': True,
                        u'autoblocked': False,
                        u'number': TEST_PHONE_NUMBER_FROM_BLACKBOX,
                        u'validation_date': str(TEST_DATE),
                        u'masked_number': mask_phone_number(TEST_PHONE_NUMBER_FROM_BLACKBOX),
                        u'valid': u'valid',
                        u'permblocked': False,
                        u'active': True,
                        u'validations_left': 0,
                        u'id': TEST_PHONE_ID_FROM_BLACKBOX,
                        u'blocked': False,
                    },
                ],
                u'uid': TEST_UID,
            }),
        )

    def test_no_phones__json_format(self):
        self.assign_all_grants()
        self.setup_blackbox_to_serve_empty_response()
        response = self.make_request(format=u'json')

        self.assert_json_responses_equal(
            response,
            json.dumps({
                u'uid': TEST_UID,
                u'phones': [],
            }),
        )

    def test_invalid_format_argument(self):
        self.assign_all_grants()

        self.make_request(format=u'invalid')

        self.assert_response_is_xml_error(u'format is invalid', u'INTERROR')

    def test_json_format_error(self):
        self.assign_no_grants()

        self.make_request(format=u'json')

        self.assert_response_is_json_error(u'NORIGHTS')

    def test_sender_in_post_data(self):
        """
        Ручка может использовать sender из POST-параметров.
        """
        # Т.к. user_phones должна уметь работать вообще без sender (по
        # сетевому адресу), мы определяем двух потребителей:
        #   foo, которому разрешено приходить с адреса 4.3.2.1
        #   bar, которому разрешено приходить с адреса 1.2.3.4.
        self.env.grants.set_grants_return_value({
            u'old_yasms_grants_foo': {
                u'grants': [],
                u'networks': [u'4.3.2.1'],
            },
            u'old_yasms_grants_bar': {
                u'grants': [],
                u'networks': [u'1.2.3.4'],
            },
        })
        self.setup_blackbox_to_serve_empty_response()

        # Передадим ручке sender=bar, а сетевой адрес foo.
        self.response = self.env.client.post(
            u'/yasms/userphones',
            data={'sender': u'bar', 'uid': TEST_UID},
            headers=[
                (u'X-Real-IP', TEST_PROXY_IP),
                (u'Ya-Consumer-Real-Ip', u'4.3.2.1'),
            ],
        )

        eq_(self.response.status_code, 200)
        # Если ручка сможет взять потребителя bar из POST-параметров, то она
        # решит, что потребитель пришёл с недопустимого адреса и вернёт ответ
        # DONTKNOWYOU.
        # Если же ручка не умеет брать потребителя из POST-параметров, то она
        # определит потребителя по адресу (foo) и вернёт ответ NORIGHTS.
        self.assert_response_is_error(u"I don't know you", u'DONTKNOWYOU')

    def test_args_in_post_data(self):
        """
        Ручка может работать с POST-параметрами.
        """
        self.assign_all_grants()
        self.setup_blackbox_to_serve_empty_response()

        self.response = self.env.client.post(
            u'/yasms/userphones',
            data={'sender': u'dev'},
        )

        # Проверим, что ручке действительно нужен uid.
        self.assert_response_is_error(u"User ID not specified", u'NOUID')

        self.response = self.env.client.post(
            u'/yasms/userphones',
            data={'sender': u'dev', 'uid': TEST_UID},
        )

        # И если задать uid, ручка вернёт хороший ответ.
        self.assert_response_is_empty_response()

    def assert_response_is_good_response(self):
        self.assert_response_is_good_response_of_blackbox()
