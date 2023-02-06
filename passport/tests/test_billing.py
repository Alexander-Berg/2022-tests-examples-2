# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.billing import (
    BaseBillingError,
    BillingInvalidResponseError,
    BillingTemporaryError,
    BillingXMLRPC,
    BillingXMLRPCFaultError,
)
from passport.backend.core.builders.billing.faker.billing import (
    billing_check_binding_response,
    billing_create_binding_response,
    billing_do_binding_response,
    billing_error_response,
    billing_list_payment_methods_response,
    billing_migrate_binding_response,
    billing_unbind_card_response,
    FakeBillingXMLRPC,
)
from passport.backend.core.builders.xmlrpc import XMLRPCRequestInfo
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.useragent.sync import RequestError
from six.moves import xmlrpc_client as xmlrpclib


TEST_TOKEN = 'token'


@with_settings(
    BILLING_XMLRPC_URL='http://yandex.ru',
    BILLING_XMLRPC_RETRIES=2,
    BILLING_XMLRPC_TIMEOUT=1,
    BILLING_TOKEN=TEST_TOKEN,
)
class TestBillingCommon(unittest.TestCase):
    def setUp(self):
        self.billing = BillingXMLRPC()
        self.response = mock.Mock()
        self.billing.useragent.request = mock.Mock(return_value=self.response)
        self.response.content = billing_list_payment_methods_response()
        self.response.status_code = 200

    def tearDown(self):
        del self.response
        del self.billing.useragent.request
        del self.billing

    def test_request_failed(self):
        self.billing.useragent.request.side_effect = RequestError
        with assert_raises(BillingTemporaryError):
            self.billing.list_payment_methods(12345, '127.0.0.1')

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'bad xml'
        with assert_raises(BillingInvalidResponseError):
            self.billing.list_payment_methods(12345, '127.0.0.1')

    def test_server_xmlrpc_fault_response(self):
        self.response.status_code = 200
        self.response.content = xmlrpclib.dumps(
            params=xmlrpclib.Fault('error', 'server error'),
            methodname='BalanceSimple.ListPaymentMethods',
            methodresponse=True,
        ).encode('utf-8')
        with assert_raises(BillingXMLRPCFaultError):
            self.billing.list_payment_methods(12345, '127.0.0.1')

    def test_internal_server_error(self):
        self.response.status_code = 500
        self.response.content = b'"server is down"'
        with assert_raises(BaseBillingError):
            self.billing.list_payment_methods(12345, '127.0.0.1')


