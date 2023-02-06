# -*- coding: utf-8 -*-

from unittest import TestCase

import mock
from nose.tools import (
    assert_raises,
    eq_,
    raises,
)
from passport.backend.core.builders.yasms.exceptions import (
    YaSmsAccessDenied,
    YaSmsDeliveryError,
    YaSmsError,
    YaSmsLimitExceeded,
    YaSmsNoSender,
    YaSmsNoText,
    YaSmsPermanentBlock,
    YaSmsPhoneNumberValueError,
    YaSmsUidLimitExceeded,
    YaSmsValueError,
)
from passport.backend.core.builders.yasms.faker import (
    FakeYaSms,
    yasms_error_xml_response,
    yasms_send_sms_response,
    yasms_send_sms_response__old,
)
from passport.backend.core.builders.yasms.utils import normalize_phone_number
from passport.backend.core.builders.yasms.yasms import YaSms
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID,
    TEST_TICKET,
)
from six.moves.urllib.parse import (
    quote,
    urljoin,
)


UID = 3232
PHONE_NUMBER = u'+79010022333'
TEST_IP = u'1.2.3.4'
TEST_USER_AGENT = u'some user agent'


class TestYaSms(TestCase):
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
        self.faker = FakeYaSms()
        self.faker.start()

    def tearDown(self):
        self.faker.stop()
        self.tvm_credentials_manager.stop()
        del self.faker
        del self.tvm_credentials_manager

    def set_response(self, method, response):
        self.faker.set_response_value(method, response)

    def get_requests(self):
        return self.faker.requests

    def build_url(self, path):
        base_url = settings.YASMS_URL
        return urljoin(base_url, path)

    def _do_request(self, **kwargs):
        raise NotImplementedError()  # pragma: no cover


@with_settings(
    YASMS_URL=u'http://foo.bar/',
    YASMS_RETRIES=1,
    YASMS_SENDER=u'passport',
)
class TestYaSmsSendSms(TestYaSms):
    send_response = yasms_send_sms_response(u'127000000003456')

    def test_send_sms(self):
        self.set_response(u'send_sms', self.send_response)

        actual = self.yasms.send_sms(
            u'+79162221133',
            u'message_text',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

        eq_(actual, {u'id': 127000000003456})
        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'GET',
            url=self.build_url(u'/sendsms?sender=passport&route=validate&phone=%2B79162221133&text=message_text&utf8=1'),
        )
        requests[0].assert_headers_contain({
            'Ya-Consumer-Client-Ip': TEST_IP,
            'Ya-Client-User-Agent': TEST_USER_AGENT,
        })

    def test_send_sms_ru(self):
        self.set_response(u'send_sms', self.send_response)

        actual = self.yasms.send_sms(
            u'+79162221133',
            u'привет',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

        eq_(actual, {u'id': 127000000003456})
        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'GET',
            url=self.build_url(
                u'/sendsms?sender=passport&route=validate&phone=%2B79162221133&text={hi}&utf8=1'.format(
                    hi=quote(u'привет'.encode(u'utf-8')),
                ),
            ),
        )

    def test_send_sms_args(self):
        self.set_response(u'send_sms', self.send_response)

        self.yasms.send_sms(
            u'+79162221133',
            u'message_text',
            from_uid=123456,
            caller='caller',
            identity='identity',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'GET',
            url=self.build_url(u'/sendsms?sender=passport&phone=%2B79162221133&text=message_text&utf8=1&from_uid=123456&no_blackbox=1&route=validate&caller=caller&identity=identity'),
        )

    def test_send_sms_args_with_template_params(self):
        self.set_response(u'send_sms', self.send_response)

        self.yasms.send_sms(
            u'+79162221133',
            u'message_text {{code}}',
            dict(code='123'),
            from_uid=123456,
            caller='caller',
            identity='identity',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )

        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'POST',
            url=self.build_url(u'/sendsms?sender=passport&phone=%2B79162221133&text=message_text {{code}}&utf8=1&from_uid=123456&no_blackbox=1&route=validate&caller=caller&identity=identity'),
            post_args={'text_template_params': '{"code": "123"}'},
        )

    def test_send_sms_with_used_gates(self):
        expected_response = yasms_send_sms_response(u'127000000003456', used_gate_ids=[1, 2])
        self.set_response(u'send_sms', expected_response)

        resp = self.yasms.send_sms(
            phone_number=u'+79162221133',
            text=u'message_text',
            used_gate_ids=u'1,2',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'GET',
            url=self.build_url(u'/sendsms?sender=passport&phone=%2B79162221133&text=message_text&utf8=1&route=validate&previous_gates=1,2'),
        )
        eq_(resp, {u'id': 127000000003456, u'used_gate_ids': u'1,2'})

    def test_send_sms_old(self):
        expected_response = yasms_send_sms_response__old(u'127000000003456')
        self.set_response(u'send_sms', expected_response)

        resp = self.yasms.send_sms(
            phone_number=u'+79162221133',
            text=u'message_text',
            client_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
        )
        requests = self.get_requests()
        eq_(len(requests), 1)
        requests[0].assert_properties_equal(
            method=u'GET',
            url=self.build_url(
                u'/sendsms?sender=passport&phone=%2B79162221133&text=message_text&utf8=1&route=validate'),
        )
        eq_(resp, {u'id': 127000000003456})


