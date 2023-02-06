# -*- coding: utf-8 -*-

from datetime import datetime
import json

from nose.tools import (
    eq_,
    istest,
    nottest,
)
from passport.backend.api.yasms import grants
from passport.backend.api.yasms.controllers import CheckPhoneView
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_phone_bindings_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.yasms.faker import yasms_check_phone_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseTestCase,
    BlackboxCommonTestCase,
    RequiredSenderWhenGrantsAreRequiredTestMixin,
)


PHONE_NUMBER = u'+79000000001'
TEST_DATE = datetime(2005, 4, 3, 2, 1, 1)


def yasms_check_phone_external_response(users, binding_limit_exceeded=False):
    response = yasms_check_phone_response(
        users,
        binding_limit_exceeded=binding_limit_exceeded,
    )
    response = json.loads(response)
    del response[u'bindings_count']
    return json.dumps(response)


@nottest
class BaseCheckPhoneViewTestCase(BaseTestCase):
    def test_unhandled_exception(self):
        self.assert_unhandled_exception_is_processed(CheckPhoneView)

    def test_no_phone_error_when_phone_is_empty(self):
        self.assign_all_grants()

        self.make_request(phone=None)
        self.assert_response_is_error(u'NOPHONE', u'NOPHONE')

        self.make_request(phone=u'')
        self.assert_response_is_error(u'NOPHONE', u'NOPHONE')

    def test_bad_arg_error_when_all_arg_is_invalid(self):
        self.assign_all_grants()

        self.make_request(all_arg=u'some shit')

        self.assert_response_is_error(u'Bad argument', u'INTERROR')

    def test_dont_know_you_error_when_invalid_sender_and_invalid_phone(self):
        self.assert_dont_know_you_error_when_invalid_sender_and_invalid_phone()

    def test_no_rights_error_when_sender_misses_rights_and_invalid_phone(self):
        self.assert_no_rights_error_when_sender_misses_rights_and_invalid_phone()

    def make_request(self, sender=u'dev', phone=PHONE_NUMBER, all_arg=None, headers=None):
        self.response = self.env.client.get(
            u'/yasms/api/checkphone',
            query_string={u'sender': sender, u'phone': phone, u'all': all_arg},
            headers=headers,
        )
        return self.response

    def assert_response_is_error(self, message, code, encoding=u'utf-8'):
        self.assert_response_is_json_error(code)

    def assert_response_is_good_response(self):
        eq_(self.response.status_code, 200)
        eq_(
            json.loads(self.response.data),
            json.loads(yasms_check_phone_external_response(
                binding_limit_exceeded=False,
                users=[],
            )),
        )

    def assert_responses_equal(self, actual, expected):
        eq_(json.loads(actual.data), json.loads(expected))


@with_settings_hosts(
    YASMS_PHONE_BINDING_LIMIT=3,
)
@istest
class TestCheckPhoneView(BaseCheckPhoneViewTestCase,
                         BlackboxCommonTestCase,
                         RequiredSenderWhenGrantsAreRequiredTestMixin):
    def test_ok_secure(self):
        self.assign_grants([grants.CHECK_PHONE])
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 1,
                    u'phone_id': 11,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 2,
                    u'phone_id': 21,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 3,
                    u'phone_id': 31,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 11,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 11},
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 31,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 31},
                ),
            ]),
        )

        response = self.make_request()

        eq_(response.status_code, 200)
        self.assert_responses_equal(
            response,
            yasms_check_phone_external_response(
                binding_limit_exceeded=True,
                users=[
                    {
                        u'uid': 1,
                        u'active': True,
                        u'phoneid': 11,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': TEST_DATE,
                    },
                    {
                        u'uid': 3,
                        u'active': True,
                        u'phoneid': 31,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': TEST_DATE,
                    },
                ],
            ),
        )

    def test_ok_not_secure(self):
        self.assign_grants([grants.CHECK_PHONE])
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 1,
                    u'phone_id': 11,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 2,
                    u'phone_id': 21,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'current',
                    u'number': PHONE_NUMBER,
                    u'uid': 3,
                    u'phone_id': 31,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'history',
                    u'number': PHONE_NUMBER,
                    u'uid': 3,
                    u'phone_id': 31,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 11,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 11},
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 21,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                ),
                dict(
                    uid=3,
                    phones=[{
                        u'id': 31,
                        u'number': PHONE_NUMBER,
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 31},
                ),
            ]),
        )

        response = self.make_request(all_arg=u'1')

        eq_(response.status_code, 200)
        self.assert_responses_equal(
            response,
            yasms_check_phone_external_response(
                binding_limit_exceeded=True,
                users=[
                    {
                        u'uid': 1,
                        u'active': True,
                        u'phoneid': 11,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': TEST_DATE,
                    },
                    {
                        u'uid': 2,
                        u'active': False,
                        u'phoneid': 21,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': TEST_DATE,
                    },
                    {
                        u'uid': 3,
                        u'active': True,
                        u'phoneid': 31,
                        u'phone': PHONE_NUMBER,
                        u'valid': u'valid',
                        u'validation_date': TEST_DATE,
                    },
                ],
            ),
        )

    def test_not_normalized_phone_number(self):
        """
        Ручка принимает ненормализованный номер.
        Нормализует его и передаёт ЧЯ.
        В ответе возвращает нормализованный номер.
        """
        self.assign_grants([grants.CHECK_PHONE])
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([
                {
                    u'type': u'current',
                    u'number': u'+79018877666',
                    u'uid': 1,
                    u'phone_id': 11,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
                {
                    u'type': u'current',
                    u'number': u'+79018877666',
                    u'uid': 2,
                    u'phone_id': 21,
                    u'bound': TEST_DATE,
                    u'flags': 0,
                },
            ]),
        )
        self.env.blackbox.set_response_value(
            u'userinfo',
            blackbox_userinfo_response_multiple([
                dict(
                    uid=1,
                    phones=[{
                        u'id': 11,
                        u'number': u'+79018877666',
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 11},
                ),
                dict(
                    uid=2,
                    phones=[{
                        u'id': 21,
                        u'number': u'+79018877666',
                        u'created': TEST_DATE,
                        u'bound': TEST_DATE,
                        u'confirmed': TEST_DATE,
                    }],
                    attributes={u'phones.secure': 21},
                ),
            ]),
        )

        response = self.make_request(phone=u'89018877666')

        actual_response = json.loads(response.data)
        eq_(len(actual_response[u'items']), 2)
        eq_(actual_response[u'items'][0][u'phone'], u'+79018877666')
        eq_(actual_response[u'items'][1][u'phone'], u'+79018877666')

        phone_bindings_requests = self.env.blackbox.get_requests_by_method(u'phone_bindings')
        eq_(len(phone_bindings_requests), 1)
        phone_bindings_requests[0].assert_query_contains({
            u'numbers': u'+79018877666',
        })

    def test_invalid_phone(self):
        self.assign_all_grants()
        self.env.blackbox.set_response_value('phone_bindings', blackbox_phone_bindings_response([]))

        self.make_request(phone=u'19211753')

        eq_(self.response.status_code, 200)
        eq_(
            json.loads(self.response.data),
            json.loads(yasms_check_phone_external_response(
                binding_limit_exceeded=False,
                users=[],
            )),
        )

    def setup_blackbox_to_serve_good_response(self):
        self.env.blackbox.set_response_value(
            u'phone_bindings',
            blackbox_phone_bindings_response([]),
        )