@with_settings(
    BILLING_XMLRPC_URL='http://yandex.ru',
    BILLING_XMLRPC_RETRIES=2,
    BILLING_XMLRPC_TIMEOUT=1,
    BILLING_TOKEN=TEST_TOKEN,
    DOMAIN_KEYSPACES=(
        ('yandex.ru', 'yandex.ru'),
        ('yandex.ua', 'yandex.ua'),
    ),
)
class TestBillingMethods(unittest.TestCase):
    def setUp(self):
        self.fake_billing = FakeBillingXMLRPC()
        self.fake_billing.start()
        self.billing = BillingXMLRPC()

    def tearDown(self):
        self.fake_billing.stop()
        del self.fake_billing

    def test_list_payment_methods(self):
        self.fake_billing.set_response_value('list_payment_methods', billing_list_payment_methods_response())

        self.billing.list_payment_methods(12345, '127.0.0.1')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.ListPaymentMethods',
            (TEST_TOKEN, {'uid': '12345', 'user_ip': '127.0.0.1'}),
        )

    def test_list_payment_methods_full_params(self):
        self.fake_billing.set_response_value('list_payment_methods', billing_list_payment_methods_response())

        self.billing.list_payment_methods(12345, '127.0.0.1', ym_schema='123')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.ListPaymentMethods',
            (TEST_TOKEN, {'uid': '12345', 'user_ip': '127.0.0.1', 'ym_schema': '123'}),
        )

    def test_create_binding(self):
        self.fake_billing.set_response_value('create_binding', billing_create_binding_response())

        self.billing.create_binding(12345)

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CreateBinding',
            (TEST_TOKEN, {'uid': '12345'}),
        )

    def test_create_binding_full_params(self):
        self.fake_billing.set_response_value('create_binding', billing_create_binding_response())

        self.billing.create_binding(
            12345,
            return_path=u'http://retpath/ололо',
            back_url='http://backurl',
            timeout=10,
            currency='rur',
            region_id=223,
            lang='ru',
            template_tag='mobile',
            domain_sfx='com.tr',
        )

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CreateBinding',
            (
                TEST_TOKEN,
                {
                    'uid': '12345',
                    'return_path': u'http://retpath/ололо',
                    'back_url': 'http://backurl',
                    'timeout': 10,
                    'currency': 'rur',
                    'region_id': 223,
                    'lang': 'ru',
                    'template_tag': 'mobile',
                    'domain_sfx': 'com.tr',
                },
            ),
        )

    def test_do_binding(self):
        self.fake_billing.set_response_value('do_binding', billing_do_binding_response())

        self.billing.do_binding('purchaseToken')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.DoBinding',
            (TEST_TOKEN, {'purchase_token': 'purchaseToken'}),
        )

    def test_check_binding(self):
        self.fake_billing.set_response_value('check_binding', billing_check_binding_response())

        self.billing.check_binding('purchaseToken')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.CheckBinding',
            (TEST_TOKEN, {'purchase_token': 'purchaseToken'}),
        )

    def test_unbind_card(self):
        self.fake_billing.set_response_value('unbind_card', billing_unbind_card_response())

        self.billing.unbind_card('sessionId', '127.0.0.1', u'passport.yandex.ua', u'АйдиКарты')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.UnbindCard',
            (
                TEST_TOKEN,
                {
                    'session_id': 'sessionId',
                    'user_ip': '127.0.0.1',
                    'host': 'yandex.ua',
                    'card': u'АйдиКарты',
                },
            ),
        )

    def test_migrate_binding__ok(self):
        self.fake_billing.set_response_value(
            'migrate_binding',
            billing_migrate_binding_response(),
        )

        self.billing.migrate_binding(1, 2, u'АйдиМиграции')

        self.fake_billing.requests[0].assert_xmlrpc_method_called(
            'BalanceSimple.MigrateBinding',
            (
                TEST_TOKEN,
                {
                    'source_uid': '1',
                    'destination_uid': '2',
                    'migration_id': u'АйдиМиграции',
                },
            ),
        )

    def test_migrate_binding__fail(self):
        self.fake_billing.set_response_value(
            'migrate_binding',
            billing_error_response('migrate_binding', 'invalid_source_account'),
        )

        with assert_raises(BaseBillingError):
            self.billing.migrate_binding(1, 2, 'tadzh')

    def test_params_description_masked(self):
        params_description = self.billing.get_params_description_for_method_call(
            'call',
            (
                TEST_TOKEN,
                {
                    'session_id': 'sessionId',
                    'user_ip': '127.0.0.1',
                    'host': 'passport.yandex.ua',
                    'card': u'АйдиКарты',
                },
            ),
        )
        eq_(
            params_description,
            u'card=АйдиКарты, host=passport.yandex.ua, session_id=*****, user_ip=127.0.0.1',
        )


def test_convert_xmlrpc_request_info_to_string():
    info = XMLRPCRequestInfo(
        url='http://xmlrpc.yandex.ru/',
        get_args={'session_id': '12345'},
        post_args='<xml>',
        method_name='Api.Method',
        method_params_description='a=1, b=2',
    )
    eq_(str(info), 'url: http://xmlrpc.yandex.ru/?session_id=%2A%2A%2A%2A%2A Method: Api.Method Params: a=1, b=2')


def test_convert_xmlrpc_request_info_with_empty_args_to_string():
    info = XMLRPCRequestInfo(
        url='http://xmlrpc.yandex.ru/',
        get_args=None,
        post_args='<xml>',
        method_name='Api.Method',
        method_params_description=None,
    )
    eq_(str(info), 'url: http://xmlrpc.yandex.ru/ Method: Api.Method')