@with_settings(
    YASMS_URL=u'http://foo.bar/',
    YASMS_RETRIES=1,
    YASMS_SENDER=u'passport',
)
class TestYaSmsErrors(TestYaSms):
    def make_error(self, exc, error_code, retries=1):
        self.set_response(
            u'send_sms',
            yasms_error_xml_response(
                u'Error description goes here',
                error_code,
                u'windows-1251',
            ),
        )

        with assert_raises(exc):
            self.yasms.send_sms(
                u'+79162221133',
                u'message_text',
                client_ip=TEST_IP,
                user_agent=TEST_USER_AGENT,
            )

        eq_(len(self.get_requests()), retries)

    def test_yasms_syntax_error(self):
        self.set_response(u'send_sms', u'invalid xml'.encode(u'utf-8'))

        with assert_raises(YaSmsError):
            self.yasms.send_sms(
                u'+79162221133',
                u'message_text',
                client_ip=TEST_IP,
                user_agent=TEST_USER_AGENT,
            )

        eq_(len(self.get_requests()), 1)

    def test_yasms_dontknowyou(self):
        return self.make_error(YaSmsAccessDenied, 'DONTKNOWYOU')

    def test_yasms_norights(self):
        return self.make_error(YaSmsAccessDenied, 'NORIGHTS')

    def test_yasms_badphone(self):
        return self.make_error(YaSmsPhoneNumberValueError, 'BADPHONE')

    def test_yasms_nouid(self):
        return self.make_error(YaSmsValueError, 'NOUID')

    def test_yasms_nophone(self):
        return self.make_error(YaSmsValueError, 'NOPHONE')

    def test_yasms_interror(self):
        return self.make_error(YaSmsError, 'INTERROR')

    def test_yasms_inteerror_retry(self):
        self.yasms.retries = 5
        self.make_error(YaSmsError, 'INTERROR', 5)

    def test_yasms_error_retry(self):
        self.yasms.retries = 5
        self.make_error(YaSmsError, 'FOO BAR', 1)

    def test_yasms_noroute(self):
        return self.make_error(YaSmsDeliveryError, 'NOROUTE')

    def test_yasms_permanentblock(self):
        return self.make_error(YaSmsPermanentBlock, 'PERMANENTBLOCK')

    def test_yasms_limitexceeded(self):
        return self.make_error(YaSmsLimitExceeded, 'LIMITEXCEEDED')

    def test_yasms_phoneblocked(self):
        return self.make_error(YaSmsPermanentBlock, 'PHONEBLOCKED')

    def test_yasms_notext(self):
        return self.make_error(YaSmsNoText, 'NOTEXT')

    def test_yasms_uid_limit_exceeded(self):
        return self.make_error(YaSmsUidLimitExceeded, 'UIDLIMITEXCEEDED')

    def test_yasms_bad_from_uid(self):
        return self.make_error(YaSmsValueError, 'BADFROMUID')

    def test_yasms_no_sender(self):
        return self.make_error(YaSmsNoSender, 'NOSENDER')

    @raises(ValueError)
    def test_timeout_does_not_make_sense_when_useragent_is_defined(self):
        user_agent = mock.Mock(name=u'User agent')
        YaSms(useragent=user_agent, timeout=1)


def test_normalize_phone_number():
    npn = normalize_phone_number
    eq_(npn(u'+79026411724'), u'+79026411724')
    eq_(npn(u'89026411724'), u'+79026411724')
    eq_(npn(u'9026411724'), u'+9026411724')
    eq_(npn(u'726411724'), u'+726411724')
    eq_(npn(u'+79026481'), u'+79026481')
    eq_(npn(u'6481'), u'+6481')
    eq_(npn(u''), u'')
