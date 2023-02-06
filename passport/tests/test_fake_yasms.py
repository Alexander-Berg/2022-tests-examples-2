# -*- coding: utf-8 -*-

from datetime import (
    datetime,
    timedelta,
)
import json
from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.builders.yasms import YaSms
from passport.backend.core.builders.yasms.exceptions import YaSmsAccessDenied
from passport.backend.core.builders.yasms.faker import (
    FakeYaSms,
    URL_PATH_TO_METHOD_NAME,
    yasms_check_phone_response,
    yasms_check_user_response,
    yasms_confirm_response,
    yasms_delete_phone_response,
    yasms_drop_phone_response,
    yasms_error_xml_response,
    yasms_have_user_once_validated_phone_response,
    yasms_multi_userphones_response,
    yasms_prolong_valid_response,
    yasms_register_response,
    yasms_remove_userphones_response,
    yasms_send_sms_response,
    yasms_userphones_response,
    yasms_validations_number_of_user_phones_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from passport.backend.core.xml.test_utils import assert_xml_documents_equal


TEST_UID = TEST_UID_ALPHA = 4814
TEST_PHONE_NUMBER = TEST_PHONE_NUMBER_ALPHA = u'+79000000001'
TEST_CONFIRM_DATE = datetime(2000, 1, 1, 13, 0, 0)
TEST_IP = u'1.2.3.4'
TEST_USER_AGENT = u'some user agent'

TEST_UID_BETA = 9141
TEST_UID_GAMMA = 3816

MINUTE = timedelta(minutes=1)


@with_settings(YASMS_URL='http://localhost/')
class FakeYaSmsTestCase(TestCase):
    def setUp(self):
        self.tvm_credentials_manager = FakeTvmCredentialsManager()
        self.tvm_credentials_manager.set_data(
            fake_tvm_credentials_data(
                ticket_data={
                    str(TEST_CLIENT_ID): {
                        'alias': 'yasms',
                        'ticket': TEST_TICKET,
                    },
                },
            ),
        )
        self.tvm_credentials_manager.start()
        self.yasms = YaSms()
        self.fake_yasms = FakeYaSms()
        self.fake_yasms.start()

    def tearDown(self):
        self.fake_yasms.stop()
        self.tvm_credentials_manager.stop()
        del self.fake_yasms
        del self.tvm_credentials_manager

    def test_set_response_value(self):
        ok_(not self.fake_yasms._mock.request.called)
        self.fake_yasms.set_response_value(
            'send_sms',
            yasms_send_sms_response(),
        )
        expected = {'id': 1}
        eq_(self.yasms.send_sms('+71231234567', 'faketext', client_ip=TEST_IP, user_agent=TEST_USER_AGENT), expected)
        ok_(self.fake_yasms._mock.request.called)

    def test_set_response_side_effect(self):
        ok_(not self.fake_yasms._mock.request.called)
        self.fake_yasms.set_response_side_effect('send_sms', TabError)
        with assert_raises(TabError):
            self.yasms.send_sms('+71231234567', 'faketext', client_ip=TEST_IP, user_agent=TEST_USER_AGENT)
        ok_(self.fake_yasms._mock.request.called)

    def test_set_response_with_error(self):
        ok_(not self.fake_yasms._mock.request.called)

        error_response = """
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
              <error>Error description goes here</error>
              <errorcode>NORIGHTS</errorcode>
            </doc>
            """.strip()

        self.fake_yasms.set_response_value('send_sms', error_response)

        with assert_raises(YaSmsAccessDenied):
            self.yasms.send_sms('+71231234567', 'faketext', client_ip=TEST_IP, user_agent=TEST_USER_AGENT)
        ok_(self.fake_yasms._mock.request.called)

    def test_getattr(self):
        eq_(self.fake_yasms._mock.foo, self.fake_yasms.foo)

    @raises(KeyError)
    def test_error_when_request_unknown_url(self):
        self.fake_yasms.set_response_value(
            u'send_sms',
            yasms_send_sms_response(),
        )
        with mock.patch.dict(URL_PATH_TO_METHOD_NAME, clear=True):
            self.yasms.send_sms('+71231234567', 'faketext', client_ip=TEST_IP, user_agent=TEST_USER_AGENT)


class TestYasmsErrorXmlResponse(TestCase):
    def test_code(self):
        assert_xml_documents_equal(
            yasms_error_xml_response(u'message', u'code'),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <error>message</error>
                <errorcode>code</errorcode>
            </doc>
            ''',
        )

    def test_encoding(self):
        assert_xml_documents_equal(
            yasms_error_xml_response(u'message', u'code', u'windows-1251'),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <error>message</error>
                <errorcode>code</errorcode>
            </doc>
            ''',
        )

    def test_no_code(self):
        assert_xml_documents_equal(
            yasms_error_xml_response(u'message'),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <error>message</error>
            </doc>
            ''',
        )


class TestRegisterResponse(TestCase):
    def test_default_values(self):
        assert_xml_documents_equal(
            yasms_register_response(),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <phone id="1" number="+71231234567" uid="1"
                       added="1" />
            </doc>
            ''',
        )

    def test_override_values(self):
        assert_xml_documents_equal(
            yasms_register_response(
                uid=2,
                phone_number='+79876543210',
                phone_id=2,
                revalidated=True,
                encoding='utf-8',
            ),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="2" number="+79876543210" uid="2"
                       revalidated="1" />
            </doc>
            ''',
        )


class TestDropPhoneResponse(TestCase):
    def test_default_values(self):
        eq_(
            json.loads(yasms_drop_phone_response()),
            {
                u'status': u'OK',
                u'uid': u'1',
            },
        )

    def test_override_status(self):
        eq_(
            json.loads(yasms_drop_phone_response(status='error', uid=2)),
            {
                'status': u'ERROR',
                'uid': u'2',
            },
        )


class TestValidationsNumberOfUserphonesResponse(TestCase):
    def test_default_values(self):
        assert_xml_documents_equal(
            yasms_validations_number_of_user_phones_response(
                phones=[{}],
            ),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone number="+79031234567"
                       validations_number="1"
                       valid="valid"
                       confirmed_date="2006-11-07 15:14:10"
                       other_accounts="0" />
            </doc>
            ''',
        )

    def test_override_values(self):
        assert_xml_documents_equal(
            yasms_validations_number_of_user_phones_response(
                phones=[{
                    u'number': u'+79010000001',
                    u'validations_number': u'3',
                    u'valid': u'msgsent',
                    u'confirmed_date': u'2000-01-01 12:10:10',
                    u'other_accounts': u'5',
                }],
            ),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone number="+79010000001"
                       validations_number="3"
                       valid="msgsent"
                       confirmed_date="2000-01-01 12:10:10"
                       other_accounts="5" />
            </doc>
            ''',
        )

    def test_no_phones(self):
        assert_xml_documents_equal(
            yasms_validations_number_of_user_phones_response(phones=[]),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc></doc>
            ''',
        )


class TestMultiUserphonesResponse(TestCase):
    def test_default_values(self):
        assert_xml_documents_equal(
            yasms_multi_userphones_response(
                phones=[{}],
            ),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <uid>1</uid>
                <phone id="1"
                       number="+79031234567"
                       active="1"
                       secure="0"
                       cyrillic="0"
                       valid="msgsent"
                       validation_date="2006-11-07 15:14:10"
                       validations_left="5"
                       autoblocked="0"
                       permblocked="0"
                       blocked="0" />
            </doc>
            ''',
        )

    def test_override_values(self):
        assert_xml_documents_equal(
            yasms_multi_userphones_response(
                uid=10,
                phones=[{
                    u'id': 13,
                    u'number': u'+79010000001',
                    u'active': False,
                    u'secure': True,
                    u'cyrillic': True,
                    u'valid': u'valid',
                    u'validation_date': datetime(2012, 11, 7, 15, 14, 10),
                    u'validations_left': 3,
                    u'autoblocked': True,
                    u'permblocked': True,
                    u'blocked': True,
                    u'pending_type': u'pending_type',
                    u'pending_phone_id': 32,
                }],
            ),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <uid>10</uid>
                <phone id="13"
                       number="+79010000001"
                       active="0"
                       secure="1"
                       cyrillic="1"
                       valid="valid"
                       validation_date="2012-11-07 15:14:10"
                       validations_left="3"
                       autoblocked="1"
                       permblocked="1"
                       blocked="1"
                       pending_type="pending_type"
                       pending_phoneid="32" />
            </doc>
            ''',
        )

    @raises(ValueError)
    def test_second_secured_phones_raises_value_error(self):
        yasms_multi_userphones_response(
            phones=[{u'secure': True}, {u'secure': True}],
        ),

    def test_no_phones(self):
        assert_xml_documents_equal(
            yasms_multi_userphones_response(),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc><uid>1</uid></doc>
            ''',
        )


class TestHaveUserOnceValidatedPhoneResponse(TestCase):
    def test_ok(self):
        assert_xml_documents_equal(
            yasms_have_user_once_validated_phone_response(u'1', u'ok'),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <have_user_once_validated_phone value="1"
                                                reason="ok"/>
            </doc>
            ''',
        )

    def test_not_ok(self):
        assert_xml_documents_equal(
            yasms_have_user_once_validated_phone_response(u'0', u'not-ok'),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <have_user_once_validated_phone value="0"
                                                reason="not-ok"/>
            </doc>
            ''',
        )


class TestCheckPhoneResponse(TestCase):
    def test_defaults(self):
        r = json.loads(yasms_check_phone_response([{}]))
        eq_(
            r,
            {
                u'binding_limit_exceeded': 0,
                u'bindings_count': 0,
                u'items': [{
                    u'uid': u'1',
                    u'active': u'1',
                    u'phoneid': u'12345',
                    u'phone': u'+71231234567',
                    u'valid': u'valid',
                    u'validation_date': u'2012-12-07 16:29:58',
                }],
            },
        )

    def test_override_defaults(self):
        r = json.loads(yasms_check_phone_response(
            [{
                u'uid': 2,
                u'active': False,
                u'phoneid': 54321,
                u'phone': u'+79040000004',
                u'valid': u'msgsent',
                u'validation_date': datetime(2011, 4, 1, 16, 18, 4),
            }],
            bindings_count=5,
            binding_limit_exceeded=True,
        ))
        eq_(
            r,
            {
                u'binding_limit_exceeded': 1,
                u'bindings_count': 5,
                u'items': [{
                    u'uid': u'2',
                    u'active': u'0',
                    u'phoneid': u'54321',
                    u'phone': u'+79040000004',
                    u'valid': u'msgsent',
                    u'validation_date': u'2011-04-01 16:18:04',
                }],
            },
        )

    def test_many_users(self):
        r = json.loads(yasms_check_phone_response([{}, {}], 0))
        eq_(len(r[u'items']), 2)


class TestCheckUserResponse(TestCase):
    def test_defaults(self):
        assert_xml_documents_equal(
            yasms_check_user_response(),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <uid>1</uid>
                <hascurrentphone>yes</hascurrentphone>
                <number>+79010000001</number>
                <cyrillic>yes</cyrillic>
                <blocked>no</blocked>
            </doc>
            ''',
        )

    def test_override_defaults(self):
        assert_xml_documents_equal(
            yasms_check_user_response(
                2,
                True,
                u'+79040000004',
                False,
                True,
            ),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <uid>2</uid>
                <hascurrentphone>yes</hascurrentphone>
                <number>+79040000004</number>
                <cyrillic>no</cyrillic>
                <blocked>yes</blocked>
            </doc>
            ''',
        )

    def test_has_no_current_phone(self):
        assert_xml_documents_equal(
            yasms_check_user_response(2, False),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <uid>2</uid>
                <hascurrentphone>no</hascurrentphone>
            </doc>
            ''',
        )


class TestProlongValidResponse(TestCase):
    def test_defaults(self):
        eq_(
            json.loads(yasms_prolong_valid_response()),
            {u'status': u'OK', u'uid': u'1'},
        )

    def test_override_defaults(self):
        eq_(
            json.loads(yasms_prolong_valid_response(status=u'error', uid=13)),
            {u'status': u'ERROR', u'uid': u'13'},
        )

    @raises(TypeError)
    def test_type_error_on_bad_uid(self):
        yasms_prolong_valid_response(uid=u'1')


class TestRemoveUserPhonesResponse(TestCase):
    def test_defaults(self):
        eq_(json.loads(yasms_remove_userphones_response()), {u'status': u'OK'})

    def test_overrides(self):
        eq_(
            json.loads(yasms_remove_userphones_response(u'Simpsons')),
            {u'status': u'SIMPSONS'},
        )


class TestDeletePhoneResponse(TestCase):
    def test_default_values(self):
        eq_(
            json.loads(yasms_delete_phone_response()),
            {
                u'uid': u'5223',
                u'status': 'OK',
            },
        )

    def test_override_values(self):
        eq_(
            json.loads(yasms_delete_phone_response(
                uid=1445,
                status=u'NOTFOUND',
            )),
            {
                u'uid': u'1445',
                u'status': 'NOTFOUND',
            },
        )


class TestConfirmResponse(TestCase):
    def test_default_values(self):
        assert_xml_documents_equal(
            yasms_confirm_response(),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="98"
                       number="+79010099888"
                       uid="30"
                       valid="1"
                       current="1"
                       left="" />
            </doc>
            ''',
        )

    def test_overriden_values(self):
        assert_xml_documents_equal(
            yasms_confirm_response(3, u'+79028877666', 4, False, False, 5),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id="3"
                       number="+79028877666"
                       uid="4"
                       valid="0"
                       current="0"
                       left="5" />
            </doc>
            ''',
        )

    def test_empty_values(self):
        assert_xml_documents_equal(
            yasms_confirm_response(phone_id=None, phone_number=None, code_checks_left=None),
            u'''
            <?xml version="1.0" encoding="utf-8"?>
            <doc>
                <phone id=""
                       number=""
                       uid="30"
                       valid="1"
                       current="1"
                       left="" />
            </doc>
            ''',
        )


class TestUserphonesResponse(TestCase):
    def test_default_values(self):
        with mock.patch(u'passport.backend.core.builders.yasms.faker.yasms.datetime') as datetime_mock:
            datetime_mock.now.return_value = TEST_CONFIRM_DATE
            response = yasms_userphones_response()
        assert_xml_documents_equal(
            response,
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <uid>1</uid>
                <phone id="1"
                       number="+79031234567"
                       active="1"
                       secure="1"
                       cyrillic="0"
                       valid="msgsent"
                       validation_date="%s"
                       validations_left="5"
                       autoblocked="0"
                       permblocked="1"
                       blocked="0" />
            </doc>
            ''' % (TEST_CONFIRM_DATE,),
        )

    def test_override_values(self):
        assert_xml_documents_equal(
            yasms_userphones_response(
                uid=8,
                id=32,
                phone_number=u'+79065544333',
                active=False,
                valid=u'valid',
                autoblocked=True,
                permblocked=False,
                secure=False,
                validation_date=datetime(2014, 12, 22, 15, 40, 0),
                pending_type=u'pending_type',
                pending_phone_id=32,
            ),
            u'''
            <?xml version="1.0" encoding="windows-1251"?>
            <doc>
                <uid>8</uid>
                <phone id="32"
                       number="+79065544333"
                       active="0"
                       secure="0"
                       cyrillic="0"
                       valid="valid"
                       validation_date="2014-12-22 15:40:00"
                       validations_left="5"
                       autoblocked="1"
                       permblocked="0"
                       blocked="0"
                       pending_type="pending_type"
                       pending_phoneid="32" />
            </doc>
            ''',
        )
